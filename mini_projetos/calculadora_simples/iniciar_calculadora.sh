#!/usr/bin/env bash
# Inicia a calculadora com o uv. Pré-requisito: uv instalado.
set -euo pipefail

# Limpa o terminal antes de iniciar
clear

echo "==========================================="
echo "   INICIANDO CALCULADORA EM PYTHON..."
echo "==========================================="

# Verifica se o comando uv existe
if ! command -v uv &> /dev/null
then
    echo "[ERRO] uv não encontrado!"
    echo "Instale em: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "[OK] uv detectado. Iniciando..."
uv run main.py
