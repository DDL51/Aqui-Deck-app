import streamlit as st

# Classe Produto
class Produto:
    def __init__(self, nome, custo, imposto, repasse, usinagem):
        self.nome = nome
        self.custo = custo
        self.imposto = imposto
        self.repasse = repasse
        self.usinagem = usinagem

    def exibir(self):
        return f"{self.nome} - Custo: {self.custo}, Imposto: {self.imposto}, Repasse: {self.repasse}, Usinagem: {self.usinagem}"

# Lista de produtos em memória
produtos = []

# Interface para cadastrar produto
st.title("Cadastro de Produtos")

nome = st.text_input("Nome do produto")
custo = st.number_input("Custo", value=0.0)
imposto = st.number_input("Imposto (%)", value=0.0)
repasse = st.number_input("Repasse", value=0.0)
usinagem = st.number_input("Usinagem", value=0.0)

if st.button("Cadastrar"):
    novo = Produto(nome, custo, imposto, repasse, usinagem)
    produtos.append(novo)
    st.success(f"Produto '{nome}' cadastrado com sucesso!")

# Exibir todos os produtos cadastrados
st.subheader("Produtos cadastrados")
for p in produtos:
    st.write(p.exibir())
