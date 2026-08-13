FROM python:3.13-slim

WORKDIR /app

COPY docker/mongodb-loader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/mongodb-loader/carregar_dados.py .
COPY ["data/mongodb/05_feira_clientes.json", "/dados/05_feira_clientes.json"]
COPY ["data/mongodb/06_feira_produtos.json", "/dados/06_feira_produtos.json"]
COPY ["data/mongodb/07_feira_pedidos.json", "/dados/07_feira_pedidos.json"]

ENTRYPOINT ["python", "carregar_dados.py"]
