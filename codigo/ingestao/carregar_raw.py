import csv
import os
import re
from pathlib import Path

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

RAW_SCHEMA = os.getenv("RAW_SCHEMA", "raw")

DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "dados/brutos")


# ============================================================
# NOMES PADRONIZADOS DAS TABELAS
# ============================================================

TABLE_NAME_MAP = {
    "olist_customers_dataset.csv": "customers",
    "olist_geolocation_dataset.csv": "geolocation",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_orders_dataset.csv": "orders",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "product_category_translation",
}


def normalize_table_name(file_path: Path) -> str:
    """
    Retorna o nome configurado acima.
    Para CSVs adicionais, cria um nome seguro automaticamente.
    """

    if file_path.name in TABLE_NAME_MAP:
        return TABLE_NAME_MAP[file_path.name]

    name = file_path.stem.lower()
    name = re.sub(r"^olist_", "", name)
    name = re.sub(r"_dataset$", "", name)
    name = re.sub(r"[^a-z0-9_]+", "_", name)

    return name.strip("_")


def read_csv_header(file_path: Path) -> list[str]:
    """
    Lê somente o cabeçalho do CSV.
    """

    with file_path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.reader(csv_file)

        headers = next(reader)

    headers = [column.strip() for column in headers]

    if not headers:
        raise ValueError(f"CSV sem cabeçalho: {file_path.name}")

    if any(not column for column in headers):
        raise ValueError(
            f"Existem colunas sem nome em {file_path.name}"
        )

    if len(headers) != len(set(headers)):
        raise ValueError(
            f"Existem nomes de colunas duplicados em {file_path.name}"
        )

    return headers


def create_raw_table(
    connection,
    table_name: str,
    columns: list[str],
):
    """
    Recria a tabela RAW usando TEXT em todas as colunas.

    Isso é proposital:
    RAW deve preservar os dados antes de decisões de tipagem
    ou transformação.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
            .format(
                sql.Identifier(RAW_SCHEMA)
            )
        )

        cursor.execute(
            sql.SQL(
                "DROP TABLE IF EXISTS {}.{} CASCADE"
            ).format(
                sql.Identifier(RAW_SCHEMA),
                sql.Identifier(table_name),
            )
        )

        column_definitions = sql.SQL(", ").join(
            sql.SQL("{} TEXT").format(
                sql.Identifier(column)
            )
            for column in columns
        )

        create_statement = sql.SQL(
            "CREATE TABLE {}.{} ({})"
        ).format(
            sql.Identifier(RAW_SCHEMA),
            sql.Identifier(table_name),
            column_definitions,
        )

        cursor.execute(create_statement)


def copy_csv_to_postgres(
    connection,
    file_path: Path,
    table_name: str,
    columns: list[str],
):
    """
    Usa COPY FROM STDIN.

    É significativamente mais rápido do que inserir
    registro por registro.
    """

    copy_statement = sql.SQL(
        """
        COPY {}.{} ({})
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE,
            DELIMITER ',',
            QUOTE '"',
            ESCAPE '"',
            ENCODING 'UTF8'
        )
        """
    ).format(
        sql.Identifier(RAW_SCHEMA),
        sql.Identifier(table_name),
        sql.SQL(", ").join(
            sql.Identifier(column)
            for column in columns
        ),
    )

    with connection.cursor() as cursor:

        with file_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as csv_file:

            cursor.copy_expert(
                copy_statement.as_string(connection),
                csv_file,
            )


def count_rows(connection, table_name: str) -> int:
    """
    Conta as linhas importadas para validação.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            sql.SQL(
                "SELECT COUNT(*) FROM {}.{}"
            ).format(
                sql.Identifier(RAW_SCHEMA),
                sql.Identifier(table_name),
            )
        )

        return cursor.fetchone()[0]


def main():

    print("=" * 70)
    print("OLIST - CARGA DA CAMADA RAW")
    print("=" * 70)

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Pasta não encontrada: {DATA_DIR}"
        )

    csv_files = sorted(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em: {DATA_DIR}"
        )

    print(f"\nArquivos encontrados: {len(csv_files)}\n")

    connection = psycopg2.connect(**DB_CONFIG)

    try:

        for file_path in csv_files:

            table_name = normalize_table_name(file_path)

            print("-" * 70)
            print(f"Arquivo : {file_path.name}")
            print(f"Tabela  : {RAW_SCHEMA}.{table_name}")

            try:

                columns = read_csv_header(file_path)

                print(f"Colunas : {len(columns)}")

                create_raw_table(
                    connection,
                    table_name,
                    columns,
                )

                copy_csv_to_postgres(
                    connection,
                    file_path,
                    table_name,
                    columns,
                )

                row_count = count_rows(
                    connection,
                    table_name,
                )

                connection.commit()

                print(f"Linhas  : {row_count:,}")
                print("Status  : OK")

            except Exception:

                connection.rollback()
                print("Status  : ERRO")
                raise

        print("\n" + "=" * 70)
        print("CARGA FINALIZADA COM SUCESSO")
        print("=" * 70)

    finally:

        connection.close()


if __name__ == "__main__":
    main()