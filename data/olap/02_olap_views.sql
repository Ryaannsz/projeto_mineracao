-- Views gerenciais sobre o esquema estrela Gold (fato_vendas + dimensões).

-- 1. Quantidade e valor comprado por produto e/ou categoria
CREATE OR REPLACE VIEW vw_vendas_por_produto_categoria AS
SELECT
    dp.id_produto,
    dp.nome        AS produto,
    dp.categoria,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total
FROM fato_vendas fv
JOIN dim_produto dp ON dp.id_produto = fv.id_produto
GROUP BY dp.id_produto, dp.nome, dp.categoria;

-- 2. Quantidade e valor comprado por cidade
CREATE OR REPLACE VIEW vw_vendas_por_cidade AS
SELECT
    dc.id_cidade,
    dc.cidade,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total
FROM fato_vendas fv
JOIN dim_cidade dc ON dc.id_cidade = fv.id_cidade
GROUP BY dc.id_cidade, dc.cidade;

-- 3. Quantidade e valor comprado por quadrimestre e/ou ano
CREATE OR REPLACE VIEW vw_vendas_por_ano_quadrimestre AS
SELECT
    dt.ano,
    dt.quadrimestre,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total
FROM fato_vendas fv
JOIN dim_tempo dt ON dt.id_tempo = fv.id_tempo
GROUP BY dt.ano, dt.quadrimestre;

CREATE OR REPLACE VIEW vw_vendas_por_ano AS
SELECT
    dt.ano,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total
FROM fato_vendas fv
JOIN dim_tempo dt ON dt.id_tempo = fv.id_tempo
GROUP BY dt.ano;

-- 4. Quantidade e valor comprado por estado civil
CREATE OR REPLACE VIEW vw_vendas_por_estado_civil AS
SELECT
    dec_.id_estado_civil,
    dec_.descricao AS estado_civil,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total
FROM fato_vendas fv
JOIN dim_estado_civil dec_ ON dec_.id_estado_civil = fv.id_estado_civil
GROUP BY dec_.id_estado_civil, dec_.descricao;

-- 5. Ranking dos produtos mais vendidos (por quantidade) em um determinado ano
CREATE OR REPLACE VIEW vw_ranking_produtos_por_ano AS
SELECT
    dt.ano,
    dp.id_produto,
    dp.nome     AS produto,
    dp.categoria,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total,
    RANK() OVER (
        PARTITION BY dt.ano
        ORDER BY SUM(fv.quantidade_vendida) DESC
    ) AS ranking_quantidade
FROM fato_vendas fv
JOIN dim_tempo dt   ON dt.id_tempo = fv.id_tempo
JOIN dim_produto dp ON dp.id_produto = fv.id_produto
GROUP BY dt.ano, dp.id_produto, dp.nome, dp.categoria;

-- 6. Ranking dos produtos com maior valor de venda por cidade, em um determinado ano
CREATE OR REPLACE VIEW vw_ranking_produtos_por_cidade_ano AS
SELECT
    dt.ano,
    dc.id_cidade,
    dc.cidade,
    dp.id_produto,
    dp.nome     AS produto,
    dp.categoria,
    SUM(fv.quantidade_vendida) AS quantidade_total,
    SUM(fv.valor_vendido)      AS valor_total,
    RANK() OVER (
        PARTITION BY dt.ano, dc.id_cidade
        ORDER BY SUM(fv.valor_vendido) DESC
    ) AS ranking_valor
FROM fato_vendas fv
JOIN dim_tempo dt   ON dt.id_tempo = fv.id_tempo
JOIN dim_cidade dc  ON dc.id_cidade = fv.id_cidade
JOIN dim_produto dp ON dp.id_produto = fv.id_produto
GROUP BY dt.ano, dc.id_cidade, dc.cidade, dp.id_produto, dp.nome, dp.categoria;

