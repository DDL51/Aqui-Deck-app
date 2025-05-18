import json

def escape_newlines(s):
    return s.replace("\n", "\\n") if isinstance(s, str) else s

def convert_json_to_toml(json_path, toml_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    with open(toml_path, "w") as f:
        f.write("[gcp_service_account]\n")
        for key, value in data.items():
            value = escape_newlines(value)
            if isinstance(value, str):
                value = value.replace('"', '\\"')  # Escapa aspas
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f'{key} = {value}\n')

    print(f"Arquivo TOML gerado em: {toml_path}")

# Uso:
convert_json_to_toml("service_account.json", ".streamlit/secrets.toml")
