# motor_regras.py (versão explícita e completa)
import pandas as pd
import re


def is_nbm(valor: str):  # precisamos validar o nbs
    reg = r"^\d{2,4}"
    return bool(re.match(reg, valor))


def is_nbm_valid(valor: str, ncm: str):
    reg = rf"^{ncm}"
    return bool(re.match(reg, valor))


def normalize_data(df_regras: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """_summary_

    Args:
        df_regras (pd.DataFrame): _description_
    """
    cclass_trib_valor = filters["cclass_trib"]
    cst_valor = filters["cst"]
    ncm_valor = filters["ncm"]

    df_exploded = df_regras.assign(ncm=df_regras["ncm"].str.split("|")).explode("ncm")

    mask = (
        (df_exploded["c_class_trib"] == cclass_trib_valor)
        & (df_exploded["cst"] == cst_valor)
        & (df_exploded["ncm"].apply(is_nbm))
        & (df_exploded["ncm"].apply(lambda x: is_nbm_valid(x, ncm_valor)))
    )

    df_filtered = df_exploded[mask]

    return df_filtered[mask]


def encontrar_regra_correspondente(dados_entrada: dict, df_regras: pd.DataFrame):
    """
    Recebe os dados de uma operação e encontra a regra mais específica na planilha,
    verificando cada condição em um bloco separado para clareza.
    """
    candidatas = []

    df_regras = normalize_data(df_regras, dados_entrada)

    for index, regra in df_regras.iterrows():
        pontos = 0
        corresponde = True

        # --- CONDIÇÕES DE CHECAGEM ---

        # 2. Checar Origem da Mercadoria
        if corresponde and dados_entrada.get("origem_mercadoria"):
            origem_regra_str = str(regra.get("Origem da Mercadoria", ""))
            if origem_regra_str.strip() != "":
                opcoes = [opt.strip().lower() for opt in origem_regra_str.split("|")]
                if dados_entrada.get("origem_mercadoria", "").lower() in opcoes:
                    pontos += 2
                else:
                    corresponde = False
        # --- Checagens do Remetente ---

        # 5. Checar Condição do Remetente
        if corresponde and dados_entrada.get("condicao_remetente"):
            cond_rem_regra_str = str(regra.get("cond_pessoa_remetente", ""))
            if cond_rem_regra_str.strip() != "":
                opcoes = [opt.strip().lower() for opt in cond_rem_regra_str.split("|")]
                if dados_entrada.get("condicao_remetente", "").lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # 6. Checar Classe do Remetente
        if corresponde and dados_entrada.get("classe_remetente"):
            classe_rem_regra_str = str(regra.get("classe_pessoa_remetente", ""))
            if classe_rem_regra_str.strip() != "":
                opcoes = [
                    opt.strip().lower() for opt in classe_rem_regra_str.split("|")
                ]
                if dados_entrada.get("classe_remetente", "").lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # --- Checagens do Destinatário ---

        # 7. Checar Classe do Destinatário
        if corresponde and dados_entrada.get("classe_destinatario"):
            classe_dest_regra_str = str(regra.get("classe_pessoa_destinatario", ""))
            if classe_dest_regra_str.strip() != "":
                opcoes = [
                    opt.strip().lower() for opt in classe_dest_regra_str.split("|")
                ]
                if dados_entrada.get("classe_destinatario", "").lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # ... Adicione blocos para as colunas 'Elemento' se necessário ...
        print(f"  -> [Debug pontos] Valor na Regra: '{pontos}')'")
        # --- FIM DAS CHECAGENS ---
        if corresponde:
            candidatas.append({"regra": regra, "pontos": pontos})

    print(f"  -> [Debug Candidatas] Valor na Regra: '{candidatas}')'")
    if not candidatas:
        return None

    melhor_candidata = max(candidatas, key=lambda c: c["pontos"])
    return melhor_candidata["regra"]
