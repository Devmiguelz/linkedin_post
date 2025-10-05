# agents/research_agent.py
from services.research_service import web_search, summarize_texts
from utils.cache import load_cache, save_cache
from utils.text_utils import normalize_text

def research_topic(user_topic: str, profile_data: dict, top_k=8, cache_ttl=60*60*24):
    """
    Agente 1 - Investigación:
    - Busca en la web usando queries relacionadas al topic + avatar del perfil.
    - Resume y retorna insights.
    """
    cache_key = f"research_{user_topic.replace(' ','_')}"
    cached = load_cache(cache_key, ttl_seconds=cache_ttl)
    if cached:
        return cached

    queries = [
        f"{user_topic} trends 2025",
        f"{user_topic} tendencias",
        f"why {user_topic} matters to {', '.join(profile_data.get('audience',[]))}",
        f"{user_topic} case study",
        f"{user_topic} ejemplo éxito",
        f"{user_topic} problemas comunes"
    ]
    results = []
    for q in queries:
        hits = web_search(q, num=top_k)
        results.extend(hits)
    snippets = [normalize_text(r.get("snippet","")) for r in results if r.get("snippet")]
    summary = summarize_texts(snippets, max_sentences=6)
    out = {
        "topic": user_topic,
        "summary": summary,
        "sources": results[:20]
    }
    save_cache(cache_key, out)
    return out
