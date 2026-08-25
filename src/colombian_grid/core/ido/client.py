"""Asynchronous client for XM's Informe Diario de Operación (IDO).

Data provenance
---------------
All endpoints consumed here belong to XM's *Informe Diario de Operación*
(IDO), the official daily operation report of the Colombian grid:

* Daily archive (``ido.xm.com.co/ArchivoIdo/...``): published every day at
  approximately 06:05 Colombia time (America/Bogota) with the *previous*
  day's data. Corrections are delivered as extra versions of the same
  archive; ``elegido`` in the raw response marks the currently selected one.
  These endpoints require no authentication.
* Coordinated dispatch (``serviciossistemareportes.xm.com.co``): anonymous
  JWT authentication against ``/api/auth/client-token``. Note that this
  service lives on a different host than the daily archive.
"""

import html
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from colombian_grid.core.base.interfaces.client import AsyncSourceClient

_COLOMBIA_TZ = ZoneInfo("America/Bogota")

_IDO_ARCHIVE_URL = "https://ido.xm.com.co/ArchivoIdo/ObtenerArchivosPorDia"

# The dispatch service lives on a different host than the daily archive.
_IDO_TOKEN_URL = "https://ido.xm.com.co/api/auth/client-token"
_DESPACHO_URL = (
    "https://serviciossistemareportes.xm.com.co/ido/XmService.svc/despachorecurso"
)

# Observed live latency for the dispatch endpoint is ~60s server-side, so a
# generous per-request timeout is required (the client default is far lower).
_DESPACHO_TIMEOUT_SECONDS = 120.0

# Verified carpeta/archivo pairs for the daily archive endpoint.
_SECTIONS = {
    "generacion": ("Ido_Generacion", "generacion"),
    "intercambios": ("Ido_Intercambios", "intercambios"),
    "disponibilidad": ("Ido_Disponibilidad", "disponibilidad"),
    "costos": ("Ido_Costos", "costos"),
}

_GENERACION_COLUMNS = [
    "fecha",
    "tipo_generacion",
    "nombrerecurso",
    "gendesp",
    "genened",
    "genprodesp",
]

# Color legend decoded from the official IDO dispatch visualization.
_COLOR_CATEGORIES = {
    "R": "Racionamientos programados en Subárea",
    "V": "Generaciones Obligatorias",
    "C": "Generación por encima del Mínimo (Seguridad)",
    "Y": "Generaciones de Seguridad",
    "P": "Generación por debajo del Máximo (Techo)",
    "N": "Techos de Generación",
    "A": "Bloques Modelo 1 y Generaciones Menores al Mínimo",
    "M": "Pruebas Autorizadas",
}

_DISPATCH_COLUMNS = [
    "recurso",
    "grupo",
    "periodo",
    "generacion",
    "agc",
    "color",
    "categoria",
]


def _now_bogota() -> datetime:
    """Current wall-clock time in Colombia's timezone (seam for tests)."""
    return datetime.now(_COLOMBIA_TZ)


def _to_iso_date(value) -> str:
    """Normalize date/datetime/ISO-string input to an ISO date string."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(str(value)).isoformat()


def _default_fecha() -> str:
    """Yesterday's date in Colombia: the latest day IDO has published data for."""
    return (_now_bogota() - timedelta(days=1)).date().isoformat()


class IdoApiError(RuntimeError):
    """Raised when the IDO service responds with a non-successful payload."""


