"""
Módulo de limpeza e normalização de ementas
"""

import re
from typing import Tuple


def clean_ementa(text: str) -> str:
    """
    Limpa e normaliza ementas de proposições conforme as regras definidas.
    
    Regras:
    - Para Requerimentos de Urgência: cortar até "regime de"
    - Para Projetos de Lei/Decretos: remover "Discussão, em turno único, do Projeto de..."
    - Remover prefixos desnecessários: "dos Srs. Líderes", "que requer", etc.
    """
    if not text:
        return ""
    
    text = text.strip()
    
    # Regra 1: Requerimentos de Urgência - extrair depois de "regime de"
    if "regime de" in text.lower():
        # Encontrar "regime de" case-insensitive
        match = re.search(r'regime\s+de\s+', text, re.IGNORECASE)
        if match:
            text = text[match.end():].strip()
    
    # Regra 2: Remover padrão "Discussão, em turno único, do Projeto de..."
    # Exemplo: "Discussão, em turno único, do Projeto de Lei nº 424-B, de 2015, que"
    text = re.sub(
        r'^Discussão,?\s*em\s+turno\s+único,?\s*do\s+Projeto\s+de\s+(Lei|Decreto\s+Legislativo)\s+nº?\s*[\d\w\-\.]+,?\s*de\s+\d{4},?\s+que\s+',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Regra 3: Remover prefixos desnecessários
    # "dos Srs. Líderes, que requer, nos termos do artigo 155..."
    text = re.sub(
        r'^dos\s+Srs\.?\s+Líderes,?\s+que\s+requer,?\s+nos\s+termos\s+do\s+artigo\s+\d+.*?[,;]\s*',
        '',
        text,
        flags=re.IGNORECASE
    )
    
    # Limpar espaços múltiplos
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def truncate_ementa(text: str, max_length: int = 200) -> str:
    """
    Trunca ementa se exceder max_length, adicionando '...'
    """
    if len(text) > max_length:
        # Encontrar última palavra completa dentro do limite
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated.rstrip(',.;:') + '...'
    return text


def extract_proposicao_info(text: str) -> Tuple[str, str]:
    """
    Extrai tipo e identificação da proposição (ex: "Requerimento nº 1.750, de 2023").
    Retorna: (tipo, identificacao)
    """
    # Padrões comuns
    patterns = [
        (r'(Requerimento)\s+nº?\s*([\d\.]+),?\s+de\s+(\d{4})', 'Requerimento'),
        (r'(Projeto\s+de\s+Lei)\s+nº?\s*([\d\w\-\.]+),?\s+de\s+(\d{4})', 'Projeto de Lei'),
        (r'(Projeto\s+de\s+Decreto\s+Legislativo)\s+nº?\s*([\d\w\-\.]+),?\s+de\s+(\d{4})', 'Projeto de Decreto Legislativo'),
    ]
    
    for pattern, tipo in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            identificacao = match.group(0)
            return tipo, identificacao
    
    return "Proposição", text[:50]


if __name__ == "__main__":
    # Testes rápidos
    test_texts = [
        "Urgência para apreciação do Projeto de Lei nº 4.503, de 2019, que altera o Decreto-Lei...",
        "Discussão, em turno único, do Projeto de Lei nº 424-B, de 2015, que acrescenta...",
        "Requerimento nº 1.750, de 2023, dos Srs. Líderes, que requer, nos termos do artigo 155...",
    ]
    
    for text in test_texts:
        cleaned = clean_ementa(text)
        print(f"Original: {text[:80]}...")
        print(f"Limpo:    {cleaned[:80]}...")
        print()
