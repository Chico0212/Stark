import os
import shutil
import re
import sys
import time
from typing import Optional
import pandas as pd
from src.utils.constants import PASTA_RESULTADOS
from src.data_loader import load_data
from src.motor_regras import find_rule
from src.external.repository import buscar_dados_operacao
from src.services.minio_client import salvar_resultado_no_minio
from src.services.langflow import generate_test_case
import zipfile


DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_RAIZ = os.path.dirname(DIRETORIO_ATUAL)
sys.path.append(DIRETORIO_RAIZ)


def limpar_pasta_resultados():
    if os.path.exists(PASTA_RESULTADOS):
        shutil.rmtree(PASTA_RESULTADOS)
        print(f"Pasta '{PASTA_RESULTADOS}' limpa com sucesso.")
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)


def sanitizar_nome_arquivo(nome_lei: str) -> str:
    if not isinstance(nome_lei, str):
        nome_lei = str(nome_lei)
    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_lei)
    nome_limpo = re.sub(r"[\s./-]+", "_", nome_limpo)
    return f"{nome_limpo}.md"


def dataframe_to_markdown(df: pd.DataFrame, item_contexto: dict) -> str:
    titulo = "Documentação de Regra Aplicada"
    if not df.empty and "lei" in df.columns:
        titulo = f"Documentação da Regra: {df['lei'].iloc[0]}"
    md = f"# {titulo}\n\n"
    md += "## Contexto da Análise (Item de Entrada)\n\n"
    md += "Esta regra foi acionada pelos seguintes dados de entrada:\n\n"
    for chave, valor in item_contexto.items():
        md += f"- **`{chave}`**: `{valor}`\n"
    md += "\n---\n\n"
    md += "## Detalhes da Regra Encontrada\n\n"
    for col in df.columns:
        md += f"### Coluna: `{col}`\n\n"
        unique_values = df[col].dropna().unique()
        if len(unique_values) > 0:
            md += "**Valor presente na regra:**\n\n"
            for val in unique_values:
                md += f"- `{val}`\n"
        else:
            md += "_Nenhum valor presente ou todos nulos_\n"
        md += "\n"
    md += "---\n\n"
    return md


def processar_operacao(
    dados_operacao: list, df_regras: pd.DataFrame, test_case_id: int
) -> Optional[tuple[pd.DataFrame, str]]:
    """
    Orquestra o fluxo: Gera .md local, envia para o Langflow, e salva a resposta no MinIO.
    """
    try:
        count = 0
        limit = 3
        resultados = []

        zip_file = os.path.join(
            PASTA_RESULTADOS,
            f"Stark_file_result_{time.strftime('%d%m%Y_%H%M')}.zip",  # '%d%m%Y_%H%M'
        )

        print(f"Analisando {len(dados_operacao)} item(ns) de entrada...")
        for item in dados_operacao:
            regra_encontrada = find_rule(item, df_regras)
            if regra_encontrada.empty:
                print(
                    f"\nResultado para o item {item}: Nenhuma regra correspondente na planilha."
                )
            else:
                for i, regra in enumerate(regra_encontrada.to_dict(orient="records")):
                    if count == limit:
                        break

                    count += 1  ## gera apenas 3 pra economizar tempo
                    resultado = {**item, **regra}
                    resultados.append(resultado)
                    regra_df_individual = pd.DataFrame([regra])

                    nbm_item = item.get("nbm_codigo", "sem_nbm")
                    lei_regra = regra.get("lei", "sem_lei")
                    identificador_unico = f"NBM_{nbm_item}__{lei_regra}"
                    nome_arquivo_md = sanitizar_nome_arquivo(identificador_unico)
                    caminho_arquivo_md = os.path.join(PASTA_RESULTADOS, nome_arquivo_md)
                    markdown_string = dataframe_to_markdown(regra_df_individual, item)

                    print(
                        f"     Documentação da ocorrência salva localmente em: '{caminho_arquivo_md}'"
                    )

                    print("      Enviando conteúdo para o Langflow para gerar teste...")
                    resposta_ia = generate_test_case(f"""
                                                     externalid: Stark_{time.strftime("dd_mm_yyyTHH:mm")}
                                                     cenário: {markdown_string}""")

                    if resposta_ia:
                        print(
                            "      Resposta recebida do Langflow. Iniciando upload para o MinIO..."
                        )

                        nome_base = os.path.splitext(nome_arquivo_md)[0]
                        nome_arquivo_teste_minio = f"{nome_base}.testcases.xml"

                        path = os.path.join(
                            f"{PASTA_RESULTADOS}", nome_arquivo_teste_minio
                        )

                        with open(path, "w") as file:
                            file.write(resposta_ia)

                        with zipfile.ZipFile(
                            zip_file,
                            "a",
                            compression=zipfile.ZIP_DEFLATED,
                        ) as zipf:
                            zipf.write(path)

                    else:
                        print(
                            "      Não foi possível obter uma resposta do Langflow para este item."
                        )
                break

        with open(zip_file, "rb") as file:
            zip_file_download_key = salvar_resultado_no_minio(
                nome_arquivo=zip_file, conteudo=file.read()
            )

        if not zip_file_download_key:
            print("      Não foi possível salvar o arquivo no minio")

        if resultados:
            print(f"\n\n{pd.DataFrame(resultados)}\n\n")
            return pd.DataFrame(resultados), zip_file_download_key
        else:
            print("\nProcesso finalizado. Nenhum resultado para salvar.")
            return None  # data frame vazio

    except Exception as e:
        import traceback

        print(f"Ocorreu um erro inesperado: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Iniciando o processo de análise de regras...")

    limpar_pasta_resultados()
    regras_df = load_data()

    if regras_df is not None:
        dados_para_analisar = buscar_dados_operacao(
            operacao_id=1, pfj_codigo="90050238000629"
        )

        if dados_para_analisar:
            processar_operacao(dados_para_analisar, regras_df, test_case_id=25630)
        else:
            print("Nenhum dado foi retornado do banco de dados para a análise.")

    print("\nExecução finalizada.")
