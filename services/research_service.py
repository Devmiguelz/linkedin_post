import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def web_search(query, num=10):
    """
    Busca usando SerpApi si está configurado. Retorna lista de {'title','link','snippet'}.
    Si no hay SerpApi, intenta una búsqueda simple por requests (fallback).
    """
    results = []
    if SERPAPI_KEY:
        url = "https://serpapi.com/search.json"
        params = {"q": query, "api_key": SERPAPI_KEY, "num": num}
        try:
            r = requests.get(url, params=params, timeout=10).json()
            organic = r.get("organic_results", [])
            for o in organic:
                results.append({
                    "title": o.get("title"),
                    "link": o.get("link"),
                    "snippet": o.get("snippet","")
                })
            return results
        except Exception as e:
            print("SerpApi error:", e)
            
    try:
        ua = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(f"https://www.bing.com/search?q={requests.utils.quote(query)}", headers=ua, timeout=8)
        text = resp.text
        # heurística simple para extraer fragmentos (no robusto)
        snippets = []
        import re
        for m in re.finditer(r'<li class="b_algo".*?>(.*?)</li>', text, flags=re.S) :
            block = m.group(1)
            title_m = re.search(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', block, flags=re.S)
            snippet_m = re.search(r'<p>(.*?)</p>', block, flags=re.S)
            if title_m:
                link = title_m.group(1)
                title = re.sub('<.*?>', '', title_m.group(2)).strip()
                snippet = re.sub('<.*?>', '', snippet_m.group(1)).strip() if snippet_m else ""
                snippets.append({"title": title, "link": link, "snippet": snippet})
                if len(snippets) >= num:
                    break
        return snippets
    except Exception as e:
        print("Fallback web_search error:", e)
    return results

def summarize_texts(texts, max_sentences=5):
    """
    Resumen heurístico: juntar textos y devolver primeras oraciones más relevantes.
    Puedes mejorar usando un LLM.
    """
    import re
    big = " ".join([t for t in texts if t])
    # Limitar por tamaño
    big = big[:12000]
    sentences = re.split(r'(?<=[.!?])\s+', big)
    return " ".join(sentences[:max_sentences])
