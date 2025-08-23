import os
from sys import stdout
from config import PASTA_RESULTADOS
from carregador_dados import carregar_regras
from motor_regras import encontrar_regra_correspondente
from gerador_xml import gerar_xml_testlink
import re
from src.external.repository import buscar_dados_operacao
import json

# Adicionar banco de dados, puxar o ncm do bd e consultar na tabela

def processar_operacao(dados_operacao, df_regras, test_case_id):
    """
    Orquestra o processo e chama o gerador de XML para o TestLink.
    """
    # print("\n--- Analisando Dados de Entrada ---")
    # print(dados_operacao)

    regra_encontrada = encontrar_regra_correspondente(dados_operacao, df_regras)

    if regra_encontrada is None:
        print("\nResultado: Os dados de entrada não se encaixam em nenhuma regra da planilha.")
    else:
        print("\nResultado: Regra correspondente encontrada! Gerando XML para TestLink...")
        print(f"  -> Base Legal: {regra_encontrada.get('Índice por dispositivo legal')}")

        # Chama a nova função geradora de XML
        xml_final = gerar_xml_testlink(dados_operacao, regra_encontrada, test_case_id)

        print("\n--- XML de Teste Gerado ---")
        print(xml_final)

        os.makedirs(PASTA_RESULTADOS, exist_ok=True)
        # Cria um nome de arquivo mais descritivo
        nome_arquivo = f"testcase_{dados_operacao.get('ncm')}_{test_case_id}.xml"
        caminho_arquivo = os.path.join(PASTA_RESULTADOS, nome_arquivo)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(xml_final)

        print(f"Arquivo salvo em: {caminho_arquivo}")

def format_ncm(ncm: str):
    reg = r"(\.00|\.0000)"
    
    final = re.sub(reg, "", ncm)
    
    if len(final) == 4 and final.endswith("00"):
        final = final[:2]

    return final

if __name__ == "__main__":
    regras_df = carregar_regras()

    if regras_df is not None:
        # dados_para_analisar = buscar_dados_operacao()
        # print(len(dados_para_analisar), f"\n\n{dados_para_analisar}\n\n")
        # nbm_codigo
        # cst_codigo_ibs_cbs
        # clas_trib_ibs_cbs
        
        # exit()
        dados_para_analisar = {
            'ncm': format_ncm('7615.10.00'),
            'cst': 200,
            'cclass_trib': 200016
        }

        # Passamos um ID único para esta execução de teste específica
        processar_operacao(dados_para_analisar, regras_df, test_case_id=25630)