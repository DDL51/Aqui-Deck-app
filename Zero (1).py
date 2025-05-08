import streamlit as st
import json
import os

# -------- CONFIGS --------
ARQ_PRODUTOS = "produtos.json"

# -------- DADOS LOCAIS --------
def carregar_dados():
    if not os.path.exists(ARQ_PRODUTOS):
        with open(ARQ_PRODUTOS, "w") as f:
            json.dump({"Fixos": [], "Produtos": [], "Alteração":[]}, f)
    with open(ARQ_PRODUTOS, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQ_PRODUTOS, "w") as f:
        json.dump(dados, f, indent=4)

# -------- APP PRINCIPAL --------
def main():
    st.title("AQUI-DECK App")

    dados = carregar_dados()
    modo = st.sidebar.radio("Escolha o modo:", ["Cadastro", "Orçamento", "Gerenciar Produtos"])

    if modo == "Cadastro":
        st.subheader("Cadastro de Produtos ou Fixos")
        tipo = st.selectbox("Tipo:", ["Fixo", "Produto",])
        if tipo =="Fixo":
            nome = st.text_input("nome do custo")
            valor = st.text_inout("valor")
        if tipo == "Produto":
            nome = st.text_input("Nome do Produto")
            base = st.number_input("Valor Base (R$)", min_value=0.0, format="%.2f")
            imposto = st.number_input("Imposto (%)", min_value=0.0, format="%.2f")
            repasse = st.number_input("Repasse (R$)", min_value=0.0, format="%.2f")
            usinagem = st.number_input("Usinagem (R$)", min_value=0.0, format="%.2f")

            if st.button("Salvar Produto") and nome.strip():
                valor_final = base + (base * imposto / 100) + repasse + usinagem
                dados["Produtos"].append({"nome": nome, "valor_base": base, "imposto": imposto, "repasse": repasse, "usinagem": usinagem, "valor_final": round(valor_final, 2)})
                salvar_dados(dados)
                st.success("Produto salvo com sucesso!")

    elif modo == "Gerenciar Produtos":
        st.subheader("Gerenciar Produtos Cadastrados")

        if not dados["Produtos"]:
            st.info("Nenhum produto cadastrado.")
        else:
            for i, produto in enumerate(dados["Produtos"]):
                with st.expander(f"{produto['nome']} - R$ {produto['valor_final']:.2f}"):
                    novo_nome = st.text_input(f"Nome do Produto ({produto['nome']})", value=produto["nome"], key=f"nome_{i}")
                    novo_base = st.number_input(f"Valor Base (R$)", value=produto["valor_base"], min_value=0.0, format="%.2f", key=f"base_{i}")
                    novo_imposto = st.number_input(f"Imposto (%)", value=produto["imposto"], min_value=0.0, format="%.2f", key=f"imposto_{i}")
                    novo_repasse = st.number_input(f"Repasse (R$)", value=produto["repasse"], min_value=0.0, format="%.2f", key=f"repasse_{i}")
                    novo_usinagem = st.number_input(f"Usinagem (R$)", value=produto["usinagem"], min_value=0.0, format="%.2f", key=f"usinagem_{i}")

                    if st.button(f"Atualizar Produto {i}"):
                        valor_final = novo_base + (novo_base * novo_imposto / 100) + novo_repasse + novo_usinagem
                        dados["Produtos"][i] = {
                            "nome": novo_nome, 
                            "valor_base": novo_base, 
                            "imposto": novo_imposto, 
                            "repasse": novo_repasse, 
                            "usinagem": novo_usinagem, 
                            "valor_final": round(valor_final, 2)
                        }
                        salvar_dados(dados)
                        st.success(f"Produto {novo_nome} atualizado com sucesso!")

                    if st.button(f"Excluir Produto {i}"):
                        dados["Produtos"].pop(i)
                        salvar_dados(dados)
                        st.warning("Produto excluído com sucesso!")
                        st.experimental_rerun()  # Atualiza a interface após exclusão

if __name__ == "__main__":
    main()
