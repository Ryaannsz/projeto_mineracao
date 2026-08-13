# Mineracao de Dados - Pet Shop Nosso Aumigo

O ambiente inicia tres bases locais e carrega os arquivos SQL e JSON da pasta de fontes:

| Base | Origem | Banco/schema |
| --- | --- | --- |
| Oracle | `01_salvador_ddl.sql` e `02_salvador_dml.sql` | `petshop` em `FREEPDB1` |
| PostgreSQL | `03_Itabuna_ddl.sql` e `04_itabuna_dml.sql` | `petshop_itabuna` |
| MongoDB | `05_Feira_Clientes.json`, `06_Feira_Produtos.json` e `07_Feira_pedidos.json` | `petshop_feira` |

O arquivo `08_Vendas_Concorrente.xlsx` permanece somente como planilha na pasta de fontes e nao e carregado em nenhum banco.

## Subir as bases

Opcionalmente, crie um arquivo `.env` a partir de `.env.example` para trocar senhas e portas. Os mesmos valores de desenvolvimento ja possuem padroes no `docker-compose.yml`.

```bash
docker compose up -d --build
docker compose logs -f mongodb-loader
```

O primeiro inicio do Oracle pode levar alguns minutos porque a imagem precisa preparar os arquivos do banco. PostgreSQL e MongoDB ficam disponiveis logo apos seus healthchecks.

O `mongodb-loader` termina depois de importar os dados. Ele usa upserts, portanto pode ser executado novamente sem duplicar documentos.

As cargas de Oracle e PostgreSQL ocorrem somente na primeira criacao de seus volumes. Para recriar todas as bases e importar novamente:

```bash
docker compose down -v
docker compose up -d --build
```

## Usar no Python

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m src.verificar_conexoes
```

O modulo `src.conexoes` oferece as funcoes `conectar_oracle()`, `conectar_postgres()` e `conectar_mongodb()`.

```python
from src.conexoes import banco_mongodb, conectar_oracle, conectar_postgres

with conectar_oracle() as oracle:
    with oracle.cursor() as cursor:
        cursor.execute("SELECT * FROM clientes FETCH FIRST 5 ROWS ONLY")
        print(cursor.fetchall())

with conectar_postgres() as postgres:
    with postgres.cursor() as cursor:
        cursor.execute("SELECT * FROM clientes LIMIT 5")
        print(cursor.fetchall())

mongo = banco_mongodb()
print(list(mongo.pedidos.find().limit(5)))
mongo.client.close()
```

As conexoes Python usam `localhost` por padrao. Caso o codigo Python execute dentro de outro container da mesma composicao, defina `ORACLE_HOST=oracle`, `POSTGRES_HOST=postgres` e `MONGODB_HOST=mongodb`.
