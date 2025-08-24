# Stark

Este repositório contém uma aplicação Python gerenciada com [`uv`](https://docs.astral.sh/uv/).
Ele possui:

* Um **script principal** (`src/main.py`)
* Um **dashboard interativo** em [Streamlit](https://streamlit.io/) (`app/dashboard.py`)
* Scripts auxiliares para inicialização (`scripts/init.sh`)
* [pre-commit](https://pre-commit.com/) configurado para manter a qualidade do código

---

## Pré-requisitos

* **Python 3.13+**
* **uv** (gerenciador de dependências Python da Astral)

Caso não tenha o `uv` instalado, rode:

## Configuração do ambiente

Para instalar dependências e configurar o projeto, rode:

```bash
make init
```

Isso irá:

* Instalar dependências do `uv`
* Configurar o `pre-commit`
* Executar verificações iniciais

---

## Execução

* **Aplicação principal:**

```bash
make stark
```

* **Dashboard Streamlit:**

```bash
make dashboard
```

---

## Contribuindo

Antes de commitar, rode:

```bash
uv run -- pre-commit run --all-files
```

ou simplesmente deixe o `pre-commit` rodar automaticamente ao fazer `git commit`.

---

## Comandos disponíveis

Você pode listar os comandos com:

```bash
make help
```
