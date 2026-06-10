#!/bin/bash
# Script de setup para o Agente Pauta Câmara (Linux/macOS)

echo ""
echo "================================================================================"
echo "SETUP - AGENTE PAUTA CÂMARA"
echo "================================================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não foi encontrado no sistema."
    echo ""
    echo "Para instalar Python:"
    echo ""
    echo "Linux (Ubuntu/Debian):"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3 python3-pip"
    echo ""
    echo "macOS:"
    echo "  brew install python3"
    echo ""
    exit 1
fi

echo "✓ Python encontrado"
python3 --version
echo ""

# Instalar pip
echo "Atualizando pip..."
python3 -m pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo "Erro ao atualizar pip"
    exit 1
fi

echo ""
echo "Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências"
    exit 1
fi

echo ""
echo "✓ Setup concluído com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Execute os testes:     python3 test_pauta.py"
echo "2. Busque uma pauta:      python3 -m pauta_camara.main 10/06/26"
echo ""
