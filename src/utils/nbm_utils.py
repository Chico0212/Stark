import re


def format_ncm(ncm: str):
    reg = r"(\.00|\.0000)"

    final = re.sub(reg, "", ncm)

    if len(final) == 4 and final.endswith("00"):
        final = final[:2]

    return final
