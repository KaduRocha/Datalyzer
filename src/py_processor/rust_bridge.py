# ------------------------------------------------------------
# Bridge para comunicação com o módulo Rust
# ------------------------------------------------------------

import rust_core  # Esse é o módulo gerado pelo `maturin develop`

import pandas as pd
import os
from py_processor.utils.tratamentos import normalize_column_names_list, normalize_column_names_df

def process_with_rust(df):
    # Transforma o DataFrame em lista de dicionários
    data = df.to_dict(orient="records")
    return rust_core.process_data(data)

def check_duplicates(df, key_columns):
    data = df.to_dict(orient="records")
    # Chama a função Rust para detectar índices de duplicados
    duplicates_indices = rust_core.check_duplicates_by_keys(data, key_columns)
    return duplicates_indices


def convert_all_values_to_str(record: dict) -> dict:
    """Converte todos os valores do dicionário para string, evitando floats, NaNs, etc."""
    str_records = {str(k): str(v) if not pd.isna(v) else "" for k, v in record.items()}
    return str_records

def compare_with_rust(df_origemA: pd.DataFrame, df_origemB: pd.DataFrame, key_columns: list):
    """
    origem_rows, destino_rows: list[dict]
    key_columns: list[str]
    """
    
    # print(f'### Entrada 1 compare_with_rust: \n {df_origemA} \n {df_origemB} \n {key_columns}')
    # os.system("PAUSE")
    
    df_origemA = normalize_column_names_df(df_origemA)
    df_origemB = normalize_column_names_df(df_origemB)
    key_columns = normalize_column_names_list(key_columns)
    

    # print(f'### Entrada 2 compare_with_rust: \n {df_origemA} \n {df_origemB} \n {key_columns}')
    # os.system("PAUSE")
    

    # Converte os DataFrames para listas de dicionários
    origemA_rows = df_origemA.to_dict(orient="records")
    origemB_rows = df_origemB.to_dict(orient="records")

    # # Converte os valores internos para string, evitando erros com PyString
    origemA = [convert_all_values_to_str(row) for row in origemA_rows]
    origemB = [convert_all_values_to_str(row) for row in origemB_rows]

    # print(f'### ENTRADA compare_records: \n {origemA} \n {origemB} \n {key_columns}')
    # os.system("PAUSE")

    only_in_origem, only_in_destino, differences = rust_core.compare_records(
        origemA, origemB, key_columns
    )

    # print(f'### only_in_origem 1 - {only_in_origem}')
    # print(f'### only_in_destino 1 - {only_in_destino}')
    # print(f'### differences 1 - {differences}')
    # os.system("PAUSE")

    return only_in_origem, only_in_destino, differences
