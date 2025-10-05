import os
import requests
from dotenv import load_dotenv
from services.generate_image import generate_images_with_runware
import asyncio

# -------------------------------
# Cargar variables de entorno
# -------------------------------
load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

BASE_URL = "https://api.linkedin.com/v2"

# Headers oficiales según documentación
HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

# -------------------------------
# 1️⃣ Subir imagen a LinkedIn
# -------------------------------
def upload_image_to_linkedin(image_path):
    """Registra y sube una imagen a LinkedIn"""
    register_url = f"{BASE_URL}/assets?action=registerUpload"
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": LINKEDIN_PERSON_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    # Paso 1: Registrar subida
    resp = requests.post(register_url, headers=HEADERS, json=register_body)
    resp.raise_for_status()
    data = resp.json()

    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = data["value"]["asset"]

    # Paso 2: Subir binario
    with open(image_path, "rb") as f:
        upload_headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
        }
        upload_resp = requests.post(upload_url, data=f, headers=upload_headers)
        upload_resp.raise_for_status()

    print(f"✅ Imagen subida correctamente: {asset_urn}")
    return asset_urn

# -------------------------------
# 2️⃣ Publicar un post (texto o imagen)
# -------------------------------
def publish_linkedin_post(text, image_urn=None):
    """Publica un post en LinkedIn con o sin imagen"""
    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "IMAGE" if image_urn else "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    # Si hay imagen, agregar metadata
    if image_urn:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "description": {"text": "Imagen generada automáticamente"},
                "media": image_urn,
                "title": {"text": "Imagen generada con IA"}
            }
        ]

    resp = requests.post(f"{BASE_URL}/ugcPosts", headers=HEADERS, json=payload)
    resp.raise_for_status()

    print("✅ Post publicado correctamente")
    print("🆔 ID del post:", resp.headers.get("x-restli-id"))
    return resp.json()

# -------------------------------
# 3️⃣ Crear post con imagen generada por IA
# -------------------------------
def create_post_with_generated_image(prompt, prompts_for_images):
    """Genera una imagen con IA, la sube y publica un post"""
    image_files = asyncio.run(generate_images_with_runware(prompts_for_images))
    image_urn = None

    if image_files:
        image_urn = upload_image_to_linkedin(image_files[0])

    return publish_linkedin_post(prompt, image_urn=image_urn)

def build_post_content(script: dict) -> str:
    """
    Construye el contenido final del post de LinkedIn a partir del guion generado por el agente.
    Retorna un texto listo para publicar en LinkedIn.
    """
    # Extraer partes del guion
    title = script.get("title", "").strip()
    structure = script.get("structure", [])
    cta = script.get("cta", "").strip()
    hashtags = script.get("hashtags", [])
    
    # Validar que structure sea lista
    if isinstance(structure, list):
        body = "\n".join(p.strip() for p in structure)
    else:
        body = str(structure).strip()

    # Construir la sección de hashtags
    if isinstance(hashtags, list) and hashtags:
        hashtags_text = " ".join(hashtags)
    elif isinstance(hashtags, str):
        hashtags_text = hashtags.strip()
    else:
        hashtags_text = ""

    # Ensamblar post completo con formato limpio
    post_parts = [title, body]
    
    if cta:
        post_parts.append(f"💬 {cta}")
    if hashtags_text:
        post_parts.append(hashtags_text)
    
    # Unir secciones con saltos de línea dobles
    post = "\n".join(part for part in post_parts if part)

    return post
