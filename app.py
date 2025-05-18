import streamlit as st
import gspread
from google.oauth2 import service_account

# Autenticação com Google Sheets
credentials_dict = st.secrets["GOOGLE_CREDENTIALS"]
credentials = service_account.Credentials.from_service_account_info(
    credentials_dict
)
gc = gspread.authorize(credentials)

# Abrir planilha pela URL
sheet_url = credentials_dict["sheet_url"]
sh = gc.open_by_url(sheet_url)

# Usar (ou criar) a aba "Dados"
try:
    aba = sh.worksheet("Dados")
except:
    aba = sh.add_worksheet(title="Dados", rows="100", cols="2")
    aba.append_row(["Nome"])  # Cabeçalho

# Interface
st.title("Cadastro de Nome")
nome = st.text_input("Digite seu nome:")

if st.button("Salvar"):
    if nome.strip():
        aba.append_row([nome.strip()])
        st.success(f"Nome '{nome}' salvo com sucesso!")
        st.markdown(f"**Ver planilha:** [Abrir]({sheet_url})")
    else:
        st.warning("Digite um nome válido.")
