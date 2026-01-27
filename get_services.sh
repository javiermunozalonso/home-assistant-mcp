#!/bin/bash

# Importar configuración
source "$(dirname "$0")/config.sh"

echo "=== Servicios Disponibles en Home Assistant ==="
echo "URL: $HA_URL"
echo ""

# Obtener todos los servicios disponibles
response=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/services")

# Separar cuerpo y código de estado
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ Services retrieved successfully"
    echo ""
    echo "All available services:"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo "❌ Failed to retrieve services"
    echo "$body"
fi