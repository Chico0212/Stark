# Variáveis
PYTHON ?= uv run
MAIN    := src/main.py
DASH    := app/dashboard.py
INIT    := scripts/init.sh

# Alvos que não geram arquivos
.PHONY: help stark dashboard init check-uv

help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@awk -F':.*##' '/^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-uv: ## Verifica se uv está instalado
	@command -v uv >/dev/null 2>&1 || { \
		echo "Erro: uv não encontrado no PATH. Instale com:"; \
		echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	}

stark: check-uv ## Executa a aplicação principal
	$(PYTHON) $(MAIN)

dashboard: check-uv ## Executa o dashboard Streamlit
	$(PYTHON) streamlit run $(DASH)

init: check-uv ## Executa inicialização do projeto
	bash $(INIT)
