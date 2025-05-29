indentaca.py

import sqlite3
from datetime import datetime
from calculadora import calcular_valor_unitario, calcular_valor_total
from listar_produtos import listar_produtos, buscar_produto_por_id
from cadastro_cliente import buscar_cliente, cadastrar_cliente

# Dentro da main:
#cliente_id = buscar_cliente(cursor)


def conectar_bd():
    return sqlite3.connect("multi_deck.db")


#def buscar_cliente_por_cpf(cursor, cpf):
   # cursor.execute("SELECT id, nome FROM clientes WHERE cpf = ?", (cpf,))
    #return cursor.fetchone()


def main():
    conn = conectar_bd()
    cursor = conn.cursor()
    print("\n=== Criar Orçamento para Cliente Já Cadastrado ===")

    # Busca inteligente: CPF ou nome
    cliente_id = buscar_cliente(cursor)
    print(f"✅ Cliente localizado com ID: {cliente_id}")
    
    for p in produtos:
    print(f"{p[0]} - {p[1]}")

    produto_id = int(input("Escolha o ID do produto: "))
    produto = buscar_produto_por_id(cursor, produto_id)
        if not produto:
            print("Produto não encontrado.")
            continue

        nome_produto, custo, imposto, repasse, usinagem = produto
        quantidade = int(input("Quantidade de peças: "))
        comprimento = float(input("Comprimento de cada peça (em mm): "))

        valor_unitario = calcular_valor_unitario(custo, imposto, repasse, usinagem)
        valor_total = calcular_valor_total(valor_unitario, quantidade, comprimento)

        cursor.execute("""
            INSERT INTO itens_orcamento (orcamento_id, produto_id, quantidade, comprimento)
            VALUES (?, ?, ?, ?)
        """, (orcamento_id, produto_id, quantidade, comprimento))

        print(f"🧮 Valor do item: R$ {valor_total:.2f}")

        cont = input("Adicionar outro item? (s/n): ").lower()
        if cont != 's':
            break

    conn.commit()
    conn.close()
    print(f"\n✅ Orçamento salvo com ID {orcamento_id}!")

if __name__ == "__main__":
    main()
