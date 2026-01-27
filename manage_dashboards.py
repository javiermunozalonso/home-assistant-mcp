#!/usr/bin/env python3
"""Script to list and manage Home Assistant dashboards."""

import asyncio
import sys
from home_assistant_mcp.client import HomeAssistantClient
from home_assistant_mcp.config import load_config


async def list_dashboards():
    """List all dashboards."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        print("📊 Dashboards disponibles:\n")
        dashboards = await client.list_dashboards()

        if not dashboards:
            print("No hay dashboards configurados.")
            return

        for i, dashboard in enumerate(dashboards, 1):
            print(f"{i}. {dashboard.title}")
            print(f"   ID: {dashboard.id}")
            print(f"   URL: {config.url}/{dashboard.url_path}")
            print(f"   Icono: {dashboard.icon or 'N/A'}")
            print(f"   En sidebar: {'Sí' if dashboard.show_in_sidebar else 'No'}")
            print(f"   Requiere admin: {'Sí' if dashboard.require_admin else 'No'}")
            print()


async def view_dashboard_config(url_path: str):
    """View dashboard configuration."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        print(f"📋 Configuración del dashboard '{url_path}':\n")
        try:
            dashboard_config = await client.get_dashboard_config(url_path)
            print(f"Título: {dashboard_config.title or 'N/A'}")
            print(f"Vistas: {len(dashboard_config.views)}")
            print()

            for i, view in enumerate(dashboard_config.views, 1):
                print(f"Vista {i}: {view.get('title', 'Sin título')}")
                print(f"  Path: {view.get('path', 'N/A')}")
                print(f"  Tarjetas: {len(view.get('cards', []))}")
                print()
        except Exception as e:
            print(f"❌ Error: {e}")


async def delete_dashboard(dashboard_id: str):
    """Delete a dashboard."""
    config = load_config()

    async with HomeAssistantClient(config) as client:
        print(f"🗑️  Eliminando dashboard '{dashboard_id}'...")
        try:
            await client.delete_dashboard(dashboard_id)
            print(f"✅ Dashboard eliminado exitosamente")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python manage_dashboards.py list")
        print("  python manage_dashboards.py view <url_path>")
        print("  python manage_dashboards.py delete <dashboard_id>")
        return

    command = sys.argv[1]

    if command == "list":
        asyncio.run(list_dashboards())
    elif command == "view":
        if len(sys.argv) < 3:
            print("❌ Falta el url_path del dashboard")
            return
        asyncio.run(view_dashboard_config(sys.argv[2]))
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Falta el ID del dashboard")
            return

        confirm = input(f"¿Seguro que quieres eliminar el dashboard '{sys.argv[2]}'? (s/n): ")
        if confirm.lower() == 's':
            asyncio.run(delete_dashboard(sys.argv[2]))
        else:
            print("Operación cancelada")
    else:
        print(f"❌ Comando desconocido: {command}")


if __name__ == "__main__":
    main()
