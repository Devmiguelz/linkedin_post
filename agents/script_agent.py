import json
from datetime import datetime
from services.openai_client import generate_text
from utils.text_utils import ask_option

from utils.path import get_path

def load_templates():
    """Carga las plantillas de guion desde el archivo JSON"""
    filepath = get_path("data/templates.json")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["templates"]

def confirm_template_selection(template):
    """Muestra la plantilla seleccionada y pregunta si desea usarla."""
    print("\n🧩 Estructura de la plantilla seleccionada:")
    print("─────────────────────────────")
    print(template["structure"])
    print("─────────────────────────────")
    confirm = input("¿Deseas usar esta plantilla? (s/n): ").strip().lower()
    return confirm in ["s", "si", "y", "yes"]

def select_template(templates):
    """Permite al usuario seleccionar y confirmar una plantilla."""
    while True:
        names = [t["name"] for t in templates]
        selected_name = ask_option("Seleccione el tipo de plantilla para generar el post:", names)
        selected_template = next(t for t in templates if t["name"] == selected_name)
        
        if confirm_template_selection(selected_template):
            print(f"\n✅ Usarás la plantilla: {selected_template['name']}")
            return selected_template
        else:
            print("\n🔁 Volviendo a mostrar las opciones...\n")

def build_script_with_template(research_insights: dict, perf: dict, profile_data: dict):
    templates = load_templates()
    selected_template = select_template(templates)

    template_text = selected_template["structure"]
    current_date = datetime.now().strftime("%d/%m/%Y")
    top_texts = [p.get("text", "")[:400] for p in perf.get("top_posts", [])][:6]

    prompt = f"""
    Eres un creador de contenido profesional para LinkedIn.
    Debes generar un post siguiendo esta plantilla:

    Plantilla:
    {template_text}

    Contexto:
    - Resumen del tema: {research_insights.get('summary')}
    - Perfil: {profile_data}
    - Ejemplos top posts: {top_texts}
    - Fecha actual: {current_date}

    Instrucciones:
    - Llena los campos entre {{}} con información coherente según el contexto.
    - Usa un tono profesional y cercano.
    - Mantén una longitud entre 200 y 400 palabras.
    - No agregues asteriscos para negritas ni otros formatos.
    - Genera un prompt para una imagen relacionada al tema.
    - Agrega una llamada a la acción final y hashtags relevantes.
    - Devuelve el resultado en formato JSON con las siguientes claves:
    {{
        "title": "Hook inicial potente",
        "content": "Texto completo generado a partir de la plantilla",
        "cta": "Pregunta o invitación al final",
        "hashtags": ["#Ejemplo1", "#Ejemplo2"],
        "prompt_for_image": "Prompt para generar una imagen"
    }}
    """

    response = generate_text(prompt, max_tokens=700)
    try:
        import re
        m = re.search(r'(\{.*\})', response, flags=re.S)
        json_str = m.group(1) if m else response
        return json.loads(json_str)
    except Exception:
        return {"raw": response}

def build_post_content(script: dict) -> str:
    """
    Construye el contenido final del post de LinkedIn a partir del guion generado por el agente.
    Retorna un texto listo para publicar en LinkedIn.
    """
    # Extraer partes del guion
    title = script.get("title", "").strip()
    structure = script.get("content", [])
    cta = script.get("cta", "").strip()
    hashtags = script.get("hashtags", [])
    
    # Validar que structure sea lista
    if isinstance(structure, list):
        body = "\n\n".join(p.strip() for p in structure)
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
    post = "\n\n".join(part for part in post_parts if part)

    return post