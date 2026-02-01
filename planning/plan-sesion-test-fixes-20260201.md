# Cleanup & Finalization Plan

The project has been successfully migrated to `FastMCP` structure with categorized tool modules (`health.py`, `entities.py`, etc.). However, the old individual tool files (`ha_*.py`) still exist in `src/home_assistant_mcp/tools/`.

## User Review Required
>
> [!IMPORTANT]
> This plan involves **deleting** 21 old Python files. Ensure you have no outstanding changes in these specific files before approving.

## Proposed Changes

### Cleanup `src/home_assistant_mcp/tools/`

Delete the following redundant files which have been replaced by the new module structure:

- [DELETE] `ha_call_service.py`
- [DELETE] `ha_create_dashboard.py`
- [DELETE] `ha_delete_dashboard.py`
- [DELETE] `ha_fire_event.py`
- [DELETE] `ha_get_area_devices.py`
- [DELETE] `ha_get_area_entities.py`
- [DELETE] `ha_get_config.py`
- [DELETE] `ha_get_dashboard.py`
- [DELETE] `ha_get_entity_area.py`
- [DELETE] `ha_get_entity_state.py`
- [DELETE] `ha_get_history.py`
- [DELETE] `ha_health_check.py`
- [DELETE] `ha_list_areas.py`
- [DELETE] `ha_list_dashboards.py`
- [DELETE] `ha_list_entities.py`
- [DELETE] `ha_list_services.py`
- [DELETE] `ha_render_template.py`
- [DELETE] `ha_toggle.py`
- [DELETE] `ha_turn_off.py`
- [DELETE] `ha_turn_on.py`
- [DELETE] `ha_update_dashboard.py`

## Verification Plan

### Automated Tests

Run the full unit test suite to ensure the new modules are correctly integrated and no hidden dependencies on the old files remain.

```bash
uv run pytest tests/unit
```

### Verification Results

All unit tests passed (93 tests).
