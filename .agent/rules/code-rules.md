---
trigger: always_on
---

1. Principios SOLID
2. Arquitectura en DDD y TDD
3. Clean Code
4. Don't repeat yourself
5. Keep it simple
6. You Ain’t Gonna Need It
7. Busca la modularización del código
8. Para lanzar ejecuciones, usa siempre uv
9. Para agregar dependencias usa uv
10. Si las dependencias no son para la ejecución, sino para el desarrollo, incluye la dependencia usando uv en el grupo --dev
11. Siempre genera tests asociados a las funcionalidades desarrolladas
12. Para la ejecución de tests, usa siempre pytest
13. Cuando se crea una función, genera la documentación asociada. Si es una clase, genera la documentación de la clase y de cada método. La documentación debe cumplir el estándar de Google Style.
14. Cuando generes tests, la estructura de los tests debe respetar la estructura original de la funcionalidad, no pueden estar todos en el mismo archivo, sino que deben estar distribuidos por archivos como lo están en el proyecto
15. Las clases deben tener sus ficheros individuales. No se pueden tener varias clases en el mismo fichero. Los nombres de estos ficheros deben ser del nombre de la clase pero en formato snake_case
