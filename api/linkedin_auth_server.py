import os
import secrets
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import urllib.parse
import uuid

# 🔹 Cargar variables de entorno
load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")
SCOPES = ["openid", "profile", "w_member_social", "email"]

# Generar un state aleatorio
STATE = uuid.uuid4()

# Codificar parámetros
encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')
encoded_scope = '%2C'.join(SCOPES)
 
AUTH_URL = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={encoded_redirect_uri}"
    f"&scope={encoded_scope}"
    f"&state={STATE}"
)

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# 🔹 Headers recomendados
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "python-linkedin-oauth/1.0"
}

# ==========================
# 🔹 Funciones auxiliares
# ==========================
def get_access_token(code):
    """Intercambiar authorization code por access token"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_URL, headers=HEADERS, data=data)
    if response.status_code != 200:
        raise Exception(f"Error al obtener access token: {response.status_code}, {response.text}")
    return response.json()

def get_linkedin_profile(access_token):
    """Obtener datos del perfil de LinkedIn usando OpenID Connect"""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "python-script"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error al obtener perfil: {response.status_code}, {response.text}")
    return response.json()

def get_admin_organizations(access_token):
    """
    Obtiene todas las organizaciones (páginas de empresa) donde el usuario autenticado es administrador aprobado.
    Devuelve una lista de URNs.
    """
    url = "https://api.linkedin.com/rest/organizationAuthorizations"
    params = {
        "q": "roleAssignee",
        "role": "ADMINISTRATOR",
        "state": "APPROVED"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202509",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(f"Error al obtener organizaciones: {resp.status_code}, {resp.text}")
    
    data = resp.json()
    org_urns = []
    elements = data.get("elements", [])
    for element in elements:
        org = element.get("organization")
        if org:
            org_urns.append(org)
    
    return org_urns

def save_to_env(access_token, refresh_token, person_urn, organization_urn):
    """Guardar token y URN en .env"""
    with open(".env", "a") as f:
        f.write(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")
        f.write(f"\nLINKEDIN_REFRESH_TOKEN={refresh_token}")
        f.write(f"\nLINKEDIN_PERSON_URN=urn:li:person:{person_urn}")
        f.write(f"\nLINKEDIN_ORGANIZATION_URN={organization_urn}")

# ==========================
# 🔹 HTTP Server
# ==========================
class LinkedInAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        code = query.get("code")
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No authorization code provided")
            return

        try:
            code = code[0]
            print(f"✅ Authorization code recibido: {code}")

            token_data = get_access_token(code)
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            print(f"🔑 Access token obtenido: {access_token}")
            if refresh_token:
                print(f"🔄 Refresh token: {refresh_token}")

            profile = get_linkedin_profile(access_token)
            #organizations = get_admin_organizations(access_token)
            #print(f"🏢 Organizaciones administradas: {organizations}")

            person_urn = profile.get("sub")
            organization_urn = "abc12345";

            save_to_env(access_token, refresh_token, person_urn, organization_urn)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b" Access Token guardado en .env. Puedes cerrar esta ventana.")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_server():
    print("🌐 Abre esta URL en tu navegador para autorizar la app:")
    print(AUTH_URL)
    print("🕐 Esperando respuesta en http://localhost:8000/callback ...")
    server = HTTPServer(("localhost", 8000), LinkedInAuthHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
