# Gestión de Dashboards de Home Assistant

Este proyecto ahora incluye soporte completo para gestionar dashboards de Home Assistant (Lovelace) mediante la API WebSocket.

## 🎯 Dashboard Creado: Luces del Salón

Se ha creado exitosamente un dashboard para controlar las luces del salón con las siguientes características:

### 📊 Detalles del Dashboard

- **Nombre**: Luces del Salón
- **ID**: salon_lights
- **URL**: http://192.168.88.114:8123/salon-lights
- **Icono**: mdi:lightbulb-group
- **Visible en sidebar**: Sí

### 💡 Luces Incluidas (8 dispositivos)

El dashboard controla todas las luces del salón:

1. **Tele 1** (light.tele_1)
2. **Tele 2** (light.tele_2)
3. **Tele 3** (light.tele_3)
4. **Tele 4** (light.tele_4)
5. **Lampara de pie** (light.lampara_de_pie)
6. **Mesa** (light.mesa)
7. **Lampara Tele** (light.lampara_tele)
8. **Salón** (light.salon) - Control grupal

### 🎨 Composición del Dashboard

El dashboard incluye:

- **1 tarjeta de entidades**: Vista compacta con todas las luces para control rápido
- **8 tarjetas individuales**: Una tarjeta tipo "light" por cada dispositivo con controles detallados (encendido/apagado, brillo, etc.)

## 🔧 Scripts de Gestión

### 1. Crear Dashboard del Salón

```bash
uv run python create_salon_dashboard.py
```

Este script:
- Detecta automáticamente el área del salón
- Encuentra todas las luces en esa área
- Crea/actualiza el dashboard con tarjetas para cada luz
- Configura controles individuales y grupales

### 2. Gestionar Dashboards

```bash
# Listar todos los dashboards
uv run python manage_dashboards.py list

# Ver configuración de un dashboard
uv run python manage_dashboards.py view salon-lights

# Eliminar un dashboard
uv run python manage_dashboards.py delete salon_lights
```

## 🚀 Uso con MCP

Las funcionalidades de dashboard están disponibles como herramientas MCP:

### Herramientas Disponibles

1. **ha_list_dashboards**: Lista todos los dashboards
   ```json
   {
     "name": "ha_list_dashboards",
     "arguments": {}
   }
   ```

2. **ha_get_dashboard**: Obtiene configuración de un dashboard
   ```json
   {
     "name": "ha_get_dashboard",
     "arguments": {
       "url_path": "salon-lights"
     }
   }
   ```

3. **ha_create_dashboard**: Crea un nuevo dashboard
   ```json
   {
     "name": "ha_create_dashboard",
     "arguments": {
       "url_path": "my-dashboard",
       "title": "Mi Dashboard",
       "icon": "mdi:home",
       "show_in_sidebar": true
     }
   }
   ```

4. **ha_update_dashboard**: Actualiza un dashboard existente
   ```json
   {
     "name": "ha_update_dashboard",
     "arguments": {
       "dashboard_id": "salon_lights",
       "title": "Nuevo Título"
     }
   }
   ```

5. **ha_delete_dashboard**: Elimina un dashboard
   ```json
   {
     "name": "ha_delete_dashboard",
     "arguments": {
       "dashboard_id": "salon_lights"
     }
   }
   ```

## 💻 Uso Programático

```python
from ha_mcp_server.client import HomeAssistantClient
from ha_mcp_server.config import load_config

async def example():
    config = load_config()

    async with HomeAssistantClient(config) as client:
        # Listar dashboards
        dashboards = await client.list_dashboards()
        for d in dashboards:
            print(f"{d.title}: {d.url_path}")

        # Obtener configuración
        config = await client.get_dashboard_config("salon-lights")
        print(f"Vistas: {len(config.views)}")

        # Crear dashboard
        dashboard = await client.create_dashboard(
            url_path="test",
            title="Test Dashboard",
            icon="mdi:test-tube"
        )

        # Actualizar dashboard
        updated = await client.update_dashboard(
            dashboard.id,
            title="Nuevo Título"
        )

        # Eliminar dashboard
        await client.delete_dashboard(dashboard.id)
```

## 🏗️ Arquitectura

### Cliente Híbrido (REST + WebSocket)

El cliente `HomeAssistantClient` ahora soporta ambos protocolos:

- **REST API**: Para entidades, servicios, estados, etc. (funcionalidad existente)
- **WebSocket API**: Para dashboards (nueva funcionalidad)

### Características Técnicas

- ✅ **Conexión lazy**: WebSocket se conecta solo cuando es necesario
- ✅ **Reutilización de conexión**: La misma conexión WebSocket se usa para múltiples peticiones
- ✅ **Autenticación automática**: El cliente gestiona el handshake de autenticación
- ✅ **Thread-safe**: Usa `asyncio.Lock` para concurrencia
- ✅ **Manejo de errores**: Errores de conexión, autenticación y peticiones
- ✅ **Cleanup adecuado**: Cierre correcto de conexiones HTTP y WebSocket

## 🔐 Configuración

Usa las mismas variables de entorno que el resto del servidor:

```bash
HA_URL=http://192.168.88.114:8123
HA_TOKEN=tu_token_aqui
HA_VERIFY_SSL=false
HA_TIMEOUT=30
```

## 📝 Notas

- Los dashboards se crean en modo "storage" (editables desde la UI de Home Assistant)
- El `url_path` debe ser único (ej: "salon-lights")
- El parámetro `url_path=None` se refiere al dashboard por defecto (lovelace)
- Algunos comandos requieren privilegios de administrador (create, update, delete)

## 🧪 Tests

El proyecto incluye tests completos:

```bash
# Tests unitarios
uv run pytest tests/unit/test_client.py -k dashboard

# Tests de integración
uv run pytest tests/integration/test_server.py -k dashboard

# Todos los tests
uv run pytest
```

**Estado actual**: ✅ 79 tests pasando (57 unitarios + 22 integración)

## 🔗 Enlaces Útiles

- [Home Assistant WebSocket API](https://developers.home-assistant.io/docs/api/websocket/)
- [Lovelace UI Configuration](https://www.home-assistant.io/dashboards/)
- [Dashboard Cards Reference](https://www.home-assistant.io/dashboards/cards/)
