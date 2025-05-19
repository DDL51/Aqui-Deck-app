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
import os

# -------- AUTENTICAÇÃO GOOGLE --------
def conectar_planilha(nome_aba="Fixos"):
    try:
        # Escopos necessários
        scope = ["https://www.googleapis.com/auth/spreadsheets", 
                 "https://www.googleapis.com/auth/drive"]

        # Carrega as credenciais
        credentials_dict = st.secrets["gcp_service_account"]

        # Autentica com Google
        creds = service_account.Credentials.from_service_account_info(
            credentials_dict, scopes=scope)
        client = gspread.authorize(creds)

        # ID da planilha
        spreadsheet_id = "1Dx4X3a0GagiB0eyv_wqOPkmkSfUtW9i6B-sQATf75H0"

        # Abre a aba específica
        worksheet = client.open_by_key(spreadsheet_id).worksheet(nome_aba)

        return worksheet

    except Exception as e:
        st.error(f"Erro na autenticação com Google Sheets: {e}")
        return None

# APP PRINCIPAL --------
def main():
    st.title("AQUI-DECK")
    modo = st.sidebar.radio("Escolha o modo:", ["Cadastro", "Orçamentos", "Gerenciar"])
    if modo == "Cadastro":
        st.subheader("Cadastro de Produtos ou Fixos")
        tipo = st.selectbox("Tipo:", ["Fixo", "Produto"])

    if tipo == "Fixo":
        nome = st.text_input("Nome do Serviço Fixo")
        valor = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        if st.button("Salvar Serviço Fixo") and nome.strip():
            worksheet = conectar_planilha("Fixos")
    if worksheet:
        try:
            worksheet.append_row([nome, valor])
            st.success("Serviço salvo com sucesso!")
        except Exception as e:
            st.error(f"Erro ao salvar na planilha: {e}")
            #

    elif tipo == "Produto":
    nome = st.text_input("Nome do Produto")
    base = st.number_input("Valor Base (R$)", min_value=0.0, format="%.2f")
    imposto = st.number_input("Imposto (%)", min_value=0.0, format="%.2f")
    repasse = st.number_input("Repasse (R$)", min_value=0.0, format="%.2f")
    usinagem = st.number_input("Usinagem (R$)", min_value=0.0, format="%.2f")

    if st.button("Salvar Produto"):
        if nome.strip():  # Verifica se o nome não está vazio
            valor_final = base + (base * imposto / 100) + repasse + usinagem

            # Conecta à aba "Produtos"
            aba_produtos = conectar_planilha("Produtos")
            if aba_produtos:
                try:
                    aba_produtos.append_row([
                        nome, base, imposto, repasse, usinagem, round(valor_final, 2)
                    ])
                    st.write("URL da planilha conectada:", st.secrets["GOOGLE_CREDENTIALS"]["sheet_url"])
                    st.success("Produto salvo com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar produto: {e}")
            else:
                st.error("Erro ao conectar à aba Produtos.")
        else:
            st.warning("O nome do produto não pode estar vazio.")
    
    
            # LISTA PRODUTOS......
def carregar_produtos():
    aba_produtos = conectar_planilha("Produtos")
    if not aba_produtos:
        return []
    linhas = aba_produtos.get_all_values()[1:]  # Ignora cabeçalho
    produtos = []
    for linha in linhas:
        try:
            produtos.append({
                "nome": linha[0],
                "valor_final": float(linha[5])  # A coluna 6 (índice 5) é o valor final
            })
        except:
            continue
    return produtos
    
    # ORÇAMENTOS....
    elif modo == "Orçamentos":
    st.subheader("Orçamento para Cliente")
    nome_cliente = st.text_input("Nome do Cliente")
    contato = st.text_input("Contato")
    bairro = st.text_input("Bairro")

    if "itens" not in st.session_state:
        st.session_state.itens = []

    produtos_disponiveis = carregar_produtos()
    nomes_produtos = [p["nome"] for p in produtos_disponiveis]
    produto_sel = st.selectbox("Produto:", nomes_produtos)
    qtd = st.number_input("Quantidade", min_value=0.0)
    comp = st.number_input("Comprimento (em mm)", min_value=0.0)

    if st.button("Adicionar Produto"):
        valor_unit = next((p["valor_final"] for p in produtos_disponiveis if p["nome"] == produto_sel), 0)
        total = (qtd * comp / 1000) * valor_unit
        st.session_state.itens.append({
            "produto": produto_sel,
            "qtd": qtd,
            "comp": comp,
            "valor_unit": valor_unit,
            "total": total
        })
        st.success(f"{produto_sel} adicionado ao pedido!")

    if st.session_state.itens:
        st.subheader("Itens do Pedido")
        total_geral = sum(i["total"] for i in st.session_state.itens)
        for i, item in enumerate(st.session_state.itens):
            st.write(f"{i+1}. {item['produto']} - Qtd: {item['qtd']} - Comp: {item['comp']} mm - Total: R$ {item['total']:.2f}")
        st.write(f"**Total Geral: R$ {total_geral:.2f}**")

        if st.button("Salvar Orçamento"):
            aba_orcamentos = conectar_planilha("Orçamentos")
            if aba_orcamentos:
                try:
                    for item in st.session_state.itens:
                        aba_orcamentos.append_row([
                            nome_cliente,
                            contato,
                            bairro,
                            item["produto"],
                            item["qtd"],
                            item["comp"],
                            item["valor_unit"],
                            round(item["total"], 2)
                        ])
                    st.success("Orçamento salvo com sucesso!")
                    st.session_state.itens.clear()
                except Exception as e:
                    st.error(f"Erro ao salvar orçamento: {e}")
            else:
                st.error("Erro ao conectar à aba Orçamentos.")    
                

    
    
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
