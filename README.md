# Mineracao de Dados - Pet Shop Nosso Aumigo

O ambiente inicia tres bases locais e carrega os arquivos SQL e JSON da pasta `data/`:

| Base | Origem | Banco/schema |
| --- | --- | --- |
| Oracle | `data/oracle/` | `petshop` em `FREEPDB1` |
| PostgreSQL | `data/postgres/` | `petshop_itabuna` |
| MongoDB | `data/mongodb/` | `petshop_feira` |

O arquivo `data/planilhas/08_vendas_concorrente.xlsx` permanece somente como planilha e nao e carregado em nenhum banco.

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
python main.py verificar-conexoes
```

## Arquitetura ETL

O projeto usa a propria raiz `mineracao_dados/` como raiz Python, sem uma pasta `src/` intermediaria:

| Pasta | Responsabilidade |
| --- | --- |
| `config/` | Le configuracoes de ambiente e credenciais. |
| `data/` | Separa dados de Oracle, PostgreSQL, MongoDB e planilhas. |
| `infrastructure/` | Abre e fecha conexoes com Oracle, PostgreSQL e MongoDB. |
| `models/` | Define contratos tipados das fontes e do modelo dimensional. |
| `repositories/` | Extrai cada fonte e concentra consultas especificas do banco. |
| `services/` | Orquestra extracao, transformacao, validacao de referencias e carga. |
| `tests/` | Testes unitarios das regras de transformacao. |

O modelo canonico preserva a origem de cada registro em chaves como `salvador:1`, `itabuna:1` e `feira_de_santana:1`. Assim, IDs iguais em bancos diferentes nao colidem no OLAP.

O lote dimensional esta definido em `models/olap.py`:

| Estrutura | Grao |
| --- | --- |
| `DimensaoCliente` | Um cliente por fonte. |
| `DimensaoData` | Uma data com chave no formato `AAAAMMDD`. |
| `DimensaoProduto` | Um produto por fonte. |
| `DimensaoServico` | Um servico por fonte. |
| `FatoItemVenda` | Um item de venda/pedido. |
| `FatoAtendimentoServico` | Um atendimento de servico. |

Para extrair e transformar tudo, sem gravar em um destino ainda:

```bash
python main.py preparar-lote
```

Esse comando retorna as quantidades de dimensoes e fatos preparadas para carga.

## Destino OLAP

O destino ainda nao foi escolhido, portanto o ETL nao esta acoplado a um banco especifico. O contrato `RepositorioOlap`, em `repositories/contracts.py`, recebe um `LoteOlap` pronto para persistir.

Quando o banco OLAP for definido, implemente um repositorio e injete-o no pipeline:

```python
from bootstrap import criar_pipeline
from models import LoteOlap


class MeuRepositorioOlap:
    def carregar(self, lote: LoteOlap) -> None:
        # Inserir dimensoes antes das tabelas fato.
        pass


pipeline = criar_pipeline()
pipeline.executar(MeuRepositorioOlap())
```

As conexoes Python usam `localhost` por padrao. Caso o codigo Python execute dentro de outro container da mesma composicao, defina `ORACLE_HOST=oracle`, `POSTGRES_HOST=postgres` e `MONGODB_HOST=mongodb`.
