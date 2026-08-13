FROM python:3.13-slim

WORKDIR /app

COPY docker/mongodb-loader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/mongodb-loader/carregar_dados.py .
COPY ["Fontes de dados - Pet Shop Nosso Aumigo/05_Feira_Clientes.json", "/dados/05_Feira_Clientes.json"]
COPY ["Fontes de dados - Pet Shop Nosso Aumigo/06_Feira_Produtos.json", "/dados/06_Feira_Produtos.json"]
COPY ["Fontes de dados - Pet Shop Nosso Aumigo/07_Feira_pedidos.json", "/dados/07_Feira_pedidos.json"]

ENTRYPOINT ["python", "carregar_dados.py"]
