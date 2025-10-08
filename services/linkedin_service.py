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
LINKEDIN_ORGANIZATION_URN = os.getenv("LINKEDIN_ORGANIZATION_URN")

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
def upload_image_to_linkedin(image_path, author=LINKEDIN_PERSON_URN):
    """Registra y sube una imagen a LinkedIn"""
    register_url = f"{BASE_URL}/assets?action=registerUpload"
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author,
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
def publish_linkedin_post(text, image_urn=None, author=LINKEDIN_PERSON_URN):
    """Publica un post en LinkedIn con o sin imagen"""

    payload = {
        "author": author,
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
def create_post_with_generated_image(prompt, prompts_for_images, mode="personal"):
    """Genera una imagen con IA, la sube y publica un post"""
    image_files = asyncio.run(generate_images_with_runware(prompts_for_images))
    image_urn = None

    AUTHOR_URN = LINKEDIN_PERSON_URN if mode == "personal" else LINKEDIN_ORGANIZATION_URN

    if image_files:
        image_urn = upload_image_to_linkedin(image_files[0], author=AUTHOR_URN)

    if not image_urn:
        print("⚠️ No se pudo subir la imagen a LinkedIn.")
        raise ValueError("No se pudo subir la imagen a LinkedIn.")

    return publish_linkedin_post(prompt, image_urn=image_urn, author=AUTHOR_URN)
