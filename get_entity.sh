#!/bin/bash

# Importar configuración
source "$(dirname "$0")/config.sh"

# Verificar que se proporcionó un ID de entidad
if [ -z "$1" ]; then
    echo "Uso: $0 <entity_id>"
    echo "Ejemplo: $0 light.living_room"
    exit 1
fi

entity_id="$1"

echo "=== Obtener Información de Entidad ==="
echo "Entity ID: $entity_id"
echo "URL: $HA_URL"
echo ""

# Obtener información de la entidad específica
response=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states/$entity_id")

# Separar cuerpo y código de estado
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ Entity information retrieved successfully"
    echo ""
    echo "Complete entity details:"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo "❌ Failed to retrieve entity information"
    echo "$body"
    echo ""
    echo "Possible reasons:"
    echo "- Entity ID does not exist"
    echo "- Entity is not available"
    echo "- Permission issues"
fi