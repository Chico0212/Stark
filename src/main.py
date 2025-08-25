import os
import re

from .config import PASTA_RESULTADOS
from .data_loader import load_data
from .motor_regras import find_rule
from .external.repository import buscar_dados_operacao
import pandas as pd
import shutil
# from services.langflow import generate_test_case


def generate_md(rules: pd.DataFrame) -> str:
    """função pra transformar rules em markdown"""
    return "Olá"


def limpar_pasta_resultados():
    """
    Apaga e recria a pasta de resultados para garantir que começa limpa
    a cada nova análise.
    """
    if os.path.exists(PASTA_RESULTADOS):
        shutil.rmtree(PASTA_RESULTADOS)
        print(f"Pasta '{PASTA_RESULTADOS}' limpa com sucesso.")
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)


# [# ADICIONADO] - Função auxiliar para criar nomes de arquivo seguros
def sanitizar_nome_arquivo(nome_lei: str) -> str:
    """
    Limpa uma string para que ela se torne um nome de arquivo válido.
    - Remove caracteres inválidos.
    - Substitui espaços e outros separadores por underscores.
    - Adiciona a extensão .md.
    """
    if not isinstance(nome_lei, str):
        nome_lei = str(nome_lei)

    # Remove caracteres que não são permitidos em nomes de arquivo
    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome_lei)
    # Substitui espaços, pontos, etc., por um único underscore
    nome_limpo = re.sub(r"[\s./-]+", "_", nome_limpo)
    return f"{nome_limpo}.md"


# [# MODIFICADO] - A função agora aceita um dicionário de contexto para enriquecer o MD.
def dataframe_to_markdown(df: pd.DataFrame, item_contexto: dict) -> str:
    """
    Gera uma explicação em Markdown para cada coluna do DataFrame (a regra)
    e também documenta o item de entrada que acionou essa regra.
    """
    titulo = "Documentação de Regra Aplicada"
    if not df.empty and "lei" in df.columns:
        titulo = f"Documentação da Regra: {df['lei'].iloc[0]}"

    md = f"# {titulo}\n\n"

    # Adiciona a seção de contexto do item de entrada
    md += "## Contexto da Análise (Item de Entrada)\n\n"
    md += "Esta regra foi acionada pelos seguintes dados de entrada:\n\n"
    for chave, valor in item_contexto.items():
        md += f"- **`{chave}`**: `{valor}`\n"
    md += "\n---\n\n"

    # O resto da função continua igual, documentando a regra em si
    md += "## Detalhes da Regra Encontrada\n\n"
    for col in df.columns:
        md += f"### Coluna: `{col}`\n\n"
        # md += f"**Descrição:** \n> (Descreva o significado da coluna `{col}` aqui)\n\n" # Opcional

        unique_values = df[col].dropna().unique()
        if len(unique_values) > 0:
            md += "**Valor presente na regra:**\n\n"
            for val in unique_values:
                md += f"- `{val}`\n"
        else:
            md += "_Nenhum valor presente ou todos nulos_\n"
        md += "\n"  # Espaçamento

    md += "---\n\n"
    return md


def processar_operacao(
    dados_operacao: list, df_regras: pd.DataFrame, test_case_id: int
):
    """
    Orquestra o processo, encontrando todas as regras correspondentes e
    processando cada uma individualmente, sem sobreposição de arquivos.
    """
    try:
        resultados = []
        print(f"Analisando {len(dados_operacao)} item(ns) de entrada...")
        for item in dados_operacao:
            regra_encontrada = find_rule(item, df_regras)
            if regra_encontrada.empty:
                print(
                    f"\nResultado para o item {item}: Nenhuma regra correspondente na planilha."
                )
            else:
                for regra in regra_encontrada.to_dict(orient="records"):
                    resultado = {**item, **regra}
                    resultados.append(resultado)

                    regra_df_individual = pd.DataFrame([regra])
                    # [# MODIFICADO] - Criação de um nome de arquivo único e descritivo
                    # Combina o NBM/NCM do item com a base legal da regra.
                    nbm_item = item.get("nbm_codigo", "sem_nbm")
                    lei_regra = regra.get("lei", "sem_lei")
                    identificador_unico = f"NBM_{nbm_item}__{lei_regra}"

                    nome_arquivo_md = sanitizar_nome_arquivo(identificador_unico)
                    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
                    caminho_arquivo_md = os.path.join(PASTA_RESULTADOS, nome_arquivo_md)

                    # Passa tanto a regra quanto o item de contexto para a função
                    markdown_string = dataframe_to_markdown(regra_df_individual, item)

                    with open(caminho_arquivo_md, "w", encoding="utf-8") as f:
                        f.write(markdown_string)

                    print(
                        f"     Documentação da ocorrência salva em: '{caminho_arquivo_md}'"
                    )
        # Salva o arquivo CSV no final
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            caminho_csv = os.path.join(PASTA_RESULTADOS, "resultados.csv")
            df_resultados.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
            print(
                f"\nProcesso finalizado. Resultados consolidados salvos em: {caminho_csv}"
            )
            return True  # Sucesso
        else:
            print("\nProcesso finalizado. Nenhum resultado para salvar.")
            return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False  # Falha


if __name__ == "__main__":
    regras_df = load_data()

    if regras_df is not None:
        dados_para_analisar = buscar_dados_operacao(operacao_id=1)
        # Passamos um ID único para esta execução de teste específica
        processar_operacao(dados_para_analisar, regras_df, test_case_id=25630)
