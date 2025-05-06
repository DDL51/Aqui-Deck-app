
import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# -------- CONFIGS --------
ARQ_PRODUTOS = "produtos.json"
PASTA_PDFS = "orcamentos"
PASTA_DRIVE_ID = "0B8YxMAd2J3kFckV4VjVhV1Y1NE0"  # ID da pasta do Google Drive
SHEET_NAME = "Nome da Planilha"
JSON_CRED_PATH = "Planilhas.json"

# Conectar à planilha do Google Sheets
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(JSON_CRED_PATH, scopes=scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Erro na autenticação com Google Sheets: {e}")
        return None

# Carregar dados de produtos
def carregar_dados():
    if not os.path.exists(ARQ_PRODUTOS):
        with open(ARQ_PRODUTOS, "w") as f:
            json.dump({"fixos": [], "produtos": []}, f)
    with open(ARQ_PRODUTOS, "r") as f:
        return json.load(f)

# Salvar dados de produtos
def salvar_dados(dados):
    with open(ARQ_PRODUTOS, "w") as f:
        json.dump(dados, f, indent=4)

# Gerar o PDF
def gerar_pdf(nome_cliente, contato, bairro, itens, total_geral):
    os.makedirs(PASTA_PDFS, exist_ok=True)
    data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"{PASTA_PDFS}/orcamento_{nome_cliente.replace(' ', '')}{data}.pdf"
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Orçamento para {nome_cliente}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Contato: {contato}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Bairro: {bairro}", ln=True, align='C')
    pdf.cell(200, 10, txt="Itens:", ln=True)
    
    for item in itens:
        pdf.cell(200, 10, txt=f"- {item['nome']} ({item['quantidade']} x R$ {item['preco']})", ln=True)
    
    pdf.cell(200, 10, txt=f"Total: R$ {total_geral}", ln=True, align='C')
    
    pdf.output(nome_arquivo)
    return nome_arquivo

# Enviar o PDF para o Google Drive
def enviar_para_drive(caminho_arquivo):
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile("mycreds.txt")
    except Exception as e:
        st.error(f"Erro na autenticação com Google Drive: {e}")
        return None

    try:
        drive = GoogleDrive(gauth)
        arquivo_drive = drive.CreateFile({"title": os.path.basename(caminho_arquivo)})
        arquivo_drive.Upload()
        arquivo_drive.Upload(param={'folder_id': PASTA_DRIVE_ID})
        st.success("Arquivo enviado para o Google Drive com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar arquivo para o Google Drive: {e}")
