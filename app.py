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

# ======================== CONFIG ========================
st.set_page_config(page_title="Analyse Douanière", layout="wide")

# Footer fixed CSS
def inject_footer():
    st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f0f2f6;
            text-align: center;
            padding: 10px;
            font-size: 13px;
            color: #777;
        }
    </style>
    <div class="footer">
        🌐 Application d'analyse douanière | Développé par SDA Team
    </div>
    """, unsafe_allow_html=True)

# Sidebar branding
def sidebar_footer():
    st.sidebar.markdown("""
    ---
    🌐 **SDA Analytics Platform**
    📈 Suivi & Visualisation des échanges douaniers
    © 2025 SDA Consulting
    """)

data_dir = "data"
admin_password = "admin123"  # A sécuriser en prod

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
    st.markdown("- Moyenne, Écart-type, Min/Max permettent une première lecture des tendances.")
    st.divider()

    colonnes_num = df.select_dtypes(include="number").columns.tolist()
    if colonnes_num:
        col_num = st.selectbox("🔢 Choisir une variable numérique :", colonnes_num)
        fig = px.histogram(df, x=col_num, nbins=20, marginal="box", title=f"Distribution de {col_num}")
        st.plotly_chart(fig, use_container_width=True)

    colonnes_cat = df.select_dtypes(include="object").columns.tolist()
    if colonnes_cat:
        col_cat = st.selectbox("🏷️ Choisir une variable catégorielle :", colonnes_cat)
        counts = df[col_cat].value_counts().reset_index()
        fig_bar = px.bar(counts, x='index', y=col_cat, title=f"Répartition de {col_cat}")
        st.plotly_chart(fig_bar, use_container_width=True)

    colonnes_date = [c for c in df.columns if "date" in c.lower() or "mois" in c.lower()]
    if colonnes_date and colonnes_num:
        date_col = st.selectbox("🗓️ Colonne temporelle :", colonnes_date)
        ts_col = st.selectbox("📉 Valeur à tracer :", colonnes_num)
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.dropna(subset=[date_col])
            df = df.sort_values(date_col)
            fig = px.line(df, x=date_col, y=ts_col, title=f"Évolution de {ts_col}")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("Erreur dans l'affichage temporel")

# ===================== MAIN APP =====================
st.title("📦 Analyse des Données Douanières")
st.markdown("Choisissez une catégorie, une année, un mois pour afficher les données.")

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
            st.dataframe(df)

            # 🔍 Filtres dynamiques
            if st.checkbox("🔎 Activer les filtres"):
                for col in df.columns:
                    if df[col].dtype == 'object':
                        filtre = st.multiselect(f"Filtrer {col}", options=df[col].unique())
                        if filtre:
                            df = df[df[col].isin(filtre)]
                st.dataframe(df)

            # 📊 Dashboard
            if st.button("📊 Générer le tableau de bord"):
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

    if st.sidebar.button("📄 Importer"):
        if new_file and new_month:
            path = os.path.join(data_dir, new_category, new_year, new_month)
            with open(path, "wb") as f:
                f.write(new_file.read())
            st.sidebar.success(f"Fichier {new_month} importé avec succès !")
        else:
            st.sidebar.warning("Remplir tous les champs")

# Injecter les bas de page
inject_footer()
sidebar_footer()
