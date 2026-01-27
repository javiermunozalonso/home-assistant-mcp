---
description: Manage project dependencies correctly using uv
---

Este workflow guía la gestión de dependencias para asegurar consistencia en el entorno.

1. Para añadir una dependencia de producción (ej. `requests`):

    ```bash
    uv add requests
    ```

2. Para añadir una dependencia de desarrollo (ej. `pytest`, `ruff`):

    ```bash
    uv add --dev pytest
    ```

3. Para sincronizar el entorno tras cambios manuales en `pyproject.toml`:

    ```bash
    uv sync
    ```

4. Analiza el README.md y agrega, si es necesario, agrega la información pertinente

5. Analiza el contenido de docs para agregar la información del nuevo componente en la documentación de mkdocs
