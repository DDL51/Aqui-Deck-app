import streamlit as st

st.set_page_config(page_title="ChatBot Simples", layout="centered")

# Título do App
st.title("ChatBot Simples")

# Histórico de mensagens na sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# Entrada do usuário
user_input = st.text_input("Você:", "")

# Respostas simples
def responder(mensagem):
    mensagem = mensagem.lower()
    if "oi" in mensagem or "olá" in mensagem:
        return "Olá! Como posso te ajudar?"
    elif "ajuda" in mensagem:
        return "Claro, estou aqui para ajudar. Pergunte algo!"
    elif "tchau" in mensagem:
        return "Até mais! Foi bom conversar com você."
    else:
        return "Desculpe, ainda estou aprendendo e não entendi isso."

# Processar a entrada do usuário
if user_input:
    resposta = responder(user_input)
    st.session_state.historico.append(("Você", user_input))
    st.session_state.historico.append(("Bot", resposta))

# Exibir o histórico
for autor, mensagem in st.session_state.historico:
    st.write(f"**{autor}:** {mensagem}")
