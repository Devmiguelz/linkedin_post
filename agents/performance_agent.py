import os
import pandas as pd
from utils.text_utils import extract_common_words
from services.linkedin_scraper import load_exported_posts
from utils.cache import load_cache, save_cache

def compute_engagement_score_local(post):
    likes = post.get("likes",0) or 0
    comments = post.get("comments",0) or 0
    shares = post.get("shares",0) or 0
    impressions = post.get("impressions", 1) or 1
    score = (comments * 3 + shares * 4 + likes * 1) / max(impressions,1)
    return score

def analyze_performance(posts_dir="data/posts", cache_ttl=60*60):
    cache_key = f"perf_{os.path.abspath(posts_dir)}"
    cached = load_cache(cache_key, ttl_seconds=cache_ttl)
    if cached:
        return cached

    posts = load_exported_posts(posts_dir)
    if not posts:
        return {"top_posts": [], "avg_length":0, "common_words": [], "counts":0}

    df = pd.DataFrame(posts)
    # normalize numeric columns
    for c in ["likes","comments","shares","impressions"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        else:
            df[c] = 0
    df["engagement"] = df.apply(lambda r: compute_engagement_score_local(r), axis=1)
    df["length"] = df["text"].fillna("").apply(len)
    top_posts = df.sort_values("engagement", ascending=False).head(20).to_dict(orient="records")
    avg_length = float(df["length"].mean())
    common_words = extract_common_words(df["text"].fillna("").tolist(), top_n=25)
    out = {
        "top_posts": top_posts,
        "avg_length": avg_length,
        "common_words": common_words,
        "counts": len(df)
    }
    save_cache(cache_key, out)
    return out
