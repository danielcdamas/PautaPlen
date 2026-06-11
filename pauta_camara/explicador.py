"""
Gera explicações em linguagem natural para as proposições da pauta,
usando a API do Google Gemini.

A explicação só é gerada se houver uma chave de API na variável de ambiente
GEMINI_API_KEY (ou GOOGLE_API_KEY). Sem chave, esta etapa é simplesmente pulada.

Modelo padrão: gemini-2.5-flash (barato e disponível no nível gratuito).
Para usar um modelo mais capaz, defina a variável GEMINI_MODEL, por exemplo:
    GEMINI_MODEL=gemini-3.5-flash
"""

import os

MODELO = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

_PROMPT = """Você é um analista legislativo. Com base APENAS nas informações abaixo, \
escreva uma explicação clara e objetiva, em 1 ou 2 parágrafos, sobre o que propõe esta \
matéria em tramitação na Câmara dos Deputados. Use português formal e acessível: explique \
o objetivo prático da proposição e o que ela muda na lei ou na prática. NÃO invente fatos, \
números de artigos ou leis que não estejam no texto fornecido.

Identificação: {identificacao}
Ementa: {ementa}
"""

# Cache do cliente — criado uma única vez.
_client = None
_client_tentado = False


def _get_client():
    """Cria (uma vez) o cliente do Gemini, ou retorna None se não for possível."""
    global _client, _client_tentado
    if _client_tentado:
        return _client
    _client_tentado = True

    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("  (sem GEMINI_API_KEY definida — explicações desativadas)")
        return None

    try:
        from google import genai
    except ImportError:
        print("  (biblioteca 'google-genai' não instalada — explicações desativadas)")
        return None

    try:
        _client = genai.Client()  # lê GEMINI_API_KEY / GOOGLE_API_KEY do ambiente
    except Exception as e:
        print(f"  (falha ao iniciar o cliente Gemini: {e})")
        _client = None
    return _client


def explicar(identificacao: str, ementa: str):
    """
    Gera um parágrafo explicativo para uma proposição.
    Retorna o texto gerado, ou None se não foi possível (sem chave, sem ementa, erro).
    """
    if not ementa:
        return None
    client = _get_client()
    if client is None:
        return None

    prompt = _PROMPT.format(identificacao=identificacao, ementa=ementa)
    try:
        resp = client.models.generate_content(model=MODELO, contents=prompt)
        return (resp.text or "").strip() or None
    except Exception as e:
        print(f"  (falha ao gerar explicação para {identificacao}: {e})")
        return None
