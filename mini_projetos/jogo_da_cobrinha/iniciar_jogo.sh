#!/usr/bin/env bash
# Inicia o Jogo da Cobrinha com o uv ou, sem ele, com o Python 3.
set -euo pipefail

clear
echo "==========================================="
echo "   INICIANDO JOGO DA COBRINHA EM PYTHON..."
echo "==========================================="

if command -v uv &> /dev/null; then
    echo "[OK] uv detectado. Iniciando a partida..."
    uv run main.py
    exit 0
fi

if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Nem uv nem Python 3 foram encontrados!"
    echo "Instale o uv em: https://docs.astral.sh/uv/"
    echo "Ou o Python via o gerenciador de pacotes do seu sistema."
    exit 1
fi

echo "[OK] Python 3 detectado (sem uv). Iniciando a partida..."
python3 main.py
