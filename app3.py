import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_extras.let_it_rain import rain
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport

# ======================== CONFIG ========================
st.set_page_config(page_title="Analyse Douanière", layout="wide")

# =========== LIBS & SETUP POUR LE STYLE ================
# === Logo en haut à gauche ===
st.sidebar.image("kiks.jpeg", width=180)  # Logo SDA Academy

# === Détecter le thème selon l'heure (sombre après 18h)
now = datetime.now()
dark_mode = now.hour >= 18 or now.hour < 6

# === CSS Thème sombre ou clair + Design général ===
theme_color = "#001f3f" if dark_mode else "#0077b6"
bg_color = "#1e1e1e" if dark_mode else "#f4f9ff"
text_color = "#ffffff" if dark_mode else "#003566"
card_color = "#2a2a2a" if dark_mode else "#ffffff"

st.markdown(f"""
    <style>
        .main {{
            background-color: {bg_color};
            color: {text_color};
        }}

        h1, h2, h3 {{
            color: {text_color};
        }}

        div[data-testid="metric-container"] {{
            background-color: {card_color};
            border: 2px solid #d4e9ff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.05);
            color: {text_color};
        }}

        button[kind="primary"] {{
            background-color: {theme_color} !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold;
        }}

        button[kind="primary"]:hover {{
            background-color: #005f8c !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #dff6ff;
        }}

        footer {{
            visibility: hidden;
        }}
    </style>
""", unsafe_allow_html=True)

# ============== AUTHENTIFICATION SIMPLE =================
users = {"admin": "1234", "josias": "2025"}

st.sidebar.title("🔐 Authentification")
username = st.sidebar.text_input("Nom d'utilisateur")
password = st.sidebar.text_input("Mot de passe", type="password")

if username in users and users[username] == password:
    st.success("Connexion réussie !")
    rain(emoji="📦", font_size=28, falling_speed=3, animation_length="medium")

    # ============== PAGE PRINCIPALE =================
    st.title("📊 Kiks Consulting Analysis")

    uploaded_file = st.file_uploader("Téléverser un fichier Excel", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu des données :", df.head())

        # ====== Graphiques interactifs ======
        if "Pays" in df.columns and "Valeur FOB (USD)" in df.columns:
            fig = px.bar(df, x="Pays", y="Valeur FOB (USD)", color="Pays",
                         title="Valeur FOB par Pays")
            st.plotly_chart(fig, use_container_width=True)

        # ====== Analyse automatique avec ydata-profiling ======
        st.subheader("📑 Rapport automatique")
        profile = ProfileReport(df, explorative=True)
        st_profile_report(profile)

else:
    st.warning("Veuillez entrer vos identifiants.")
