# main.py
import json
from datetime import datetime
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

def main():
    # Paso 1: Elegir tipo de tema
    tema_choice = ask_option(
        "Seleccionar como quieres elegir el tema del post:",
        ["Automático", "Semi-Automatico", "Manual"]
    )

    temas = [
        "Tendencias tecnológicas 2025-2026: lenguajes, frameworks y paradigmas emergentes",
        "Diseño de software escalable: arquitecturas limpias, DDD y buen dominio técnico",
        "Automatización práctica: integraciones reales con n8n, herramientas no-code y low-code",
        "Desarrollo híbrido: combinar .NET, Python y otros stacks en soluciones modernas",
        "Agentes autónomos e IA multimodal como asistentes del sistema",
        "Copilots e IA generativa integrados en el ciclo de vida del software (CI/CD, QA, monitoreo)",
        "Productividad del desarrollador: scripts, automatización y uso estratégico de IA",
        "Equipos inteligentes: Scrum 2.0, colaboración híbrida y herramientas de apoyo",
        "Carreras tech 2026: nuevos roles, habilidades y estrategias de preparación",
        "Branding personal para ingenieros: autoridad, nicho y visibilidad en mercados competitivos",
        "Del código manual a la orquestación: evolución del desarrollo de software",
        "Ecosistema moderno: contenedores, microservicios, serverless y nube como estándar",
        "No-code vs código: criterios para elegir, límites, casos de éxito",
        "Tecnología con propósito: emprendimiento responsable, software sostenible y ética tech",
        "Historias de software: narrativas de startups, fracasos, pivot y éxito tecnológico"
    ]
    selected_topic = ""
    if tema_choice == "Automático":
        selected_topic = get_trending_topic(temas)
    elif tema_choice == "Semi-Automatico":
        selected_topic = ask_option("Selecciona un tema:", temas)
    else:
        selected_topic = input("\n✍️ Escribe el tema que quieres usar: ").strip()


    if not selected_topic:        
        print("⚠️ No se ha proporcionado un tema.")
        return main()

    print(f"\n🧠 Generando contenido para el tema: {selected_topic}")

    # Paso 2: Ejecutar flujo de generación
    out = run_flow(selected_topic)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"output_run_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ Resultado guardado en output_run_{timestamp}.json")

    script = out.get("script", {})
    promt_for_image = script.get("promt_for_image", "")
    post_text = build_post_content(script)

    print("\n📄 Contenido generado:")
    print(f"{post_text}\n")

    # Paso 3: Menú principal
    main_choice = ask_option(
        "¿Qué quieres hacer ahora?",
        [
            "Publicar en perfil personal",
            "Publicar en cuenta de empresa",
            "Generar nuevamente sin publicar",
            "Salir"
        ]
    )

    if main_choice == "Salir":
        print("👋 Saliendo del programa...")
        return

    if "Generar nuevamente" in main_choice:
        print("🔁 Reiniciando generación...")
        return main()  # vuelve a empezar el flujo completo

    mode = "personal" if "personal" in main_choice.lower() else "organization"

    # Paso 4: Confirmar publicación
    publish = ask_option("¿Deseas publicar este post en LinkedIn?", ["Sí", "No"], default="Sí")
    if publish == "Sí":
        print("\n📢 Publicando en LinkedIn...")
        try:
            create_post_with_generated_image(post_text, [promt_for_image], mode=mode)
            print("✅ Publicación exitosa en LinkedIn")
        except Exception as e:
            print(f"❌ Error publicando en LinkedIn: {e}")
    else:
        print("⏭️ Publicación omitida. Puedes revisar el archivo generado.")

if __name__ == "__main__":
    main()
