import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Escopo de acesso
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Carrega as credenciais do arquivo secrets.toml
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

# Autenticação com gspread
gc = gspread.authorize(credentials)

st.title("Leitor de Google Sheets com Streamlit")

# ID da planilha (já preenchido com sua planilha real)
sheet_id = "1Dx4X3a0GagiB0eyv_wqOPkmkSfUtW9i6B-sQATf75H0"

try:
    # Abre a planilha
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.sheet1  # primeira aba

    # Lê os dados
    data = worksheet.get_all_values()
    st.write("Dados da planilha:")
    st.table(data)

except Exception as e:
    st.error(f"Erro ao acessar a planilha: {e}")
