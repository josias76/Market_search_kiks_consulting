# 📁 Arborescence
# ├── app.py
# ├── data/
# │   ├── Agroalimentaire/
# │   │   └── 2023/
# │   │       └── 01.xlsx, 02.xlsx, ...
# │   └── Matériaux_de_construction/
# │       └── 2024/03.xlsx, ...
# └── requirements.txt

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

# ======================== CONFIG ========================
st.set_page_config(page_title="Analyse Douanière", layout="wide")

# Chemin vers les données et mot de passe admin
data_dir = "data"
admin_password = "admin123"
user_login = {"admin": "admin123", "analyste": "pass456"}

# ==================== UTILS =====================
def list_categories():
    return [cat for cat in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, cat))]

def list_years(category):
    path = os.path.join(data_dir, category)
    return sorted([y for y in os.listdir(path) if os.path.isdir(os.path.join(path, y))])

def list_months(category, year):
    path = os.path.join(data_dir, category, year)
    return sorted([f for f in os.listdir(path) if f.endswith(".xlsx")])

def load_data(category, year, month_file):
    path = os.path.join(data_dir, category, year, month_file)
    return pd.read_excel(path)

# ================== DASHBOARD ===================
def show_dashboard(df):
    st.markdown("## 📊 Tableau de bord interactif")
    st.subheader("📌 Statistiques globales")
    st.write(df.describe())

    st.markdown("**🧠 Interprétation :**")
    st.markdown("- Les statistiques descriptives permettent de cerner les tendances principales. Par exemple, une moyenne élevée peut signaler une dominance de certaines valeurs dans le marché.")
    st.divider()

    colonnes_num = df.select_dtypes(include="number").columns.tolist()
    if colonnes_num:
        col_num = st.selectbox("🔢 Choisir une variable numérique :", colonnes_num)
        fig = px.histogram(df, x=col_num, nbins=20, marginal="box", title=f"Distribution de {col_num}")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"📌 **Interprétation** : Une distribution de {col_num} permet de détecter les valeurs aberrantes, les asymétries du marché ou les pics saisonniers.")

    colonnes_cat = df.select_dtypes(include="object").columns.tolist()
    if colonnes_cat:
        col_cat = st.selectbox("🏷️ Choisir une variable catégorielle :", colonnes_cat)
        counts = df[col_cat].value_counts().reset_index()
        
        fig_bar = px.bar(counts, x='index', y=col_cat, title=f"Répartition de {col_cat}")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown(f"📌 **Interprétation** : Cette répartition nous renseigne sur la dominance de certaines catégories dans les échanges douaniers.")

    colonnes_date = [c for c in df.columns if "date" in c.lower() or "mois" in c.lower()]
    if colonnes_date and colonnes_num:
        date_col = st.selectbox("🗓️ Colonne temporelle :", colonnes_date)
        ts_col = st.selectbox("📉 Valeur à tracer :", colonnes_num)
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.dropna(subset=[date_col])
            df = df.sort_values(date_col)
            fig = px.line(df, x=date_col, y=ts_col, title=f"Évolution de {ts_col} dans le temps")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"📌 **Interprétation** : Ce graphique permet d’identifier des tendances saisonnières ou des anomalies dans la variable {ts_col} au cours du temps.")
        except:
            st.warning("Erreur dans l'affichage temporel")

# ===================== PAGE D'ACCUEIL =====================
st.title("📦 Analyse des Données Douanières")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("### 🔐 Connexion requise")
    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username in user_login and password == user_login[username]:
            st.session_state.auth = True
            st.success("Connexion réussie !")
        else:
            st.error("Identifiants incorrects")
    st.stop()

# ===================== APP INTERACTIVE =====================
st.markdown("### 📂 Choisissez une catégorie, année et fichier pour commencer")
categories = list_categories()
category = st.selectbox("📁 Choisissez une catégorie :", categories)

if category:
    years = list_years(category)
    year = st.selectbox("📅 Choisissez une année :", years)

    if year:
        months = list_months(category, year)
        month = st.selectbox("🗂️ Choisissez un fichier mensuel :", months)

        if month:
            df = load_data(category, year, month)

            if st.checkbox("📌 Activer les filtres"):
                for col in df.columns:
                    if df[col].dtype == 'object':
                        filtre = st.multiselect(f"Filtrer {col}", options=df[col].unique())
                        if filtre:
                            df = df[df[col].isin(filtre)]
                st.dataframe(df)
            else:
                st.dataframe(df)

            if st.button("🧬 Profiling complet du dataset"):
                profile = ProfileReport(df, title="Profiling Report", explorative=True)
                st_profile_report(profile)

            if st.button("📊 Générer le tableau de bord intéractif"):
                show_dashboard(df)

# ================== IMPORT PAR ADMIN ===================
st.sidebar.markdown("## 🔐 Importation admin")
mdp = st.sidebar.text_input("Mot de passe", type="password")

if mdp == admin_password:
    st.sidebar.success("Connecté comme admin")
    st.sidebar.markdown("### 📁 Importer un fichier")

    new_category = st.sidebar.selectbox("Catégorie :", categories)
    new_year = st.sidebar.selectbox("Année :", list_years(new_category))
    new_month = st.sidebar.text_input("Nom du fichier (ex: 05.xlsx)")
    new_file = st.sidebar.file_uploader("Uploader un fichier Excel", type=["xlsx"])

    if st.sidebar.button("📤 Importer"):
        if new_file and new_month:
            path = os.path.join(data_dir, new_category, new_year, new_month)
            with open(path, "wb") as f:
                f.write(new_file.read())
            st.sidebar.success(f"Fichier {new_month} importé avec succès !")
        else:
            st.sidebar.warning("Remplir tous les champs")

# ================== FOOTER ===================
st.sidebar.markdown("---")
st.sidebar.markdown("[📘 Documentation](https://github.com) | ⓒ 2025 SDA Academy")

st.markdown("---")
st.markdown("<center>Développé avec ❤️ par SDA Academy</center>", unsafe_allow_html=True)
