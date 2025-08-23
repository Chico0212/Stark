# carregador_dados.py
import pandas as pd
from config import ARQUIVO_EXCEL, NOME_DA_ABA

def carregar_regras():
    """
    Lê a planilha do arquivo Excel e a retorna como um DataFrame.
    Trata erros de arquivo não encontrado.
    """
    try:
        regras_df = pd.read_excel(ARQUIVO_EXCEL, sheet_name=NOME_DA_ABA, usecols=["CST", "cClassTrib\n", "NCMs", "Condição \nPessoa Remetente/Prestador", "Condição\n Pessoa Destinatário"])
        print(f"Planilha '{NOME_DA_ABA}' carregada com sucesso.")
        
        regras_df.columns = ["cst", "c_class_trib", "ncm", "cond_pessoa_remetente", "cond_pessoa_destinatario"]

        return regras_df
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{ARQUIVO_EXCEL}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"ERRO CRÍTICO ao carregar a planilha: {e}")
        return None