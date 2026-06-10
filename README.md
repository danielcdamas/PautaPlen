# Agente Pauta Câmara

Agente especializado em buscar e processar pautas (ordem do dia) de sessões deliberativas da Câmara dos Deputados.

## 📋 Funcionalidades

- ✅ Busca sessões no site da Câmara por data (DD/MM/AA)
- ✅ Localiza e baixa PDF da pauta
- ✅ Extrai proposições e ementas do PDF
- ✅ Limpa e normaliza texto conforme regras definidas
- ✅ Exporta em múltiplos formatos (PDF, JSON, TXT)
- ✅ Enumera proposições de 1..n

## 🚀 Instalação

### Dependências

```bash
pip install -r requirements.txt
```

Requer Python 3.8+

## 📖 Uso

### Como linha de comando

```bash
python -m pauta_camara.main DD/MM/AA [workspace_path]
```

**Exemplo:**
```bash
python -m pauta_camara.main 10/06/26 .
```

### Como módulo Python

```python
from pauta_camara import fetch_pauta_by_date

resultado = fetch_pauta_by_date(
    date_str="10/06/26",
    workspace_path=".",
    confirm_download=True
)

if resultado['sucesso']:
    print(f"Total de proposições: {resultado['total']}")
    for prop in resultado['proposicoes']:
        print(f"{prop['numero']}. {prop['identificacao']}")
```

## 🧪 Testes

Executar suite de testes:

```bash
python test_pauta.py
```

Testes incluem:
- Limpeza de ementas (regras de Requerimentos e Projetos)
- Parsing de proposições
- Conversão de datas

## 📁 Estrutura

```
├── pauta_camara/
│   ├── __init__.py           # Exports públicos
│   ├── main.py              # Função principal (coordenação)
│   ├── fetcher.py           # Busca sessões e PDFs
│   ├── parser.py            # Extração de proposições
│   └── cleaner.py           # Limpeza de ementas
├── requirements.txt          # Dependências
├── test_pauta.py            # Suite de testes
└── pautas/                  # Saída (criado automaticamente)
    ├── pauta-20260610.pdf   # PDF baixado
    ├── pauta-20260610.json  # Proposições (JSON)
    └── pauta-20260610.txt   # Proposições (TXT legível)
```

## 📤 Formato de Saída

### JSON (`pauta-YYYYMMDD.json`)

```json
{
  "data_sessao": "10/06/26",
  "data_extracao": "2026-06-10T14:30:00",
  "total_itens": 4,
  "proposicoes": [
    {
      "numero": 1,
      "tipo": "Requerimento",
      "identificacao": "Requerimento nº 1.750, de 2023",
      "ementa_limpa": "Urgência para apreciação do Projeto de Lei nº 4.503..."
    }
  ]
}
```

### TXT (`pauta-YYYYMMDD.txt`)

```
PAUTA DA SESSÃO DELIBERATIVA
Data: 10/06/26
Total de itens: 4
================================================================================

1. Requerimento nº 1.750, de 2023
   Tipo: Requerimento
   Ementa: Urgência para apreciação do Projeto de Lei nº 4.503...

2. Projeto de Lei nº 424-B, de 2015
   Tipo: Projeto de Lei
   Ementa: Acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666...
```

## 🛠 Regras de Limpeza de Ementa

O agente aplica as seguintes transformações:

| Padrão Original | Transformação |
|---|---|
| `...regime de urgência para apreciação...` | Inicia após "regime de" |
| `Discussão, em turno único, do Projeto de Lei nº X, de YYYY, que...` | Remove prefixo, inicia após "que" |
| `...dos Srs. Líderes, que requer, nos termos do artigo 155...` | Remove prefixo administrativo |
| Ementa > 200 caracteres | Trunca com "..." |

## ⚙️ Configuração

### Formato de data

Formato esperado: **DD/MM/AA** (ex: `10/06/26`)

O agente converte automaticamente para:
- Interno: YYYYMMDD (ex: `20260610`)
- Exibição: DD/MM/AA

### Destino de arquivos

Padrão: `pautas/` no workspace (criado automaticamente se não existir)

### Confirmação de download

Por padrão, o agente solicita confirmação antes de baixar o PDF.

## 🔗 Referência do Site

- **Base URL**: https://www.camara.leg.br/plenario
- **Tipo de sessão buscado**: "Sessão Deliberativa" ou "Sessão Deliberativa Extraordinária"

## 📝 Exemplo de Saída Completa

```
================================================================================
AGENTE PAUTA CÂMARA - Buscando pauta para 10/06/26
================================================================================

[1/5] Buscando sessão para 10/06/26...
✓ Sessão encontrada: Sessão Deliberativa Extraordinária de 10/06/2026

[2/5] Buscando link da pauta na sessão...
✓ Link da pauta encontrado

[3/5] Confirmação de download:
   URL: https://www2.camara.leg.br/a/...
   Deseja baixar o PDF? (s/n): s

[4/5] Baixando PDF...
✓ PDF baixado: pauta-20260610.pdf

[5/5] Extraindo proposições...
✓ 4 proposições extraídas
JSON salvo: pauta-20260610.json
TXT salvo: pauta-20260610.txt

================================================================================
RESUMO - PAUTA DE 10/06/26
================================================================================

1. Requerimento nº 1.750, de 2023
    Urgência para apreciação do Projeto de Lei nº 4.503, de 2019, que altera...

2. Requerimento nº 5.728, de 2025
    Urgência para apreciação do Projeto de Lei nº 5.815, de 2025, que institui...

3. Projeto de Lei nº 424-B, de 2015
    Acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666, de 21 de junho de 1993...

4. Projeto de Lei nº 4.225-A, de 2023
    Dispõe sobre os direitos das pessoas com Transtorno do Déficit de Atenção...

================================================================================
✓ Total: 4 itens
📁 PDF: pauta-20260610.pdf
📄 Resumo: pauta-20260610.json e .txt
================================================================================
```

## 🐛 Troubleshooting

### "Nenhuma sessão encontrada para DD/MM/AA"

- Verifique se a data está no formato correto (DD/MM/AA)
- A sessão pode não ter sido publicada naquele dia
- Tente uma data próxima (dia anterior/próximo)

### "Não foi possível encontrar o link da pauta"

- O layout do site pode ter mudado
- A pauta pode estar em um formato diferente (HTML vs PDF)

### Erro ao baixar PDF

- Verifique conexão com a internet
- A URL do PDF pode estar indisponível
- Tente novamente em alguns minutos

## 📞 Suporte

Para questões sobre o site da Câmara, visite: https://www2.camara.leg.br/

## 📄 Licença

Este agente é fornecido para fins de pesquisa e acesso a informações públicas.

---

**Versão**: 0.2  
**Última atualização**: 2026-06-10
