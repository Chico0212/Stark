# motor_regras.py (versão explícita e completa)
import pandas as pd


def encontrar_regra_correspondente(dados_entrada, df_regras):
    """
    Recebe os dados de uma operação e encontra a regra mais específica na planilha,
    verificando cada condição em um bloco separado para clareza.
    """
    candidatas = []

    for index, regra in df_regras.iterrows():
        pontos = 0
        corresponde = True

        # --- CONDIÇÕES DE CHECAGEM ---

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