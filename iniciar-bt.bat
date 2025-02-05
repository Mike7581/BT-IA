@echo off
title Iniciando BT...

:: Ir para a pasta do script
cd /d "%~dp0"

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não encontrado! Instale o Python e tente novamente.
    pause
    exit
)

:: Instalar dependências
echo Instalando dependências...
pip install -r dependencias.txt

:: Baixar o modelo do spaCy
echo Baixando o modelo do spaCy...
python -m spacy download pt_core_news_sm

:: Iniciar o BT
echo Iniciando o BT...
start python "BT-1.py"
exit
