#!/bin/bash
# run.sh — Lance le backend FastAPI et le frontend Streamlit simultanément
# Usage : bash run.sh

set -e

# Vérifie que le fichier .env existe
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env introuvable !"
    echo "   Copiez .env.example en .env et renseignez votre clé GROQ_API_KEY."
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════╗"
echo "║         UFC AI JUDGE v1.0            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "🚀 Démarrage du backend FastAPI sur http://localhost:8000"
echo "🎨 Démarrage du frontend Streamlit sur http://localhost:8501"
echo ""
echo "Appuyez sur Ctrl+C pour tout arrêter."
echo ""

# Lance le backend en arrière-plan
uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Petite pause pour laisser FastAPI démarrer
sleep 2

# Lance Streamlit au premier plan
streamlit run frontend/app.py --server.port 8501 --server.address localhost

# Nettoyage à l'arrêt
kill $BACKEND_PID 2>/dev/null
echo "Serveurs arrêtés."
