"""
Busca sessões do plenário e suas pautas usando a API de Dados Abertos
da Câmara dos Deputados (https://dadosabertos.camara.leg.br).

Esta abordagem substitui o antigo web scraping do site, que era frágil
e parou de funcionar quando o layout do site mudou. A API é estável e
devolve os dados já estruturados em JSON.
"""

import io
import requests
import PyPDF2
from typing import Optional, List, Dict


API_BASE = "https://dadosabertos.camara.leg.br/api/v2"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 15


def date_br_to_iso(date_str: str) -> Optional[str]:
    """
    Converte uma data DD/MM/AA (ou DD/MM/AAAA) para AAAA-MM-DD,
    formato exigido pela API. Ex: '10/06/26' -> '2026-06-10'.
    """
    try:
        dia, mes, ano = date_str.strip().split('/')
        if len(ano) == 2:
            ano = '20' + ano  # assume século 21 (ex: 26 -> 2026)
        return f"{int(ano):04d}-{int(mes):02d}-{int(dia):02d}"
    except Exception:
        return None


def find_session_by_date(date_str: str) -> Optional[Dict]:
    """
    Procura a Sessão Deliberativa do plenário numa data (DD/MM/AA).

    Retorna um dict {'id', 'tipo', 'descricao', 'dataHoraInicio'} ou None.
    """
    iso = date_br_to_iso(date_str)
    if not iso:
        print(f"Data inválida: {date_str} (use o formato DD/MM/AA)")
        return None

    print(f"Buscando sessão do plenário para {date_str}...")
    try:
        resp = requests.get(
            f"{API_BASE}/eventos",
            params={"dataInicio": iso, "dataFim": iso, "itens": 100},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        eventos = resp.json().get("dados", [])
    except requests.RequestException as e:
        print(f"Erro ao consultar a API de eventos: {e}")
        return None

    for ev in eventos:
        tipo = ev.get("descricaoTipo") or ""
        orgaos = ev.get("orgaos") or []
        no_plenario = any(o.get("sigla") == "PLEN" for o in orgaos)
        if no_plenario and "Sessão Deliberativa" in tipo:
            return {
                "id": ev.get("id"),
                "tipo": tipo,
                "descricao": ev.get("descricao"),
                "dataHoraInicio": ev.get("dataHoraInicio"),
            }

    print(f"Nenhuma Sessão Deliberativa do plenário encontrada para {date_str}")
    return None


def fetch_pauta_items(evento_id: int) -> List[Dict]:
    """
    Busca os itens da pauta (ordem do dia) de um evento, via API.
    Retorna a lista crua de itens, como vêm da API.
    """
    try:
        resp = requests.get(
            f"{API_BASE}/eventos/{evento_id}/pauta",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("dados", [])
    except requests.RequestException as e:
        print(f"Erro ao buscar a pauta do evento {evento_id}: {e}")
        return []


def fetch_proposicao_detalhe(prop_id: int) -> Dict:
    """
    Busca os detalhes de uma proposição pela API (inclui 'ementaDetalhada'
    e 'urlInteiroTeor').
    Retorna um dict (vazio em caso de erro).
    """
    try:
        resp = requests.get(
            f"{API_BASE}/proposicoes/{prop_id}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("dados", {}) or {}
    except requests.RequestException as e:
        print(f"Erro ao buscar detalhe da proposição {prop_id}: {e}")
        return {}


def fetch_inteiro_teor_texto(url: Optional[str], max_chars: int = 12000) -> str:
    """
    Baixa o PDF do inteiro teor de uma proposição e devolve o texto extraído,
    limitado a `max_chars` caracteres (para controlar o custo da IA).
    Retorna string vazia se não houver URL ou em caso de erro.
    """
    if not url:
        return ""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  (falha ao baixar inteiro teor: {e})")
        return ""

    try:
        leitor = PyPDF2.PdfReader(io.BytesIO(resp.content))
        partes = []
        total = 0
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ""
            partes.append(texto)
            total += len(texto)
            if total >= max_chars:
                break
        return "\n".join(partes)[:max_chars].strip()
    except Exception as e:
        print(f"  (falha ao ler o PDF do inteiro teor: {e})")
        return ""


if __name__ == "__main__":
    # Teste rápido
    sessao = find_session_by_date("10/06/26")
    print("Sessão encontrada:", sessao)
    if sessao:
        itens = fetch_pauta_items(sessao["id"])
        print(f"{len(itens)} itens na pauta")
