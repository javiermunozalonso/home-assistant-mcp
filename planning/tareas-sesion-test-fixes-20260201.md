# Task: Repair and Modernize MCP Server

- [/] Analyze current project state and structural inconsistencies <!-- id: 0 -->
- [x] Align file structure with new `tools/__init__.py` categories <!-- id: 1 -->
  - [x] Delete redundant tool files <!-- id: 4 -->
    - [x] Verify cleanup with tests <!-- id: 5 -->
    - [ ] Fix test imports to match new structure <!-- id: 6 -->
- [ ] Migrate `server.py` to use `FastMCP` (via `core.py`?) <!-- id: 2 -->
  - [/] Fix any failing tests
    - [x] Fix `ha_get_history` JSON errors by requesting JSON output
    - [x] Fix `ha_list_services` JSON errors
    - [x] Fix `ha_list_entities` JSON errors
    - [x] Fix `ha_list_areas` JSON errors
    - [x] Fix dashboard test assertions
    - [x] Fix control/service test assertions
    - [x] Run full test suite to verify success <!-- id: 3 -->
