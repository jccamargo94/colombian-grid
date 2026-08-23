
<div align="center">
  <img alt="colombian-grid logo" src="assets/logo.svg" width="70">
  <h1>Colombian Grid</h1>
  <p><i>Un paquete de Python para acceder a datos públicos del mercado eléctrico colombiano.</i></p>
</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/colombian-grid)](https://pypi.org/project/colombian-grid/)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-070394)](https://jccamargo94.github.io/colombian-grid/)

</div>

---

`colombian-grid` es una librería de Python diseñada para facilitar el acceso a datos públicos del mercado de electricidad de Colombia, consumiendo directamente el API de Paratec y XM. La librería ofrece una interfaz asíncrona para consultar datos de generadores, infraestructura de transmisión, hidrología y datos del mercado.

## Características Principales
- **Múltiples Fuentes de Datos**: Accede a datos de Paratec y XM, dos de las principales fuentes de información del mercado energético colombiano.
- **Interfaz Asíncrona**: Construida con `asyncio` y `httpx` para operaciones de I/O no bloqueantes y de alto rendimiento.
- **Validación de Datos**: Usa `Pydantic` para validar la estructura y tipos de datos de las respuestas del API (opcional).
- **Manejo Automático de Paginación**: Para consultas en rangos de fechas extensos, la librería automáticamente segmenta las peticiones para cumplir con los límites del API de XM.
- **Clientes Sincrónicos y Asincrónicos**: Ofrece flexibilidad para integrarse tanto en proyectos asíncronos como en scripts síncronos tradicionales.

## ¿Cómo empezar?
Instalar este paquete es muy sencillo. Solo necesitas ejecutar el siguiente comando:

```bash
pip install colombian-grid
```

¡Y listo! Ya puedes comenzar a usarlo en tus proyectos.

## ¿Tienes dudas o sugerencias?
Consulta nuestra [documentación](https://jccamargo94.github.io/colombian-grid/) o abre un issue en nuestro repositorio. Estamos aquí para ayudarte. 😊
