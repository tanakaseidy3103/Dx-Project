# Power BI Quick Start

Este guia serve para o primeiro teste visual do AI Operations Copilot. Nesta etapa, você não precisa entender Python, PostgreSQL ou Machine Learning. Vamos apenas carregar os dados Synthetic Data no Power BI Desktop.

## 1. Arquivos para importar

Use os arquivos da subpasta `powerbi`, preparados para a configuração regional em português:

```text
data/generated/powerbi/stores.csv
data/generated/powerbi/products.csv
data/generated/powerbi/customers.csv
data/generated/powerbi/sales.csv
data/generated/powerbi/inventory.csv
```

Esses dados são fictícios. Eles representam lojas, produtos, clientes, vendas e estoque.

## 2. Importar os CSVs

No Power BI Desktop:

1. Selecione **Obter dados**.
2. Escolha **Texto/CSV**.
3. Selecione cada arquivo acima e clique em **Carregar**.
4. Repita até carregar as cinco tabelas.

Use o caminho completo da pasta atual:

```text
C:\Users\eduardo\OneDrive - nkz.ac.jp\デスクトップ\DX Project\data\generated\powerbi
```

Esses arquivos usam `;` como separador e `,` como separador decimal. Assim, o Power BI em português deve reconhecer `3461,36` como número decimal e `0,05` como desconto sem conversão manual.

## 3. Criar relacionamentos

Abra a visão **Modelo** e crie estes relacionamentos, sempre do lado com uma linha para o lado com várias linhas:

| Tabela de origem | Coluna | Tabela de destino | Coluna |
| --- | --- | --- | --- |
| stores | `store_id` | sales | `store_id` |
| products | `product_id` | sales | `product_id` |
| customers | `customer_id` | sales | `customer_id` |
| stores | `store_id` | inventory | `store_id` |
| products | `product_id` | inventory | `product_id` |

Use cardinalidade **Um para muitos (1:*)** e direção de filtro **Única**.

## 4. Criar os primeiros Measures

Na tabela `sales`, selecione **Nova medida** e crie:

```DAX
Total Sales =
SUMX(
    sales,
    sales[quantity] * sales[unit_price] * (1 - sales[discount])
)
```

```DAX
Total Quantity = SUM(sales[quantity])
```

```DAX
Customers = DISTINCTCOUNT(sales[customer_id])
```

Na tabela `inventory`, crie:

```DAX
Inventory Units = SUM(inventory[stock_on_hand])
```

```DAX
Stockout Risk Items =
COUNTROWS(
    FILTER(
        inventory,
        inventory[stock_on_hand] <= inventory[reorder_point]
    )
)
```

## 5. Criar a primeira página

Nomeie a página como **Executive Overview** e adicione:

- Quatro cartões: `Total Sales`, `Total Quantity`, `Customers`, `Inventory Units`
- Um gráfico de linha com `sales[sale_date]` no eixo e `Total Sales` nos valores
- Um gráfico de barras com `stores[store_name]` no eixo e `Total Sales` nos valores
- Um cartão ou tabela com `Stockout Risk Items`
- Um segmentador com `stores[region]`

O objetivo desta página é responder: **quanto vendemos, quantos clientes compraram, qual loja vende mais e quantos itens estão em risco de reposição?**

## 6. O que está acontecendo no projeto

O fluxo completo planejado é:

```text
Synthetic CSV
    -> Python ETL
    -> PostgreSQL
    -> Power BI
    -> Machine Learning
    -> AI Operations Copilot
```

Para este primeiro teste, estamos começando pelo Power BI com os CSVs já gerados. Depois vamos conectar o Power BI ao PostgreSQL e adicionar as páginas de Store Analysis, Product Analysis, Forecast & Risk e AI Insights.

## 7. Observações

- Os números são Synthetic Data e não representam uma empresa real.
- Ainda não há um arquivo `.pbix` pronto; a primeira montagem será feita no Power BI Desktop.
- Não publique métricas de precisão do Machine Learning antes de executar a avaliação.
- O AI Copilot deve explicar os dados, mas não deve afirmar uma causa que os dados não comprovam.