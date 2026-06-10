"""
Módulo para buscar sessões e pautas no site da Câmara dos Deputados
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from datetime import datetime
import re


class CamaraFetcher:
    BASE_URL = "https://www.camara.leg.br/plenario"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def fetch_sessions_page(self) -> Optional[str]:
        """
        Busca a página principal do plenário e retorna o HTML.
        """
        try:
            response = self.session.get(self.BASE_URL, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erro ao buscar página de sessões: {e}")
            return None
    
    def parse_sessions(self, html: str, date_str: str) -> List[Dict]:
        """
        Faz parsing do HTML da página de sessões e busca por uma data específica.
        date_str formato: DD/MM/AA (ex: 10/06/26)
        
        Retorna lista de dicts com: {'data': '10/06/26', 'tipo': 'Sessão Deliberativa', 'link': '...'}
        """
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        sessions = []
        
        # Procura por links e títulos que mencionem "Sessão Deliberativa"
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link.get('href')
            
            # Procura por padrão de data DD/MM/YYYY ou DD/MM/AA
            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', text)
            if date_match:
                found_date = date_match.group(0)
                # Normalizar: converter YYYY para AA se necessário
                parts = found_date.split('/')
                if len(parts[2]) == 4:
                    # Converter 2026 para 26
                    parts[2] = parts[2][-2:]
                normalized_date = '/'.join(parts)
                
                if normalized_date == date_str and "Sessão Deliberativa" in text:
                    sessions.append({
                        'data': normalized_date,
                        'tipo': text,
                        'link': href if href.startswith('http') else self.BASE_URL + href
                    })
        
        return sessions
    
    def fetch_session_page(self, session_url: str) -> Optional[str]:
        """
        Busca a página de uma sessão específica.
        """
        try:
            response = self.session.get(session_url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erro ao buscar página de sessão ({session_url}): {e}")
            return None
    
    def find_pauta_pdf_link(self, session_html: str) -> Optional[str]:
        """
        Busca o link para o PDF da pauta dentro da página de sessão.
        """
        if not session_html:
            return None
        
        soup = BeautifulSoup(session_html, 'html.parser')
        
        # Procura por links que contenham "pauta", "ordem", "pdf"
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True).lower()
            href = link.get('href', '').lower()
            
            if any(keyword in text or keyword in href for keyword in ['pauta', 'ordem do dia']):
                full_url = link.get('href')
                if full_url and not full_url.startswith('http'):
                    full_url = self.BASE_URL + full_url
                return full_url
        
        return None
    
    def download_pdf(self, pdf_url: str, output_path: str) -> bool:
        """
        Baixa um PDF e salva em output_path.
        """
        try:
            response = self.session.get(pdf_url, timeout=self.timeout)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"PDF baixado com sucesso: {output_path}")
            return True
        except requests.RequestException as e:
            print(f"Erro ao baixar PDF ({pdf_url}): {e}")
            return False


def find_session_by_date(date_str: str) -> Optional[Dict]:
    """
    Função principal: busca uma sessão pela data (DD/MM/AA).
    Retorna dict com: {'data': '...', 'tipo': '...', 'link': '...'}
    """
    fetcher = CamaraFetcher()
    
    print(f"Buscando sessões para {date_str}...")
    html = fetcher.fetch_sessions_page()
    if not html:
        return None
    
    sessions = fetcher.parse_sessions(html, date_str)
    
    if not sessions:
        print(f"Nenhuma sessão encontrada para {date_str}")
        return None
    
    if len(sessions) > 1:
        print(f"Múltiplas sessões encontradas para {date_str}:")
        for i, s in enumerate(sessions, 1):
            print(f"  {i}. {s['tipo']}")
        print("Usando a primeira sessão encontrada.")
    
    return sessions[0]


if __name__ == "__main__":
    # Teste
    session = find_session_by_date("10/06/26")
    if session:
        print(f"Sessão encontrada: {session}")
