"""
frontend/app.py
Interface utilisateur Streamlit pour l'UFC AI Judge.
Lance avec : streamlit run frontend/app.py
"""

import time
import json

import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration de la page
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="UFC AI Judge",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS personnalisé — thème sombre cinématique
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

    /* Fond global */
    .stApp {
        background-color: #0a0a0f;
        color: #e8e8e0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111118;
        border-right: 1px solid #2a2a3a;
    }

    /* Titre principal */
    .main-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 4rem;
        letter-spacing: 0.08em;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0;
        line-height: 1;
    }
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        letter-spacing: 0.3em;
        color: #e53935;
        text-align: center;
        text-transform: uppercase;
        margin-top: 4px;
        margin-bottom: 2rem;
    }

    /* Séparateur rouge */
    .red-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e53935, transparent);
        margin: 1.5rem 0;
        border: none;
    }

    /* Carte de score */
    .score-card {
        background: linear-gradient(135deg, #16161f 0%, #1e1e2e 100%);
        border: 1px solid #2a2a3a;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .score-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: #e53935;
    }
    .score-card .fighter-name {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6rem;
        letter-spacing: 0.05em;
        color: #ffffff;
        margin-bottom: 0.25rem;
    }
    .score-card .score-value {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3.5rem;
        color: #e53935;
        line-height: 1;
    }
    .score-card .score-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 0.2em;
        color: #666;
        text-transform: uppercase;
    }

    /* Badges de stat */
    .stat-badge {
        display: inline-block;
        background: #1e1e2e;
        border: 1px solid #2a2a3a;
        border-radius: 6px;
        padding: 0.3rem 0.7rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #aaa;
        margin: 0.2rem;
    }
    .stat-badge span {
        color: #e8e8e0;
        font-weight: 600;
    }

    /* Sections */
    .section-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.4rem;
        letter-spacing: 0.1em;
        color: #e8e8e0;
        border-left: 3px solid #e53935;
        padding-left: 0.75rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* Transcript box */
    .transcript-box {
        background: #0f0f18;
        border: 1px solid #1e1e2e;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #888;
        line-height: 1.7;
        max-height: 200px;
        overflow-y: auto;
    }

    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #16161f, #1a1a28);
        border: 1px solid #2a2a3a;
        border-left: 3px solid #e53935;
        border-radius: 8px;
        padding: 1.25rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #ccc;
        line-height: 1.7;
        font-style: italic;
    }

    /* Buttons */
    .stButton > button {
        background: #e53935 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.1em !important;
        padding: 0.6rem 1.5rem !important;
        width: 100%;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #c62828 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(229,57,53,0.3) !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #111118 !important;
        border: 1px solid #2a2a3a !important;
        color: #e8e8e0 !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #e53935 !important;
        box-shadow: 0 0 0 1px #e53935 !important;
    }

    /* Labels */
    .stTextInput label, .stTextArea label {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        color: #666 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #111118 !important;
        border: 1px solid #2a2a3a !important;
        color: #aaa !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: #e53935 !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #e53935 !important;
    }

    /* Metric */
    [data-testid="stMetricValue"] {
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 2rem !important;
        color: #e8e8e0 !important;
    }

    /* Masque le hamburger menu et le footer */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

API_BASE_URL = "http://localhost:8000"

CATEGORY_LABELS = {
    "ko": "KO",
    "submission": "Soumission",
    "takedown": "Takedown",
    "strike": "Frappe",
    "defense": "Défense",
    "strike_taken": "Coup subi",
    "takedown_taken": "Takedown subi",
    "ko_taken": "KO subi",
    "submission_taken": "Soumission subie",
}

POSITIVE_CATS = {"ko", "submission", "takedown", "strike", "defense"}


# ---------------------------------------------------------------------------
# Helper : vérification que le backend est actif
# ---------------------------------------------------------------------------

def check_backend_health() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Helper : appel API analyse
# ---------------------------------------------------------------------------

def call_analyze_api(youtube_url: str, fighter_1: str, fighter_2: str) -> dict:
    payload = {
        "youtube_url": youtube_url,
        "fighter_1": fighter_1,
        "fighter_2": fighter_2,
    }
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        json=payload,
        timeout=600,  # 10 min max (vidéos longues)
    )
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Helper : graphiques Plotly
# ---------------------------------------------------------------------------

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#aaa", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
)


