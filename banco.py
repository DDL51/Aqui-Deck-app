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
            imposto% REAL,
            repasse REAL,
            usinagem REAL,
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

    # Tabela cadastro de clientes 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            contato TEXT,
            bairro TEXT,
            rua TEXT,
        )
    """)

    # Tabela ORÇAMENTO 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            contato TEXT,
            bairro TEXT,
            rua TEXT,
            quantidade TEXT,
            comprimento TEXT,
            Valor unitário TEXT 
            
            vamor total pagar TEXT 
        )
    """)

    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso.")

if __name__ == "__main__":
    criar_banco()
