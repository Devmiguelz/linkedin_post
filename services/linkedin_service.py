import os
import requests
from dotenv import load_dotenv
from services.generate_image import generate_images_with_runware 
import asyncio

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

HEADERS = {
    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.linkedin.com/v2"

def upload_image_to_linkedin(image_path):
    register_url = f"{BASE_URL}/assets?action=registerUpload"
    register_body = {
        "registerUploadRequest": {
            "owner": LINKEDIN_PERSON_URN,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ],
        }
    }

    resp = requests.post(register_url, headers=HEADERS, json=register_body)
    resp.raise_for_status()
    data = resp.json()

    upload_url = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = data["value"]["asset"]

    with open(image_path, "rb") as f:
        upload_resp = requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"})
        upload_resp.raise_for_status()

    print(f"✅ Imagen subida: {asset_urn}")
    return asset_urn

def publish_linkedin_post(text, image_urn=None):
    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE" if not image_urn else "IMAGE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    if image_urn:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {"status": "READY", "media": image_urn}
        ]

    resp = requests.post(f"{BASE_URL}/ugcPosts", headers=HEADERS, json=payload)
    resp.raise_for_status()
    print("✅ Post publicado correctamente")
    return resp.json()

def create_post_with_generated_image(prompt, scenes):
    image_files = asyncio.run(generate_images_with_runware(scenes))
    image_urn = None
    if image_files:
        image_urn = upload_image_to_linkedin(image_files[0])
    return publish_linkedin_post(prompt, image_urn=image_urn)
