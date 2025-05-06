
import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# -------- CONFIGS --------
ARQ_PRODUTOS = "produtos.json"
PASTA_PDFS = "orcamentos"
SHEET_NAME = "Nome da Planilha"
JSON_CRED_PATH = "Planilhas.json"

# -------- AUTENTICAÇÃO GOOGLE --------
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(JSON_CRED_PATH, scopes=scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Erro na autenticação com Google Sheets: {e}")
        return None

# -------- DADOS LOCAIS --------
def carregar_dados():
    if not os.path.exists(ARQ_PRODUTOS):
        with open(ARQ_PRODUTOS, "w") as f:
            json.dump({"fixos": [], "produtos": []}, f)
    with open(ARQ_PRODUTOS, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQ_PRODUTOS, "w") as f:
        json.dump(dados, f, indent=4)

# -------- PDF --------
def gerar_pdf(nome_cliente, contato, bairro, itens, total_geral):
    os.makedirs(PASTA_PDFS, exist_ok=True)
    data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"{PASTA_PDFS}/orcamento_{nome_cliente.replace(' ', '_')}_{data}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"Orçamento - AQUI-DECK", ln=True, align="C")
    pdf.cell(200, 10, f"Cliente: {nome_cliente}", ln=True)
    pdf.cell(200, 10, f"Contato: {contato} - Bairro: {bairro}", ln=True)
    pdf.cell(200, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(5)

    pdf.cell(40, 10, "Produto")
    pdf.cell(30, 10, "Qtd")
    pdf.cell(40, 10, "Comp. (mm)")
    pdf.cell(40, 10, "Valor")
    pdf.cell(40, 10, "Total", ln=True)

    for item in itens:
        pdf.cell(40, 10, item["produto"])
        pdf.cell(30, 10, str(item["qtd"]))
        pdf.cell(40, 10, str(item["comp"]))
        pdf.cell(40, 10, f"R$ {item['valor_unit']:.2f}")
        pdf.cell(40, 10, f"R$ {item['total']:.2f}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, f"Total Geral: R$ {total_geral:.2f}", ln=True)
    pdf.output(nome_arquivo)
    return nome_arquivo
    #nova função envia para Driver 
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def enviar_para_drive(nome_arquivo):
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = Credentials.from_service_account_file(JSON_CRED_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': os.path.basename(nome_arquivo),
            'mimeType': 'application/pdf'
        }
        media = MediaFileUpload(nome_arquivo, mimetype='application/pdf')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success(f"Arquivo enviado ao Google Drive! ID: {file.get('id')}")
    except Exception as e:
        st.error(f"Erro ao enviar para o Google Drive: {e}")

# -------- APP PRINCIPAL --------
def main():
    st.title("AQUI-DECK App")

    dados = carregar_dados()
    modo = st.sidebar.radio("Escolha o modo:", ["Cadastro", "Orçamento"])

    if modo == "Cadastro":
        st.subheader("Cadastro de Produtos ou Fixos")
        tipo = st.selectbox("Tipo:", ["Fixo", "Produto"])

        if tipo == "Fixo":
            nome = st.text_input("Nome do Serviço Fixo")
            valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            if st.button("Salvar Serviço Fixo") and nome.strip():
                dados["fixos"].append({"nome": nome, "valor": valor})
                salvar_dados(dados)
                st.success("Serviço salvo com sucesso!")

        elif tipo == "Produto":
            nome = st.text_input("Nome do Produto")
            base = st.number_input("Valor Base (R$)", min_value=0.0, format="%.2f")
            imposto = st.number_input("Imposto (%)", min_value=0.0, format="%.2f")
            repasse = st.number_input("Repasse (R$)", min_value=0.0, format="%.2f")
            usinagem = st.number_input("Usinagem (R$)", min_value=0.0, format="%.2f")

            valor_final = base + (base * imposto / 100) + repasse + usinagem
            st.write(f"Valor Final: R$ {valor_final:.2f}")

            if st.button("Salvar Produto") and nome.strip():
                dados["produtos"].append({"nome": nome, "valor": round(valor_final, 2)})
                salvar_dados(dados)
                st.success("Produto salvo com sucesso!")

    elif modo == "Orçamento":
        st.subheader("Orçamento para Cliente")
        nome_cliente = st.text_input("Nome do Cliente")
        contato = st.text_input("Contato")
        bairro = st.text_input("Bairro")

        if "itens" not in st.session_state:
            st.session_state.itens = []

        nomes_produtos = [p["nome"] for p in dados["produtos"]]
        produto_sel = st.selectbox("Produto:", nomes_produtos)
        qtd = st.number_input("Quantidade", min_value=0.0)
        comp = st.number_input("Comprimento (em mm)", min_value=0.0)

        if st.button("Adicionar Produto"):
            valor_unit = next((p["valor"] for p in dados["produtos"] if p["nome"] == produto_sel), 0)
            total = (qtd * comp / 1000) * valor_unit
            st.session_state.itens.append({
                "produto": produto_sel,
                "qtd": qtd,
                "comp": comp,
                "valor_unit": valor_unit,
                "total": total
            })
            st.success(f"{produto_sel} adicionado ao pedido!")
#butao
        if name == "main": main()
            from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ID da pasta no Google Drive
PASTA_ID = "0B8YxMAd2J3kFckV4VjVhV1Y1NE0"

def enviar_para_drive(caminho_arquivo):
    try:
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(JSON_CRED_PATH, scopes=scope)
        service = build("drive", "v3", credentials=creds)

        nome_arquivo = os.path.basename(caminho_arquivo)
        arquivo_metadata = {
            "name": nome_arquivo,
            "parents": [PASTA_ID]
        }
        media = MediaFileUpload(caminho_arquivo, resumable=True)

        service.files().create(
            body=arquivo_metadata,
            media_body=media,
            fields="id"
        ).execute()

        st.success(f"PDF enviado para o Google Drive com sucesso.")
    except Exception as e:
        st.error(f"Erro ao enviar para o Google Drive: {e}")