def render_score_comparison(stats: list[dict]) -> go.Figure:
    """Graphique en barres horizontales comparant les notes finales."""
    names = [s["name"].split()[-1] for s in stats]  # Prénom court
    scores = [s["final_score"] for s in stats]
    colors = ["#e53935", "#1565c0"]

    fig = go.Figure()
    for i, (name, score, color) in enumerate(zip(names, scores, colors)):
        fig.add_trace(
            go.Bar(
                x=[score],
                y=[name],
                orientation="h",
                marker=dict(color=color, line=dict(color="rgba(0,0,0,0)")),
                text=f"  {score}/10",
                textposition="outside",
                textfont=dict(family="Bebas Neue", size=16, color=color),
                name=name,
                hovertemplate=f"<b>{name}</b><br>Note : {score}/10<extra></extra>",
            )
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis=dict(range=[0, 11], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(family="Bebas Neue", size=18, color="#fff")),
        barmode="overlay",
        showlegend=False,
        height=130,
        bargap=0.3,
    )
    return fig


def render_actions_radar(stats: list[dict]) -> go.Figure:
    """Radar chart : répartition des types d'actions par combattant."""
    categories = ["takedown", "strike", "defense", "ko", "submission"]
    labels = [CATEGORY_LABELS[c] for c in categories]
    colors = ["#e53935", "#1565c0"]

    fig = go.Figure()
    for i, s in enumerate(stats):
        values = [s["actions_by_category"].get(c, 0) for c in categories]
        values_closed = values + [values[0]]  # Ferme le polygone
        labels_closed = labels + [labels[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=values_closed,
                theta=labels_closed,
                fill="toself",
                fillcolor=f"rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:7],16)},0.15)",
                line=dict(color=colors[i], width=2),
                name=s["name"].split()[-1],
            )
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                showticklabels=False,
                showline=False,
                gridcolor="#2a2a3a",
            ),
            angularaxis=dict(
                gridcolor="#2a2a3a",
                linecolor="#2a2a3a",
                tickfont=dict(color="#aaa", size=10),
            ),
        ),
        legend=dict(
            font=dict(family="Inter", size=11, color="#aaa"),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=320,
    )
    return fig


def render_actions_timeline(actions: list[dict], fighter_1: str, fighter_2: str) -> go.Figure:
    """Graphique linéaire de l'évolution des scores cumulés au fil des actions."""
    colors = {"fighter_1": "#e53935", "fighter_2": "#1565c0"}

    score_f1, score_f2 = 5.0, 5.0
    coeff = 0.05
    history_f1, history_f2 = [score_f1], [score_f2]
    x_labels = [0]

    f1_lower = fighter_1.lower().split()
    f2_lower = fighter_2.lower().split()

    for i, action in enumerate(actions):
        name_lower = action["fighter"].lower()
        pts = action["score"] * coeff
        if any(t in name_lower for t in f1_lower):
            score_f1 = round(max(0, min(10, score_f1 + pts)), 2)
        elif any(t in name_lower for t in f2_lower):
            score_f2 = round(max(0, min(10, score_f2 + pts)), 2)
        history_f1.append(score_f1)
        history_f2.append(score_f2)
        x_labels.append(i + 1)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_labels, y=history_f1,
            mode="lines", line=dict(color="#e53935", width=2.5),
            name=fighter_1.split()[-1],
            fill="tozeroy",
            fillcolor="rgba(229,57,53,0.05)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_labels, y=history_f2,
            mode="lines", line=dict(color="#1565c0", width=2.5),
            name=fighter_2.split()[-1],
            fill="tozeroy",
            fillcolor="rgba(21,101,192,0.05)",
        )
    )
    # Ligne de base à 5
    fig.add_hline(y=5, line=dict(color="#333", width=1, dash="dash"))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis=dict(
            title="Nᵉ action",
            showgrid=False,
            color="#555",
            title_font=dict(size=10),
        ),
        yaxis=dict(
            title="Score cumulé",
            range=[0, 10.5],
            showgrid=True,
            gridcolor="#1a1a2a",
            color="#555",
            title_font=dict(size=10),
        ),
        legend=dict(
            font=dict(family="Inter", size=11, color="#aaa"),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=280,
    )
    return fig


