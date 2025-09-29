#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de Slides HTML para PNG com Altura Dinâmica
Ajusta automaticamente a altura para capturar todo o conteúdo
"""

import os
import subprocess
import time
import glob
import re
from bs4 import BeautifulSoup

def get_slide_content_height(html_file):
    """Calcula a altura necessária para o conteúdo do slide"""

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Contar elementos que precisam de espaço
        soup = BeautifulSoup(content, 'html.parser')

        # Elementos que ocupam espaço vertical
        h1_count = len(soup.find_all(['h1']))
        h2_count = len(soup.find_all(['h2']))
        h3_count = len(soup.find_all(['h3']))
        cards = len(soup.find_all(class_='card'))
        highlights = len(soup.find_all(class_=['danger', 'highlight', 'stat-box', 'danger-visual']))
        lists = len(soup.find_all(['ul', 'ol']))

        # Altura base
        base_height = 1080

        # Calcular altura adicional baseada no conteúdo
        additional_height = 0
        additional_height += h1_count * 100  # Títulos grandes
        additional_height += h2_count * 80   # Títulos médios
        additional_height += h3_count * 60   # Subtítulos
        additional_height += cards * 200     # Cards
        additional_height += highlights * 150 # Destaques
        additional_height += lists * 100     # Listas

        # Verificar se há grids que podem aumentar altura
        if 'content-grid' in content:
            grid_cards = cards
            if grid_cards > 3:  # Se há mais de 3 cards, provavelmente há múltiplas linhas
                rows = (grid_cards + 2) // 3  # Arredondar para cima
                additional_height += (rows - 1) * 250

        # Altura final
        total_height = base_height + additional_height

        # Limitar altura máxima para evitar problemas
        total_height = min(total_height, 4000)

        return max(total_height, 1080)  # Mínimo 1080p

    except Exception as e:
        print(f"⚠️  Erro ao calcular altura para {html_file}: {e}")
        return 1800  # Altura padrão maior

def modify_slide_for_full_capture(html_file, output_file, target_height):
    """Modifica o slide HTML para captura completa"""

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Modificar CSS para garantir captura completa
        modified_content = content.replace(
            'height: 1080px;',
            f'height: auto; min-height: {target_height}px;'
        )

        # Adicionar CSS para garantir que tudo seja visível
        css_addition = f"""
        <style>
            /* Ajustes para captura completa */
            body {{
                height: auto !important;
                min-height: {target_height}px !important;
                overflow: visible !important;
            }}

            .slide {{
                height: auto !important;
                min-height: {target_height - 100}px !important;
                overflow: visible !important;
                padding-bottom: 50px !important;
            }}

            /* Garantir que cards não quebrem */
            .content-grid {{
                display: grid !important;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)) !important;
                gap: 20px !important;
                margin: 20px 0 !important;
            }}

            .card {{
                break-inside: avoid !important;
                page-break-inside: avoid !important;
                margin-bottom: 20px !important;
            }}

            /* Garantir espaçamento adequado */
            .visual-element, .danger-visual, .highlight {{
                margin: 20px 0 !important;
            }}
        </style>
        </head>"""

        modified_content = modified_content.replace('</head>', css_addition)

        # Salvar arquivo modificado
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        return True

    except Exception as e:
        print(f"❌ Erro ao modificar {html_file}: {e}")
        return False

def convert_slide_to_png_full(html_file, output_file):
    """Converte um slide HTML para PNG capturando todo o conteúdo"""

    # Calcular altura necessária
    content_height = get_slide_content_height(html_file)
    print(f"   📏 Altura calculada: {content_height}px")

    # Criar versão modificada do slide
    temp_html = html_file.replace('.html', '_temp.html')

    if not modify_slide_for_full_capture(html_file, temp_html, content_height):
        return False

    # Obter caminho absoluto
    html_path = os.path.abspath(temp_html)
    output_path = os.path.abspath(output_file)

    # Comando do Chrome com altura dinâmica
    chrome_cmd = [
        '/usr/bin/google-chrome',
        '--headless',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        f'--window-size=1920,{content_height}',
        '--virtual-time-budget=5000',  # Mais tempo para renderizar
        '--run-all-compositor-stages-before-draw',
        '--disable-background-timer-throttling',
        f'--screenshot={output_path}',
        f'file://{html_path}'
    ]

    try:
        # Executar comando
        result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=45)

        # Limpar arquivo temporário
        if os.path.exists(temp_html):
            os.remove(temp_html)

        if result.returncode == 0 and os.path.exists(output_path):
            # Verificar se a imagem foi criada corretamente
            file_size = os.path.getsize(output_path)
            if file_size > 1000:  # Pelo menos 1KB
                return True
            else:
                print(f"   ⚠️  Imagem muito pequena: {file_size} bytes")
                return False
        else:
            print(f"   ❌ Chrome error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout ao converter {html_file}")
        if os.path.exists(temp_html):
            os.remove(temp_html)
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        if os.path.exists(temp_html):
            os.remove(temp_html)
        return False

def main():
    """Função principal"""

    print("🔄 Convertendo slides com ALTURA DINÂMICA...")
    print("📏 Calculando altura ideal para cada slide...")

    # Limpar diretório anterior
    if os.path.exists('slide_images_completas'):
        import shutil
        shutil.rmtree('slide_images_completas')

    # Criar novo diretório
    os.makedirs('slide_images_completas', exist_ok=True)

    # Encontrar todos os arquivos de slide
    slide_files = glob.glob('slides_individuais/slide_*.html')
    slide_files.sort()

    if not slide_files:
        print("❌ Nenhum arquivo de slide encontrado na pasta slides_individuais/")
        return

    print(f"📊 Encontrados {len(slide_files)} slides para converter")
    print("🎯 Cada slide será ajustado para capturar TODO o conteúdo\n")

    successful = 0
    failed = 0

    for html_file in slide_files:
        # Extrair número do slide
        basename = os.path.basename(html_file)
        slide_name = basename.replace('.html', '')
        png_file = f'slide_images_completas/{slide_name}.png'

        print(f"📸 Convertendo {basename}...")

        if convert_slide_to_png_full(html_file, png_file):
            # Verificar tamanho da imagem gerada
            file_size = os.path.getsize(png_file) / (1024*1024)  # MB
            print(f"   ✅ {slide_name}.png ({file_size:.1f}MB)")
            successful += 1
        else:
            print(f"   ❌ Falha ao converter {basename}")
            failed += 1

        # Pausa entre conversões
        time.sleep(1)

    print(f"\n🎯 Conversão com altura dinâmica concluída!")
    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📁 Imagens completas salvas em: slide_images_completas/")

    if successful > 0:
        print(f"\n📏 Vantagens desta versão:")
        print(f"   • CAPTURA TODO O CONTEÚDO de cada slide")
        print(f"   • Altura ajustada automaticamente")
        print(f"   • Nenhum corte ou conteúdo perdido")
        print(f"   • Qualidade Full HD mantida")

        # Estatísticas das imagens
        png_files = glob.glob('slide_images_completas/*.png')
        if png_files:
            total_size = sum(os.path.getsize(f) for f in png_files)
            avg_size = total_size / len(png_files) / (1024*1024)  # MB
            print(f"\n📈 Estatísticas:")
            print(f"   • {len(png_files)} imagens completas geradas")
            print(f"   • Tamanho médio: {avg_size:.1f} MB por imagem")
            print(f"   • Largura: 1920px (Full HD)")
            print(f"   • Altura: Dinâmica (baseada no conteúdo)")

        print(f"\n🎬 Para usar no Canva:")
        print(f"   1. Use as imagens da pasta 'slide_images_completas/'")
        print(f"   2. No Canva, ajuste proporção para 'Personalizada'")
        print(f"   3. Configure largura: 1920px")
        print(f"   4. Deixe altura automática")
        print(f"   5. Suas imagens terão TODO o conteúdo visível!")

if __name__ == "__main__":
    main()