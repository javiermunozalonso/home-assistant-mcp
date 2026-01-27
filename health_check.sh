#!/bin/bash

# Importar configuración
source "$(dirname "$0")/config.sh"

echo "=== Home Assistant API Health Check ==="
echo "URL: $HA_URL"
echo ""

# Health check endpoint
response=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/")

# Separar cuerpo y código de estado
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "HTTP Status: $http_code"
echo "Complete API response:"
echo "$body" | jq '.' 2>/dev/null || echo "$body"

if [ "$http_code" = "200" ]; then
    echo "✅ API connection successful"
else
    echo "❌ API connection failed"
fi