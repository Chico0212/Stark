# motor_regras.py (versão explícita e completa)
import pandas as pd
import re
from .utils.nbm_utils import format_ncm


def is_nbm(valor: str):  # precisamos validar o nbs
    reg = r"^\d{2,4}"
    return bool(re.match(reg, valor))


def is_nbm_valid(valor: str, ncm: str):
    reg = rf"^{ncm}"
    return bool(re.match(reg, valor))


def reduce_ncm(ncm: str) -> str | None:
    ncm_list = ncm.split(".")
    if len(ncm_list) > 1:
        return ".".join(ncm_list[:-1])
    if len(ncm) > 2:
        return ncm[:-2]
    return None


def apply_ncm_hierarchy(df: pd.DataFrame, ncm: str):
    mask = df["ncm"].apply(lambda x: is_nbm_valid(x, ncm))

    if mask.any():
        return df[mask]

    reduced = reduce_ncm(ncm)
    if reduced:
        return apply_ncm_hierarchy(df, format_ncm(reduced))

    return pd.DataFrame(columns=df.columns)


def apply_filters(rules: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """_summary_

    Args:
        rules (pd.DataFrame): _description_
    """
    cclass_trib = filters["clas_trib_ibs_cbs"]
    cst = filters["cst_codigo_ibs_cbs"]
    ncm = format_ncm(filters["nbm_codigo"])

    mask = (
        (rules["c_class_trib"] == float(cclass_trib))
        & (rules["cst"] == float(cst))
        & (rules["ncm"].apply(is_nbm))
    )

    return apply_ncm_hierarchy(rules[mask], ncm)


def find_rule(filters: dict, rules: pd.DataFrame):
    """
    Recebe os dados de uma operação e encontra a regra mais específica na planilha,
    verificando cada condição em um bloco separado para clareza.
    """
    rules = apply_filters(rules, filters)

    return rules
