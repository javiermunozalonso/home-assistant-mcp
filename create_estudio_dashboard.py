#!/usr/bin/env python3
"""Script to create a comprehensive dashboard for the studio (estudio) area.

Groups devices by action nature:
- Color/RGB control lights
- Basic on/off controls
- Media players
- Covers/blinds
- Environmental sensors
"""

import asyncio
from home_assistant_mcp.client import HomeAssistantClient
from home_assistant_mcp.config import load_config


async def categorize_entities(client, area_name: str):
    """Categorize entities by their action nature.

    Args:
        client: HomeAssistantClient instance
        area_name: Name of the area to categorize

    Returns:
        Dictionary with categorized entities
    """
    categories = {
        "color_lights": [],
        "basic_lights": [],
        "media_players": [],
        "covers": [],
        "sensors": [],
        "switches": [],
        "climate": []
    }

    # Get all entities in the area
    all_entity_ids = await client.get_area_entities(area_name)

    for entity_id in all_entity_ids:
        try:
            state = await client.get_state(entity_id)
            domain = entity_id.split('.')[0]
            friendly_name = state.attributes.get('friendly_name', entity_id)

            entity_info = {
                'id': entity_id,
                'name': friendly_name,
                'state': state.state
            }

            # Categorize by domain and capabilities
            if domain == 'light':
                # Check for color capabilities
                has_rgb = 'rgb_color' in state.attributes or 'hs_color' in state.attributes
                has_color_temp = 'color_temp' in state.attributes

                if has_rgb or has_color_temp:
                    entity_info['capabilities'] = []
                    if has_rgb:
                        entity_info['capabilities'].append('rgb')
                    if has_color_temp:
                        entity_info['capabilities'].append('color_temp')
                    if 'brightness' in state.attributes:
                        entity_info['capabilities'].append('brightness')
                    categories['color_lights'].append(entity_info)
                else:
                    categories['basic_lights'].append(entity_info)

            elif domain == 'media_player':
                categories['media_players'].append(entity_info)

            elif domain == 'cover':
                categories['covers'].append(entity_info)

            elif domain in ['sensor', 'binary_sensor']:
                # Only include useful sensors (not diagnostic ones)
                if any(keyword in entity_id.lower() for keyword in
                       ['temperature', 'humidity', 'battery', 'illuminance', 'occupancy', 'presence']):
                    categories['sensors'].append(entity_info)

            elif domain == 'switch':
                # Exclude diagnostic switches
                if not any(keyword in entity_id.lower() for keyword in
                          ['permit_join', 'overtemp', 'alarm']):
                    categories['switches'].append(entity_info)

            elif domain == 'climate':
                categories['climate'].append(entity_info)

        except Exception as e:
            print(f"⚠️  Warning: Could not process {entity_id}: {e}")
            continue

    return categories


async def create_cards_for_category(category_name: str, entities: list) -> list:
    """Create cards for a specific category of entities.

    Args:
        category_name: Name of the category
        entities: List of entity information dictionaries

    Returns:
        List of card configurations
    """
    cards = []

    if not entities:
        return cards

    # Create a summary card with all entities
    entity_ids = [e['id'] for e in entities]

    if category_name == 'color_lights':
        # Create individual light cards for color lights
        for entity in entities:
            card = {
                "type": "light",
                "entity": entity['id'],
                "name": entity['name']
            }
            cards.append(card)

    elif category_name == 'media_players':
        # Media player cards with controls
        for entity in entities:
            card = {
                "type": "media-control",
                "entity": entity['id']
            }
            cards.append(card)

    elif category_name == 'covers':
        # Cover control cards
        for entity in entities:
            card = {
                "type": "cover",
                "entity": entity['id'],
                "name": entity['name']
            }
            cards.append(card)

    elif category_name == 'sensors':
        # Sensor cards in entities format
        cards.append({
            "type": "entities",
            "title": "Sensores Ambientales",
            "entities": entity_ids
        })

    else:
        # Default entities card
        cards.append({
            "type": "entities",
            "entities": entity_ids
        })

    return cards


