# GUIA DE INSTALAÇÃO E PRIMEIRA USO

Agente Pauta Câmara - Versão 0.2

## 📋 Pré-requisitos

- **Python 3.8+** (não instalado no momento)
- **pip** (gerenciador de pacotes Python)
- Conexão com a internet

## 🪟 Instalação no Windows

### Passo 1: Instalar Python

1. Acesse [python.org](https://www.python.org/downloads/)
2. Clique em "Download Python" (versão 3.10 ou superior recomendada)
3. Execute o instalador
4. **IMPORTANTE**: Marque a opção **"Add Python to PATH"** durante a instalação
5. Clique em "Install Now"
6. Aguarde a conclusão

### Passo 2: Verificar instalação

Abra PowerShell ou CMD e execute:

```powershell
python --version
```

Você deve ver algo como: `Python 3.10.x`

### Passo 3: Instalar dependências

Na pasta do projeto, execute:

```powershell
setup.bat
```

Ou manualmente:

```powershell
pip install -r requirements.txt
```

## 🐧 Instalação no Linux/macOS

### Passo 1: Instalar Python

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

**macOS (com Homebrew):**
```bash
brew install python3
```

### Passo 2: Verificar instalação

```bash
python3 --version
```

### Passo 3: Instalar dependências

Na pasta do projeto:

```bash
bash setup.sh
```

Ou manualmente:

```bash
pip3 install -r requirements.txt
```

## ✅ Testar instalação

Depois de instalar as dependências, execute os testes:

```
Windows:  python test_pauta.py
Linux:    python3 test_pauta.py
```

Você deve ver:
```
================================================================================
TESTE 1: LIMPEZA DE EMENTAS
================================================================================
...
✓ TODOS OS TESTES CONCLUÍDOS COM SUCESSO
```

## 🚀 Primeira utilização

### Opção 1: Interface CLI (Recomendado para iniciantes)

```
Windows:  python cli.py
Linux:    python3 cli.py
```

Isso abrirá um menu interativo onde você pode:
1. Buscar pauta por data
2. Listar pautas já baixadas
3. Ver informações sobre o agente

### Opção 2: Linha de comando

```
Windows:  python -m pauta_camara.main 10/06/26
Linux:    python3 -m pauta_camara.main 10/06/26
```

### Opção 3: Integração com VS Code Copilot

Abra o VS Code nesta pasta e use o Copilot com comandos como:
- "Qual é a pauta de hoje?"
- "Traga a pauta de 15/06/26"
- "Pauta da Sessão Deliberativa"

## 📂 Estrutura de arquivos criados

Após usar o agente, você verá:

```
seu-projeto/
├── pautas/
│   ├── pauta-20260610.pdf       ← PDF baixado do site
│   ├── pauta-20260610.json      ← Proposições em formato JSON
│   └── pauta-20260610.txt       ← Proposições em formato legível
```

## 📖 Exemplos de uso

### Exemplo 1: Buscar pauta de hoje

```
Windows:  python -m pauta_camara.main 10/06/26
Linux:    python3 -m pauta_camara.main 10/06/26
```

Output esperado:
```
================================================================================
AGENTE PAUTA CÂMARA - Buscando pauta para 10/06/26
================================================================================

[1/5] Buscando sessão para 10/06/26...
✓ Sessão encontrada: Sessão Deliberativa Extraordinária de 10/06/2026

[2/5] Buscando link da pauta na sessão...
✓ Link da pauta encontrado

[3/5] Confirmação de download:
   URL: https://www2.camara.leg.br/...
   Deseja baixar o PDF? (s/n): s

[4/5] Baixando PDF...
✓ PDF baixado: pauta-20260610.pdf

[5/5] Extraindo proposições...
✓ 4 proposições extraídas

================================================================================
RESUMO - PAUTA DE 10/06/26
================================================================================

1. Requerimento nº 1.750, de 2023
    Urgência para apreciação do Projeto de Lei nº 4.503, de 2019...

2. Projeto de Lei nº 424-B, de 2015
    Acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666...

✓ Total: 4 itens
📁 PDF: pauta-20260610.pdf
📄 Resumo: pauta-20260610.json e .txt
================================================================================
```

### Exemplo 2: Usar em Python

```python
from pauta_camara import fetch_pauta_by_date

# Buscar pauta
resultado = fetch_pauta_by_date(
    date_str="10/06/26",
    workspace_path=".",
    confirm_download=True
)

if resultado['sucesso']:
    print(f"Pauta baixada com {resultado['total']} proposições")
    
    # Listar proposições
    for prop in resultado['proposicoes']:
        print(f"\n{prop['numero']}. {prop['identificacao']}")
        print(f"   {prop['ementa_truncada']}")
else:
    print(f"Erro: {resultado['mensagem']}")
```

## 🔧 Troubleshooting

### "Python não foi encontrado"

**Solução:**
- Desinstale Python completamente
- Reinstale marcando "Add Python to PATH"
- Feche e reabra o terminal
- Tente novamente

### "ModuleNotFoundError: No module named 'requests'"

**Solução:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### "Nenhuma sessão encontrada para DD/MM/AA"

**Possíveis causas:**
- Data inválida ou fora do período de sessões
- Sessão não publicada
- Problema com acesso ao site

**Solução:**
- Tente uma data próxima (dia anterior/próximo)
- Visite https://www.camara.leg.br/plenario para verificar manualmente
- Aguarde alguns minutos e tente novamente

### "Não foi possível encontrar o link da pauta"

**Possível causa:** Layout do site mudou

**Solução:**
- Atualize para a versão mais recente do agente
- Reporte o problema com a data utilizada

## 📞 Suporte

- **Site da Câmara**: https://www2.camara.leg.br/
- **Documentação completa**: Veja [README.md](README.md)
- **Arquivo de configuração**: [.agent.md](.agent.md)

## ⚙️ Configurações avançadas

### Alterar pasta de destino

Edite [pauta_camara/main.py](pauta_camara/main.py) linha ~85 e mude `pautas_dir` conforme necessário.

### Alterar formato de data

Edite [pauta_camara/main.py](pauta_camara/main.py) função `format_date_iso()` para aceitar outros formatos.

### Desabilitar confirmação de download

```python
resultado = fetch_pauta_by_date("10/06/26", ".", confirm_download=False)
```

---

**Versão**: 0.2  
**Última atualização**: 2026-06-10  
**Status**: Pronto para instalação e uso
