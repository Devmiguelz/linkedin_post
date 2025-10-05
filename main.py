# main.py
import json
import argparse
from agents.research_agent import research_topic
from agents.performance_agent import analyze_performance
from agents.script_agent import build_script
from agents.hook_agent import pick_top_hooks

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
    temas = ["Productividad", "Desarrollo personal", "Liderazgo", "Programación", "Inteligencia Artificial"]
    selected_topic = ask_option("¿Sobre qué tema quieres crear tu publicación?", temas)
    out = run_flow(selected_topic)
    import json
    with open("output_run.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("✅ Resultado guardado en output_run.json")
