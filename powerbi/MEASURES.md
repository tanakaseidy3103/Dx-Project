# Power BI Measures

Crie estas medidas na tabela `sales` ou `inventory` conforme indicado. Elas são a primeira camada de KPI do relatório e devem ser usadas nos cartões, gráficos e filtros.

## Sales Measures

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

```DAX
Gross Profit =
SUMX(
    sales,
    sales[quantity]
        * (
            sales[unit_price] * (1 - sales[discount])
            - RELATED(products[unit_cost])
        )
)
```

```DAX
Gross Margin = DIVIDE([Gross Profit], [Total Sales])
```

```DAX
Sales Previous Period =
CALCULATE(
    [Total Sales],
    DATEADD(sales[sale_date], -1, MONTH)
)
```

```DAX
Sales Growth =
DIVIDE(
    [Total Sales] - [Sales Previous Period],
    [Sales Previous Period]
)
```

## Inventory Measures

Crie estas medidas na tabela `inventory`:

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

```DAX
Stockout Risk Rate =
DIVIDE(
    [Stockout Risk Items],
    COUNTROWS(inventory)
)
```

## Formatting

| Measure | Format |
| --- | --- |
| `Total Sales` | Currency ou número decimal com duas casas |
| `Gross Profit` | Currency ou número decimal com duas casas |
| `Gross Margin` | Percentage |
| `Sales Growth` | Percentage |
| `Stockout Risk Rate` | Percentage |
| `Customers` | Whole number |
| `Total Quantity` | Whole number |
| `Inventory Units` | Whole number |
| `Stockout Risk Items` | Whole number |

## Nota sobre datas

Para crescimento mensal, crie a tabela calendário conforme [CALENDAR.md](CALENDAR.md) e use a medida `Sales Previous Month` baseada em `Calendar[Date]`.
