#!/usr/bin/env bash

################################################################################
# Script: verify-skill.sh
# Description: Verify that mcp-builder skill is properly installed and working
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header "Verificación de la Skill mcp-builder"

# Test 1: Check directory structure
print_info "Test 1: Verificando estructura de directorios..."
if [ -d ".claude/skills/mcp-builder" ]; then
    print_success "Directorio principal existe"
else
    print_error "Directorio principal no encontrado"
    exit 1
fi

if [ -d ".claude/skills/mcp-builder/reference" ]; then
    print_success "Directorio reference/ existe"
else
    print_error "Directorio reference/ no encontrado"
    exit 1
fi

if [ -d ".claude/skills/mcp-builder/scripts" ]; then
    print_success "Directorio scripts/ existe"
else
    print_error "Directorio scripts/ no encontrado"
    exit 1
fi

# Test 2: Check essential files
print_info "\nTest 2: Verificando archivos esenciales..."

files=(
    ".claude/skills/mcp-builder/SKILL.md"
    ".claude/skills/mcp-builder/LICENSE.txt"
    ".claude/skills/mcp-builder/reference/python_mcp_server.md"
    ".claude/skills/mcp-builder/reference/mcp_best_practices.md"
    ".claude/skills/mcp-builder/reference/evaluation.md"
    ".claude/skills/mcp-builder/scripts/evaluation.py"
    ".claude/skills/mcp-builder/scripts/connections.py"
    ".claude/skills/mcp-builder/scripts/requirements.txt"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$(basename $file) encontrado"
    else
        print_error "$(basename $file) no encontrado"
        exit 1
    fi
done

# Test 3: Check SKILL.md metadata
print_info "\nTest 3: Verificando metadatos de SKILL.md..."
if grep -q "name: mcp-builder" .claude/skills/mcp-builder/SKILL.md; then
    print_success "Skill name correcto"
else
    print_error "Skill name incorrecto o no encontrado"
    exit 1
fi

if grep -q "description:" .claude/skills/mcp-builder/SKILL.md; then
    print_success "Skill description presente"
else
    print_error "Skill description no encontrada"
    exit 1
fi

# Test 4: Check Python scripts syntax
print_info "\nTest 4: Verificando sintaxis de scripts Python..."

if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v uv &> /dev/null; then
    PYTHON="uv run python"
else
    print_error "No se encontró Python (ni venv ni uv)"
    exit 1
fi

if $PYTHON -m py_compile .claude/skills/mcp-builder/scripts/evaluation.py 2>/dev/null; then
    print_success "evaluation.py tiene sintaxis válida"
else
    print_error "evaluation.py tiene errores de sintaxis"
    exit 1
fi

if $PYTHON -m py_compile .claude/skills/mcp-builder/scripts/connections.py 2>/dev/null; then
    print_success "connections.py tiene sintaxis válida"
else
    print_error "connections.py tiene errores de sintaxis"
    exit 1
fi

# Test 5: Check file sizes (should not be empty)
print_info "\nTest 5: Verificando tamaños de archivos..."

min_sizes=(
    ".claude/skills/mcp-builder/reference/python_mcp_server.md:20000"
    ".claude/skills/mcp-builder/reference/mcp_best_practices.md:5000"
    ".claude/skills/mcp-builder/reference/evaluation.md:15000"
    ".claude/skills/mcp-builder/SKILL.md:1000"
)

for entry in "${min_sizes[@]}"; do
    file="${entry%%:*}"
    min_size="${entry##*:}"
    actual_size=$(wc -c < "$file" | tr -d ' ')

    if [ "$actual_size" -gt "$min_size" ]; then
        print_success "$(basename $file): ${actual_size} bytes (> ${min_size})"
    else
        print_error "$(basename $file): ${actual_size} bytes (esperado > ${min_size})"
        exit 1
    fi
done

# Test 6: Check content of key files
print_info "\nTest 6: Verificando contenido de archivos clave..."

if grep -q "FastMCP" .claude/skills/mcp-builder/reference/python_mcp_server.md; then
    print_success "python_mcp_server.md menciona FastMCP"
else
    print_error "python_mcp_server.md no menciona FastMCP"
    exit 1
fi

if grep -q "Pydantic" .claude/skills/mcp-builder/reference/python_mcp_server.md; then
    print_success "python_mcp_server.md menciona Pydantic"
else
    print_error "python_mcp_server.md no menciona Pydantic"
    exit 1
fi

if grep -q "Tool Naming" .claude/skills/mcp-builder/reference/mcp_best_practices.md; then
    print_success "mcp_best_practices.md contiene Tool Naming"
else
    print_error "mcp_best_practices.md no contiene Tool Naming"
    exit 1
fi

# Test 7: Check .gitignore updates
print_info "\nTest 7: Verificando .gitignore..."

if [ -f ".gitignore" ]; then
    if grep -q ".claude/skills/\*\*/__pycache__/" .gitignore; then
        print_success ".gitignore contiene patrón para __pycache__"
    else
        print_info ".gitignore no contiene patrón para __pycache__ (no crítico)"
    fi
else
    print_info ".gitignore no existe (no crítico)"
fi

# Test 8: Test importing scripts (optional, requires dependencies)
print_info "\nTest 8: Verificando importabilidad de scripts (opcional)..."

if $PYTHON -c "import sys; sys.path.insert(0, '.claude/skills/mcp-builder/scripts'); import connections" 2>/dev/null; then
    print_success "connections.py se puede importar"
else
    print_info "connections.py no se puede importar (puede necesitar dependencias)"
fi

# Final report
print_header "Resultado de la Verificación"

echo -e "${GREEN}✅ Todos los tests esenciales pasaron correctamente${NC}\n"
echo "La skill mcp-builder está correctamente instalada y lista para usar."
echo ""
echo "Archivos de referencia disponibles:"
echo "  - .claude/skills/mcp-builder/reference/python_mcp_server.md"
echo "  - .claude/skills/mcp-builder/reference/mcp_best_practices.md"
echo "  - .claude/skills/mcp-builder/reference/evaluation.md"
echo ""
echo "Para instalar dependencias de los scripts:"
echo "  ./install-mcp-builder-skill.sh --install-deps"
echo ""
