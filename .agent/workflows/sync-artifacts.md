---
description: Sync generated artifacts to the planning directory
---

Este workflow automatiza la copia de artefactos generados (tasks, planes) a la carpeta `planning/` en la raíz del repositorio, manteniendo un histórico.

1. Asegúrate de que existe la carpeta `planning` en la raíz del repositorio.
    // turbo

    ```bash
    mkdir -p planning
    ```

2. Copia los artefactos actuales a una nueva carpeta con timestamp dentro de `planning/`.
    Reemplaza `[UUID]` con el UUID de la sesión actual de Antigravity (carpeta en `.gemini/antigravity/brain/`).
    // turbo

    ```bash
    UUID="26eb60c6-0e0f-4712-9fa2-ca366b97e540"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    SOURCE_DIR="$HOME/.gemini/antigravity/brain/$UUID"
    DEST_DIR="planning/$UUID/$TIMESTAMP"

    mkdir -p "$DEST_DIR"
    cp "$SOURCE_DIR"/*.md "$DEST_DIR/"
    echo "Artifacts copied to $DEST_DIR"
    ```
