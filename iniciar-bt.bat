@echo off
title Iniciando BT... (Não se preocupe, não é um vírus :P)

:: Ir para a pasta do script
cd /d "%~dp0"

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não encontrado! Instale o Python e tente novamente.
    pause
    exit
)

:: Verifica se o pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip não encontrado! Certifique-se de que o pip está instalado.
    pause
    exit
)

:: Verifica se o arquivo BT-1.py existe
if not exist "BT-1.py" (
    echo Arquivo BT-1.py não encontrado! Verifique se o arquivo está na pasta correta.
    pause
    exit
)

:: Cria e ativa um ambiente virtual (se não existir)
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)
echo Ativando ambiente virtual...
call venv\Scripts\activate

:: Instala dependências e modelo NLP
echo Instalando dependências...
pip install -r dependencias.txt
echo Baixando modelo de linguagem...
python -m spacy download pt_core_news_sm

:: Inicia o BT
echo Iniciando o BT...
python "BT-1.py"

:: Mantém o terminal aberto após a execução
pause