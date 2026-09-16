# Power BI Calendar Table

Crie uma tabela calculada no Power BI em **Modelagem -> Nova tabela**:

```DAX
Calendar =
ADDCOLUMNS(
    CALENDAR(
        MIN(sales[sale_date]),
        MAX(sales[sale_date])
    ),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month", FORMAT([Date], "mmm"),
    "Year Month", FORMAT([Date], "yyyy-MM"),
    "Quarter", "Q" & FORMAT([Date], "Q")
)
```

Depois, na visão **Modelo**, crie o relacionamento:

```text
Calendar[Date] 1 -> * sales[sale_date]
```

Selecione a tabela `Calendar`, abra **Ferramentas de tabela** e marque **Marcar como tabela de datas**, usando a coluna `Date`.

Ordene `Calendar[Month]` por `Calendar[Month Number]` para que os meses apareçam na ordem correta.

## Measures com calendário

Depois de criar a tabela, use estas versões:

```DAX
Sales Previous Month =
CALCULATE(
    [Total Sales],
    DATEADD(Calendar[Date], -1, MONTH)
)
```

```DAX
Sales Growth =
DIVIDE(
    [Total Sales] - [Sales Previous Month],
    [Sales Previous Month]
)
```

Use `Calendar[Date]` no eixo dos gráficos, e não `sales[sale_date]`, para que os filtros de período sejam consistentes entre as páginas.
