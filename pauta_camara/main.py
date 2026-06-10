"""
Função principal do agente Pauta Câmara
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from .fetcher import find_session_by_date, CamaraFetcher
from .parser import parse_pauta_file, PautaParser
from .cleaner import truncate_ementa


def format_date_iso(date_str: str) -> str:
    """
    Converte DD/MM/AA para YYYYMMDD (formato interno).
    """
    try:
        parts = date_str.split('/')
        day, month, year = parts[0], parts[1], parts[2]
        
        # Converter AA para YYYY
        year_int = int(year)
        if year_int < 50:
            year_full = 2000 + year_int
        else:
            year_full = 1900 + year_int
        
        return f"{year_full}{month.zfill(2)}{day.zfill(2)}"
    except:
        return None


def create_output_directory(workspace_path: str) -> str:
    """
    Cria/verifica existência do diretório pautas/.
    """
    pautas_dir = os.path.join(workspace_path, 'pautas')
    Path(pautas_dir).mkdir(exist_ok=True)
    return pautas_dir


def save_pauta_json(proposicoes: List[Dict], output_path: str, date_str: str) -> str:
    """
    Salva proposições em formato JSON.
    """
    data = {
        'data_sessao': date_str,
        'data_extracao': datetime.now().isoformat(),
        'total_itens': len(proposicoes),
        'proposicoes': [
            {
                'numero': p['numero'],
                'tipo': p['tipo'],
                'identificacao': p['identificacao'],
                'ementa_limpa': p['ementa_truncada']
            }
            for p in proposicoes
        ]
    }
    
    json_path = output_path.replace('.pdf', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON salvo: {json_path}")
    return json_path


def save_pauta_txt(proposicoes: List[Dict], output_path: str, date_str: str) -> str:
    """
    Salva proposições em formato TXT legível.
    """
    txt_path = output_path.replace('.pdf', '.txt')
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"PAUTA DA SESSÃO DELIBERATIVA\n")
        f.write(f"Data: {date_str}\n")
        f.write(f"Total de itens: {len(proposicoes)}\n")
        f.write(f"{'='*80}\n\n")
        
        for prop in proposicoes:
            f.write(f"{prop['numero']}. {prop['identificacao']}\n")
            f.write(f"   Tipo: {prop['tipo']}\n")
            f.write(f"   Ementa: {prop['ementa_truncada']}\n\n")
    
    print(f"TXT salvo: {txt_path}")
    return txt_path


def fetch_pauta_by_date(date_str: str, workspace_path: str, confirm_download: bool = True) -> Optional[Dict]:
    """
    Função principal que coordena a busca e download da pauta.
    
    Args:
        date_str: Data no formato DD/MM/AA (ex: 10/06/26)
        workspace_path: Caminho do workspace/projeto
        confirm_download: Se True, solicita confirmação antes de baixar
    
    Returns:
        Dict com resultado: {
            'sucesso': bool,
            'data': str,
            'pdf_path': str,
            'json_path': str,
            'txt_path': str,
            'proposicoes': List[Dict],
            'total': int,
            'mensagem': str
        }
    """
    
    resultado = {
        'sucesso': False,
        'data': date_str,
        'pdf_path': None,
        'json_path': None,
        'txt_path': None,
        'proposicoes': [],
        'total': 0,
        'mensagem': ''
    }
    
    print(f"\n{'='*80}")
    print(f"AGENTE PAUTA CÂMARA - Buscando pauta para {date_str}")
    print(f"{'='*80}\n")
    
    # Passo 1: Buscar sessão
    print(f"[1/5] Buscando sessão para {date_str}...")
    session = find_session_by_date(date_str)
    
    if not session:
        resultado['mensagem'] = f"Nenhuma sessão encontrada para {date_str}"
        print(f"❌ {resultado['mensagem']}")
        return resultado
    
    print(f"✓ Sessão encontrada: {session['tipo']}")
    
    # Passo 2: Buscar página da sessão e link da pauta
    print(f"\n[2/5] Buscando link da pauta na sessão...")
    fetcher = CamaraFetcher()
    session_html = fetcher.fetch_session_page(session['link'])
    
    if not session_html:
        resultado['mensagem'] = "Não foi possível buscar a página da sessão"
        print(f"❌ {resultado['mensagem']}")
        return resultado
    
    pauta_url = fetcher.find_pauta_pdf_link(session_html)
    if not pauta_url:
        resultado['mensagem'] = "Não foi possível encontrar o link da pauta"
        print(f"❌ {resultado['mensagem']}")
        return resultado
    
    print(f"✓ Link da pauta encontrado")
    
    # Passo 3: Confirmar download
    if confirm_download:
        print(f"\n[3/5] Confirmação de download:")
        print(f"   URL: {pauta_url}")
        response = input("   Deseja baixar o PDF? (s/n): ").strip().lower()
        if response != 's':
            resultado['mensagem'] = "Download cancelado pelo usuário"
            print(f"⚠ {resultado['mensagem']}")
            return resultado
    
    # Passo 4: Baixar PDF
    print(f"\n[4/5] Baixando PDF...")
    pautas_dir = create_output_directory(workspace_path)
    date_iso = format_date_iso(date_str)
    pdf_filename = f"pauta-{date_iso}.pdf"
    pdf_path = os.path.join(pautas_dir, pdf_filename)
    
    if not fetcher.download_pdf(pauta_url, pdf_path):
        resultado['mensagem'] = "Falha ao baixar o PDF"
        print(f"❌ {resultado['mensagem']}")
        return resultado
    
    resultado['pdf_path'] = pdf_path
    print(f"✓ PDF baixado: {pdf_filename}")
    
    # Passo 5: Parsear e extrair proposições
    print(f"\n[5/5] Extraindo proposições...")
    proposicoes = parse_pauta_file(pdf_path)
    
    if not proposicoes:
        resultado['mensagem'] = "Nenhuma proposição encontrada no PDF"
        print(f"⚠ {resultado['mensagem']}")
    else:
        print(f"✓ {len(proposicoes)} proposições extraídas")
        
        # Salvar em JSON e TXT
        resultado['json_path'] = save_pauta_json(proposicoes, pdf_path, date_str)
        resultado['txt_path'] = save_pauta_txt(proposicoes, pdf_path, date_str)
    
    resultado['proposicoes'] = proposicoes
    resultado['total'] = len(proposicoes)
    resultado['sucesso'] = True
    resultado['mensagem'] = "Pauta processada com sucesso"
    
    # Exibir resumo
    print(f"\n{'='*80}")
    print(f"RESUMO - PAUTA DE {date_str}")
    print(f"{'='*80}\n")
    
    for prop in proposicoes[:10]:  # Mostrar primeiras 10
        print(f"{prop['numero']}. {prop['identificacao']}")
        print(f"    {prop['ementa_truncada']}\n")
    
    if len(proposicoes) > 10:
        print(f"... e {len(proposicoes) - 10} proposições mais")
    
    print(f"\n{'='*80}")
    print(f"✓ Total: {len(proposicoes)} itens")
    print(f"📁 PDF: {pdf_filename}")
    print(f"📄 Resumo: pauta-{date_iso}.json e .txt")
    print(f"{'='*80}\n")
    
    return resultado


if __name__ == "__main__":
    # Teste
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python -m pauta_camara.main DD/MM/AA [workspace_path]")
        print("Exemplo: python -m pauta_camara.main 10/06/26 .")
        sys.exit(1)
    
    date_str = sys.argv[1]
    workspace_path = sys.argv[2] if len(sys.argv) > 2 else "."
    
    resultado = fetch_pauta_by_date(date_str, workspace_path)
    
    if resultado['sucesso']:
        print("\n✓ Sucesso! Verifique a pasta pautas/")
    else:
        print(f"\n❌ Erro: {resultado['mensagem']}")