-- 7. Percentual de venda de cada produto em um determinado quadrimestre e ano
CREATE OR REPLACE VIEW vw_percentual_vendas_produto_periodo AS
SELECT
    dt.ano,
    dt.quadrimestre,
    dp.id_produto,
    dp.nome     AS produto,
    dp.categoria,
    SUM(fv.quantidade_vendida) AS quantidade_produto,
    SUM(fv.valor_vendido)      AS valor_produto,
    ROUND(
        100.0 * SUM(fv.quantidade_vendida)
        / NULLIF(SUM(SUM(fv.quantidade_vendida)) OVER (PARTITION BY dt.ano, dt.quadrimestre), 0),
        2
    ) AS percentual_quantidade,
    ROUND(
        100.0 * SUM(fv.valor_vendido)
        / NULLIF(SUM(SUM(fv.valor_vendido)) OVER (PARTITION BY dt.ano, dt.quadrimestre), 0),
        2
    ) AS percentual_valor
FROM fato_vendas fv
JOIN dim_tempo dt   ON dt.id_tempo = fv.id_tempo
JOIN dim_produto dp ON dp.id_produto = fv.id_produto
GROUP BY dt.ano, dt.quadrimestre, dp.id_produto, dp.nome, dp.categoria;

-- 8. Diferença na quantidade de vendas de cada produto entre dois anos consecutivos
CREATE OR REPLACE VIEW vw_diferenca_vendas_produto_ano AS
WITH vendas_produto_ano AS (
    SELECT
        dt.ano,
        dp.id_produto,
        dp.nome     AS produto,
        dp.categoria,
        SUM(fv.quantidade_vendida) AS quantidade_total,
        SUM(fv.valor_vendido)      AS valor_total
    FROM fato_vendas fv
    JOIN dim_tempo dt   ON dt.id_tempo = fv.id_tempo
    JOIN dim_produto dp ON dp.id_produto = fv.id_produto
    GROUP BY dt.ano, dp.id_produto, dp.nome, dp.categoria
)
SELECT
    ano,
    id_produto,
    produto,
    categoria,
    quantidade_total,
    valor_total,
    LAG(quantidade_total) OVER (PARTITION BY id_produto ORDER BY ano) AS quantidade_total_ano_anterior,
    quantidade_total
        - LAG(quantidade_total) OVER (PARTITION BY id_produto ORDER BY ano) AS diferenca_quantidade,
    LAG(valor_total) OVER (PARTITION BY id_produto ORDER BY ano) AS valor_total_ano_anterior,
    valor_total
        - LAG(valor_total) OVER (PARTITION BY id_produto ORDER BY ano) AS diferenca_valor
FROM vendas_produto_ano;

-- 9. Diferença entre nossas vendas e as da concorrente, por quadrimestre e ano.
--
-- fato_vendas_concorrente só traz valor mensal agregado (sem quantidade,
-- produto, cidade ou perfil de cliente), por isso a quantidade da
-- concorrente e sua diferença não existem nesta view — só o comparativo
-- de valor, que é o que a fonte permite calcular sem fabricar dado.
CREATE OR REPLACE VIEW vw_diferenca_vendas_concorrente AS
SELECT
    dt.ano,
    dt.quadrimestre,
    COALESCE(nossa.quantidade_total, 0) AS quantidade_vendida_nossa,
    COALESCE(nossa.valor_total, 0)      AS valor_vendido_nossa,
    fvc.valor_vendido                   AS valor_vendido_concorrente,
    COALESCE(nossa.valor_total, 0) - fvc.valor_vendido AS diferenca_valor
FROM fato_vendas_concorrente fvc
JOIN dim_tempo dt ON dt.id_tempo = fvc.id_tempo
LEFT JOIN (
    SELECT
        fv.id_tempo,
        SUM(fv.quantidade_vendida) AS quantidade_total,
        SUM(fv.valor_vendido)      AS valor_total
    FROM fato_vendas fv
    GROUP BY fv.id_tempo
) nossa ON nossa.id_tempo = fvc.id_tempo;

CREATE OR REPLACE VIEW vw_diferenca_vendas_concorrente_ano AS
SELECT
    ano,
    SUM(quantidade_vendida_nossa) AS quantidade_vendida_nossa,
    SUM(valor_vendido_nossa)      AS valor_vendido_nossa,
    SUM(valor_vendido_concorrente) AS valor_vendido_concorrente,
    SUM(diferenca_valor)          AS diferenca_valor
FROM vw_diferenca_vendas_concorrente
GROUP BY ano;
