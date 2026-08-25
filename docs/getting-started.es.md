# Comenzando

`colombian-grid` te permite consultar datos públicos del mercado eléctrico colombiano (Paratec, XM e IDO) desde Python, sin tener que lidiar directamente con las APIs REST subyacentes.

## Instalación

Con `pip`:

```bash
pip install colombian-grid
```

Con `uv`:

```bash
uv add colombian-grid
```

## Importando los clientes

Todos los clientes se pueden importar directamente desde el paquete raíz:

```python
from colombian_grid import AsyncIdoClient, AsyncParatecClient, AsyncXMClient, SyncXMClient
```

## API de XM — datos de mercado

El API de XM provee datos del mercado eléctrico (generación, demanda, precios, etc.). Hay dos clientes disponibles: uno asíncrono (`AsyncXMClient`, recomendado) y uno síncrono (`SyncXMClient`), ambos con la misma interfaz.

### Cliente asíncrono

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        print("Generación del Sistema (Enero 2024):")
        print(data.head())

asyncio.run(main())
```

### Cliente síncrono

Ideal para scripts simples que no requieren concurrencia:

```python
from datetime import date
from colombian_grid import SyncXMClient

with SyncXMClient() as client:
    data = client.get_data(
        metric="DemaReal",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
    )
    print("Demanda Real del Sistema (Enero 2024):")
    print(data.head())
```

## API de Paratec — datos de infraestructura

El API de Paratec provee datos sobre la infraestructura del sistema eléctrico: generadores, subestaciones, líneas de transmisión e hidrología. Solo tiene cliente asíncrono (`AsyncParatecClient`).

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        generadores = await client.get_generation_data()
        print(f"Se encontraron {len(generadores)} generadores.")

        subestaciones = await client.get_substation_data()
        print(f"Se encontraron {len(subestaciones)} subestaciones.")

asyncio.run(main())
```

`AsyncParatecClient` implementa `async with`, así que la conexión HTTP subyacente se cierra automáticamente al salir del bloque — no necesitas cerrarla manualmente.

## API de IDO — Informe Diario de Operación

El [Informe Diario de Operación (IDO)](https://ido.xm.com.co/) de XM resume la operación diaria del sistema: generación, intercambios internacionales, disponibilidad, costos y despacho coordinado. Solo tiene cliente asíncrono (`AsyncIdoClient`). Por defecto las consultas devuelven el día anterior en hora de Colombia, ya que el IDO publica los datos del día previo alrededor de las 06:05 (hora colombiana), con correcciones que llegan como nuevas versiones (V1, V2...).

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        generacion = await client.generacion()      # ayer (hora Colombia)
        despacho = await client.despacho_recurso()  # despacho del día en curso
        print(f"Registros de generación: {len(generacion)}")

asyncio.run(main())
```

Ten en cuenta:

- El servidor `ido.xm.com.co` sirve una cadena de certificados TLS incompleta (una configuración errónea conocida del proveedor), por lo que la verificación TLS estándar falla. Si lo necesitas, pasa `tls_verify=False` al constructor como solución explícita y deliberada; preferimos que mantengas la verificación activa y reportes el problema a XM.
- `despacho_recurso()` no acepta fecha: el servicio ignora cualquier parámetro de fecha y siempre devuelve el despacho coordinado del día actual. Además es un endpoint lento (puede tardar cerca de un minuto); el cliente ya aplica internamente un timeout mayor para él.

`AsyncIdoClient` también implementa `async with`, así que la conexión HTTP subyacente se cierra automáticamente al salir del bloque.

## Próximos pasos

- Revisa la sección de [Ejemplos](examples.md) para ver más casos de uso, incluyendo subestaciones y líneas de transmisión.
- Consulta la [Referencia API](api-reference.md) para ver la firma completa de cada método.
