"""
Tests for the IDO client (XM Informe Diario de Operación).

All HTTP traffic is mocked at the AsyncHttpClient boundary, mirroring the
approach used in tests/xm and tests/httpx. No live network access happens.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import httpx
import pandas as pd
import pytest

from colombian_grid.core.ido.client import AsyncIdoClient, IdoApiError
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient

IDO_ARCHIVE_URL = "https://ido.xm.com.co/ArchivoIdo/ObtenerArchivosPorDia"
IDO_TOKEN_URL = "https://ido.xm.com.co/api/auth/client-token"
DESPACHO_URL = (
    "https://serviciossistemareportes.xm.com.co/ido/XmService.svc/despachorecurso"
)

AUTH_FIXTURE = {
    "access_token": "jwt-token",
    "token_type": "Bearer",
    "expires_in": 3600,
}

# Realistic dispatch fixture based on the verified upstream response shape.
DESPACHO_FIXTURE = {
    "globales": {
        "codigo": "DE0000035129",
        "descripcion": "Despacho Coordinado",
        "version": "V1",
    },
    "categoriasdespachorecurso": [
        {
            "grupo": None,
            "nombre_recurso": "AGUA FRESCA",
            "registrodespachorecurso": [
                {"agc": 0.0, "color": None, "generacion": 3.3, "periodo": "1"},
                {"agc": 1.1, "color": "P", "generacion": 4.4, "periodo": "2"},
            ],
            "total": 7.7,
        },
        {
            "grupo": "TERMICA",
            "nombre_recurso": "TERMOVALLE",
            "registrodespachorecurso": [
                {"agc": 0.0, "color": "Z", "generacion": 9.9, "periodo": "24"}
            ],
            "total": 9.9,
        },
    ],
}


def _mock_response(json_data):
    """Build a mock httpx.Response like the existing XM/HTTPX tests do."""
    response = AsyncMock()
    response.status_code = 200
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=json_data)
    return response


# Realistic nested fixture based on the verified upstream payload shape:
# {"ok": ..., "payload": {"globales": ..., "items": [{"elemento": [...], "subtotales": ...}]}}
GENERACION_FIXTURE = {
    "ok": True,
    "fecha": "2026-08-23",
    "versiones": [{"nombre": "IDOR_20260823_V1", "ver": 1}],
    "elegido": {"nombre": "IDOR_20260823_V1", "ver": 1},
    "payload": {
        "globales": {"fechaPublicacion": "2026-08-24"},
        "items": [
            {
                "elemento": [
                    {
                        "nombre": "Autogeneración",
                        "contenido": [
                            {
                                "gendesp": 1.5,
                                "genened": 2.0,
                                "genprodesp": 1.8,
                                "nombrerecurso": "RECURSO A",
                            },
                            {
                                "gendesp": 0.0,
                                "genened": 0.5,
                                "genprodesp": 0.0,
                                "nombrerecurso": "RECURSO B",
                            },
                        ],
                    },
                    {
                        "nombre": "Generación Cogenerador",
                        "contenido": [
                            {
                                "gendesp": 3.25,
                                "genened": 3.25,
                                "genprodesp": 3.0,
                                "nombrerecurso": "RECURSO C",
                            }
                        ],
                    },
                ],
                "subtotales": [{"nombre": "Autogeneración", "total": 2.5}],
            }
        ],
    },
}


class TestFamilyADailyArchive:
    @pytest.mark.asyncio
    async def test_generacion_flattens_nested_payload(self):
        """generacion() returns one tidy row per resource observation."""
        with patch.object(
            AsyncHttpClient,
            "get",
            return_value=_mock_response(GENERACION_FIXTURE),
        ) as mock_get:
            async with AsyncIdoClient() as client:
                df = await client.generacion("2026-08-23")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == [
            "fecha",
            "tipo_generacion",
            "nombrerecurso",
            "gendesp",
            "genened",
            "genprodesp",
        ]

        first = df.iloc[0]
        assert first["fecha"] == "2026-08-23"
        assert first["tipo_generacion"] == "Autogeneración"
        assert first["nombrerecurso"] == "RECURSO A"
        assert first["gendesp"] == 1.5
        assert first["genened"] == 2.0
        assert first["genprodesp"] == 1.8

        cogenerador = df[df["tipo_generacion"] == "Generación Cogenerador"]
        assert len(cogenerador) == 1
        assert cogenerador.iloc[0]["nombrerecurso"] == "RECURSO C"

        # The upstream request must target the daily archive endpoint with
        # the right carpeta/archivo pair for the generacion section.
        request_url = mock_get.call_args.args[0]
        assert request_url == IDO_ARCHIVE_URL
        assert mock_get.call_args.kwargs["params"] == {
            "fecha": "2026-08-23",
            "carpeta": "Ido_Generacion",
            "archivo": "generacion",
        }

    @pytest.mark.asyncio
    async def test_generacion_raises_on_ok_false(self):
        """An ok:false archive response raises a clear IdoApiError."""
        with patch.object(
            AsyncHttpClient,
            "get",
            return_value=_mock_response({"ok": False, "fecha": "2099-01-01"}),
        ):
            async with AsyncIdoClient() as client:
                with pytest.raises(IdoApiError, match="generacion"):
                    await client.generacion("2099-01-01")

    @pytest.mark.asyncio
    async def test_generacion_accepts_datetime_and_defaults_to_yesterday_bogota(self):
        """datetime input is normalized; missing fecha defaults to yesterday in COT."""
        fixed_now = datetime(2026, 8, 24, 5, 30, tzinfo=ZoneInfo("America/Bogota"))
        with (
            patch("colombian_grid.core.ido.client._now_bogota", return_value=fixed_now),
            patch.object(
                AsyncHttpClient,
                "get",
                return_value=_mock_response(GENERACION_FIXTURE),
            ) as mock_get,
        ):
            async with AsyncIdoClient() as client:
                await client.generacion(datetime(2026, 8, 23, 13, 0))
                await client.generacion()

        requested = [call.kwargs["params"]["fecha"] for call in mock_get.call_args_list]
        assert requested == ["2026-08-23", "2026-08-23"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method,archivo,carpeta,collections",
        [
            (
                "intercambios",
                "intercambios",
                "Ido_Intercambios",
                ["exportaciones", "importaciones"],
            ),
            (
                "disponibilidad",
                "disponibilidad",
                "Ido_Disponibilidad",
                ["categoriasdisponibilidad"],
            ),
            ("costos", "costos", "Ido_Costos", ["costos"]),
        ],
    )
    async def test_other_sections_return_tidy_rows(
        self, method, archivo, carpeta, collections
    ):
        """Remaining archive sections flatten to one row per upstream entry."""
        payload = {
            key: [{"nombre": f"entry-{key}", "valor": 1.0}] for key in collections
        }
        fixture = {
            "ok": True,
            "fecha": "2026-08-23",
            "payload": {"globales": {}, **payload},
        }
        with patch.object(
            AsyncHttpClient,
            "get",
            return_value=_mock_response(fixture),
        ) as mock_get:
            async with AsyncIdoClient() as client:
                df = await getattr(client, method)("2026-08-23")

        assert mock_get.call_args.kwargs["params"] == {
            "fecha": "2026-08-23",
            "carpeta": carpeta,
            "archivo": archivo,
        }
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(collections)
        leading = ["fecha", "direccion"] if method == "intercambios" else ["fecha"]
        assert list(df.columns)[: len(leading)] == leading
        assert df.iloc[-1]["nombre"] == f"entry-{collections[-1]}"


class TestDespachoRecurso:
    @pytest.mark.asyncio
    async def test_authenticates_with_empty_body_and_bearer_header(self):
        """Auth POST carries an empty body; dispatch GET carries the Bearer token.

        The token endpoint answers HTTP 411 unless the request is sent with an
        explicit (empty) body, so Content-Length: 0 must reach the wire.
        """
        with (
            patch.object(
                AsyncHttpClient, "post", return_value=_mock_response(AUTH_FIXTURE)
            ) as mock_post,
            patch.object(
                AsyncHttpClient, "get", return_value=_mock_response(DESPACHO_FIXTURE)
            ) as mock_get,
        ):
            async with AsyncIdoClient() as client:
                await client.despacho_recurso()

        assert mock_post.call_args.args[0] == IDO_TOKEN_URL
        post_kwargs = mock_post.call_args.kwargs
        assert post_kwargs.get("data") == b""
        wire_request = httpx.Request("POST", IDO_TOKEN_URL, **post_kwargs)
        assert wire_request.headers["Content-Length"] == "0"

        assert mock_get.call_args.args[0] == DESPACHO_URL
        assert (
            mock_get.call_args.kwargs["headers"]["Authorization"] == "Bearer jwt-token"
        )

    @pytest.mark.asyncio
    async def test_reuses_cached_token_across_calls(self):
        """Two dispatch calls trigger a single token acquisition."""
        with (
            patch.object(
                AsyncHttpClient, "post", return_value=_mock_response(AUTH_FIXTURE)
            ) as mock_post,
            patch.object(
                AsyncHttpClient, "get", return_value=_mock_response(DESPACHO_FIXTURE)
            ),
        ):
            async with AsyncIdoClient() as client:
                await client.despacho_recurso()
                await client.despacho_recurso()

        assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_flattens_dispatch_with_color_categories(self):
        """Rows are long-format; color letters decode to categoria; nulls stay null."""
        with (
            patch.object(
                AsyncHttpClient, "post", return_value=_mock_response(AUTH_FIXTURE)
            ),
            patch.object(
                AsyncHttpClient, "get", return_value=_mock_response(DESPACHO_FIXTURE)
            ),
        ):
            async with AsyncIdoClient() as client:
                df = await client.despacho_recurso()

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == [
            "recurso",
            "grupo",
            "periodo",
            "generacion",
            "agc",
            "color",
            "categoria",
        ]
        assert len(df) == 3

        first = df.iloc[0]
        assert first["recurso"] == "AGUA FRESCA"
        assert pd.isna(first["grupo"])
        assert int(first["periodo"]) == 1
        assert first["generacion"] == pytest.approx(3.3)
        assert first["agc"] == pytest.approx(0.0)
        assert pd.isna(first["color"])
        assert pd.isna(first["categoria"])

        flagged = df[df["color"] == "P"].iloc[0]
        assert flagged["categoria"] == "Generación por debajo del Máximo (Techo)"
        assert flagged["periodo"] == 2

        unknown = df[df["color"] == "Z"].iloc[0]
        assert unknown["recurso"] == "TERMOVALLE"
        assert unknown["grupo"] == "TERMICA"
        assert unknown["periodo"] == 24
        assert pd.isna(unknown["categoria"])

        # Upstream report metadata is exposed alongside the observations.
        assert df.attrs["globales"]["codigo"] == "DE0000035129"
        assert df.attrs["globales"]["descripcion"] == "Despacho Coordinado"


class TestConfigurationAndExports:
    def test_tls_verify_false_applies_only_to_ido_requests(self):
        """tls_verify=False plumbs verify=False into this client's HTTP stack."""
        insecure = AsyncIdoClient(tls_verify=False)
        secure = AsyncIdoClient()

        assert insecure._http_client.kwargs.get("verify") is False
        assert "verify" not in secure._http_client.kwargs

    def test_async_ido_client_is_exported_from_package_root(self):
        import colombian_grid

        assert colombian_grid.AsyncIdoClient is AsyncIdoClient
        assert "AsyncIdoClient" in colombian_grid.__all__
