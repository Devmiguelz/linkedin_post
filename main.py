# main.py
import json
from agents.research_agent import research_topic
from agents.performance_agent import analyze_performance
from agents.script_agent import build_script
from agents.hook_agent import pick_top_hooks
from services.linkedin_service import create_post_with_generated_image, build_post_content
from services.openai_client import get_trending_topic

def run_flow(user_topic, profile_path="data/profile_data.json"):
    profile = json.load(open(profile_path, "r", encoding="utf-8"))
    print("1) Research agent -> buscando y resumiendo...")
    research = research_topic(user_topic, profile)
    print("2) Performance agent -> analizando posts históricos...")
    perf = analyze_performance()
    print("3) Script agent -> generando guión...")
    script = build_script(research, perf, profile)
    print("4) Hook agent -> seleccionando hooks...")
    hooks = pick_top_hooks(user_topic, n=3)
    result = {
        "profile": profile,
        "research": research,
        "performance": perf,
        "script": script,
        "hooks": hooks
    }
    return result

def ask_option(prompt, options, default=None):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    while True:
        choice = input("Seleccione una opción: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
        print("⚠️ Opción inválida, intente de nuevo.")

if __name__ == "__main__":
    temas = [
        "Inteligencia Artificial Generativa",
        "Agentes autónomos e IA multimodal",
        "Integración de IA en productos .NET y Python",
        "Arquitectura limpia y DDD moderno",
        "Automatización con n8n y herramientas no-code",
        "Scrum y equipos híbridos con IA",
        "Carreras y empleos en la era de la IA",
        "Branding personal para desarrolladores",
        "Productividad con IA y copilots",
        "Futuro del desarrollo de software 2026",
    ]
    selected_topic = get_trending_topic(temas)
    out = run_flow(selected_topic)
    
    with open("output_run.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("✅ Resultado guardado en output_run.json")

    script = out.get("script", {})
    promt_for_image = script.get("promt_for_image", "")

    post_text = build_post_content(script)

    print("\n📢 Publicando en LinkedIn...")
    try:
        create_post_with_generated_image(post_text, [promt_for_image])
        print("✅ Publicación exitosa en LinkedIn")
    except Exception as e:
        print(f"❌ Error publicando en LinkedIn: {e}")
