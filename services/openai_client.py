import numpy as np
from datetime import datetime
from openai import OpenAI

client = OpenAI()

def generate_text(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 512, temperature: float = 0.7) -> str:
    """
    Genera texto usando OpenAI Chat API con el nuevo cliente.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente experto en creación de contenido viral para LinkedIn."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] No se pudo generar texto con OpenAI: {e}"

def embed_texts(texts, model: str = "text-embedding-3-small"):
    """
    Genera embeddings usando OpenAI Embeddings API.
    Retorna un array de NumPy.
    """
    try:
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)
    except Exception as e:
        print(f"[ERROR] No se pudo generar embeddings con OpenAI: {e}")
        # fallback: embeddings aleatorios
        rng = np.random.default_rng(0)
        return rng.standard_normal((len(texts), 384))

def get_trending_topic():
    """
    Selecciona el tema más viral del día entre la lista dada.
    """

    prompt = f"""
    Eres un analista de tendencias experto en tecnología, negocios, liderazgo, innovación y emprendimiento. Investiga en internet cuáles son los temas más virales y relevantes actualmente en LinkedIn. No te limites a IA o software: incluye también tendencias en negocios globales, sostenibilidad, macroeconomía, cultura laboral, management, startups y transformación digital. Con base en lo que esté resonando hoy en redes profesionales, identifica los temas con mayor tracción. Sugiere tres posibles ideas de contenido, pero al final SOLO devuelve el título del tema más viral. Solo el título.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    topic = response.choices[0].message.content.strip()
    print(f"🔥 Tema viral del día: {topic}")
    return topic