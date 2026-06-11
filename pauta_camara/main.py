"""
Função principal do agente Pauta Câmara.

Fluxo: dada uma data (DD/MM/AA), encontra a Sessão Deliberativa do plenário
pela API de Dados Abertos, baixa a pauta já estruturada e salva em JSON e TXT.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from .fetcher import find_session_by_date, fetch_pauta_items
from .cleaner import truncate_ementa


# Mapeia a sigla do tipo (vinda da API) para um nome legível.
SIGLA_TO_NOME = {
    "PL": "Projeto de Lei",
    "PLP": "Projeto de Lei Complementar",
    "PLV": "Projeto de Lei de Conversão",
    "PEC": "Proposta de Emenda à Constituição",
    "PDL": "Projeto de Decreto Legislativo",
    "PDC": "Projeto de Decreto Legislativo",
    "MPV": "Medida Provisória",
    "MSC": "Mensagem",
    "REQ": "Requerimento",
    "EMS": "Emenda do Senado",
}


def format_date_iso(date_str: str) -> Optional[str]:
    """
    Converte DD/MM/AA para YYYYMMDD (usado no nome dos arquivos).
    Ex: '10/06/26' -> '20260610'.
    """
    try:
        dia, mes, ano = date_str.split('/')
        ano_int = int(ano)
        ano_full = 2000 + ano_int if ano_int < 50 else 1900 + ano_int
        return f"{ano_full}{mes.zfill(2)}{dia.zfill(2)}"
    except Exception:
        return None


def create_output_directory(workspace_path: str) -> str:
    """Cria/verifica o diretório pautas/."""
    pautas_dir = os.path.join(workspace_path, 'pautas')
    Path(pautas_dir).mkdir(exist_ok=True)
    return pautas_dir


def _item_para_proposicao(item: Dict, numero: int) -> Dict:
    """Converte um item cru da API no formato usado pelo agente."""
    prop = item.get("proposicao_") or {}
    sigla = prop.get("siglaTipo") or ""
    nome_tipo = SIGLA_TO_NOME.get(sigla, sigla or item.get("topico") or "Item")

    identificacao = item.get("titulo")
    if not identificacao:
        if sigla:
            identificacao = f"{sigla} {prop.get('numero')}/{prop.get('ano')}"
        else:
            identificacao = f"Item {numero}"

    ementa = (prop.get("ementa") or "").strip()
    ementa_truncada = truncate_ementa(ementa, max_length=200) if ementa else "(sem ementa)"

    relator = item.get("relator") or {}

    return {
        'numero': numero,
        'tipo': nome_tipo,
        'identificacao': identificacao,
        'ementa': ementa,
        'ementa_truncada': ementa_truncada,
        'regime': item.get("regime"),
        'relator': relator.get("nome"),
    }


def save_pauta_json(proposicoes: List[Dict], json_path: str, sessao: Dict, date_str: str) -> str:
    """Salva a pauta em JSON."""
    data = {
        'data_sessao': date_str,
        'sessao': sessao,
        'data_extracao': datetime.now().isoformat(),
        'total_itens': len(proposicoes),
        'proposicoes': proposicoes,
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON salvo: {json_path}")
    return json_path


def save_pauta_txt(proposicoes: List[Dict], txt_path: str, sessao: Dict, date_str: str) -> str:
    """Salva a pauta em TXT legível."""
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("PAUTA DA SESSÃO DELIBERATIVA\n")
        f.write(f"Data: {date_str}\n")
        if sessao.get("descricao"):
            f.write(f"Sessão: {sessao['descricao']}\n")
        f.write(f"Total de itens: {len(proposicoes)}\n")
        f.write(f"{'='*80}\n\n")

        for prop in proposicoes:
            f.write(f"{prop['numero']}. {prop['identificacao']}\n")
            f.write(f"   Tipo: {prop['tipo']}\n")
            if prop.get('regime'):
                f.write(f"   Regime: {prop['regime']}\n")
            f.write(f"   Ementa: {prop['ementa_truncada']}\n\n")
    print(f"TXT salvo: {txt_path}")
    return txt_path


def fetch_pauta_by_date(date_str: str, workspace_path: str, confirm_download: bool = True) -> Dict:
    """
    Coordena a busca da pauta de uma data (DD/MM/AA) via API.

    O parâmetro confirm_download é mantido por compatibilidade, mas não é
    mais usado: a API não exige download de PDF, então não há o que confirmar.
    """
    resultado = {
        'sucesso': False,
        'data': date_str,
        'pdf_path': None,
        'json_path': None,
        'txt_path': None,
        'proposicoes': [],
        'total': 0,
        'mensagem': '',
    }

    print(f"\n{'='*80}")
    print(f"AGENTE PAUTA CÂMARA - Buscando pauta para {date_str}")
    print(f"{'='*80}\n")

    # Passo 1: encontrar a sessão
    print(f"[1/3] Buscando sessão para {date_str}...")
    sessao = find_session_by_date(date_str)
    if not sessao:
        resultado['mensagem'] = f"Nenhuma sessão encontrada para {date_str}"
        print(f"❌ {resultado['mensagem']}")
        return resultado
    print(f"✓ Sessão encontrada: {sessao['descricao']} (evento {sessao['id']})")

    # Passo 2: buscar a pauta da sessão
    print(f"\n[2/3] Buscando pauta da sessão...")
    itens = fetch_pauta_items(sessao['id'])
    proposicoes = [_item_para_proposicao(it, i) for i, it in enumerate(itens, 1)]

    if not proposicoes:
        resultado['sucesso'] = True
        resultado['mensagem'] = "Sessão encontrada, mas a pauta está vazia (sem itens publicados)"
        print(f"⚠ {resultado['mensagem']}")
        return resultado
    print(f"✓ {len(proposicoes)} proposições na pauta")

    # Passo 3: salvar em JSON e TXT
    print(f"\n[3/3] Salvando arquivos...")
    pautas_dir = create_output_directory(workspace_path)
    date_iso = format_date_iso(date_str) or "pauta"
    json_path = os.path.join(pautas_dir, f"pauta-{date_iso}.json")
    txt_path = os.path.join(pautas_dir, f"pauta-{date_iso}.txt")

    resultado['json_path'] = save_pauta_json(proposicoes, json_path, sessao, date_str)
    resultado['txt_path'] = save_pauta_txt(proposicoes, txt_path, sessao, date_str)
    resultado['proposicoes'] = proposicoes
    resultado['total'] = len(proposicoes)
    resultado['sucesso'] = True
    resultado['mensagem'] = "Pauta processada com sucesso"

    # Resumo
    print(f"\n{'='*80}")
    print(f"RESUMO - PAUTA DE {date_str}")
    print(f"{'='*80}\n")
    for prop in proposicoes[:10]:
        print(f"{prop['numero']}. {prop['identificacao']}")
        print(f"    {prop['ementa_truncada']}\n")
    if len(proposicoes) > 10:
        print(f"... e mais {len(proposicoes) - 10} proposições")

    print(f"\n{'='*80}")
    print(f"✓ Total: {len(proposicoes)} itens")
    print(f"📄 Resumo: pauta-{date_iso}.json e .txt")
    print(f"{'='*80}\n")

    return resultado


if __name__ == "__main__":
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
        sys.exit(1)
