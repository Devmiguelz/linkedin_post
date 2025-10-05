from services.openai_client import generate_text
import json

def build_script(research_insights: dict, perf: dict, profile_data: dict):
    """
    Agente 3 - Guión: arma un prompt para crear un guion/brief para la publicación en LinkedIn.
    Devuelve un dict con title, structure, CTA y recomendaciones.
    """
    top_texts = [p.get("text","")[:400] for p in perf.get("top_posts", [])][:6]
    prompt = f"""
    Eres un creador de guiones para publicaciones virales en LinkedIn. Usa la siguiente información para construir un post atractivo, profesional y con alto potencial de engagement.

    Perfil (voz y audiencia):
    {profile_data}

    Resumen de investigación:
    {research_insights.get('summary')}

    Posts top (ejemplos breves):
    {top_texts}

    Genera una respuesta en formato JSON EXACTO con las siguientes claves:

    {{
        "title": "<línea inicial potente/hook (1-2 frases)>",
        "structure": texto entre 150 y 250 palabras cada párrafo en un ítem de lista ["párrafo 1", "párrafo 2", ...],
        "cta": "Llamada a la acción (máx 1 línea)",
        "tone": "tono recomendado (ej. cercano, profesional, provocador)",
        "recommended_length_chars": 200,
        "hashtags": ["#Ejemplo1", "#Ejemplo2", "#Ejemplo3"]
        "promt_for_image": "prompt para generar imagen relacionada con el post"
    }}

    Instrucciones:
    - Puedes generar entre **1 y 4 párrafos**, según lo que consideres necesario para explicar bien la idea.
    - Mantén un lenguaje natural, directo y profesional.
    - El post completo debe tener entre **500 palabras** máximo.
    - Los hashtags deben ser relevantes al tema del post (tecnología, IA, programación, liderazgo, productividad, empleo, etc.).
    - No incluyas emojis.
    - El formato final **debe ser JSON válido**.
    """
    text = generate_text(prompt, max_tokens=600)
    # intentar parsear JSON si el LLM devuelve JSON
    try:
        # buscar primer { y último } y parsear
        import re
        m = re.search(r'(\{.*\})', text, flags=re.S)
        json_str = m.group(1) if m else text
        data = json.loads(json_str)
        return data
    except Exception:
        # fallback: devolver raw text
        return {"raw": text}
