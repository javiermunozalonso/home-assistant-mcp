#!/usr/bin/env python3
"""Script to create a dashboard for controlling living room lights."""

import asyncio
import json
from home_assistant_mcp.client import HomeAssistantClient
from home_assistant_mcp.config import load_config


async def main():
    """Create a dashboard for salon lights."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        print("🔍 Buscando luces en el salón...")

        # Get all areas to find the salon
        areas = await client.get_areas()
        print(f"Áreas disponibles: {areas}")

        # Try to find salon area (could be "salon", "Salón", "living_room", etc.)
        salon_area = None
        for area in areas:
            area_name = await client.get_area_name(area)
            print(f"  - {area} -> {area_name}")
            if area_name and "sal" in area_name.lower():
                salon_area = area
                print(f"✅ Área del salón encontrada: {area} ({area_name})")
                break

        if not salon_area:
            print("❌ No se encontró el área del salón. Usando todas las luces...")
            # Get all light entities
            lights = await client.get_entities_by_domain("light")
            light_ids = [light.entity_id for light in lights[:5]]  # Limit to first 5
        else:
            # Get light entities in the salon
            light_ids = await client.get_area_entities(salon_area, domain="light")

        if not light_ids:
            print("❌ No se encontraron luces en el salón")
            return

        print(f"\n💡 Luces encontradas ({len(light_ids)}):")
        for light_id in light_ids:
            state = await client.get_state(light_id)
            friendly_name = state.attributes.get("friendly_name", light_id)
            print(f"  - {light_id} ({friendly_name}) - Estado: {state.state}")

        print(f"\n📊 Creando dashboard para el salón...")

        # Create dashboard configuration with cards for each light
        cards = []

        # Add a horizontal stack with all lights
        cards.append({
            "type": "entities",
            "title": "Control de Luces del Salón",
            "entities": light_ids
        })

        # Add individual light cards with more details
        for light_id in light_ids:
            state = await client.get_state(light_id)
            friendly_name = state.attributes.get("friendly_name", light_id)

            # Check if light supports brightness
            supported_features = state.attributes.get("supported_features", 0)
            supports_brightness = (supported_features & 1) != 0  # SUPPORT_BRIGHTNESS = 1

            card = {
                "type": "light",
                "entity": light_id,
                "name": friendly_name
            }
            cards.append(card)

        # Create the dashboard
        try:
            dashboard = await client.create_dashboard(
                url_path="salon-lights",
                title="Luces del Salón",
                icon="mdi:lightbulb-group",
                show_in_sidebar=True,
                require_admin=False
            )
            print(f"✅ Dashboard creado: {dashboard.title}")
            print(f"   ID: {dashboard.id}")
            print(f"   URL: {config.url}/salon-lights")

            # Save the dashboard configuration
            dashboard_config = {
                "views": [
                    {
                        "title": "Luces",
                        "path": "lights",
                        "cards": cards
                    }
                ]
            }

            await client.save_dashboard_config(dashboard_config, url_path="salon-lights")
            print(f"✅ Configuración del dashboard guardada con {len(cards)} tarjetas")

            print(f"\n🎉 ¡Dashboard creado exitosamente!")
            print(f"   Accede a él en: {config.url}/salon-lights")

        except Exception as e:
            print(f"❌ Error al crear el dashboard: {e}")
            print(f"   El dashboard puede ya existir. Intentando actualizar...")

            # Try to update existing dashboard
            try:
                dashboards = await client.list_dashboards()
                salon_dashboard = None
                for d in dashboards:
                    if d.url_path == "salon-lights":
                        salon_dashboard = d
                        break

                if salon_dashboard:
                    print(f"📝 Actualizando dashboard existente...")
                    dashboard_config = {
                        "views": [
                            {
                                "title": "Luces",
                                "path": "lights",
                                "cards": cards
                            }
                        ]
                    }
                    await client.save_dashboard_config(dashboard_config, url_path="salon-lights")
                    print(f"✅ Dashboard actualizado exitosamente")
                    print(f"   Accede a él en: {config.url}/salon-lights")
                else:
                    print(f"❌ No se pudo actualizar el dashboard")
            except Exception as e2:
                print(f"❌ Error al actualizar: {e2}")


if __name__ == "__main__":
    asyncio.run(main())
