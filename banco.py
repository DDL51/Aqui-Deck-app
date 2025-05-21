import sqlite3

def criar_banco():
    conn = sqlite3.connect("aqui_deck.db")
    cursor = conn.cursor()

    # Tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            custo REAL,
            imposto REAL,
            repasse REAL,
            usinagem REAL,
            valor_final REAL
        )
    """)

    # Tabela de fixos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL
        )
    """)

    # Tabela de vendas (orçamentos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            contato TEXT,
            bairro TEXT,
            produto TEXT,
            qtd REAL,
            comp REAL,
            valor_unit REAL,
            total REAL
        )
    """)

    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso.")

if __name__ == "__main__":
    criar_banco()
