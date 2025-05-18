import streamlit as st
import json

st.title("Conversor JSON para secrets.toml (Google Service Account)")

st.markdown("Cole aqui o conteúdo do seu arquivo **service_account.json**:")

input_json = st.text_area("JSON da conta de serviço", height=300)

def escape_newlines(s):
    return s.replace("\n", "\\n") if isinstance(s, str) else s

if st.button("Converter para TOML"):
    try:
        data = json.loads(input_json)
        toml_lines = ["[gcp_service_account]"]
        for key, value in data.items():
            value = escape_newlines(value)
            if isinstance(value, str):
                value = value.replace('"', '\\"')  # Escapa aspas
                toml_lines.append(f'{key} = "{value}"')
            else:
                toml_lines.append(f'{key} = {value}')
        toml_result = "\n".join(toml_lines)

        st.success("Conversão concluída!")
        st.code(toml_result, language="toml")

    except Exception as e:
        st.error(f"Erro ao processar JSON: {e}")
