# Ejemplos de Uso

Aquí encontrarás ejemplos prácticos de cómo utilizar `colombian-grid` para diferentes casos de uso.

## API de XM

### Ejemplo 1: Obtener Métricas Disponibles

Antes de solicitar datos, puedes consultar todas las métricas que ofrece el API de XM.

```python
import asyncio
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        metrics = await client.get_available_metrics()
        print("Métricas disponibles en el API de XM:")
        print(metrics[["MetricId", "MetricName", "Entity", "MaxDays"]])

asyncio.run(main())
```

### Ejemplo 2: Consultar Generación por Recurso con Filtros

Puedes filtrar los datos por códigos de recursos específicos (por ejemplo, plantas de generación).

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Consultar generación para las plantas GUAJIRA1 y GUAJIRA2
        data = await client.get_data(
            metric="Gene",
            entity="Recurso",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            filter_by=["GUAJIRA1", "GUAJIRA2"],
        )
        print("Generación para GUAJIRA1 y GUAJIRA2:")
        print(data)

asyncio.run(main())
```

### Ejemplo 3: Consulta Síncrona de Precios de Bolsa

Si prefieres un enfoque síncrono, puedes usar `SyncXMClient`.

```python
from datetime import date
from colombian_grid import SyncXMClient

with SyncXMClient() as client:
    precio_bolsa = client.get_data(
        metric="PrecBolsNaci",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
    )
    print("Precio de Bolsa Nacional (primeros 10 días de Enero 2024):")
    print(precio_bolsa)
```

## API de Paratec

### Ejemplo 4: Datos de Generadores e Hidrología

Consulta datos sobre generadores y registros hidrológicos.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        generadores = await client.get_generation_data()
        print(f"Total de generadores: {len(generadores)}")

        hidrologia = await client.get_hydro_data()
        print(f"Registros de hidrología: {len(hidrologia)}")

asyncio.run(main())
```

### Ejemplo 5: Datos de Subestaciones

Consulta el listado de subestaciones registradas en Paratec.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        subestaciones = await client.get_substation_data()
        print(f"Total de subestaciones: {len(subestaciones)}")
        print(subestaciones[0])

asyncio.run(main())
```

### Ejemplo 6: Datos de Líneas de Transmisión

Consulta el listado de líneas de transmisión.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        lineas = await client.get_transmission_line_data()
        print(f"Total de líneas de transmisión: {len(lineas)}")
        print(lineas[0])

asyncio.run(main())
```

!!! tip
    Todos los métodos de `AsyncParatecClient` (`get_generation_data`, `get_substation_data`, `get_transmission_line_data`, `get_hydro_data`) se pueden llamar dentro del mismo bloque `async with`, reutilizando la misma conexión HTTP.

## API de IDO

### Ejemplo 7: Generación del Día Anterior

El archivo diario de generación del Informe Diario de Operación (IDO). Sin argumentos devuelve el día anterior en hora de Colombia; también acepta `datetime.date`, `datetime.datetime` o un string ISO.

```python
import asyncio
from datetime import date
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        # Ayer en hora de Colombia (los datos se publican ~06:05 COT)
        ayer = await client.generacion()
        print(ayer.head())

        # O una fecha concreta
        especifica = await client.generacion(date(2026, 7, 15))
        print(especifica[["fecha", "tipo_generacion", "nombrerecurso", "gendesp"]].head())

asyncio.run(main())
```

Cada fila es una observación por recurso (`nombrerecurso`) y tipo de generación (`tipo_generacion`), con las columnas `gendesp`, `genened` y `genprodesp`. Los subtotales se excluyen a propósito para evitar dobles conteos.

### Ejemplo 8: Intercambios Internacionales con Totales

Los intercambios internacionales con países vecinos llegan en formato largo, con una fila por país y dirección. Estos datos no están disponibles a través del API pública de XM.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        intercambios = await client.intercambios()
        print(intercambios[["direccion", "pais", "programada", "real"]])

        # Totales por dirección ("exportaciones" / "importaciones")
        totales = intercambios.attrs["totales"]
        print(totales["exportaciones"])

asyncio.run(main())
```

La columna `direccion` distingue entre `"exportaciones"` e `"importaciones"`; los totales de cada dirección viajan en `df.attrs["totales"]`.

### Ejemplo 9: Disponibilidad por Recurso

La disponibilidad declara, por categoría de generación (`tipogen`), la capacidad efectiva y la disponibilidad de cada recurso.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        disponibilidad = await client.disponibilidad()

        # Los subtotales se repiten en cada fila de su categoría;
        # tómalos una vez por categoría:
        print(
            disponibilidad.groupby("tipogen")[
                ["subtotal", "subtotal_capefectiva"]
            ].first()
        )

asyncio.run(main())
```

Además de `subtotal` y `subtotal_capefectiva`, cada fila trae `capacidadefectiva`, `disponibilidad` y `porcentaje`.

### Ejemplo 10: Despacho Coordinado del Día

`despacho_recurso()` devuelve el programa de despacho coordinado del día en curso, en 24 periodos horarios. Ojo: el endpoint es lento y puede tardar cerca de un minuto en responder — ten paciencia. No recibe fecha porque el servicio siempre devuelve el día actual.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        despacho = await client.despacho_recurso()
        print(despacho[["recurso", "periodo", "generacion", "color", "categoria"]].head())

        # Metadatos del reporte (codigo, descripcion, version)
        print(despacho.attrs["globales"])

asyncio.run(main())
```

La columna `color` replica la letra de estado del tablero oficial del IDO (R, V, C, Y, P, N, A, M) y `categoria` traduce esa letra a su significado legible (por ejemplo, `"Racionamientos programados en Subárea"`); vale `None` cuando el color es nulo o desconocido.
