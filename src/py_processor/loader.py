import pandas as pd
from pathlib import Path
import yaml
from sqlalchemy import create_engine
from py_processor.utils.tratamentos import normalize_column_names_list , normalize_column_names_df
import re

def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Carrega o arquivo de configuração YAML contendo as definições das fontes de dados.
    
    Args:
        config_path (str): Caminho relativo para o arquivo de configuração YAML.

    Returns:
        dict: Dicionário com os parâmetros definidos no arquivo YAML.
    """
    base_path = Path(__file__).parents[2].resolve()  # ponto raiz do projeto (src)
    full_path = (base_path / config_path).resolve()

    if not full_path.exists():
        raise FileNotFoundError(f"Configuração não encontrada: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_file(config: dict, source_key: str) -> pd.DataFrame:
    """
    Carrega um arquivo local (CSV, TXT, Excel, JSON) com base nas configurações fornecidas no arquivo YAML.

    Args:
        config (dict): Configuração geral carregada via load_config.
        source_key (str): Nome da chave da fonte (ex: 'origemA') a ser lida.

    Returns:
        pd.DataFrame: Dados carregados no formato DataFrame.
    """
    if source_key not in config.get("sources", {}):
        raise KeyError(f"Fonte '{source_key}' não encontrada no config.yaml")

    source = config["sources"][source_key]
    base_path = Path(__file__).parents[2].resolve()
    file_path = (base_path / source["file_path"]).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Obtém a extensão do arquivo (.csv, .xlsx, etc.)
    ext = file_path.suffix.lower()

    # Lista de encodings a tentar caso o arquivo não seja lido corretamente
    encodings_to_try = [
        source.get("encoding", "utf-8")
        , "utf-8-sig"
        , "latin1"
        , "ISO-8859-1"
        , "cp1252"
    ]

    try:
        # Leitura para arquivos Excel
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, dtype=str)
            df = normalize_column_names_df(df)
            return df
        
        # Leitura para arquivos JSON
        elif ext == ".json":
            df = pd.read_json(file_path, encoding=source.get("encoding", "utf-8"))
            df = normalize_column_names_df(df)
            return df
        
        # Leitura para arquivos CSV ou TXT com fallback de encoding
        elif ext in [".csv", ".txt"]:
            separator = source.get("separator", ",")
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, sep=separator, encoding=enc, dtype=str)
                    df = normalize_column_names_df(df)
                    return df
                except UnicodeDecodeError:
                    continue
            raise UnicodeDecodeError(
                f"Não foi possível decodificar o arquivo '{file_path}' com os encodings testados: {encodings_to_try}"
            )

        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

    except Exception as e:
        raise RuntimeError(f"Erro ao carregar arquivo '{file_path}': {e}")

def load_database(config: dict, source: str) -> pd.DataFrame:
# def load_database(config: dict, source: str, keys: list[str]) -> pd.DataFrame:
    """
    Conecta a um banco de dados relacional e executa uma query para retornar os dados como DataFrame.
    
    A query pode ser definida diretamente ou construída com base na tabela e cláusula WHERE definidas.

    Args:
        config (dict): Dicionário de configuração carregado via load_config.
        source (str): Nome da fonte no config.yaml.

    Returns:
        pd.DataFrame: Dados extraídos do banco de dados.
    """

    if source not in config.get("sources", {}):
        raise KeyError(f"Fonte '{source}' não encontrada no config.yaml")

    source = config["sources"][source]

    if source.get("type") != "database":
        raise ValueError(f"Fonte '{source}' não é do tipo 'database'.")

    # Parâmetros da conexão
    db_type = source.get("db_type")
    user = source.get("username")
    password = source.get("password")
    host = source.get("host")
    port = source.get("port")
    database = source.get("database")

    # Lista de colunas opcionais
    columns = source.get("columns", [])
    columns = normalize_column_names_list(columns)
    # keys = normalize_column_names_list(keys)
    # columns = ', '.join(columns)

    # Monta a query a partir do config
    query = source.get("query")
    if not query:
        table = source.get("table")
        if not table:
            raise ValueError(f"Você deve informar 'query' ou 'table' para a fonte '{source}'.")

        where_clause = source.get("where")

        # Valida se a cláusula WHERE contém comandos perigosos
        if where_clause:
            if re.search(r";|--|drop|delete|insert|update", where_clause, re.IGNORECASE):
                raise ValueError(f"Cláusula WHERE potencialmente insegura detectada para a fonte '{source}'.")

        query = f"SELECT * FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"

    # Monta a string de conexão conforme o tipo de banco
    if db_type == "postgresql":
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

    elif db_type == "mysql":
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    elif db_type == "sqlserver":
        driver = source.get("driver", "ODBC Driver 17 for SQL Server")
        url = f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver={driver.replace(' ', '+')}"

    elif db_type == "oracle":
        service_name = source.get("service_name")
        if not service_name or not re.match(r"^[a-zA-Z0-9_.-]+$", service_name):
            raise ValueError(f"'service_name' inválido ou não informado para conexões Oracle.")
        url = f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={service_name}"

    else:
        raise ValueError(f"Tipo de banco '{db_type}' não suportado.")

    # Executa a consulta e retorna os dados
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df

    except Exception as e:
        raise RuntimeError(f"Erro ao conectar e carregar dados do banco '{db_type}': {e}")
