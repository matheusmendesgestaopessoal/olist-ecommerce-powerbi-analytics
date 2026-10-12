let
    DataInicial = List.Min(stg_orders[order_purchase_date]),
    DataFinal = List.Max(stg_orders[order_purchase_date]),

    ListaDatas = List.Dates(
        DataInicial,
        Duration.Days(DataFinal - DataInicial) + 1,
        #duration(1, 0, 0, 0)
    ),

    TabelaDatas = Table.FromList(
        ListaDatas,
        Splitter.SplitByNothing(),
        {"date"}
    ),

    TipoData = Table.TransformColumnTypes(
        TabelaDatas,
        {{"date", type date}}
    ),

    Ano = Table.AddColumn(
        TipoData,
        "year",
        each Date.Year([date]),
        Int64.Type
    ),

    MesNumero = Table.AddColumn(
        Ano,
        "month_number",
        each Date.Month([date]),
        Int64.Type
    ),

    MesNome = Table.AddColumn(
        MesNumero,
        "month_name",
        each Date.MonthName([date], "pt-BR"),
        type text
    ),

    Trimestre = Table.AddColumn(
        MesNome,
        "quarter",
        each "T" & Text.From(Date.QuarterOfYear([date])),
        type text
    ),

    AnoMes = Table.AddColumn(
        Trimestre,
        "year_month",
        each Date.ToText([date], "yyyy-MM"),
        type text
    )
in
    AnoMes