async def main():
    """Create a comprehensive dashboard for the studio area."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        print("🔍 Analizando dispositivos del estudio...")

        # Categorize entities
        categories = await categorize_entities(client, 'estudio')

        # Print summary
        print("\n📊 RESUMEN DE DISPOSITIVOS:\n")
        print(f"🎨 Luces con control de color: {len(categories['color_lights'])}")
        print(f"💡 Luces básicas (on/off): {len(categories['basic_lights'])}")
        print(f"📺 Media players: {len(categories['media_players'])}")
        print(f"🪟 Persianas/Covers: {len(categories['covers'])}")
        print(f"🌡️  Sensores: {len(categories['sensors'])}")
        print(f"🔌 Interruptores: {len(categories['switches'])}")

        # Create views for the dashboard
        views = []

        # View 1: Color Lights Control
        if categories['color_lights']:
            print(f"\n🎨 Creando vista de control de color...")
            color_cards = await create_cards_for_category('color_lights', categories['color_lights'])

            # Add a master control card at the top
            color_entity_ids = [e['id'] for e in categories['color_lights']]
            color_cards.insert(0, {
                "type": "entities",
                "title": "Control de Luces RGB",
                "entities": color_entity_ids
            })

            views.append({
                "title": "Luces RGB",
                "path": "color-lights",
                "icon": "mdi:palette",
                "cards": color_cards
            })

        # View 2: Basic Controls (lights, switches)
        basic_entities = categories['basic_lights'] + categories['switches']
        if basic_entities:
            print(f"🔌 Creando vista de controles básicos...")
            basic_cards = [{
                "type": "entities",
                "title": "Controles Básicos",
                "entities": [e['id'] for e in basic_entities]
            }]

            views.append({
                "title": "Controles",
                "path": "basic-controls",
                "icon": "mdi:toggle-switch",
                "cards": basic_cards
            })

        # View 3: Media Players
        if categories['media_players']:
            print(f"📺 Creando vista de media players...")
            media_cards = await create_cards_for_category('media_players', categories['media_players'])

            views.append({
                "title": "Media",
                "path": "media",
                "icon": "mdi:television",
                "cards": media_cards
            })

        # View 4: Covers
        if categories['covers']:
            print(f"🪟 Creando vista de persianas...")
            cover_cards = await create_cards_for_category('covers', categories['covers'])

            views.append({
                "title": "Persianas",
                "path": "covers",
                "icon": "mdi:window-shutter",
                "cards": cover_cards
            })

        # View 5: Sensors
        if categories['sensors']:
            print(f"🌡️  Creando vista de sensores...")
            sensor_cards = await create_cards_for_category('sensors', categories['sensors'])

            views.append({
                "title": "Sensores",
                "path": "sensors",
                "icon": "mdi:thermometer",
                "cards": sensor_cards
            })

        # Create the dashboard
        print(f"\n📊 Creando dashboard del estudio...")

        dashboard_config = {
            "views": views
        }

        try:
            dashboard = await client.create_dashboard(
                url_path="estudio-control",
                title="Control del Estudio",
                icon="mdi:desk",
                show_in_sidebar=True,
                require_admin=False
            )
            print(f"✅ Dashboard creado: {dashboard.title}")
            print(f"   ID: {dashboard.id}")
            print(f"   URL: {config.url}/estudio-control")

            # Save the dashboard configuration
            await client.save_dashboard_config(dashboard_config, url_path="estudio-control")
            print(f"✅ Configuración guardada con {len(views)} vistas")

            print(f"\n🎉 ¡Dashboard creado exitosamente!")
            print(f"\n📋 VISTAS CREADAS:")
            for view in views:
                print(f"   • {view['title']} ({view['icon']}) - {len(view['cards'])} tarjetas")
            print(f"\n🌐 Accede al dashboard en: {config.url}/estudio-control")

        except Exception as e:
            print(f"❌ Error al crear el dashboard: {e}")
            print(f"   El dashboard puede ya existir. Intentando actualizar...")

            # Try to update existing dashboard
            try:
                dashboards = await client.list_dashboards()
                estudio_dashboard = None
                for d in dashboards:
                    if d.url_path == "estudio-control":
                        estudio_dashboard = d
                        break

                if estudio_dashboard:
                    print(f"📝 Actualizando dashboard existente...")
                    await client.save_dashboard_config(dashboard_config, url_path="estudio-control")
                    print(f"✅ Dashboard actualizado exitosamente")
                    print(f"\n📋 VISTAS ACTUALIZADAS:")
                    for view in views:
                        print(f"   • {view['title']} ({view['icon']}) - {len(view['cards'])} tarjetas")
                    print(f"\n🌐 Accede al dashboard en: {config.url}/estudio-control")
                else:
                    print(f"❌ No se pudo encontrar el dashboard para actualizar")
            except Exception as e2:
                print(f"❌ Error al actualizar: {e2}")


if __name__ == "__main__":
    asyncio.run(main())
