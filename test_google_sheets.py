import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Définir le scope d'accès
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Charger les credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_creds.json", scope)
client = gspread.authorize(creds)

# Ouvrir le Google Sheet
SHEET_ID = "1hDLA-eGfVDeNj08RC-VrwXbHrRhO76XTNTWcdp4YY0A"  # Remplace par l’ID de ton Google Sheets
sheet = client.open_by_key(SHEET_ID).sheet1

# Écrire une ligne test
sheet.append_row(["2025-03-10", "Test", "Python", "test@email.com"])

print("✅ Connexion réussie et ligne ajoutée !")