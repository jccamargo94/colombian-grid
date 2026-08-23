<div align="center">
  <img alt="colombian-grid logo" src="./docs/assets/logo.svg" width="70">
  <h1>Colombian Grid</h1>
  <p><i>Consulta, extrae y procesa datos públicos del mercado eléctrico colombiano con Python.</i></p>
</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/colombian-grid)](https://pypi.org/project/colombian-grid/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-070394)](https://jccamargo94.github.io/colombian-grid/)

</div>

---

## Acerca del Proyecto

`colombian-grid` es una librería de Python que ofrece una interfaz simple y asíncrona para acceder y procesar datos públicos del mercado eléctrico colombiano. Actualmente implementa dos fuentes de datos:

- **[Paratec](https://paratec.xm.com.co/)**: datos de infraestructura — generadores, líneas de transmisión, subestaciones e hidrología.
- **[XM](https://www.xm.com.co/)**: datos de mercado — generación, demanda, precios y otras métricas, con segmentación automática de rangos de fechas y salida en `DataFrame` de pandas.

### Características Principales

- 🔌 **Múltiples Fuentes de Datos**: APIs de Paratec (infraestructura) y XM (datos de mercado)
- ⚡ **Clientes Asíncronos y Síncronos**: clientes asíncronos para alto rendimiento, más un cliente síncrono de XM para scripts simples
- 🤖 **Segmentación Automática**: las peticiones a XM dividen automáticamente los rangos de fechas extensos para respetar los límites del API
- 🔁 **Lógica de Reintentos Integrada**: backoff exponencial con jitter para errores transitorios
- 📊 **Integración con Pandas**: los datos de XM se devuelven como DataFrames de pandas para facilitar el análisis
- ✅ **Type Safety**: totalmente tipado (incluye un marcador `py.typed`), con validación opcional de esquemas Pydantic

## Instalación

### PyPI

```bash
pip install colombian-grid
```

## Inicio Rápido

Importa los clientes desde el paquete raíz:

```python
from colombian_grid import AsyncParatecClient, AsyncXMClient, SyncXMClient
```

### API de XM - Datos de Mercado

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Obtener datos de generación del sistema
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        print(data.head())

asyncio.run(main())
```

`SyncXMClient` ofrece la misma interfaz `get_data(...)` / `get_available_metrics()` para scripts no asíncronos, usando `with SyncXMClient() as client: ...`.

### API de Paratec - Datos de Infraestructura

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        # Obtener datos de generadores
        generators = await client.get_generation_data()
        print(f"Se encontraron {len(generators)} generadores")

        # También disponibles: get_substation_data(), get_transmission_line_data(), get_hydro_data()

asyncio.run(main())
```

Tanto `AsyncParatecClient` como `AsyncXMClient` aceptan los argumentos opcionales `timeout` y `max_retries` en su constructor, y soportan el gestor de contexto `async with`, que cierra automáticamente la conexión HTTP subyacente.

## Documentación

Para guías completas, referencia del API y ejemplos, visita nuestro [sitio de documentación](https://jccamargo94.github.io/colombian-grid/).

### Construir la Documentación Localmente

```bash
# Instalar dependencias de documentación
uv pip install mkdocs mkdocs-material "mkdocstrings[python]" mkdocs-static-i18n

# Construir y servir la documentación
uv run mkdocs serve
```

La documentación estará disponible en `http://127.0.0.1:8000`.

## Desarrollo

Este proyecto usa `uv` para la gestión de dependencias. Para configurar un entorno de desarrollo:

```bash
# Clonar el repositorio
git clone https://github.com/jccamargo94/colombian-grid.git
cd colombian-grid

# Instalar dependencias
uv sync

# Ejecutar pruebas
uv run pytest

# Ejecutar pre-commit hooks
uv run pre-commit run --all-files
```

## Licencia

Distribuido bajo la Licencia MIT. Ver [`LICENSE`](LICENSE) para más detalles.

## ¿Tienes dudas o sugerencias?

Consulta nuestra [documentación](https://jccamargo94.github.io/colombian-grid/) o abre un issue en nuestro repositorio. Estamos aquí para ayudarte. 😊