def render_action_breakdown(stats: list[dict]) -> go.Figure:
    """Barres groupées : actions positives vs négatives par combattant."""
    names = [s["name"].split()[-1] for s in stats]
    positives = [s["total_positive_points"] for s in stats]
    negatives = [-s["total_negative_points"] for s in stats]  # Négatif pour affichage

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Points positifs",
            x=names, y=positives,
            marker_color=["#e53935", "#1565c0"],
            text=positives,
            textposition="outside",
            textfont=dict(size=12, color="#aaa"),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Points négatifs",
            x=names, y=negatives,
            marker_color=["rgba(229,57,53,0.3)", "rgba(21,101,192,0.3)"],
            text=[s["total_negative_points"] for s in stats],
            textposition="outside",
            textfont=dict(size=12, color="#555"),
        )
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="overlay",
        yaxis=dict(showgrid=True, gridcolor="#1a1a2a", zeroline=True, zerolinecolor="#333"),
        xaxis=dict(showgrid=False, tickfont=dict(family="Bebas Neue", size=15, color="#fff")),
        showlegend=True,
        legend=dict(font=dict(size=10, color="#aaa"), bgcolor="rgba(0,0,0,0)"),
        height=260,
    )
    return fig


# ---------------------------------------------------------------------------
# Sidebar : paramètres
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div style="font-family: Bebas Neue, sans-serif; font-size: 1.4rem; '
        'letter-spacing: 0.1em; color: #e8e8e0; margin-bottom: 0.5rem;">⚙️ CONFIGURATION</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

    youtube_url = st.text_input(
        "URL YouTube",
        value="https://www.youtube.com/watch?v=JuBBIJ7adjM",
        help="Lien vers la vidéo YouTube du combat.",
    )

    fighter_1 = st.text_input("Combattant 1", value="Khabib Nurmagomedov")
    fighter_2 = st.text_input("Combattant 2", value="Conor McGregor")

    st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

    # Vérification du backend
    backend_ok = check_backend_health()
    if backend_ok:
        st.success("✅ Backend connecté", icon="🟢")
    else:
        st.error("❌ Backend hors ligne\n\nLancez : `uvicorn backend.main:app --reload`", icon="🔴")

    st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

    analyze_btn = st.button("🥊 LANCER L'ANALYSE", disabled=not backend_ok)

    st.markdown(
        '<div style="font-family: Inter, sans-serif; font-size: 0.65rem; '
        'color: #333; margin-top: 2rem; text-align: center; letter-spacing: 0.1em;">'
        'UFC AI JUDGE v1.0 • GROQ + WHISPER</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Header principal
# ---------------------------------------------------------------------------

st.markdown('<h1 class="main-title">UFC AI JUDGE</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Analyse audio intelligente de combats</p>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="red-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Logique d'analyse
# ---------------------------------------------------------------------------

if analyze_btn:
    if not youtube_url.strip():
        st.error("Veuillez entrer une URL YouTube.")
    elif not fighter_1.strip() or not fighter_2.strip():
        st.error("Veuillez renseigner les deux noms de combattants.")
    else:
        # Placeholder de progression
        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        steps = [
            (10, "🎧 Téléchargement de l'audio depuis YouTube..."),
            (30, "🧠 Transcription Whisper en cours..."),
            (60, "🔍 Analyse LLM par chunks..."),
            (85, "📊 Calcul des scores..."),
            (95, "✍️ Génération du résumé narratif..."),
        ]

        for pct, msg in steps[:2]:
            status_placeholder.info(msg)
            progress_bar.progress(pct)
            time.sleep(0.5)

        try:
            status_placeholder.info("🚀 Pipeline en cours (cela peut prendre 1-3 minutes)...")
            progress_bar.progress(20)

            result = call_analyze_api(youtube_url, fighter_1, fighter_2)

            progress_bar.progress(100)
            status_placeholder.success("✅ Analyse terminée !")
            time.sleep(0.8)
            status_placeholder.empty()
            progress_bar.empty()

            # ----------------------------------------------------------------
            # Affichage des résultats
            # ----------------------------------------------------------------

            stats = result.get("fighter_stats", [])
            actions = result.get("all_actions", [])

            # ── Scores finaux ──────────────────────────────────────────────
            st.markdown('<div class="section-title">VERDICT FINAL</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            for col, s in zip([col1, col2], stats):
                with col:
                    st.markdown(
                        f"""
                        <div class="score-card">
                            <div class="fighter-name">{s['name']}</div>
                            <div class="score-value">{s['final_score']}</div>
                            <div class="score-label">/ 10</div>
                            <div style="margin-top: 0.75rem;">
                                <span class="stat-badge">+ <span>{s['total_positive_points']} pts</span></span>
                                <span class="stat-badge">- <span>{s['total_negative_points']} pts</span></span>
                                <span class="stat-badge">Actions <span>{len([a for a in actions if s['name'].split()[-1].lower() in a['fighter'].lower()])}</span></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # ── Graphique comparaison scores ───────────────────────────────
            st.plotly_chart(
                render_score_comparison(stats),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            # ── Résumé narratif ────────────────────────────────────────────
            if result.get("summary"):
                st.markdown('<div class="section-title">RÉSUMÉ DU COMBAT</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="summary-box">{result["summary"]}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

            # ── Graphiques d'analyse ───────────────────────────────────────
            st.markdown('<div class="section-title">ANALYSE DÉTAILLÉE</div>', unsafe_allow_html=True)

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown(
                    '<p style="font-family: Inter; font-size: 0.7rem; letter-spacing: 0.15em; '
                    'text-transform: uppercase; color: #555; margin-bottom: 0.5rem;">RADAR DES ACTIONS</p>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    render_actions_radar(stats),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            with chart_col2:
                st.markdown(
                    '<p style="font-family: Inter; font-size: 0.7rem; letter-spacing: 0.15em; '
                    'text-transform: uppercase; color: #555; margin-bottom: 0.5rem;">POINTS +/-</p>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    render_action_breakdown(stats),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            # ── Évolution du score ─────────────────────────────────────────
            if actions:
                st.markdown(
                    '<p style="font-family: Inter; font-size: 0.7rem; letter-spacing: 0.15em; '
                    'text-transform: uppercase; color: #555; margin-bottom: 0.5rem;">ÉVOLUTION DU SCORE EN TEMPS RÉEL</p>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    render_actions_timeline(actions, fighter_1, fighter_2),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            st.markdown('<hr class="red-divider">', unsafe_allow_html=True)

            # ── Métadonnées ────────────────────────────────────────────────
            meta_col1, meta_col2, meta_col3 = st.columns(3)
            with meta_col1:
                st.metric("Mots transcrits", f"{result['transcript_word_count']:,}")
            with meta_col2:
                st.metric("Chunks analysés", result["chunks_analyzed"])
            with meta_col3:
                st.metric("Actions détectées", len(actions))

            # ── Transcription ──────────────────────────────────────────────
            with st.expander("📄 Voir la transcription complète"):
                st.markdown(
                    f'<div class="transcript-box">{result["transcript"]}</div>',
                    unsafe_allow_html=True,
                )

            # ── Détail JSON des actions ────────────────────────────────────
            with st.expander("🔎 Détail de toutes les actions détectées"):
                df = pd.DataFrame(actions)
                if not df.empty:
                    df["category"] = df["category"].map(
                        lambda c: CATEGORY_LABELS.get(c, c)
                    )
                    df.columns = ["Combattant", "Action", "Catégorie", "Points"]
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Bouton export CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="⬇️ Exporter en CSV",
                        data=csv,
                        file_name=f"ufc_analysis_{fighter_1.split()[-1]}_{fighter_2.split()[-1]}.csv",
                        mime="text/csv",
                    )

            # ── Export JSON complet ────────────────────────────────────────
            with st.expander("📦 Export JSON complet"):
                st.download_button(
                    label="⬇️ Télécharger le JSON complet",
                    data=json.dumps(result, indent=2, ensure_ascii=False),
                    file_name=f"ufc_analysis_{fighter_1.split()[-1]}_{fighter_2.split()[-1]}.json",
                    mime="application/json",
                )

        except requests.exceptions.ConnectionError:
            status_placeholder.empty()
            progress_bar.empty()
            st.error(
                "❌ Impossible de joindre le backend.\n\n"
                "Vérifiez que le serveur FastAPI tourne sur `localhost:8000`.\n\n"
                "```bash\nuvicorn backend.main:app --reload --port 8000\n```"
            )
        except requests.exceptions.HTTPError as e:
            status_placeholder.empty()
            progress_bar.empty()
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            st.error(f"❌ Erreur API : {detail}")
        except Exception as e:
            status_placeholder.empty()
            progress_bar.empty()
            st.error(f"❌ Erreur inattendue : {e}")

else:
    # ── État initial (pas encore d'analyse) ───────────────────────────────
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem; color: #333;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🥊</div>
            <div style="font-family: Bebas Neue, sans-serif; font-size: 1.5rem;
                        letter-spacing: 0.1em; color: #444;">
                ENTREZ UNE URL YOUTUBE ET LANCEZ L'ANALYSE
            </div>
            <div style="font-family: Inter, sans-serif; font-size: 0.8rem;
                        color: #333; margin-top: 0.5rem;">
                Le pipeline complet prend généralement 1 à 3 minutes selon la durée de la vidéo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
