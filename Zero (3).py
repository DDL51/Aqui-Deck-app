import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2 import service_account

# -------- CONFIGS --------
ARQ_PRODUTOS = "produtos.json"
PASTA_PDFS = "orcamentos"
SHEET_NAME = "AQUI-DECK"

#Carregar credenciais do secret
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
import streamlit as st
import json
from google.oauth2 import service_account

# Carregar credenciais do secrets.toml
credentials_dict = st.secrets["GOOGLE_CREDENTIALS"]
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
# -------- AUTENTICAÇÃO GOOGLE --------
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
        creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open(SHEET_NAME).sheet1
    except Exception as e:
        st.error(f"Erro na autenticação com Google Sheets: {e}")
        return None

# -------- DADOS LOCAIS --------
def carregar_dados():
    if not os.path.exists(ARQ_PRODUTOS):
        with open(ARQ_PRODUTOS, "w") as f:
            json.dump({"Fixos": [], "Produtos": []}, f)
    with open(ARQ_PRODUTOS, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQ_PRODUTOS, "w") as f:
        json.dump(dados, f, indent=4)

# ORÇAMENTO........

CAMINHO_ORCAMENTOS = "orcamentos.json"
def carregar_orcamentos():
    if os.path.exists(CAMINHO_ORCAMENTOS):
        with open(CAMINHO_ORCAMENTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def salvar_orcamentos(lista_orcamentos):
    with open(CAMINHO_ORCAMENTOS, "w", encoding="utf-8") as f:
        json.dump(lista_orcamentos, f, indent=4, ensure_ascii=False)

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

# -------- ENVIAR PARA DRIVE --------
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

        drive = GoogleDrive(gauth)
        arquivo_drive = drive.CreateFile({
            'title': os.path.basename(caminho_arquivo),
            'parents': [{'id': PASTA_DRIVE_ID}]
        })
        arquivo_drive.SetContentFile(caminho_arquivo)
        arquivo_drive.Upload()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar para o Google Drive: {e}")
        return False
    
# APP PRINCIPAL --------
def main():
    st.title("AQUI-DECK")
    
    dados = carregar_dados()
    modo = st.sidebar.radio("Escolha o modo:", ["Cadastro", "Orçamentos", "Gerenciar"])
#PRIMEIRO NÍVEL 
    if modo == "Cadastro":
        st.subheader("Cadastro de Produtos ou Fixos")
        tipo = st.selectbox("Tipo:", ["Fixo", "Produto",])

        if tipo == "Fixo":
            nome = st.text_input("Nome do Serviço Fixo")
            valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
            if st.button("Salvar Serviço Fixo") and nome.strip():
                dados["Fixos"].append({"nome": nome, "valor": valor})
                salvar_dados(dados)
                st.success("Serviço salvo com sucesso!")

        elif tipo == "Produto":
            nome = st.text_input("Nome do Produto")
            base = st.number_input("Valor Base (R$)", min_value=0.0, format="%.2f")
            imposto = st.number_input("Imposto (%)", min_value=0.0, format="%.2f")
            repasse = st.number_input("Repasse (R$)", min_value=0.0, format="%.2f")
            usinagem = st.number_input("Usinagem (R$)", min_value=0.0, format="%.2f")
            if st.button("Salvar Produto") and nome.strip():
                valor_final = base + (base * imposto / 100) + repasse + usinagem
                dados["Produtos"].append({
                        "nome": nome,
                        "valor_base": base,
                        "imposto": imposto,
                        "repasse": repasse,
                        "usinagem": usinagem,
                        "valor_final": round(valor_final, 2)})
                salvar_dados(dados)
                st.success("Produto salvo com sucesso!")
# DEGUNDO NÍVEL 
    
    elif modo == "Orçamentos":
        st.subheader("Orçamento para Cliente")
        nome_cliente = st.text_input("Nome do Cliente")
        contato = st.text_input("Contato")
        bairro = st.text_input("Bairro")

        if "itens" not in st.session_state:
            st.session_state.itens = []

        nomes_produtos = [p["nome"] for p in dados["Produtos"]]
        produto_sel = st.selectbox("Produto:", nomes_produtos)
        qtd = st.number_input("Quantidade", min_value=0.0)
        comp = st.number_input("Comprimento (em mm)", min_value=0.0)

        if st.button("Adicionar Produto"):
            valor_unit = next((p["valor_final"] for p in dados["Produtos"] if p["nome"] == produto_sel), 0)
            total = (qtd * comp / 1000) * valor_unit
            st.session_state.itens.append({"produto": produto_sel, "qtd": qtd, "comp": comp, "valor_unit": valor_unit, "total": total})
            st.success(f"{produto_sel} adicionado ao pedido!")

        if st.session_state.itens:
            st.subheader("Itens do Pedido")
            total_geral = sum(i["total"] for i in st.session_state.itens)
            for i, item in enumerate(st.session_state.itens):
                st.write(f"{i+1}. {item['produto']} - Qtd: {item['qtd']} - Comp: {item['comp']} mm - Total: R$ {item['total']:.2f}")
            st.write(f"**Total Geral: R$ {total_geral:.2f}**")

        if st.button("Salvar Orçamento e Enviar"):
            if nome_cliente.strip() and contato.strip():
                arquivo = gerar_pdf(nome_cliente, contato, bairro, st.session_state.itens, total_geral)
                sucesso = enviar_para_drive(arquivo)

                if sucesso:
                    orcamentos = carregar_orcamentos()
                    novo_orcamento = {
                        "nome_cliente": nome_cliente,
                        "contato": contato,
                        "bairro": bairro,
                        "itens": st.session_state.itens,
                        "total": total_geral,
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    orcamentos.append(novo_orcamento)
                    salvar_orcamentos(orcamentos)
                    st.success("Orçamento salvo e PDF enviado para o Google Drive!")
                    st.session_state.itens = []
            else:
                st.warning("Preencha nome do cliente e contato.")
                
# TERCEIRO NÍVEL :      
    elif modo == "Gerenciar":
        sub_modo = st.radio("O que deseja gerenciar?", ["Produtos", "Orçamentos"])

        if sub_modo == "Produtos":
        # (mantenha aqui a lógica atual de gerenciamento de produtos)
            if not dados["Produtos"]:
                st.info("Nenhum produto cadastrado.")
            else:
                nomes_produtos = [p["nome"] for p in dados["Produtos"]]
                index_produto = st.selectbox("Selecione um produto para editar", options=range(len(nomes_produtos)), format_func=lambda i: nomes_produtos[i])
                produto = dados["Produtos"][index_produto]

                novo_nome = st.text_input("Nome do Produto", value=produto["nome"])
                novo_base = st.number_input("Valor Base (R$)", value=produto["valor_base"], min_value=0.0, format="%.2f")
                novo_imposto = st.number_input("Imposto (%)", value=produto["imposto"], min_value=0.0, format="%.2f")
                novo_repasse = st.number_input("Repasse (R$)", value=produto["repasse"], min_value=0.0, format="%.2f")
                novo_usinagem = st.number_input("Usinagem (R$)", value=produto["usinagem"], min_value=0.0, format="%.2f")

                st.markdown(f"<span style='color:red; font-weight:bold;'>Valor Final Atual: R$ {produto['valor_final']:.2f}</span>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Atualizar Produto"):
                    valor_final = novo_base + (novo_base * novo_imposto / 100) + novo_repasse + novo_usinagem
                    dados["Produtos"][index_produto] = {
                        "nome": novo_nome,
                        "valor_base": novo_base,
                        "imposto": novo_imposto,
                        "repasse": novo_repasse,
                        "usinagem": novo_usinagem,
                        "valor_final": round(valor_final, 2)} 
                    salvar_dados(dados)
                    st.success("Produto atualizado com sucesso!")

            with col2:
                if st.button("Excluir Produto"):
                    dados["Produtos"].pop(index_produto)
                    salvar_dados(dados)
                    st.success("Produto excluído com sucesso!")
                    st.experimental_rerun()
            
        elif sub_modo == "Orçamentos":
            orcamentos = carregar_orcamentos()
            if not orcamentos:
                st.info("Nenhum orçamento salvo.")
            else:
                dados["Orcamento"] = orcamentos
                st.success("Orçamento salvo com sucesso!")
                st.write("Orçamentos carregados:", orcamentos)

                indices = [f"{i+1} - {o['nome_cliente']} ({o['data']})" for i, o in enumerate(orcamentos)]
                index = st.selectbox("Selecione um orçamento:", range(len(orcamentos)), format_func=lambda i: indices[i])
                orcamento = orcamentos[index]

                st.subheader("Editar Orçamento")
                nome_cliente = st.text_input("Nome do Cliente", value=orc["nome_cliente"])
                contato = st.text_input("Contato", value=orc["contato"])
                bairro = st.text_input("Bairro", value=orc["bairro"])
                salvar_orcamentos(orcamentos)
                st.success("Orçamento atualizado com sucesso!")

                if st.button("Excluir Orçamento"):
                    orcamentos.pop(index)
                    salvar_orcamentos(orcamentos)
                    st.success("Orçamento excluído com sucesso!")
                    st.experimental_rerun()
        #Fim das alterações               
if __name__ == "__main__":
 main()
