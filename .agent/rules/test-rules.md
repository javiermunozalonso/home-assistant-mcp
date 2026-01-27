---
trigger: always_on
---

# Reglas para la implementación de tests

## 1. Objetivo

Definir unas normas claras para organizar y clasificar los tests de Python usando una **estructura híbrida**:

* Separar por **tipo de test** (`unit`, `integration`, `e2e`).
* Dentro de cada tipo, **espejar la estructura** de `src/` (lo que tú ya haces) cuando tenga sentido.

---

## 2. Estructura de directorios (obligatoria)

1. El código de producción debe vivir bajo `src/`:

```text
src/
  <nombre_proyecto>/
    ...
```

1. Todos los tests deben vivir bajo el directorio raíz `tests/`, con división por tipo:

```text
tests/
  unit/
  integration/
  e2e/
```

1. Dentro de `tests/unit/` se debe **respetar la estructura de carpetas de `src/`**:

```text
src/
  myproj/
    auth/
      login.py
    payments/
      gateway.py

tests/
  unit/
    auth/
      test_login.py
    payments/
      test_gateway.py
```

1. En `tests/integration/` y `tests/e2e/`:

   * Se **puede** espejar la estructura de `src/` si es útil.
   * O bien agrupar por funcionalidad / flujo de negocio. Ejemplo:

```text
tests/
  integration/
    auth/
      test_auth_flows.py
    payments/
      test_payments_with_db.py
  e2e/
    test_full_checkout_flow.py
```

---

## 3. Convenciones de nombres de ficheros y tests

1. Todos los ficheros de test deben seguir el patrón:

* `test_*.py` (recomendado), o
* `*_test.py` (pero hay que elegir uno y usarlo SIEMPRE; por defecto `test_*.py`).

1. Dentro de cada fichero:

* Cada test debe ser una función con nombre `test_*`:

```python
def test_login_returns_token():
    ...
```

1. Los nombres de fichero en `tests/unit/` deben tener relación directa con el módulo:

* `src/myproj/auth/login.py` → `tests/unit/auth/test_login.py`
* `src/myproj/payments/gateway.py` → `tests/unit/payments/test_gateway.py`

---

## 4. Criterios para clasificar los tests

### 4.1. Tests unitarios (`tests/unit/`)

Un test se debe colocar en `tests/unit/` si:

1. Prueba **una unidad lógica pequeña** (función, método, clase).
2. No accede a servicios externos:

   * Sin llamadas HTTP reales.
   * Sin acceso a BBDD real.
   * Sin acceso a colas/mensajería real.
3. Toda dependencia externa se **simula/mokea**.

Ejemplos:

* Lógica de validación.
* Cálculos puros.
* Servicios que trabajan sobre repositorios mockeados.

### 4.2. Tests de integración (`tests/integration/`)

Un test se debe colocar en `tests/integration/` si:

1. Prueba la interacción entre **múltiples componentes** (ej: servicio + repositorio + BBDD).
2. Usa recursos “reales” o “semi-reales”:

   * BBDD de pruebas (local o en contenedor).
   * Cola de mensajería de pruebas.
   * Servicios HTTP simulados vía docker, testcontainers, etc.
3. El test puede ser más lento que uno unitario, pero debe seguir siendo **razonablemente rápido** para el día a día.

### 4.3. Tests end-to-end (`tests/e2e/`)

Un test se debe colocar en `tests/e2e/` si:

1. Cubre **flujos completos de negocio** (ejemplo: login → crear pedido → pagar).
2. Recorre casi toda la pila: API / UI / BBDD / colas / etc.
3. Suele requerir un entorno más pesado:

   * Stack levantado con docker-compose o similar.
   * Datos de prueba cargados.

---

## 5. Requisitos de aislamiento y dependencias

1. Tests en `tests/unit/`:

   * No pueden depender del **orden** de ejecución.
   * No pueden depender del **estado compartido** entre tests.
   * No deben realizar I/O real (disco, red, etc., salvo casos muy controlados).

2. Tests en `tests/integration/` y `tests/e2e/`:

   * Deben dejar el entorno en un estado **limpio**:

     * Limpiar BBDD.
     * Resetear colas.
     * Borrar ficheros temporales.
   * Se permite I/O, pero controlado.

---

## 6. Uso de `pytest` y markers

1. Debe usarse `pytest` como framework principal.

2. Los tests de integración y e2e deben marcarse:

```python
import pytest

@pytest.mark.integration
def test_auth_flow_with_db():
    ...

@pytest.mark.e2e
def test_full_checkout_flow():
    ...
```

1. Archivo `pytest.ini` (o equivalente) con la declaración de markers:

```ini
# pytest.ini
[pytest]
markers =
    integration: tests de integración (requieren recursos externos)
    e2e: tests end-to-end (flujos completos y entornos pesados)
```

1. Requisitos de ejecución estándar:

* Ejecutar todos los **unitarios**:

  ```bash
  pytest tests/unit
  ```

* Ejecutar **integración**:

  ```bash
  pytest tests/integration -m integration
  ```

* Ejecutar **e2e**:

  ```bash
  pytest tests/e2e -m e2e
  ```

---

## 7. Fixtures y utilidades de test

1. Los fixtures globales se definen en `tests/conftest.py` o en `tests/<tipo>/conftest.py` si son específicos.

2. Los fixtures de integración/e2e que levanten recursos externos (BBDD, contenedores, etc.) deben estar **aislados en sus carpetas**:

```text
tests/
  integration/
    conftest.py   # fixtures que levantan DB, etc.
  e2e/
    conftest.py   # fixtures para entorno completo
```

1. Cualquier dato estático de test (JSON, ficheros de ejemplo…) debe ir en:

```text
tests/
  data/
    ...
```

o bien en `tests/<tipo>/data/` si es muy específico de un tipo de test.

---

## 8. Requisitos para CI/CD

1. **Obligatorio** ejecutar `tests/unit/` en cada push y cada PR.

2. Tests de integración:

   * Ejecutar al menos en:

     * PR hacia ramas principales (`main`/`develop`).
     * Pipeline nocturno o programado, si son algo más lentos.

3. Tests e2e:

   * Pueden ejecutarse:

     * En merges a `main`.
     * En pipelines nocturnos.
   * Debe documentarse en el repo cómo levantar el entorno necesario (docker-compose, scripts, etc.).

Ejemplo de comandos estándar en CI:

```bash
# Fast suite
pytest tests/unit

# Full backend suite (ej: en PR a main)
pytest tests/unit tests/integration -m "not e2e"

# Suite completa (ej: nightly)
pytest tests -m "integration or e2e" 
```

---

## 9. Requisitos para nuevas contribuciones

1. Todo nuevo código en `src/` debe venir acompañado de tests en la carpeta adecuada:

   * Lógica pura → `tests/unit/...`
   * Integración con BBDD/servicios → `tests/integration/...`
   * Nuevos flujos de negocio completos → `tests/e2e/...`

2. Si se mueve un módulo dentro de `src/`, deben moverse sus tests unitarios manteniendo la correspondencia de rutas.

3. No se aceptan PRs que:

   * Añadan tests unitarios fuera de `tests/unit/`.
   * Mezclen lógica de integración dentro de un test ubicado bajo `tests/unit/`.

---

Si quieres, en el siguiente paso puedo:

* Convertir esto en un `README_tests.md` listo para pegar en tu repo, o
* Generarte un esqueleto de proyecto (`src/`, `tests/`, `pyproject.toml`, `pytest.ini`) con todo esto ya “cableado”.
