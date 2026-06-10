#!/usr/bin/env python
"""
Interface CLI interativa para o Agente Pauta Câmara
Permite buscar pautas de forma simples e intuitiva
"""

import os
import sys
from datetime import datetime, timedelta
from pauta_camara.main import fetch_pauta_by_date


def get_date_input(prompt: str = "Data (DD/MM/AA): ") -> str:
    """
    Solicita entrada de data do usuário com validação.
    """
    while True:
        date_input = input(prompt).strip()
        
        if date_input.lower() in ['hoje', '0', '']:
            # Usar data de hoje
            today = datetime.now()
            date_input = today.strftime('%d/%m/%y')
            print(f"Usando data de hoje: {date_input}")
            return date_input
        
        if date_input.lower() == 'ontem':
            # Usar data de ontem
            yesterday = datetime.now() - timedelta(days=1)
            date_input = yesterday.strftime('%d/%m/%y')
            print(f"Usando data de ontem: {date_input}")
            return date_input
        
        # Validar formato DD/MM/AA
        parts = date_input.split('/')
        if len(parts) == 3 and len(parts[0]) <= 2 and len(parts[1]) <= 2 and len(parts[2]) <= 2:
            return date_input
        
        print("❌ Formato inválido. Use DD/MM/AA (ex: 10/06/26) ou 'hoje', 'ontem'")


def display_menu():
    """
    Exibe menu principal.
    """
    print("\n" + "="*80)
    print("AGENTE PAUTA CÂMARA - Menu Principal")
    print("="*80)
    print("\n1. Buscar pauta por data")
    print("2. Listar pautas baixadas")
    print("3. Sobre este agente")
    print("4. Sair")
    print()


def list_downloaded_pautas(workspace_path: str = "."):
    """
    Lista todas as pautas já baixadas.
    """
    pautas_dir = os.path.join(workspace_path, 'pautas')
    
    if not os.path.exists(pautas_dir):
        print("\n❌ Nenhuma pauta foi baixada ainda.\n")
        return
    
    print("\n" + "="*80)
    print("PAUTAS DISPONÍVEIS")
    print("="*80 + "\n")
    
    pdfs = [f for f in os.listdir(pautas_dir) if f.endswith('.pdf')]
    
    if not pdfs:
        print("❌ Nenhum PDF encontrado na pasta pautas/\n")
        return
    
    for i, pdf in enumerate(sorted(pdfs), 1):
        pdf_path = os.path.join(pautas_dir, pdf)
        size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        date_modified = datetime.fromtimestamp(os.path.getmtime(pdf_path))
        
        # Tentar extrair data do nome
        date_str = pdf.replace('pauta-', '').replace('.pdf', '')
        if len(date_str) == 8:  # YYYYMMDD
            date_str = f"{date_str[6:8]}/{date_str[4:6]}/{date_str[2:4]}"
        
        print(f"{i}. {pdf}")
        print(f"   Data: {date_str} | Tamanho: {size_mb:.2f} MB | Modificado: {date_modified.strftime('%d/%m/%Y %H:%M')}")
        
        # Mostrar resumo se existir
        txt_path = pdf_path.replace('.pdf', '.txt')
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Procurar linha "Total de itens: X"
                for line in lines:
                    if 'Total de itens:' in line:
                        print(f"   {line.strip()}")
                        break
        print()


def show_about():
    """
    Exibe informações sobre o agente.
    """
    print("\n" + "="*80)
    print("SOBRE O AGENTE PAUTA CÂMARA")
    print("="*80 + "\n")
    
    print("Versão: 0.2")
    print("Propósito: Buscar e processar pautas de sessões deliberativas da Câmara dos Deputados")
    print()
    print("Funcionalidades:")
    print("  ✓ Busca sessões por data (DD/MM/AA)")
    print("  ✓ Localiza e baixa PDF da pauta")
    print("  ✓ Extrai proposições e ementas")
    print("  ✓ Limpa e normaliza texto conforme regras")
    print("  ✓ Exporta em múltiplos formatos (PDF, JSON, TXT)")
    print()
    print("Site de origem: https://www.camara.leg.br/plenario")
    print()
    print("Para mais informações, veja README.md")
    print()


def main():
    """
    Loop principal da CLI.
    """
    workspace_path = os.getcwd()
    
    print("\n" + "="*80)
    print("BEM-VINDO AO AGENTE PAUTA CÂMARA")
    print("="*80)
    print("\nWorkspace: " + workspace_path)
    print()
    
    while True:
        display_menu()
        choice = input("Escolha uma opção (1-4): ").strip()
        
        if choice == '1':
            # Buscar pauta por data
            print()
            date_str = get_date_input()
            
            # Confirmar
            confirm = input(f"\nBuscar pauta para {date_str}? (s/n): ").strip().lower()
            if confirm != 's':
                print("Cancelado.\n")
                continue
            
            # Executar busca
            resultado = fetch_pauta_by_date(date_str, workspace_path, confirm_download=True)
            
            if resultado['sucesso']:
                input("\nPressione Enter para continuar...")
            else:
                input(f"\n❌ {resultado['mensagem']}\nPressione Enter para continuar...")
        
        elif choice == '2':
            # Listar pautas
            list_downloaded_pautas(workspace_path)
            input("Pressione Enter para continuar...")
        
        elif choice == '3':
            # Sobre
            show_about()
            input("Pressione Enter para continuar...")
        
        elif choice == '4':
            print("\nEncerrando... Até logo!\n")
            sys.exit(0)
        
        else:
            print("❌ Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
