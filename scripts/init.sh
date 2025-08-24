#!/usr/bin/env bash
set -euo pipefail

# Função para instalar o uv
install_uv() {
    echo "Instalando uv..."
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget &> /dev/null; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        echo "Erro: nem curl nem wget estão instalados. Instale um deles e rode novamente." >&2
        exit 1
    fi
    export PATH="$HOME/.cargo/bin:$PATH"
}

# Verifica se o uv está instalado
if ! command -v uv &> /dev/null; then
    echo "uv não encontrado."
    install_uv
else
    echo "uv já instalado."
fi

# Sincroniza todos os grupos
uv sync --all-groups

# Instala o pre-commit
uv run pre-commit install

# Roda pre-commit em todos os arquivos
uv run -- pre-commit run --all-files
