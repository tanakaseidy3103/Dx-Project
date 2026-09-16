# Data Dictionary

Este documento explica os cinco CSVs usados no primeiro teste do Power BI.

## stores.csv

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `store_id` | Texto | Identificador único da loja |
| `store_name` | Texto | Nome de exibição da loja |
| `region` | Texto | Região da loja |
| `store_type` | Texto | Tipo da loja |
| `opened_date` | Data | Data de abertura |

## products.csv

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `product_id` | Texto | Identificador único do produto |
| `product_name` | Texto | Nome de exibição do produto |
| `category` | Texto | Categoria do produto |
| `unit_cost` | Número decimal | Custo unitário |
| `unit_price` | Número decimal | Preço unitário |

## customers.csv

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `customer_id` | Texto | Identificador único do cliente fictício |
| `segment` | Texto | Segmento do cliente |
| `region` | Texto | Região do cliente |
| `signup_date` | Data | Data de cadastro |

## sales.csv

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `sale_id` | Número inteiro | Identificador único da venda |
| `sale_date` | Data | Data da venda |
| `store_id` | Texto | Loja onde ocorreu a venda |
| `product_id` | Texto | Produto vendido |
| `customer_id` | Texto | Cliente associado à venda |
| `quantity` | Número inteiro | Quantidade vendida |
| `unit_price` | Número decimal | Preço aplicado na venda |
| `discount` | Número decimal | Desconto entre 0 e 1 |

Medidas derivadas importantes:

```text
Sales Amount = quantity * unit_price * (1 - discount)
Gross Profit = quantity * (unit_price * (1 - discount) - unit_cost)
```

## inventory.csv

| Coluna | Tipo | Descrição |
| --- | --- | --- |
| `inventory_date` | Data | Data do estoque |
| `store_id` | Texto | Loja do estoque |
| `product_id` | Texto | Produto em estoque |
| `stock_on_hand` | Número inteiro | Quantidade disponível |
| `reorder_point` | Número inteiro | Limite para reposição |
| `stock_in` | Número inteiro | Quantidade recebida |
| `stock_out` | Número inteiro | Quantidade que saiu |

Regra inicial de risco de falta:

```text
Stockout Risk = stock_on_hand <= reorder_point
```

## Relacionamentos no Power BI

As tabelas `stores`, `products` e `customers` funcionam como dimensões. `sales` e `inventory` são tabelas de fatos.

```text
stores[store_id]       1 -> * sales[store_id]
products[product_id]   1 -> * sales[product_id]
customers[customer_id] 1 -> * sales[customer_id]
stores[store_id]       1 -> * inventory[store_id]
products[product_id]   1 -> * inventory[product_id]
```

No Power BI, configure os campos de data como tipo **Date** e os campos monetários como **Decimal number**. `discount` deve permanecer como número decimal; para exibição percentual, formate o campo ou a medida como Percentage.
