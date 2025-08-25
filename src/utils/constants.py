TEMPLATE_MARKDOWN = """
# Relatório de Enquadramento Fiscal

---

## Lei e Redução

### Lei
**Descrição:** Coluna que representa a lei que enquadra um NCM em uma redução.
> `{lei}`

### Critério de Redução
**Descrição:** O tipo de benefício fiscal aplicado.
> `{criterio_reducao}`

### Percentual de Redução
**Descrição:** O percentual efetivo da redução na base de cálculo.
> `{percentual_reducao}` %

---

## Classificação Tributária

### CST (Código de Situação Tributária)
**Descrição:** Código que identifica a situação tributária da mercadoria.
> `{cst}`

### Classe de Tributação
**Descrição:** Código de classificação para fins de tributação específica.
> `{c_class_trib}`

### NCM (Nomenclatura Comum do Mercosul)
**Descrição:** Código para identificar a natureza das mercadorias.
> `{ncm}`

---

## Partes Envolvidas

### Remetente
- **Condição:** `{condicao_pessoa_remetente}`
- **Classe:** `{classe_pessoa_remetente}`
- **Elemento:** `{elemento_pessoa_remetente}`

### Destinatário
- **Condição:** `{condicao_pessoa_destinatario}`
- **Classe:** `{classe_pessoa_destinatario}`
- **Elemento:** `{elemento_pessoa_destinatario}`

"""
# Arquivo de entrada
ARQUIVO_EXCEL = "resouces/RegimesDiferenciados.xlsx"
NOME_DA_ABA = "Regimes Diferenciados"

# Diretório de saída
PASTA_RESULTADOS = "results"
TEMP_RESULTS = "temp"
