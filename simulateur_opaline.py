import streamlit as st
import smtplib
import pandas as pd
import gspread
import json
import os
import datetime
import time
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 📌 Récupérer les credentials depuis Streamlit Cloud Secrets
creds_json = os.getenv("GOOGLE_SHEETS_CREDS")

if not creds_json:
    raise ValueError("Erreur : GOOGLE_SHEETS_CREDS n'est pas défini sur Streamlit Cloud !")

try:
    creds_dict = json.loads(creds_json)
except json.JSONDecodeError:
    raise ValueError("Erreur : Les credentials JSON sont mal formatés.")

# 📌 Connexion à Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📌 Ouvrir le Google Sheet principal
SHEET_ID = "1hDLA-eGfVDeNj08RC-VrwXbHrRhO76XTNTWcdp4YY0A"  # Remplace par ton vrai ID
sheet = client.open_by_key(SHEET_ID).sheet1

# 📌 Vérifier et ajouter les en-têtes si elles ne sont pas présentes
def verifier_et_ajouter_entetes():
    entetes = [
        "Date", "Nom", "Prénom", "Email",
        "Nombre de clients mensuels", "Nombre de kits 1P", "Nombre de kits 2P",
        "Chiffre d'Affaires (€)", "Coût Total (€)", "Bénéfice Net (€)"
    ]
    premiere_ligne = sheet.row_values(1)

    if premiere_ligne != entetes:
        sheet.insert_row(entetes, 1)

verifier_et_ajouter_entetes()

# 📌 Configuration de la page
st.set_page_config(page_title="Simulateur de Rentabilité Opaline", layout="wide")

# 📌 Affichage du logo Opaline
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://quozyli.com/wp-content/uploads/2025/03/logo_opaline.png" width="320">
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 Titre principal
st.markdown("<h1 style='text-align: center; font-size: 40px;'>📊 Simulateur de Rentabilité Opaline</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: grey;'>Estimez vos gains en quelques secondes</h3>", unsafe_allow_html=True)

# 📌 Ligne de séparation
st.markdown("<hr style='border: 2px solid #55833D;'>", unsafe_allow_html=True)

# 📌 Inputs utilisateur
st.markdown("<h2 style='margin-top: 30px;'>📌 Informations de votre activité</h2>", unsafe_allow_html=True)
clients = st.number_input("Nombre de clients mensuels", min_value=1, value=50, step=1)
kits_1p = st.number_input("Nombre de kits 1 personne vendus/mois (14€ HT)", min_value=0, value=100, step=1)
kits_2p = st.number_input("Nombre de kits 2 personnes vendus/mois (22€ HT)", min_value=0, value=50, step=1)

# 📌 Paramètres financiers
prix_1p = 14  
prix_2p = 22  
cout_par_kit = 12.15  

# 📌 Calculs financiers
chiffre_affaires = (kits_1p * prix_1p) + (kits_2p * prix_2p)
cout_total = (kits_1p + kits_2p) * cout_par_kit
profit = chiffre_affaires - cout_total

# 📌 Affichage des résultats
st.markdown("<hr style='border: 2px solid #55833D;'>", unsafe_allow_html=True)
st.markdown(f"""
    <div style="text-align: center; font-size: 28px; font-weight: bold; padding: 20px; border: 2px solid #55833D; border-radius: 10px; background-color: #f2f2f2; color: black;">
        💰 <span style="color: #55833D;">Chiffre d’affaires mensuel :</span> {chiffre_affaires:.2f} €<br><br>
        📉 <span style="color: #555;">Coût total :</span> {cout_total:.2f} €<br><br>
        🚀 <span style="color: #55833D;">Bénéfice net estimé :</span> {profit:.2f} €
    </div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border: 2px solid #55833D;'>", unsafe_allow_html=True)

# 📌 Fonction pour enregistrer les données dans Google Sheets
def enregistrer_donnees(nom, prenom, email):
    date_aujourdhui = datetime.datetime.today().strftime('%Y-%m-%d')
    
    existing_emails = sheet.col_values(4)
    if email not in existing_emails:

# 📌 Vérification avant insertion dans Google Sheets
test_data = [
    datetime.datetime.today().strftime('%Y-%m-%d'),
    nom, prenom, email, clients, kits_1p, kits_2p,
    chiffre_affaires, cout_total, profit
]

st.write("🔍 Données envoyées à Google Sheets :", json.dumps(test_data, indent=4))

        sheet.append_row([
            date_aujourdhui, nom, prenom, email, clients, kits_1p, kits_2p, 
            chiffre_affaires, cout_total, profit
        ])

# 📌 Capture des informations utilisateur avec **loader visuel**
st.markdown("<h2 style='margin-top: 40px;'>📩 Recevez votre analyse</h2>", unsafe_allow_html=True)
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
email = st.text_input("Email")

if st.button("📨 Envoyer mon analyse"):
    if email and nom and prenom:
        with st.spinner("📩 Traitement en cours..."):
            progress_bar = st.progress(0)
            for percent in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent + 1)

            enregistrer_donnees(nom, prenom, email)

        st.success(f"📩 Un email a été envoyé à {email} avec votre simulation.")
    else:
        st.warning("Veuillez remplir tous les champs.")
