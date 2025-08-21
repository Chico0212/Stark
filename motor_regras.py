# motor_regras.py (versão explícita e completa)
import pandas as pd
import re

def is_nbs(valor: str):
    if len(valor) < 2:
        return True

    # if not re.match(r"^\d\.", valor):
    #     valor = re.sub(r"^\d", "",valor)

    return bool(re.match(r"^\d\.", valor))

def formatar_ncm(valor):
    if pd.isna(valor) or valor == '':
        return valor
    
    # Remove pontos existentes e espaços
    valor_limpo = str(valor).replace('.', '').replace(' ', '')
    
    # Preenche com zeros à direita até ter 8 dígitos
    valor_padded = valor_limpo.ljust(8, '0')
    
    # Formata como XXXX.XX.XX
    return f"{valor_padded[:4]}.{valor_padded[4:6]}.{valor_padded[6:8]}"

def normalize_data(df_regras: pd.DataFrame) -> pd.DataFrame:
    """_summary_

    Args:
        df_regras (pd.DataFrame): _description_
    """
    # cliente == pfj_codigo / informante_est_codigo == CNPJ
    # dof <- idf[] == itens do dof
    # idf <- NCM, idf_tributo
    # idf_tributo == ibs e cbs 
    
    filtered_df = (df_regras
                .assign(valores=df_regras['NCMs'].str.split('|'))
                .explode('valores'))
                # .loc[lambda x: ~x['valores'].apply(is_nbs)]) # resolver isso
    
    return filtered_df.assign(valores_formatados=lambda x: x['valores'].apply(formatar_ncm))

def encontrar_regra_correspondente(dados_entrada: dict, df_regras: pd.DataFrame):
    """
    Recebe os dados de uma operação e encontra a regra mais específica na planilha,
    verificando cada condição em um bloco separado para clareza.
    """
    candidatas = []
    
    cclass_trib_valor = dados_entrada['cclass_trib']
    cst_valor = dados_entrada['cst']
    ncm_valor = dados_entrada['ncm']

    # BUSCA EM HIERARQUIA
    # 1. BUSCAR DE FORMAS DIFERENTES 
    ## 3101.00.00, 3101.00, 31.01, 3101
    # 2. FORMATAR OS VALORES NA NORMALIZAÇÃO
    ## 31         -> 3100.00.00
    ## 3101       -> 3101.00.00
    ## 31.01      -> 3101.00.00
    ## 3101.10    -> 3100.10.00
    ## 3101.10.10 -> 3100.10.10
    
    # PFJ -> CST, CCLASS_TRIB, NCM[] -> FILTRO TABELA

    df_regras = normalize_data(df_regras)
    
    dados_para_analisar = {
            'ncm': '3101.00.00',
            'cst': '200',
            'cclass_trib': '200033.0'
            # ... adicione outros campos conforme necessário
        }

    filtro = filtro = (df_regras['cClassTrib'] == cclass_trib_valor) & \
         (df_regras['CST'] == cst_valor) & \
         (df_regras['valores_formatados'] == ncm_valor)


    # df_regras['cClassTrib' == dados_entrada['cclass_trib']]['CST' == dados_entrada['cst']]['valores_formatados' == dados_entrada['ncm']]
    df_regras = df_regras[filtro]

    for index, regra in df_regras.iterrows():
        pontos = 0
        corresponde = True

        # --- CONDIÇÕES DE CHECAGEM ---

        # teste = normalize_data(df_regras)
        
        # 1. Checar NCMs
        ncms_regra_str = str(regra.get('NCMs', ''))
        ncms_regra = [ncm.strip().lower() for ncm in ncms_regra_str.split('|') if ncm.strip()]

        #Apenas para a regra que nos interessa, para não poluir a tela com prints
        if not ncms_regra or dados_entrada.get('ncm', '').lower() not in ncms_regra:
            continue  # Se o NCM é obrigatório e não bate, essa regra é inválida.
        pontos = 1

        # 2. Checar Origem da Mercadoria
        if corresponde and dados_entrada.get('origem_mercadoria'):
            origem_regra_str = str(regra.get('Origem da Mercadoria', ''))
            if origem_regra_str.strip() != '':
                opcoes = [opt.strip().lower() for opt in origem_regra_str.split('|')]
                if dados_entrada.get('origem_mercadoria', '').lower() in opcoes:
                    pontos += 2
                else:
                    corresponde = False

        # 3. Checar CST
        if corresponde and dados_entrada.get('cst'):
            cst_regra = regra.get('CST')
            # --- DEBUG SIMPLES ---
            # Imprime os valores EXATOS que serão comparados, antes de convertê-los.

            if pd.notna(cst_regra) and str(cst_regra).strip() != '':
                if str(dados_entrada.get('cst', '')) == str(int(cst_regra)):
                    print(f"  -> [Debug CST] Valor na Regra: '{str(cst_regra)}' | Valor na Entrada: '{str(dados_entrada.get('cst', ''))}'")
                    pontos += 1
                else:
                    corresponde = False

        # 4. Checar cClassTrib (vamos assumir que a coluna se chama 'cClassTrib\n' como no seu exemplo)
        if corresponde and dados_entrada.get('cclass_trib'):
            cclass_regra_str = str(regra.get('cClassTrib\n', ''))
            if cclass_regra_str.strip() != '':
                opcoes = [opt.strip().lower() for opt in cclass_regra_str.split('|')]
                print(f"  -> [Debug cClassTrib] Valor na Regra: '{str(cclass_regra_str)}' | Valor na Entrada: '{str(dados_entrada.get('cclass_trib', ''))}'")
                if dados_entrada.get('cclass_trib', '').lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # --- Checagens do Remetente ---

        # 5. Checar Condição do Remetente
        if corresponde and dados_entrada.get('condicao_remetente'):
            cond_rem_regra_str = str(regra.get('Condição \nPessoa Remetente/Prestador', ''))
            if cond_rem_regra_str.strip() != '':
                opcoes = [opt.strip().lower() for opt in cond_rem_regra_str.split('|')]
                if dados_entrada.get('condicao_remetente', '').lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # 6. Checar Classe do Remetente
        if corresponde and dados_entrada.get('classe_remetente'):
            classe_rem_regra_str = str(regra.get('Classe \nPessoa Remetente/Prestador', ''))
            if classe_rem_regra_str.strip() != '':
                opcoes = [opt.strip().lower() for opt in classe_rem_regra_str.split('|')]
                if dados_entrada.get('classe_remetente', '').lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # --- Checagens do Destinatário ---

        # 7. Checar Classe do Destinatário
        if corresponde and dados_entrada.get('classe_destinatario'):
            classe_dest_regra_str = str(regra.get('Classe\n Pessoa Destinatário', ''))
            if classe_dest_regra_str.strip() != '':
                opcoes = [opt.strip().lower() for opt in classe_dest_regra_str.split('|')]
                if dados_entrada.get('classe_destinatario', '').lower() in opcoes:
                    pontos += 5
                else:
                    corresponde = False

        # ... Adicione blocos para as colunas 'Elemento' se necessário ...
        print(f"  -> [Debug pontos] Valor na Regra: '{pontos}')'")
        # --- FIM DAS CHECAGENS ---
        if corresponde:
            candidatas.append({'regra': regra, 'pontos': pontos})
    print(f"  -> [Debug Candidatas] Valor na Regra: '{candidatas}')'")
    if not candidatas:
        return None

    melhor_candidata = max(candidatas, key=lambda c: c['pontos'])
    return melhor_candidata['regra']