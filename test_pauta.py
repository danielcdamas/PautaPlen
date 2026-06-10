#!/usr/bin/env python
"""
Script de teste para o Agente Pauta Câmara
Testa a limpeza de ementas, parsing e busca de sessões
"""

import sys
from pauta_camara.cleaner import clean_ementa, extract_proposicao_info, truncate_ementa


def test_cleaner():
    """
    Testa o módulo de limpeza de texto.
    """
    print("\n" + "="*80)
    print("TESTE 1: LIMPEZA DE EMENTAS")
    print("="*80 + "\n")
    
    test_cases = [
        {
            'input': "Requerimento nº 1.750, de 2023, dos Srs. Líderes, que requer, nos termos do artigo 155 do Regimento Interno da Câmara dos Deputados, regime de urgência para apreciação do Projeto de Lei nº 4.503, de 2019, que altera o Decreto-Lei nº 2.848, de 7 de dezembro de 1940.",
            'label': 'Requerimento de Urgência'
        },
        {
            'input': "Discussão, em turno único, do Projeto de Lei nº 424-B, de 2015, que acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666, de 21 de junho de 1993.",
            'label': 'Projeto de Lei'
        },
        {
            'input': "Discussão, em turno único, do Projeto de Decreto Legislativo nº 51-A, de 2011, que altera a Lei nº 10.962, de 15 de dezembro de 2004.",
            'label': 'Decreto Legislativo'
        },
        {
            'input': "Requerimento nº 5.728, de 2025, dos Srs. Líderes, que requer regime de urgência para apreciação do Projeto de Lei nº 5.815, de 2025, que institui o Programa Nacional de Acompanhamento Anual Pediátrico.",
            'label': 'Requerimento PNAPE'
        }
    ]
    
    for case in test_cases:
        print(f"📋 {case['label']}")
        print(f"Original:  {case['input'][:100]}...")
        cleaned = clean_ementa(case['input'])
        print(f"Limpo:     {cleaned[:100]}...")
        
        tipo, id_prop = extract_proposicao_info(case['input'])
        print(f"Tipo:      {tipo}")
        print(f"ID:        {id_prop}")
        
        truncated = truncate_ementa(cleaned, max_length=150)
        print(f"Truncado:  {truncated}\n")


def test_parser():
    """
    Testa o módulo de parsing.
    """
    print("\n" + "="*80)
    print("TESTE 2: PARSING DE PROPOSIÇÕES")
    print("="*80 + "\n")
    
    from pauta_camara.parser import PautaParser
    
    test_text = """
    PAUTA DA SESSÃO DELIBERATIVA DE 10/06/2026
    
    1. Requerimento nº 1.750, de 2023
    Urgência para apreciação do Projeto de Lei nº 4.503, de 2019, que altera o Decreto-Lei nº 2.848, de 7 de dezembro de 1940 - Código Penal.
    
    2. Requerimento nº 5.728, de 2025
    Urgência para apreciação do Projeto de Lei nº 5.815, de 2025, que institui o Programa Nacional de Acompanhamento Anual Pediátrico.
    
    3. Projeto de Lei nº 424-B, de 2015
    Acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666, de 21 de junho de 1993, permitindo a dispensa de licitação para aquisição de hemoderivados.
    """
    
    proposicoes = PautaParser._parse_proposicoes(test_text)
    
    print(f"✓ {len(proposicoes)} proposições encontradas\n")
    
    for prop in proposicoes:
        print(f"  {prop['numero']}. {prop['identificacao']}")
        print(f"     Tipo: {prop['tipo']}")
        print(f"     Ementa: {prop['ementa_truncada']}\n")


def test_date_conversion():
    """
    Testa conversão de datas.
    """
    print("\n" + "="*80)
    print("TESTE 3: CONVERSÃO DE DATAS")
    print("="*80 + "\n")
    
    from pauta_camara.main import format_date_iso
    
    test_dates = [
        "10/06/26",
        "15/12/25",
        "01/01/00",
        "31/12/99"
    ]
    
    for date_str in test_dates:
        iso = format_date_iso(date_str)
        print(f"{date_str} → {iso}")


def run_all_tests():
    """
    Executa todos os testes.
    """
    print("\n" + "="*80)
    print("TESTES DO AGENTE PAUTA CÂMARA")
    print("="*80)
    
    try:
        test_cleaner()
        test_parser()
        test_date_conversion()
        
        print("\n" + "="*80)
        print("✓ TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
