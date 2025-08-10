import json
import pandas as pd
import logging
from pathlib import Path
from py_processor.utils.tratamentos import normalize_column_names_list , infer_column_types
from py_processor.loader import load_config, load_file, load_database
from py_processor.validator import check_duplicates
import py_processor.rust_bridge as rust_bridge
from py_processor.utils.logger import logger
import os

def duplicated(origem, key_columns, source):
    
    # print(f'#### 1 - origem:  {origem}') #MKDKR - RETIRAR.
    # print(f'#### 1 - key_columns:  {key_columns}') #MKDKR - RETIRAR.
    # os.system("PAUSE") #MKDKR - RETIRAR.

    key_columns = normalize_column_names_list(key_columns)
    duplicates = check_duplicates(origem, key_columns)
    if not duplicates.empty:
        # Mascara booleana para duplicados
        duplicate_mask = origem.duplicated(subset=key_columns, keep=False)

        # Filtra duplicados
        duplicates = origem[duplicate_mask]

        # Define caminho absoluto
        output_path = Path("../data/output") / f"{source}_duplicados.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)  # Garante que a pasta exista

        # Salva com separador ; (CSV estilo Excel brasileiro)
        duplicates.to_csv(output_path, index=False, sep=";", encoding="utf-8")

        logger.info(f"Arquivo com duplicados salvo em: {output_path.resolve()}")
    else:
        logger.info("Nenhum registro duplicado encontrado com base nas chaves configuradas.")

    # MKDKR - Verificação de registros duplicados via RUST. Tempo: 37 Segungos
    # duplicates = rust_bridge.check_duplicates(df, key_columns)
    # if duplicates:
    #     print(f"Registros duplicados encontrados nas linhas (0-based): {duplicates.count()}")
    # else:
    #     print("Nenhum registro duplicado encontrado com base nas chaves configuradas.")

def main():
    try:
        # Ajuste aqui o caminho correto para o config.yaml
        config_path = Path(__file__).parent / "config" / "config.yaml"

        # Carrega config
        config = load_config(str(config_path))

        # # Pega as keys do config
        # key_columns = config.get("validation", {}).get("key_columns", [])
        # if not key_columns:
        #     logger.warning("Nenhuma chave configurada para validação de duplicatas")
        #     return
        
        ### ANALISA DADOS ORIGEM A ###
        # Use a chave da fonte no config.yaml, por exemplo 'origemA'
        logger.info(f"\n\n####  ANALISANDO ORIGEM A  ####")
        source = "origemA"
        origemType = config["sources"][source]["type"]
        key_columns = config["sources"][source].get("key_columns", [])
        
        if origemType == 'file':
            df_origemA = load_file(config, source)
        elif origemType == 'database':
            df_origemA = load_database(config, source)
        else:
            logger.info(f'Type de origem de dados não identificada. Arquivo ou Database')

        logger.info(f'{source} carregada com {len(df_origemA)} registros')

        # # Inferir nos Datatypes das colunas.
        # tipos = infer_column_types(df_origemA)
        # print(f'type:  {tipos}')
        # os.system("PAUSE")

        # Verifica se existe registros duplicados na ORIGEM A.
        logger.info(f"Iniciando verificação de duplicidade na origem {source}")
        duplicated(df_origemA, key_columns, source)


        ### ANALISA DADOS ORIGEM B ###
        logger.info(f"\n\n####  ANALISANDO ORIGEM B  ####")
        source = "origemB"
        origemType = config["sources"][source]["type"]
        key_columns = config["sources"][source].get("key_columns", [])
        key_columns = normalize_column_names_list(key_columns)
        
        if origemType == 'file':
            df_origemB = load_file(config, source)
        elif origemType == 'database':
            df_origemB = load_database(config, source)
            df_origemB.columns = [col.upper() for col in df_origemB.columns]
        else:
            logger.info(f'Type de origem de dados não identificada. Arquivo ou Database')

        logger.info(f'{source} carregada com {len(df_origemB)} registros')

        # Verifica se existe registros duplicados na ORIGEM B.
        logger.info(f"Iniciando verificação de duplicidade na origem {source}")
        duplicated(df_origemB, key_columns, source)

        ### ANALISA DIFERENÇA DE DADOS ENTRE ORIGENS A e B ###
        logger.info(f"\n\n####  Iniciando verificação de diferenças entre origens na origem A e B.  ####")
        diffs_origemA, diffs_origemB, diffs_AB = rust_bridge.compare_with_rust(
              df_origemA
            , df_origemB
            , key_columns
        )

        msg = ''
        if diffs_origemA is not None and len(diffs_origemA) > 0:
            # Exportar os dados em CSV
            pd.DataFrame(diffs_origemA).to_csv("../data/output/only_in_origemA.csv", sep=";", index=False)

            # Também salva em JSON para inspeção detalhada
            with open("../data/output/only_in_origemA.json", "w", encoding="utf-8") as f:
                json.dump(diffs_origemA, f, indent=2, ensure_ascii=False)
            msg = 'Resultados salvos em: data/output/'
        if diffs_origemB is not None and len(diffs_origemB) > 0:
            # Exportar os dados em CSV
            pd.DataFrame(diffs_origemB).to_csv("../data/output/only_in_origemB.csv", sep=";", index=False)

            # Também salva em JSON para inspeção detalhada
            with open("../data/output/only_in_origemB.json", "w", encoding="utf-8") as f:
                json.dump(diffs_origemB, f, indent=2, ensure_ascii=False)
            msg = 'Resultados salvos em: data/output/'
        if diffs_AB is not None and len(diffs_AB) > 0:
            # Exportar os dados em CSV
            pd.DataFrame(diffs_AB).to_csv("../data/output/differences.csv", sep=";", index=False)

            # Também salva em JSON para inspeção detalhada
            with open("../data/output/differences.json", "w", encoding="utf-8") as f:
                json.dump(diffs_AB, f, indent=2, ensure_ascii=False)
            msg = 'Resultados salvos em: data/output/'

        logger.info(f"Verificação de diferenças finalizada. {msg}")

    except Exception as e:
        logger.exception(f"Erro ao executar o processo: {e}")

if __name__ == "__main__":
    main()
