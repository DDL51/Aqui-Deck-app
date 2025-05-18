import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Autenticação
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
gc = gspread.authorize(credentials)

# Acessa a planilha
sheet = gc.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
aba = sheet.worksheet("Produtos")

# Interface simples
nome = st.text_input("Digite um nome para salvar na planilha:")
if st.button("Salvar"):
    if nome.strip():
        aba.append_row([nome])
        st.success("Salvo com sucesso!")
    else:
        st.warning("Nome vazio.")
