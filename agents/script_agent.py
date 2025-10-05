from services.openai_client import generate_text
import json

def build_script(research_insights: dict, perf: dict, profile_data: dict):
    """
    Agente 3 - Guión: arma un prompt para crear un guion/brief para la publicación en LinkedIn.
    Devuelve un dict con title, structure, CTA y recomendaciones.
    """
    top_texts = [p.get("text","")[:400] for p in perf.get("top_posts", [])][:6]
    prompt = f"""
    Eres un creador de guiones para publicaciones en LinkedIn. Trabaja con la siguiente información:

    Perfil (voz y audiencia):
    {profile_data}

    Resumen de investigación:
    {research_insights.get('summary')}

    Posts top (ejemplos breves):
    {top_texts}

    Genera en formato JSON:
    {{
    "title": "<línea inicial potente/hook (1-2 frases)>",
    "structure": ["párrafo1 (2-3 frases)", "párrafo2 (2-3 frases)", "cierre + CTA (1 frase)"],
    "cta": "Llamada a la acción (máx 1 línea)",
    "tone": "tono recomendado (ej. cercano, profesional, provocador)",
    "recommended_length_chars": 200
    }}

    Asegúrate de ser conciso y práctico.
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
