# Skills Documentation

This document describes the skills installed in this project and how to manage them.

---

## Installed Skills

### mcp-builder

**Source**: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)
**Version**: Latest from main branch
**Location**: `.claude/skills/mcp-builder`

#### Description

Official Anthropic skill that provides comprehensive guidance for developing Model Context Protocol (MCP) servers. This skill is particularly relevant for this project as we're building a Python-based MCP server for Home Assistant integration.

#### Contents

**Reference Documentation:**
- `reference/python_mcp_server.md` (25KB) - Complete guide for Python MCP server development
- `reference/mcp_best_practices.md` (7KB) - Best practices for MCP server design
- `reference/evaluation.md` (21KB) - Evaluation methodologies for MCP implementations
- `reference/node_mcp_server.md` (28KB) - Node.js/TypeScript MCP guide (for reference)

**Utility Scripts:**
- `scripts/evaluation.py` - Script to evaluate MCP server implementation quality
- `scripts/connections.py` - Utilities for managing MCP connections
- `scripts/example_evaluation.xml` - Example evaluation configuration
- `scripts/requirements.txt` - Python dependencies for scripts

**License:**
- `LICENSE.txt` - Skill license information

#### Key Topics Covered

The skill provides guidance on:
- Tool design and implementation
- Input/output schema definition with Pydantic (Python) or Zod (TypeScript)
- Error handling best practices
- Authentication and configuration management
- Pagination for large datasets
- Testing with MCP Inspector
- Type coverage and code quality
- DRY principles and consistent patterns

---

## Installation & Management

### Installation Script

The repository includes an automated installation script: `install-mcp-builder-skill.sh`

This script:
- ✅ Downloads all skill files from the official Anthropic repository
- ✅ Creates the proper directory structure
- ✅ Updates `.gitignore` to exclude generated files
- ✅ Verifies installation integrity
- ✅ Provides detailed installation report
- ✅ Optionally installs Python dependencies

### Usage

#### Fresh Installation

```bash
./install-mcp-builder-skill.sh
```

This will:
1. Check for required dependencies (curl)
2. Create `.claude/skills/mcp-builder/` directory structure
3. Download all skill files from GitHub
4. Update `.gitignore` with appropriate patterns
5. Verify that all essential files are present
6. Display installation report

#### Update Existing Installation

```bash
./install-mcp-builder-skill.sh --update
```

This will re-download all files, overwriting existing ones with the latest versions from the Anthropic repository.

#### Install with Python Dependencies

```bash
./install-mcp-builder-skill.sh --install-deps
```

This will also install the Python packages required by the evaluation scripts using `uv` (or `pip` if `uv` is not available).

#### Help

```bash
./install-mcp-builder-skill.sh --help
```

---

## Using the Skill

### With Claude Code

The skill is automatically detected by Claude Code when placed in `.claude/skills/`. No additional configuration is needed.

You can reference it in conversations:
- "Use the mcp-builder skill to review my server implementation"
- "Check if my MCP server follows best practices"
- "Evaluate my tool definitions according to mcp-builder guidelines"

### Reading References

All reference documents are markdown files and can be read directly:

```bash
# View Python MCP guide (most relevant for this project)
cat .claude/skills/mcp-builder/reference/python_mcp_server.md

# View best practices
cat .claude/skills/mcp-builder/reference/mcp_best_practices.md

# View evaluation guide
cat .claude/skills/mcp-builder/reference/evaluation.md
```

### Running Evaluation Scripts

If you installed Python dependencies:

```bash
# Run evaluation script
python .claude/skills/mcp-builder/scripts/evaluation.py

# Or with uv
uv run python .claude/skills/mcp-builder/scripts/evaluation.py
```

---

## Version Control

### What's Tracked in Git

✅ **Included in repository:**
- All skill files (`.claude/skills/mcp-builder/**`)
- Installation script (`install-mcp-builder-skill.sh`)
- This documentation (`SKILLS.md`)

❌ **Excluded from repository:**
- Python bytecode (`.claude/skills/**/__pycache__/`)
- Compiled Python files (`.claude/skills/**/*.pyc`)
- Node modules if any (`.claude/skills/**/node_modules/`)

### Deployment to Other Machines

When you clone this repository on another machine (e.g., Raspberry Pi):

```bash
# Clone the repository
git clone <your-repo-url>
cd ha_connection

# The skill is already there!
ls -la .claude/skills/mcp-builder/

# Optional: Update to latest version
./install-mcp-builder-skill.sh --update

# Optional: Install Python dependencies for evaluation scripts
./install-mcp-builder-skill.sh --install-deps
```

---

## Adding More Skills

To add additional skills from the Anthropic repository or other sources:

1. **Create a new installation script** or modify the existing one
2. **Add to `.claude/skills/`** directory
3. **Document in this file** (SKILLS.md)
4. **Update CLAUDE.md** with skill information

Example structure:
```
.claude/
  skills/
    mcp-builder/        # MCP development guidance
    another-skill/      # Another skill
    custom-skill/       # Your custom skill
```

---

## Troubleshooting

### Installation Issues

**Problem**: `curl: command not found`
**Solution**: Install curl:
```bash
# macOS
brew install curl

# Debian/Ubuntu
sudo apt-get install curl

# Raspberry Pi OS
sudo apt-get install curl
```

**Problem**: Download fails
**Solution**: Check internet connection and GitHub availability:
```bash
curl -I https://raw.githubusercontent.com/anthropics/skills/main/skills/mcp-builder/SKILL.md
```

**Problem**: Permission denied when running script
**Solution**: Make script executable:
```bash
chmod +x install-mcp-builder-skill.sh
```

### Usage Issues

**Problem**: Claude Code doesn't detect the skill
**Solution**:
- Ensure files are in `.claude/skills/mcp-builder/`
- Restart Claude Code
- Check that `SKILL.md` exists

**Problem**: Evaluation scripts don't work
**Solution**: Install Python dependencies:
```bash
./install-mcp-builder-skill.sh --install-deps
```

---

## Maintenance

### Updating Skills

It's recommended to periodically update skills to get the latest improvements:

```bash
# Check current version
git log .claude/skills/mcp-builder/

# Update to latest
./install-mcp-builder-skill.sh --update

# Commit updates if significant
git add .claude/skills/mcp-builder/
git commit -m "Update mcp-builder skill to latest version"
```

### Cleaning Up

To remove the skill:

```bash
rm -rf .claude/skills/mcp-builder/
```

To reinstall:

```bash
./install-mcp-builder-skill.sh
```

---

## References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [MCP-Builder Skill](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)

---

**Last Updated**: 2026-01-27
