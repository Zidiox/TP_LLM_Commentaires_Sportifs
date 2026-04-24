# 🥊 UFC AI Judge

> **Analyse audio intelligente de combats UFC** — Pipeline complet YouTube → Whisper STT → LLaMA 3.3 → Dashboard interactif

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Whisper%20%2B%20LLaMA-F55036?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

**Contributeurs :** Guillaume GUTHIER, Hippolyte GINESTE , Willen AMICHE

---

## 📋 Description

**UFC AI Judge** est une application web qui analyse automatiquement un combat UFC à partir d'une simple URL YouTube. Elle télécharge l'audio, le transcrit via Whisper, l'analyse avec un LLM pour extraire les actions clés, puis calcule une note objective pour chaque combattant, le tout affiché dans un dashboard interactif.

### Pipeline de données

```
URL YouTube
    │
    ▼  yt-dlp
Téléchargement audio
    │
    ▼  Groq Whisper Large v3
Transcription texte
    │
    ▼  Découpage en chunks (150 mots)
    │
    ▼  Groq LLaMA 3.3 70B  ──►  JSON structuré par action
Analyse LLM × N chunks         {fighter, action, category, score}
    │
    ▼  Python (scorer.py)   ──►  Calcul déterministe
Scoring backend                       Note /10
    │
    ▼  Streamlit + Plotly
Dashboard interactif
    │
    └──► Suppression du fichier audio temporaire
```

---

## ✨ Fonctionnalités

- **Transcription automatique** : audio YouTube → texte via Groq Whisper Large v3
- **Analyse LLM structurée** : extraction d'actions en JSON (frappe, takedown, soumission, défense...)
- **Scoring Python pur** : note calculée côté serveur
- **Dashboard interactif** : radar, timeline d'évolution des scores, comparaison +/-
- **Résumé narratif** : commentaire journalistique généré par le LLM
- **Moniteur LLM** : suivi des tokens (analyse, résumé, total) dans l'interface
- **Mini-player YouTube** : lecture intégrée avec marqueurs d'actions cliquables
- **Export** : CSV des actions + JSON complet téléchargeables
- **Architecture modulaire** : facile à étendre

---

## 🏗️ Architecture

```
ufc-ai-judge/
│
├── backend/
│   ├── main.py              # FastAPI — routes & orchestration
│   ├── config.py            # Variables d'env & constantes
│   ├── models.py            # Schémas Pydantic (requêtes/réponses)
│   │
│   ├── services/
│   │   ├── downloader.py    # yt-dlp : YouTube → fichier audio
│   │   ├── transcriber.py   # Groq Whisper : fichier audio → texte
│   │   ├── analyzer.py      # Groq LLaMA : texte → JSON actions
│   │   └── scorer.py        # Python : actions → note /10
│   │
│   └── utils/
│       └── text_utils.py    # Découpage & nettoyage du texte
│
├── frontend/
│   └── app.py               # Interface Streamlit + graphiques Plotly
│
├── temp/                    # Fichiers audio temporaires (auto-nettoyé)
├── .env                     # 🔒 Clé API (non versionné)
├── .env.example             # Template de configuration
├── requirements.txt
└── README.md
```

---

## ⚙️ Prérequis

| Outil | Version | Installation |
|---|---|---|
| Python | ≥ 3.11 | [python.org](https://python.org) |
| Clé API Groq | — | [console.groq.com](https://console.groq.com) (gratuit) |

---

## 🚀 Installation & Lancement

### 1. Cloner le dépôt

```bash
git clone https://github.com/Zidiox/TP_LLM_Commentaires_Sportifs.git
cd ufc-ai-judge
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate       # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la clé API

```bash
cp .env.example .env
# Éditez .env et renseignez votre clé Groq :
# GROQ_API_KEY=gsk_...
```

### 5. Lancer l'application

Dans deux terminaux séparés :

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

Ouvrez **http://localhost:8501** dans votre navigateur.

---

## 🎮 Utilisation

1. Collez une URL YouTube d'un combat UFC dans le champ dédié
2. Renseignez les noms des deux combattants
3. Cliquez sur **"LANCER L'ANALYSE"**
4. Patientez 1 à 3 minutes (selon la durée de la vidéo)
5. Consultez le dashboard : notes, radar, timeline, résumé narratif
6. Exportez les résultats en CSV ou JSON si besoin

---

## 📊 Barème de scoring

| Action | Points |
|---|---:|
| KO ou soumission réussie | **+5** |
| Takedown réussi | **+3** |
| Frappe significative | **+2** |
| Bonne défense | **+1** |
| Coup subi | **−1** |
| Takedown subi | **−2** |
| KO ou soumission subie | **−5** |

**Note finale** = `5.0 + Σ(points × 0.05)`, contenue entre **0** et **10**.

---

## 🔌 API REST

Le backend expose les endpoints suivants :

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Vérification de l'état du serveur |
| `POST` | `/analyze` | Lance le pipeline complet d'analyse |

### Exemple d'appel direct

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=JuBBIJ7adjM",
    "fighter_1": "Khabib Nurmagomedov",
    "fighter_2": "Conor McGregor"
  }'
```

Swagger disponible sur **http://localhost:8000/docs**

---

## 🔒 Sécurité

- La clé API Groq est chargée exclusivement via `.env`
- Le fichier `.env` est listé dans `.gitignore`
- Les fichiers audio temporaires sont automatiquement supprimés après traitement

---

## 📝 Licence

MIT — Voir [LICENSE](LICENSE) pour les détails.

---