from .conexoes import carregar_configuracao, conectar_mongodb, conectar_oracle, conectar_postgres


def main() -> None:
    configuracao = carregar_configuracao()

    with conectar_oracle(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            print(f"Oracle: conectado, {cursor.fetchone()[0]} clientes em Salvador")

    with conectar_postgres(configuracao) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM clientes")
            print(f"PostgreSQL: conectado, {cursor.fetchone()[0]} clientes em Itabuna")

    cliente = conectar_mongodb(configuracao)
    try:
        banco = cliente[configuracao.mongodb_database]
        print(f"MongoDB: conectado, {banco.clientes.count_documents({})} clientes em Feira de Santana")
    finally:
        cliente.close()


if __name__ == "__main__":
    main()
