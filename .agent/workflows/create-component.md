---
description: Create a new component following DDD and SOLID principles
---

Este workflow guía la creación de nuevas funcionalidades asegurando el cumplimiento de las reglas de arquitectura.

1. Identifica la capa a la que pertenece el componente (Domain, Application, Infrastructure, UI).

2. Crea el fichero de la clase en la ubicación correcta usando snake_case.
    Ejemplo: `src/domain/new_entity.py`

    ```bash
    touch src/domain/new_entity.py
    ```

3. Define la clase asegurando:
    - Principio de Responsabilidad Única (SRP).
    - Documentación (docstrings) para la clase y cada método.
    - Type hints estrictos.

4. Crea el fichero de test correspondiente en la estructura espejo de `tests/`.
    Ejemplo: `tests/domain/test_new_entity.py`

    ```bash
    touch tests/domain/test_new_entity.py
    ```

5. Implementa los tests cubriendo casos de éxito y error.

6. Lanza los tests para verificar.
    // turbo

    ```bash
    uv run pytest
    ```

7. Analiza el README.md y agrega, si es necesario, agrega la información pertinente

8. Analiza el contenido de docs para agregar la información del nuevo componente en la documentación de mkdocs