class AsyncIdoClient(AsyncSourceClient):
    """Async client for XM's Informe Diario de Operación (IDO).

    Example:
        >>> async with AsyncIdoClient() as client:
        ...     generation = await client.generacion()          # yesterday (COT)
        ...     dispatch = await client.despacho_recurso()      # today's dispatch

    Note:
        The upstream ``ido.xm.com.co`` host serves an incomplete TLS chain;
        see the constructor's ``tls_verify`` documentation before disabling
        verification.
    """

    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        tls_verify: bool = True,
    ):
        """Initialize the async IDO client.

        Args:
            timeout: Request timeout in seconds (default: 30.0).
            max_retries: Maximum number of retries for failed requests.
            tls_verify: Keep TLS certificate verification enabled (default).
                WARNING: the ``ido.xm.com.co`` host serves an INCOMPLETE
                certificate chain (the leaf certificate is issued by
                GlobalSign RSA OV SSL CA 2018, but the intermediate is not
                sent), so standard verification fails even though browsers
                succeed. Only pass ``tls_verify=False`` as a deliberate,
                explicit workaround for that upstream misconfiguration;
                verification is never disabled silently, and users are
                encouraged to prefer ``True`` and report the issue to XM.
        """
        super().__init__(
            timeout=timeout,
            max_retries=max_retries,
            **({} if tls_verify else {"verify": False}),
        )
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    async def _ensure_token(self) -> str:
        """Acquire (and cache) an anonymous JWT for the dispatch endpoint.

        The token endpoint rejects bodyless POSTs with HTTP 411, so the
        request is sent with an explicit empty byte body, which makes httpx
        emit a ``Content-Length: 0`` header. Tokens live for ~1 hour and are
        reused across calls within this client instance.
        """
        if self._token is not None and time.monotonic() < self._token_expires_at:
            return self._token
        response = await self._http_client.post(_IDO_TOKEN_URL, data=b"")
        response.raise_for_status()
        payload = response.json()
        self._token = payload["access_token"]
        expires_in = float(payload.get("expires_in", 3600))
        self._token_expires_at = time.monotonic() + max(expires_in - 60.0, 60.0)
        return self._token

    async def _fetch_section(self, section: str, fecha: str) -> dict:
        """Fetch one daily-archive section and validate its ``ok`` flag."""
        carpeta, archivo = _SECTIONS[section]
        response = await self._http_client.get(
            _IDO_ARCHIVE_URL,
            params={"fecha": fecha, "carpeta": carpeta, "archivo": archivo},
        )
        response.raise_for_status()
        # httpx Response.json() is synchronous (unlike aiohttp).
        data = response.json()
        if data.get("ok") is not True:
            raise IdoApiError(
                f"IDO archive request failed for section '{section}' on {fecha}: "
                f"upstream returned ok={data.get('ok')!r}"
            )
        return data

    @staticmethod
    def _resolve_fecha(fecha) -> str:
        """Resolve optional user input to an ISO date string."""
        return _to_iso_date(fecha) if fecha is not None else _default_fecha()

    async def generacion(self, fecha=None) -> pd.DataFrame:
        """Fetch the daily generation archive for ``fecha``.

        Flattens the nested upstream payload into one row per resource
        observation. Subtotals (``subtotales``) are intentionally excluded to
        avoid double counting. Data for ``fecha`` is published around 06:05
        Colombia time on the following day.

        Args:
            fecha: Day to fetch (``datetime.date``, ``datetime.datetime`` or
                ISO string). Defaults to yesterday in Colombia time.

        Returns:
            DataFrame with columns: ``fecha``, ``tipo_generacion`` (upstream
            ``elemento.nombre``, e.g. "Autogeneración"), ``nombrerecurso``,
            ``gendesp``, ``genened``, ``genprodesp``.

        Raises:
            IdoApiError: If the upstream response reports ``ok=false``.
        """
        fecha_iso = self._resolve_fecha(fecha)
        data = await self._fetch_section("generacion", fecha_iso)
        payload = data.get("payload", {})
        rows = []
        for item in payload.get("items", []):
            for elemento in item.get("elemento", []):
                # Upstream ships HTML-escaped names ("Autogeneraci&oacute;n").
                tipo = html.unescape(elemento.get("nombre") or "")
                for contenido in elemento.get("contenido", []):
                    rows.append(
                        {
                            "fecha": fecha_iso,
                            "tipo_generacion": tipo,
                            "nombrerecurso": html.unescape(
                                contenido.get("nombrerecurso") or ""
                            ),
                            "gendesp": contenido.get("gendesp"),
                            "genened": contenido.get("genened"),
                            "genprodesp": contenido.get("genprodesp"),
                        }
                    )
        return pd.DataFrame(rows, columns=_GENERACION_COLUMNS)

    async def _fetch_collection(
        self, section: str, fecha: str, collections: tuple[str, ...]
    ) -> pd.DataFrame:
        """Flatten list-shaped payload collections into one row per entry.

        Source field names are preserved as-is; for sections with more than
        one collection (e.g. intercambios) a ``direccion`` discriminator
        column marks the origin of each row.
        """
        data = await self._fetch_section(section, fecha)
        payload = data.get("payload", {})
        rows = []
        for collection in collections:
            entries = payload.get(collection, [])
            if isinstance(entries, dict):
                entries = [entries]
            for entry in entries or []:
                row: dict = {"fecha": fecha}
                if len(collections) > 1:
                    row["direccion"] = collection
                row.update(entry)
                rows.append(row)
        if not rows:
            leading = ["fecha", "direccion"] if len(collections) > 1 else ["fecha"]
            return pd.DataFrame(columns=leading)
        frame = pd.DataFrame(rows)
        leading = [
            column for column in ("fecha", "direccion") if column in frame.columns
        ]
        return frame[leading + [c for c in frame.columns if c not in leading]]

    async def intercambios(self, fecha=None) -> pd.DataFrame:
        """Fetch the daily international exchanges archive for ``fecha``.

        The upstream payload nests one country-level list per direction;
        this method explodes it into one row per country and direction.

        Args:
            fecha: Day to fetch (``date``/``datetime``/ISO string); defaults
                to yesterday in Colombia time.

        Returns:
            Long-format DataFrame with columns: ``fecha``, ``direccion``
            ("exportaciones"/"importaciones"), ``pais``, ``programada`` and
            ``real``. Per-direction totals are exposed via
            ``df.attrs["totales"]`` keyed by direction.

        Raises:
            IdoApiError: If the upstream response reports ``ok=false``.
        """
        data = await self._fetch_section("intercambios", self._resolve_fecha(fecha))
        payload = data.get("payload", {})
        rows = []
        totales: dict[str, dict] = {}
        for direccion in ("exportaciones", "importaciones"):
            entries = payload.get(direccion, [])
            if isinstance(entries, dict):
                entries = [entries]
            totales[direccion] = {}
            for entry in entries or []:
                totales[direccion] = {
                    k: v for k, v in entry.items() if not isinstance(v, list)
                }
                for link in entry.get("intercambios", []) or []:
                    rows.append(
                        {
                            "fecha": data.get("fecha"),
                            "direccion": direccion,
                            "pais": link.get("pais"),
                            "programada": link.get("programada"),
                            "real": link.get("real"),
                        }
                    )
        frame = pd.DataFrame(
            rows, columns=["fecha", "direccion", "pais", "programada", "real"]
        )
        frame.attrs["totales"] = totales
        return frame

    async def disponibilidad(self, fecha=None) -> pd.DataFrame:
        """Fetch the daily availability archive for ``fecha``.

        Each availability category (``tipogen``) carries a nested resource
        list; this method explodes it into one row per resource.

        Args:
            fecha: Day to fetch (``date``/``datetime``/ISO string); defaults
                to yesterday in Colombia time.

        Returns:
            DataFrame with columns: ``fecha``, ``tipogen``,
            ``nombrerecurso``, ``capacidadefectiva``, ``disponibilidad``,
            ``porcentaje`` plus per-category ``subtotal`` and
            ``subtotal_capefectiva`` repeated on each row of that category.

        Raises:
            IdoApiError: If the upstream response reports ``ok=false``.
        """
        data = await self._fetch_section("disponibilidad", self._resolve_fecha(fecha))
        payload = data.get("payload", {})
        rows = []
        categories = payload.get("categoriasdisponibilidad", [])
        if isinstance(categories, dict):
            categories = [categories]
        for category in categories or []:
            subtotal = category.get("subtotal")
            subtotal_cap = category.get("subtotal_capefectiva")
            tipogen = category.get("tipogen") or category.get("tipo")
            for record in category.get("registrodisponibilidad", []) or []:
                rows.append(
                    {
                        "fecha": data.get("fecha"),
                        "tipogen": tipogen,
                        "nombrerecurso": html.unescape(
                            record.get("nombrerecurso") or ""
                        ),
                        "capacidadefectiva": record.get("capacidadefectiva"),
                        "disponibilidad": record.get("disponibilidad"),
                        "porcentaje": record.get("porcentaje"),
                        "subtotal": subtotal,
                        "subtotal_capefectiva": subtotal_cap,
                    }
                )
        return pd.DataFrame(
            rows,
            columns=[
                "fecha",
                "tipogen",
                "nombrerecurso",
                "capacidadefectiva",
                "disponibilidad",
                "porcentaje",
                "subtotal",
                "subtotal_capefectiva",
            ],
        )

    async def costos(self, fecha=None) -> pd.DataFrame:
        """Fetch the daily costs archive for ``fecha``.

        Args:
            fecha: Day to fetch (``date``/``datetime``/ISO string); defaults
                to yesterday in Colombia time.

        Returns:
            DataFrame with a ``fecha`` column followed by the source fields
            of each cost entry.

        Raises:
            IdoApiError: If the upstream response reports ``ok=false``.
        """
        return await self._fetch_collection(
            "costos", self._resolve_fecha(fecha), ("costos",)
        )

    async def despacho_recurso(self) -> pd.DataFrame:
        """Fetch today's coordinated resource dispatch.

        This endpoint deliberately accepts NO date parameter: it was verified
        that the service ignores any ``fecha`` argument (byte-identical
        responses across several formats) and always returns the CURRENT
        day's program. Accepting a date parameter would therefore be
        misleading. Data arrives in 24 hourly periods.

        Returns:
            Long-format DataFrame with columns:

            - ``recurso``: resource name (upstream ``nombre_recurso``).
            - ``grupo``: group the resource belongs to (may be null).
            - ``periodo``: hour of the day as int (1-24).
            - ``generacion``: dispatched generation in kWh.
            - ``agc``: AGC (automatic generation control) value.
            - ``color``: status letter from the visualization (or null).
            - ``categoria``: human-readable meaning of the color letter;
              None when the color is null or unknown.

            Report metadata is exposed via ``df.attrs["globales"]``
            (e.g. ``codigo``, ``descripcion``, ``version``).
        """
        token = await self._ensure_token()
        response = await self._http_client.get(
            _DESPACHO_URL,
            headers={"Authorization": f"Bearer {token}"},
            # This endpoint has been observed taking ~60s server-side.
            timeout=_DESPACHO_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        # httpx Response.json() is synchronous (unlike aiohttp).
        data = response.json()
        rows = []
        for category in data.get("categoriasdespachorecurso", []):
            recurso = category.get("nombre_recurso")
            grupo = category.get("grupo")
            for record in category.get("registrodespachorecurso", []):
                color = record.get("color")
                rows.append(
                    {
                        "recurso": recurso,
                        "grupo": grupo,
                        "periodo": int(record["periodo"]),
                        "generacion": float(record["generacion"]),
                        "agc": float(record["agc"]),
                        "color": color,
                        "categoria": _COLOR_CATEGORIES.get(color) if color else None,
                    }
                )
        dispatch = pd.DataFrame(rows, columns=_DISPATCH_COLUMNS)
        dispatch.attrs["globales"] = data.get("globales", {})
        return dispatch
