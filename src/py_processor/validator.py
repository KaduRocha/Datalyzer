import pandas as pd
import os
from py_processor.utils.tratamentos import normalize_column_names_list, normalize_column_names_df

def check_duplicates(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """
    Retorna os registros duplicados com base nas chaves fornecidas.
    """
    if not keys:
        raise ValueError("Nenhuma chave primária definida para validação de duplicidade.")
    
    # print(f'#### 1 - origem:  {df}') #MKDKR - RETIRAR.
    # print(f'#### 1 - key_columns:  {keys}') #MKDKR - RETIRAR.
    # os.system("PAUSE") #MKDKR - RETIRAR.

    duplicates = df[df.duplicated(subset=keys, keep=False)]
    return duplicates
