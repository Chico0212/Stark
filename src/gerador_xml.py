# gerador_xml.py (versão final com formatação manual e precisa)
import html


def gerar_xml_testlink(dados_entrada, regra_aplicada, internal_id):
    """
    Gera um caso de teste completo no formato XML do TestLink,
    com formatação manual para garantir a saída exata.
    """
    # --- 1. Extrair e Preparar os Dados ---
    ncm = dados_entrada.get("ncm", "N/A")
    cst = dados_entrada.get("cst", "N/A")
    cclass_trib = str(dados_entrada.get("cclass_trib", "N/A")).split(".")[0]

    percentual_reducao = regra_aplicada.get("Percentual de redução \n%")
    base_legal = html.escape(str(regra_aplicada.get("Índice por dispositivo legal")))

    cst_desc = f"CST {cst}"
    cclass_trib_desc = f"cClassTrib {cclass_trib}"

    # --- 2. Preparar os Conteúdos dos Passos ---

    # Summary e Preconditions
    summary_html = f"<p>Validar CBS/IBS 2026 para NCM {ncm}, CST {cst} ({cst_desc}) e cClassTrib {cclass_trib} ({cclass_trib_desc}).</p>"
    preconditions_html = f"<p>Ano fiscal 2026. Regra aplicável: {base_legal}.</p>"

    # Actions e Expected Results dos Passos
    actions1_html = (
        f"<p>Selecionar NCM {ncm}; depois CST {cst} e cClassTrib {cclass_trib}.</p>"
    )
    expected1_html = "<p>Campos de tributação habilitados.</p>"

    actions2_html = "<p>Informar Base de Cálculo CBS/IBS: 1000.00.</p>"
    expected2_html = "<p>Base aceita.</p>"

    # Cálculos para o passo 3
    base_calculo = 1000.0
    aliquota_padrao = 10.0
    aliquota_efetiva = aliquota_padrao * (1 - (float(percentual_reducao) / 100.0))
    valor_cbs = base_calculo * (aliquota_efetiva / 100.0)

    actions3_html = (
        "<p>Com uma Base de Cálculo de R$ 1.000,00, validar a apuração da CBS.</p>"
    )
    expected3_html = f"""<p>O sistema deve exibir os seguintes valores, baseados na regra de {percentual_reducao}% de redução:</p>
    <ul>
      <li>Alíquota Padrão: <b>{aliquota_padrao:.1f}%</b></li>
      <li>Percentual de Redução: <b>{float(percentual_reducao):.1f}%</b></li>
      <li>Alíquota Efetiva: <b>{aliquota_efetiva:.1f}%</b></li>
      <li>Valor CBS: <b>R$ {valor_cbs:.2f}</b></li>
    </ul>"""

    # --- 3. Construir a String XML Final ---

    testcase_name = f"CT001 - NCM - {ncm} - {cst_desc} - {cclass_trib_desc}"

    xml_output = f"""<?xml version="1.0" encoding="UTF-8"?>
<testcases>
<testcase internalid="{internal_id}" name="{testcase_name}">
    <node_order><![CDATA[1]]></node_order>
    <externalid><![CDATA[277]]></externalid>
    <version><![CDATA[1]]></version>
    <summary><![CDATA[{summary_html}]]></summary>
    <preconditions><![CDATA[{preconditions_html}]]></preconditions>
    <execution_type><![CDATA[1]]></execution_type>
    <importance><![CDATA[2]]></importance>
    <steps>
        <step>
            <step_number><![CDATA[1]]></step_number>
            <actions><![CDATA[{actions1_html}]]></actions>
            <expectedresults><![CDATA[{expected1_html}]]></expectedresults>
            <execution_type><![CDATA[1]]></execution_type>
        </step>
        <step>
            <step_number><![CDATA[2]]></step_number>
            <actions><![CDATA[{actions2_html}]]></actions>
            <expectedresults><![CDATA[{expected2_html}]]></expectedresults>
            <execution_type><![CDATA[1]]></execution_type>
        </step>
        <step>
            <step_number><![CDATA[3]]></step_number>
            <actions><![CDATA[{actions3_html}]]></actions>
            <expectedresults><![CDATA[{expected3_html}]]></expectedresults>
            <execution_type><![CDATA[1]]></execution_type>
        </step>
    </steps>
</testcase>
</testcases>"""

    return xml_output
