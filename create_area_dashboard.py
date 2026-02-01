#!/usr/bin/env python3
"""Generic script to create a comprehensive dashboard for any Home Assistant area.

Groups devices by action nature:
- Color/RGB control lights
- Basic on/off controls
- Media players
- Covers/blinds
- Environmental sensors

Usage:
    python create_area_dashboard.py <area_name>
    python create_area_dashboard.py salon
    python create_area_dashboard.py estudio
    python create_area_dashboard.py dormitorio
"""

import asyncio
import argparse
import sys
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
        "climate": [],
        "automations": [],
        "scenes": []
    }

    # Get all entities in the area
    all_entity_ids = await client.get_area_entities(area_name)

    if not all_entity_ids:
        print(f"⚠️  No se encontraron entidades en el área '{area_name}'")
        return categories

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

            elif domain == 'automation':
                categories['automations'].append(entity_info)

            elif domain == 'scene':
                categories['scenes'].append(entity_info)

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

    elif category_name == 'automations':
        # Automation execution buttons
        for entity in entities:
            card = {
                "type": "button",
                "entity": entity['id'],
                "name": entity['name'],
                "icon": "mdi:play-circle",
                "tap_action": {
                    "action": "call-service",
                    "service": "automation.trigger",
                    "service_data": {
                        "entity_id": entity['id']
                    }
                },
                "show_name": True,
                "show_icon": True
            }
            cards.append(card)

    elif category_name == 'scenes':
        # Scene activation cards
        cards.append({
            "type": "entities",
            "title": "Escenas",
            "entities": entity_ids
        })

    else:
        # Default entities card
        cards.append({
            "type": "entities",
            "entities": entity_ids
        })

    return cards


def get_area_display_name(area_name: str) -> str:
    """Convert area name to a display-friendly format.

    Args:
        area_name: Area name (e.g., 'salon', 'estudio', 'dormitorio')

    Returns:
        Display name (e.g., 'Salón', 'Estudio', 'Dormitorio')
    """
    # Common Spanish area name mappings
    name_map = {
        'salon': 'Salón',
        'estudio': 'Estudio',
        'dormitorio': 'Dormitorio',
        'cocina': 'Cocina',
        'bano': 'Baño',
        'bano_pasillo': 'Baño Pasillo',
        'entrada': 'Entrada',
        'recibidor': 'Recibidor',
        'habitacion_marcos': 'Habitación Marcos',
        'habitacion_invitados': 'Habitación Invitados',
        'cuarto_marcos': 'Cuarto Marcos',
        'dormitorio_invitados': 'Dormitorio Invitados',
        'estudio_marta': 'Estudio Marta',
        'ordenador': 'Ordenador',
        'casa': 'Casa'
    }

    return name_map.get(area_name.lower(), area_name.replace('_', ' ').title())


def get_area_icon(area_name: str) -> str:
    """Get an appropriate icon for the area.

    Args:
        area_name: Area name

    Returns:
        MDI icon name
    """
    icon_map = {
        'salon': 'mdi:sofa',
        'estudio': 'mdi:desk',
        'dormitorio': 'mdi:bed',
        'cocina': 'mdi:stove',
        'bano': 'mdi:shower',
        'bano_pasillo': 'mdi:shower',
        'entrada': 'mdi:door',
        'recibidor': 'mdi:door-open',
        'habitacion_marcos': 'mdi:bed',
        'habitacion_invitados': 'mdi:bed-double',
        'cuarto_marcos': 'mdi:bed',
        'dormitorio_invitados': 'mdi:bed-double',
        'estudio_marta': 'mdi:desk',
        'ordenador': 'mdi:desktop-tower',
        'casa': 'mdi:home'
    }

    return icon_map.get(area_name.lower(), 'mdi:floor-plan')


