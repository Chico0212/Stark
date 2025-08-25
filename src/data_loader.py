# carregador_dados.py
import pandas as pd
from .config import ARQUIVO_EXCEL, NOME_DA_ABA


def explode_items(df: pd.DataFrame, col: str):
    return df.assign(ncm=df[col].str.split("|")).explode(col)


def load_data():
    """
    Lê a planilha do arquivo Excel e a retorna como um DataFrame.
    Trata erros de arquivo não encontrado.
    """
    try:
        rules = pd.read_excel(
            ARQUIVO_EXCEL,
            sheet_name=NOME_DA_ABA,
        )

        print(f"Planilha '{NOME_DA_ABA}' carregada com sucesso.")

        rules.columns = [
            "lei",
            "criterio_reducao",
            "percentual_reducao",
            "cst",
            "c_class_trib",
            "ncm",
            "condicao_pessoa_remetente",
            "classe_pessoa_remetente",
            "elemento_pessoa_remetente",
            "condicao_pessoa_destinatario",
            "classe_pessoa_destinatario",
            "elemento_pessoa_destinatario",
        ]

        return explode_items(rules, "ncm")
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{ARQUIVO_EXCEL}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar a planilha: {e}")
        return None
