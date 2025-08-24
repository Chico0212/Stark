import os
from config import PASTA_RESULTADOS
from src.data_loader import load_data
from motor_regras import find_rule
from gerador_xml import gerar_xml_testlink
from src.external.repository import buscar_dados_operacao
import pandas as pd
from src.services.langflow import generate_test_case


def generate_md(rules: pd.DataFrame) -> str:
    return "Olá"


def processar_operacao(
    dados_operacao: dict, df_regras: pd.DataFrame, test_case_id: int
):
    """
    Orquestra o processo e chama o gerador de XML para o TestLink.
    """
    # print("\n--- Analisando Dados de Entrada ---")
    # print(dados_operacao)
    for item in dados_operacao:
        regra_encontrada = find_rule(item, df_regras)

        if regra_encontrada.empty:
            print(
                "\nResultado: Os dados de entrada não se encaixam em nenhuma regra da planilha."
            )
        else:
            print(
                "\nResultado: Regra correspondente encontrada! Gerando XML para TestLink..."
            )
            print(f"  -> Base Legal: {regra_encontrada.get('lei')}")

            # integração com o service
            print(generate_test_case(generate_md(regra_encontrada)))

            # Chama a nova função geradora de XML
            xml_final = gerar_xml_testlink(item, regra_encontrada, test_case_id)

            print("\n--- XML de Teste Gerado ---")
            print(xml_final)

            os.makedirs(PASTA_RESULTADOS, exist_ok=True)
            # Cria um nome de arquivo mais descritivo
            nome_arquivo = f"testcase_{dados_operacao.get('ncm')}_{test_case_id}.xml"
            caminho_arquivo = os.path.join(PASTA_RESULTADOS, nome_arquivo)

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(xml_final)

            print(f"Arquivo salvo em: {caminho_arquivo}")


if __name__ == "__main__":
    regras_df = load_data()

    if regras_df is not None:
        dados_para_analisar = buscar_dados_operacao(operacao_id=1)

        # print(len(dados_para_analisar), f"\n\n{dados_para_analisar}\n\n")
        # nbm_codigo
        # cst_codigo_ibs_cbs
        # clas_trib_ibs_cbs

        # exit()
        # dados_para_analisar = {
        #     "ncm": format_ncm("7615.10.00"),
        #     "cst": 200,
        #     "cclass_trib": 200016,
        # }

        # Passamos um ID único para esta execução de teste específica
        processar_operacao(dados_para_analisar, regras_df, test_case_id=25630)
