"""
Módulo para parsing de PDF e HTML da pauta
"""

import PyPDF2
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from .cleaner import clean_ementa, extract_proposicao_info, truncate_ementa


class PautaParser:
    """
    Extrai proposições e ementas do PDF ou HTML da pauta.
    """
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> List[Dict]:
        """
        Extrai texto do PDF e parseia para encontrar proposições.
        """
        proposicoes = []
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                full_text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    full_text += page.extract_text()
            
            proposicoes = PautaParser._parse_proposicoes(full_text)
        
        except Exception as e:
            print(f"Erro ao ler PDF ({pdf_path}): {e}")
        
        return proposicoes
    
    @staticmethod
    def extract_from_html(html: str) -> List[Dict]:
        """
        Extrai proposições de um HTML da pauta.
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text('\n')
        return PautaParser._parse_proposicoes(text)
    
    @staticmethod
    def _parse_proposicoes(text: str) -> List[Dict]:
        """
        Faz parsing do texto bruto para encontrar proposições e ementas.
        
        Padrões procurados:
        - Requerimento nº X, de YYYY
        - Projeto de Lei nº X, de YYYY
        - Projeto de Decreto Legislativo nº X, de YYYY
        """
        proposicoes = []
        
        if not text:
            return proposicoes
        
        # Dividir texto em blocos usando regex para identificar proposições
        # Padrão: tipo + numero + ano + resto do texto até a próxima proposição
        pattern = r'((?:Requerimento|Projeto\s+de\s+(?:Lei|Decreto\s+Legislativo))\s+nº?\s*[\d\w\-\.]+,?\s+de\s+\d{4}[^\n]*(?:\n(?!(?:Requerimento|Projeto|PROJETO|REQUERIMENTO))[^\n]*)*)'
        
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        numero = 1
        
        for match in matches:
            proposicao_text = match.group(1).strip()
            
            if proposicao_text:
                # Extrair tipo e identificação
                tipo, identificacao = extract_proposicao_info(proposicao_text)
                
                # Limpar ementa
                ementa = clean_ementa(proposicao_text)
                
                # Truncar se necessário
                ementa_truncada = truncate_ementa(ementa, max_length=200)
                
                proposicoes.append({
                    'numero': numero,
                    'tipo': tipo,
                    'identificacao': identificacao,
                    'ementa': ementa,
                    'ementa_truncada': ementa_truncada,
                    'texto_bruto': proposicao_text[:500]  # Manter para debug
                })
                
                numero += 1
        
        return proposicoes


def parse_pauta_file(file_path: str) -> List[Dict]:
    """
    Wrapper que detecta se é PDF ou HTML e faz parsing apropriado.
    """
    if file_path.endswith('.pdf'):
        return PautaParser.extract_from_pdf(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()
            return PautaParser.extract_from_html(html)
        except Exception as e:
            print(f"Erro ao ler arquivo ({file_path}): {e}")
            return []


if __name__ == "__main__":
    # Teste com arquivo de exemplo
    test_text = """
    Requerimento nº 1.750, de 2023
    Urgência para apreciação do Projeto de Lei nº 4.503, de 2019, que altera o Decreto-Lei nº 2.848, de 7 de dezembro de 1940.
    
    Projeto de Lei nº 424-B, de 2015
    Acrescenta o Inciso XXXII ao art. 24 da Lei nº 8.666, de 21 de junho de 1993, e altera o art. 3º da Lei nº 10.972.
    """
    
    proposicoes = PautaParser._parse_proposicoes(test_text)
    for prop in proposicoes:
        print(f"{prop['numero']}. {prop['identificacao']}")
        print(f"   {prop['ementa_truncada']}\n")
