CREATE TABLE dim_tempo (
    id_tempo SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ano SMALLINT NOT NULL,
    quadrimestre SMALLINT NOT NULL CHECK (quadrimestre BETWEEN 1 AND 3),
    CONSTRAINT uq_dim_tempo_periodo UNIQUE (ano, quadrimestre)
);

CREATE TABLE dim_produto (
    id_produto BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    CONSTRAINT uq_dim_produto UNIQUE (nome, categoria)
);

CREATE TABLE dim_cidade (
    id_cidade SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_estado_civil (
    id_estado_civil SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE fato_vendas (
    id_fato BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_tempo SMALLINT NOT NULL REFERENCES dim_tempo(id_tempo),
    id_produto BIGINT NOT NULL REFERENCES dim_produto(id_produto),
    id_cidade SMALLINT NOT NULL REFERENCES dim_cidade(id_cidade),
    id_estado_civil SMALLINT NOT NULL REFERENCES dim_estado_civil(id_estado_civil),
    quantidade_vendida INTEGER NOT NULL CHECK (quantidade_vendida > 0),
    valor_vendido NUMERIC(14,2) NOT NULL CHECK (valor_vendido >= 0),
    CONSTRAINT uq_fato_vendas_grao UNIQUE (
        id_tempo, id_produto, id_cidade, id_estado_civil
    )
);
