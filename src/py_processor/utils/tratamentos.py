# ------------------------------------------------------------
# Módulo de tratamento e normalização de dados
# ------------------------------------------------------------

import pandas as pd
import unicodedata
import os
from typing import List

# MODULO 1 - Este módulo contém funções utilitárias para padronizar nomes de colunas,
def normalize_column_names_list(columns: List[str]) -> List[str]:
    """
    Normaliza uma lista de nomes de colunas:
    - Remove acentos
    - Converte para letras maiúsculas
    - Substitui espaços por underscores
    - Remove espaços extras

    Parâmetros:
        columns (List[str]): Lista de nomes de colunas a serem normalizadas.

    Retorno:
        List[str]: Lista de nomes normalizados.
    """
    def normalize(text: str) -> str:
        # Remove acentuação
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        # Remove espaços extras, converte para maiúsculo e troca espaços por "_"
        return text.strip().upper().replace(" ", "_")

    return [normalize(col) for col in columns]

def normalize_column_names_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza os nomes das colunas de um DataFrame:
    - Remove acentos
    - Converte para letras maiúsculas
    - Substitui espaços por underscores
    - Remove espaços extras

    Parâmetros:
        df (pd.DataFrame): DataFrame com colunas a serem normalizadas.

    Retorno:
        pd.DataFrame: DataFrame com colunas normalizadas.
    """
    def normalize(col: str) -> str:
        col = unicodedata.normalize('NFKD', col)
        col = ''.join(c for c in col if not unicodedata.combining(c))
        col = col.strip().upper().replace(" ", "_")
        return col

    df.columns = [normalize(col) for col in df.columns]
    return df
# MODULO 1 - FIM.

# MODULO 2 - INICIO.
# Lista de formatos de datas comuns usados para inferência de colunas do tipo datetime
COMMON_DATE_FORMATS = [ 
      "%Y-%m-%d"
    , "%d/%m/%Y"
    , "%Y/%m/%d"
    , "%d-%m-%Y"
    , "%Y%m%d"
    , "%d%m%Y"
]

def datetime_series(series: pd.Series) -> bool:
    """
    Verifica se uma série de dados pode ser interpretada como datetime,
    com base em formatos de datas comuns.

    Parâmetros:
        series (pd.Series): Série de dados a ser avaliada.

    Retorno:
        bool: True se a série puder ser convertida para datetime, False caso contrário.
    """
    for fmt in COMMON_DATE_FORMATS:
        try:
            pd.to_datetime(series, format=fmt, errors='raise')
            return True
        except Exception:
            continue
    return False

# Identificar tipos de dados em um DataFrame e realizar verificações de datas.
def infer_column_types(df: pd.DataFrame, sample_size: int = 100) -> dict:
    """
    Infere o tipo de dados de cada coluna de um DataFrame com base em uma amostra.

    Tipos possíveis: 'numeric', 'datetime', 'string', 'unknown'.

    Parâmetros:
        df (pd.DataFrame): DataFrame de entrada.
        sample_size (int): Número de linhas a serem utilizadas para inferência.

    Retorno:
        dict: Dicionário com o nome da coluna como chave e tipo inferido como valor.
    """
    inferred = {}
    sample_df = df.head(sample_size)

    for col in sample_df.columns:
        series = sample_df[col].dropna()

        if series.empty:
            inferred[col] = "unknown"
            continue

        try:
            pd.to_numeric(series)
            inferred[col] = "numeric"
            continue
        except:
            pass

        if datetime_series(series):
            inferred[col] = "datetime"
            continue

        inferred[col] = "string"

    return inferred
# MODULO 2 - FIM.