import pandas as pd
import numpy as np
from services.openai_client import embed_texts
from utils.cache import load_cache, save_cache

HOOKS_CSV = "data/hooks.csv"

def load_hooks():
    df = pd.read_csv(HOOKS_CSV)
    return df.fillna("")

def pick_top_hooks(topic_text, n=3):
    """
    Carga hooks, usa embeddings para medir similitud con el tema, 
    utiliza caché para evitar recalcular y devuelve n adaptados.
    """
    # 1. Cargar hooks
    df = load_hooks()
    templates = df["hook_text"].tolist()

    # 2. Intentar cargar embeddings cacheados
    cache_key = "hooks_embeddings_v1"
    cache = load_cache(cache_key, ttl_seconds=60*60*24)  # 24h de vida

    if cache:
        print("⚡ Usando embeddings cacheados de hooks")
        hook_embs = np.array(cache["embeddings"])
    else:
        print("💡 Generando embeddings nuevos para hooks...")
        hook_embs = embed_texts(templates)
        save_cache(cache_key, {"embeddings": hook_embs.tolist()})

    # 3. Generar embedding del tema actual
    topic_emb = embed_texts([topic_text])[0]

    # 4. Calcular similitud coseno
    sims = np.dot(hook_embs, topic_emb) / (
        np.linalg.norm(hook_embs, axis=1) * np.linalg.norm(topic_emb) + 1e-9
    )

    # 5. Obtener los n más similares
    top_idxs = np.argsort(sims)[-n:][::-1]
    selected = []
    for i in top_idxs:
        row = df.iloc[i].to_dict()
        template = row.get("hook_text", "")
        adapted = (
            template.replace("{topic}", topic_text)
                    .replace("{x}", topic_text)
                    .replace("[tema]", topic_text)
        )
        selected.append({
            "id": row.get("id"),
            "hook": adapted.strip(),
            "similarity": float(sims[i]),
            "meta": row
        })

    return selected