import os
import pandas as pd
from datetime import datetime, timedelta
import random
import zipfile
import shutil

# === Paramètres ===
output_dir = "Petrole_Derives"
zip_output_path = "Petrole_Derives_2020_2024.zip"
years = range(2020, 2025)
months = range(1, 13)

# === Produits du secteur pétrole ===
petrole_products = [
    "Pétrole brut", "Essence", "Gazole", "Kérosène", "Mazout",
    "Bitume", "Lubrifiants", "Gaz de pétrole liquéfié (GPL)",
    "Huile moteur", "Additifs pétroliers", "Fioul lourd", "Coke de pétrole"
]
zones = ["Nord", "Sud", "Est", "Ouest"]
provinces = ["Fès", "Kénitra", "Oujda", "Tanger", "Casablanca", "Agadir"]
bureaux = ["Aéroport", "Port", "Poste Frontière"]
operateurs = ["PetroMaroc", "AfricOil", "EnergyPlus", "MarocFuel", "PetroLog", "HydroCarb"]

# === Nettoyer dossier précédent ===
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# === Génération des fichiers ===
for year in years:
    year_dir = os.path.join(output_dir, str(year))
    os.makedirs(year_dir, exist_ok=True)

    for month in months:
        data = []
        for i in range(10):  # 10 lignes par mois
            date = datetime(year, month, 1) + timedelta(days=random.randint(0, 27))
            data.append({
                "N°": i + 1,
                "ZONE": random.choice(zones),
                "PROVINCE": random.choice(provinces),
                "BUREAU": random.choice(bureaux),
                "OPERATEUR": random.choice(operateurs),
                "DESIGNATION": random.choice(petrole_products),
                "CATEGORIE": "Pétrole et Dérivés",
                "FLUX": random.choice(["Entrée", "Sortie"]),
                "TONNAGE": round(random.uniform(100, 5000), 2),
                "DATE": date.strftime("%Y-%m-%d")
            })
        df = pd.DataFrame(data)
        file_name = f"{year}_{str(month).zfill(2)}.xlsx"
        df.to_excel(os.path.join(year_dir, file_name), index=False)

# === Création du fichier ZIP ===
with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf: 
    for root, _, files in os.walk(output_dir):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, output_dir)
            zipf.write(full_path, arcname=relative_path)

print(f"✅ Fichier ZIP généré : {zip_output_path}")
