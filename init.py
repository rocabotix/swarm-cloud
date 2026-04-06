# init.py - Vérification rapide du projet avant de lancer
import os
from dotenv import load_dotenv
from config import ANTHROPIC_API_KEY, THEMATIQUES

load_dotenv()

print("=" * 60)
print("🔧 INITIALISATION DU POLYMARKET INSIDER SWARM")
print("=" * 60)

# Vérification des clés
if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.startswith("sk-ant-"):
    print("✅ ANTHROPIC_API_KEY → OK")
else:
    print("❌ ANTHROPIC_API_KEY manquante ou invalide dans .env")

print(f"✅ Thématiques activées : {THEMATIQUES}")

# Vérification des fichiers obligatoires
fichiers_requis = ["models.py", "config.py", "api_client.py", "swarm_graph.py", "reporter.py", "main.py", "test_swarm.py"]
manquants = [f for f in fichiers_requis if not os.path.exists(f)]

if manquants:
    print(f"⚠️ Fichiers manquants : {manquants}")
else:
    print("✅ Tous les fichiers du projet sont présents")

print("\n🎉 Initialisation terminée !")
print("   Tape maintenant : python test_swarm.py")
print("   (pour tester le swarm complet)")