# API Reference

This section contains the technical reference for the main classes and methods of `colombian-grid`, generated automatically from the source code's docstrings.

## Module `colombian_grid.core.xm`

::: colombian_grid.core.xm.AsyncXMClient
    handler: python
    options:
      members:
        - get_available_metrics
        - get_data

::: colombian_grid.core.xm.SyncXMClient
    handler: python
    options:
      members:
        - get_available_metrics
        - get_data

## Module `colombian_grid.core.paratec`

::: colombian_grid.core.paratec.AsyncParatecClient
    handler: python
    options:
      members:
        - get_generation_data
        - get_substation_data
        - get_transmission_line_data
        - get_hydro_data

## Module `colombian_grid.core.ido`

::: colombian_grid.core.ido.AsyncIdoClient
    handler: python
    options:
      members:
        - __init__
        - generacion
        - intercambios
        - disponibilidad
        - costos
        - despacho_recurso
