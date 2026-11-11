@echo off
REM Inicia o Jogo da Velha com o uv ou, sem ele, com o Python. Pre-requisito: um dos dois.
title Iniciando Jogo da Velha...
cls

echo ===========================================
echo   VERIFICANDO AMBIENTE...
echo ===========================================

where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] uv detectado. Iniciando a partida...
    uv run main.py
    pause
    exit
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Nem uv nem Python foram encontrados!
    echo Instale o uv em: https://docs.astral.sh/uv/
    echo Ou o Python em: https://python.org
    pause
    exit
)

echo [OK] Python detectado (sem uv). Iniciando a partida...
python main.py
pause
