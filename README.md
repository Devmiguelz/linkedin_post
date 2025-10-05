# LinkedIn Viral AI - Multiagente

Descripción:
Sistema multiagente para generar publicaciones con alto potencial de viralidad en LinkedIn,
usando investigación web, análisis de rendimiento de tus posts y hooks probados.

Instalación básica:
1. Crear venv:
   python -m venv .venv
   source .venv/bin/activate   # windows: .venv\Scripts\activate

2. Instalar dependencias:
   pip install -r requirements.txt

3. Copiar .env:
   cp .env.example .env
   Rellenar OPENAI_API_KEY y SERPAPI_KEY si las tienes.

4. Datos:
   - Rellena `data/profile_data.json` con tu información.
   - Añade export de posts LinkedIn como JSON en `data/posts/` (o usar manualmente los ejemplos).

Ejecución:
   python main.py --topic "product management"

Salida:
   - `output_run.json` con research, performance, script y hooks.

Notas:
- Respeta TOS de LinkedIn al scrapear. Recomendado usar export de datos o la API.
- Para producción: añade manejo de errores, reintentos y cifrado de llaves.
