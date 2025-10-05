# services/linkedin_scraper.py
import json
import os

def load_exported_posts(directory="data/posts"):
    """
    Lee JSONs en data/posts y devuelve lista de posts.
    """
    posts = []
    if not os.path.exists(directory):
        return posts
    for fname in os.listdir(directory):
        if fname.endswith(".json"):
            with open(os.path.join(directory, fname), "r", encoding="utf-8") as f:
                try:
                    posts.append(json.load(f))
                except Exception as e:
                    print("Error leyendo", fname, e)
    return posts

# Opcional: función placeholder para scraping con Playwright (no implementada por defecto)
def scrape_linkedin_profile(username, password, profile_url, max_posts=50):
    """
    Si decides usar Playwright, implementa aquí el scraping respetando TOS.
    Función placeholder para que la completes si aceptas la responsabilidad.
    """
    raise NotImplementedError("scrape_linkedin_profile no implementado. Usa export manual.")
