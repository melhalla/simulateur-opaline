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

# 📌 Fonction pour enregistrer les données dans Google Sheets (sans vérification des doublons)
def enregistrer_donnees(nom, prenom, email):
    date_aujourdhui = datetime.datetime.today().strftime('%Y-%m-%d')

    # Enregistrement direct sans vérification de l'existence de l'email
    sheet.append_row([
        date_aujourdhui, nom, prenom, email, clients, kits_1p, kits_2p, 
        chiffre_affaires, cout_total, profit
    ])
# 📌 Fonction pour envoyer un email
def envoyer_email(nom, prenom, destinataire):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "blanchisserie.opaline@gmail.com"
    sender_password = "ezylyxtieibbytgc"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = destinataire
    msg['Subject'] = "Opaline - Opportunité de Franchise"

    body = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <img src="https://quozyli.com/wp-content/uploads/2025/03/Group-28.png" width="150" alt="Opaline" style="display: block; margin: auto;">
        <h2 style="text-align: center; color: #55833D;">Opaline - Votre simulation de rentabilité</h2>
        
        <p>Bonjour <strong>{nom} {prenom}</strong>,</p>
        
        <p>Merci d'avoir utilisé notre simulateur de rentabilité Opaline. Nous sommes ravis de voir votre intérêt pour cette opportunité unique.</p>
        
        <p>Voici un aperçu de votre potentiel financier en rejoignant notre réseau :</p>
        <ul>
            <li><strong>Chiffre d’affaires mensuel estimé :</strong> {chiffre_affaires:.2f} €</li>
            <li><strong>Coût total estimé :</strong> {cout_total:.2f} €</li>
            <li><strong>Bénéfice net estimé :</strong> {profit:.2f} €</li>
        </ul>

        <p>Opaline, c’est bien plus qu’une simple franchise : c’est une **opportunité clé en main** pour développer votre propre blanchisserie industrielle et générer des revenus récurrents. En tant que franchisé, vous bénéficiez :</p>
        <ul>
            <li>✅ D’une solution tout-en-un avec machines et gestion informatisée</li>
            <li>✅ D’un accompagnement complet pour réussir votre lancement</li>
            <li>✅ D’un marché en forte croissance grâce aux besoins des conciergeries et hôtelleries</li>
        </ul>

        <p>Si cette opportunité vous intéresse, nous serions ravis d’échanger avec vous pour approfondir votre projet et répondre à toutes vos questions.</p>

        <p><strong>📅 Nous pouvons convenir d’un rendez-vous pour discuter ensemble.</strong></p>

        <p>Nous vous enverrons également très prochainement un **business plan détaillé**, afin que vous puissiez analyser plus en profondeur les chiffres et le potentiel de votre future blanchisserie.</p>

        <p>📩 <strong>N’hésitez pas à nous contacter dès maintenant pour planifier un échange :</strong></p>
        <p style="text-align: center;">
            📧 <a href="mailto:contact@blanchisserie-opaline.com" style="color: #55833D; font-weight: bold;">contact@blanchisserie-opaline.com</a>
        </p>

        <p>À très bientôt,</p>
        <p><strong>L’équipe Opaline - La franchise de blanchisserie</strong></p>
    </div>
</body>
</html>
    """

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# 📌 Capture des informations utilisateur avec loader
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
email = st.text_input("Email")

if st.button("📨 Envoyer mon analyse"):
    if email and nom and prenom:
        with st.spinner("📩 Traitement en cours..."):
            enregistrer_donnees(nom, prenom, email)
            success = envoyer_email(nom, prenom, email)

        if success:
            st.success(f"📩 Un email a été envoyé à {email} avec votre simulation.")
    else:
        st.warning("Veuillez remplir tous les champs.")
