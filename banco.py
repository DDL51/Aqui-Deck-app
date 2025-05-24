import sqlite3

def criar_banco():
    conn = sqlite3.connect("aqui_deck.db")
    cursor = conn.cursor()

    # Ativar suporte a chaves estrangeiras (SQLite precisa disso)
    cursor.execute("PRAGMA foreign_keys = ON")

    # Tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            custo REAL,
            imposto REAL,
            repasse REAL,
            usinagem REAL
        )
    """)

    # Tabela de custos fixos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor REAL
        )
    """)

    # Tabela de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            contato TEXT,
            bairro TEXT,
            rua TEXT
        )
    """)

    # Tabela de orçamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            quantidade REAL,
            comprimento REAL,
            valor_unitario REAL,
            valor_total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # Tabela itens do orçamento (um orçamento pode ter vários produtos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_orcamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER,
            produto_id INTEGER,
            quantidade REAL,
            comprimento REAL,
            FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Banco de dados com FKs criado com sucesso.")

if __name__ == "__main__":
    criar_banco()
