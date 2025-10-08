# main.py
import json
from datetime import datetime
from agents.research_agent import research_topic
from agents.performance_agent import analyze_performance
from agents.script_agent import build_script_with_template, build_post_content
from agents.hook_agent import pick_top_hooks
from services.linkedin_service import create_post_with_generated_image
from services.openai_client import get_trending_topic
from utils.text_utils import ask_option

def run_flow(user_topic, profile_path="data/profile_data.json"):
    profile = json.load(open(profile_path, "r", encoding="utf-8"))
    print("1) Research agent -> buscando y resumiendo...")
    research = research_topic(user_topic, profile)
    print("2) Performance agent -> analizando posts históricos...")
    perf = analyze_performance()
    print("3) Script agent -> generando guión...")
    script = build_script_with_template(research, perf, profile)
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

def main():
    # Paso 1: Elegir tipo de tema
    tema_choice = ask_option(
        "Seleccionar como quieres elegir el tema del post:",
        ["Automático", "Semi-Automatico", "Manual"]
    )

    temas = [
        # 🚀 Tendencias y aspiraciones
        "Tendencias tecnológicas 2025-2026: lenguajes, frameworks y paradigmas que marcarán la próxima ola",
        "Arquitectura limpia y DDD moderno: ¿realmente escalable o exceso de complejidad?",
        "Automatización práctica: cómo integrar n8n y herramientas no-code sin perder control técnico",
        "Desarrollo híbrido .NET + Python: cómo combinar ecosistemas sin duplicar esfuerzos",
        "Agentes autónomos e IA multimodal: casos reales y riesgos de su adopción prematura",
        "Productividad del desarrollador en 2026: IA, scripts y automatización como ventaja competitiva",
        "Historias de software: éxitos y fracasos reales de startups tecnológicas",
        "Tecnología con propósito: emprendimientos sostenibles y ética en la era de la automatización",

        # ⚖️ Temas críticos y debates
        "¿Puede n8n o herramientas no-code sostener software de gran escala? Análisis de costos y límites",
        "El mito de la IA que reemplaza desarrolladores: ¿productividad o dependencia?",
        "Microservicios vs Monolitos modernos: ¿qué arquitectura tiene más sentido en 2026?",
        "Copilots e IA generativa: ¿mejoran la calidad del código o crean deuda técnica invisible?",
        "Scrum 2.0 y equipos híbridos con IA: ¿más eficiencia o más burocracia digital?",
        "Cloud y costos ocultos: cómo evitar sorpresas en proyectos medianos y grandes",
        "No-code vs código tradicional: ¿democratización o pérdida de control?"
    ]
    selected_topic = ""
    if tema_choice == "Automático":
        selected_topic = get_trending_topic()
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
    prompt_for_image = script.get("prompt_for_image", "")
    post_text = build_post_content(script)

    print("\n📄 Contenido generado:")
    print(f"{post_text}\n")

    print("🖼️ Prompt para imagen:")
    print(f"{prompt_for_image}\n")

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

    create_post_with_generated_image(post_text, [prompt_for_image], mode=mode)

if __name__ == "__main__":
    main()
