@echo off
REM Script de setup para o Agente Pauta Câmara
REM Instala Python e dependências (Windows)

echo.
echo ================================================================================
echo SETUP - AGENTE PAUTA CÂMARA
echo ================================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python não foi encontrado no sistema.
    echo.
    echo Para instalar Python:
    echo 1. Visite https://www.python.org/downloads/
    echo 2. Baixe a versão 3.8 ou superior para Windows
    echo 3. Durante a instalação, marque "Add Python to PATH"
    echo 4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version
echo.

REM Instalar pip
echo Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Erro ao atualizar pip
    pause
    exit /b 1
)

echo.
echo Instalando dependências...
pip install -r requirements.txt

if errorlevel 1 (
    echo Erro ao instalar dependências
    pause
    exit /b 1
)

echo.
echo ✓ Setup concluído com sucesso!
echo.
echo Próximos passos:
echo 1. Execute os testes: python test_pauta.py
echo 2. Busque uma pauta: python -m pauta_camara.main 10/06/26
echo.
pause
