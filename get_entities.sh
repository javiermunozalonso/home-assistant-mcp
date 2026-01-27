#!/bin/bash

# Importar configuración
source "$(dirname "$0")/config.sh"

echo "=== Obtener Entidades de Home Assistant ==="
echo "URL: $HA_URL"
echo ""

# Obtener todas las entidades
response=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states")

# Separar cuerpo y código de estado
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ Entities retrieved successfully"
    echo ""
    echo "Total entities found:"
    echo "$body" | jq 'length' 2>/dev/null || echo "Could not parse JSON"
    echo ""
    echo "All entities:"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo "❌ Failed to retrieve entities"
    echo "$body"
fi