async def create_dashboard_for_area(area_name: str):
    """Create a comprehensive dashboard for a specific area.

    Args:
        area_name: Name of the area to create dashboard for
    """
    config = load_config()

    async with HomeAssistantClient(config) as client:
        # Verify area exists
        areas = await client.get_areas()
        if area_name not in areas:
            print(f"❌ Error: El área '{area_name}' no existe.")
            print(f"\n📋 Áreas disponibles:")
            for area in sorted(areas):
                display_name = get_area_display_name(area)
                print(f"   • {area} ({display_name})")
            return False

        display_name = get_area_display_name(area_name)
        print(f"🔍 Analizando dispositivos de '{display_name}'...")

        # Categorize entities
        categories = await categorize_entities(client, area_name)

        # Check if area has any entities
        total_entities = sum(len(v) for v in categories.values())
        if total_entities == 0:
            print(f"❌ No se encontraron dispositivos en '{display_name}'")
            return False

        # Print summary
        print(f"\n📊 RESUMEN DE DISPOSITIVOS EN '{display_name.upper()}':\n")
        print(f"🎨 Luces con control de color: {len(categories['color_lights'])}")
        print(f"💡 Luces básicas (on/off): {len(categories['basic_lights'])}")
        print(f"📺 Media players: {len(categories['media_players'])}")
        print(f"🪟 Persianas/Covers: {len(categories['covers'])}")
        print(f"🌡️  Sensores: {len(categories['sensors'])}")
        print(f"🔌 Interruptores: {len(categories['switches'])}")
        print(f"❄️  Climatización: {len(categories['climate'])}")
        print(f"🤖 Automatizaciones: {len(categories['automations'])}")
        print(f"🎬 Escenas: {len(categories['scenes'])}")

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

        # View 5: Climate
        if categories['climate']:
            print(f"❄️  Creando vista de climatización...")
            climate_cards = await create_cards_for_category('climate', categories['climate'])

            views.append({
                "title": "Clima",
                "path": "climate",
                "icon": "mdi:thermostat",
                "cards": climate_cards
            })

        # View 6: Sensors
        if categories['sensors']:
            print(f"🌡️  Creando vista de sensores...")
            sensor_cards = await create_cards_for_category('sensors', categories['sensors'])

            views.append({
                "title": "Sensores",
                "path": "sensors",
                "icon": "mdi:thermometer",
                "cards": sensor_cards
            })

        # View 7: Automations
        if categories['automations']:
            print(f"🤖 Creando vista de automatizaciones...")
            automation_cards = await create_cards_for_category('automations', categories['automations'])

            views.append({
                "title": "Automatizaciones",
                "path": "automations",
                "icon": "mdi:robot",
                "cards": automation_cards
            })

        # View 8: Scenes
        if categories['scenes']:
            print(f"🎬 Creando vista de escenas...")
            scene_cards = await create_cards_for_category('scenes', categories['scenes'])

            views.append({
                "title": "Escenas",
                "path": "scenes",
                "icon": "mdi:palette-outline",
                "cards": scene_cards
            })

        # If no views were created, return
        if not views:
            print(f"❌ No se pudieron crear vistas para '{display_name}'")
            return False

        # Create the dashboard
        print(f"\n📊 Creando dashboard de '{display_name}'...")

        # Generate unique URL path and title
        url_path = f"{area_name}-control"
        dashboard_title = f"Control {display_name}"
        area_icon = get_area_icon(area_name)

        dashboard_config = {
            "views": views
        }

        try:
            dashboard = await client.create_dashboard(
                url_path=url_path,
                title=dashboard_title,
                icon=area_icon,
                show_in_sidebar=True,
                require_admin=False
            )
            print(f"✅ Dashboard creado: {dashboard.title}")
            print(f"   ID: {dashboard.id}")
            print(f"   URL: {config.url}/{url_path}")

            # Save the dashboard configuration
            await client.save_dashboard_config(dashboard_config, url_path=url_path)
            print(f"✅ Configuración guardada con {len(views)} vistas")

            print(f"\n🎉 ¡Dashboard creado exitosamente!")
            print(f"\n📋 VISTAS CREADAS:")
            for view in views:
                print(f"   • {view['title']} ({view['icon']}) - {len(view['cards'])} tarjetas")
            print(f"\n🌐 Accede al dashboard en: {config.url}/{url_path}")

            return True

        except Exception as e:
            print(f"❌ Error al crear el dashboard: {e}")
            print(f"   El dashboard puede ya existir. Intentando actualizar...")

            # Try to update existing dashboard
            try:
                dashboards = await client.list_dashboards()
                area_dashboard = None
                for d in dashboards:
                    if d.url_path == url_path:
                        area_dashboard = d
                        break

                if area_dashboard:
                    print(f"📝 Actualizando dashboard existente...")
                    await client.save_dashboard_config(dashboard_config, url_path=url_path)
                    print(f"✅ Dashboard actualizado exitosamente")
                    print(f"\n📋 VISTAS ACTUALIZADAS:")
                    for view in views:
                        print(f"   • {view['title']} ({view['icon']}) - {len(view['cards'])} tarjetas")
                    print(f"\n🌐 Accede al dashboard en: {config.url}/{url_path}")
                    return True
                else:
                    print(f"❌ No se pudo encontrar el dashboard para actualizar")
                    return False
            except Exception as e2:
                print(f"❌ Error al actualizar: {e2}")
                return False


async def list_areas():
    """List all available areas in Home Assistant."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        areas = await client.get_areas()
        print("📋 Áreas disponibles en Home Assistant:\n")
        for area in sorted(areas):
            display_name = get_area_display_name(area)
            icon = get_area_icon(area)
            print(f"   {icon}  {area} → {display_name}")
        print(f"\n💡 Uso: python create_area_dashboard.py <nombre_area>")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Crea un dashboard completo para un área de Home Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s salon          # Crea dashboard para el salón
  %(prog)s estudio        # Crea dashboard para el estudio
  %(prog)s dormitorio     # Crea dashboard para el dormitorio
  %(prog)s --list         # Lista todas las áreas disponibles
        """
    )

    parser.add_argument(
        'area',
        nargs='?',
        help='Nombre del área para crear el dashboard'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='Lista todas las áreas disponibles'
    )

    args = parser.parse_args()

    # Show list of areas
    if args.list:
        asyncio.run(list_areas())
        return

    # Require area name if not listing
    if not args.area:
        parser.print_help()
        print("\n❌ Error: Debes especificar un área o usar --list")
        sys.exit(1)

    # Create dashboard for the area
    success = asyncio.run(create_dashboard_for_area(args.area))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
