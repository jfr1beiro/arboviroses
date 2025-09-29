#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção Rápida para Slides Completos
Modifica cada slide para ter altura maior e captura completa
"""

import os
import subprocess
import glob
import time

def fix_slide_html(html_file, output_file):
    """Modifica o HTML do slide para captura completa"""

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substituir altura fixa por altura automática
        fixed_content = content.replace(
            'height: 1080px;',
            'height: auto; min-height: 1500px;'
        ).replace(
            'width: 1920px;\n            height: 1080px;',
            'width: 1920px;\n            height: auto;\n            min-height: 1800px;'
        )

        # Adicionar CSS para garantir captura completa
        css_fix = """
            /* Fix para captura completa */
            body {
                height: auto !important;
                min-height: 1800px !important;
                overflow: visible !important;
                padding-bottom: 100px !important;
            }

            .slide {
                height: auto !important;
                min-height: 1700px !important;
                overflow: visible !important;
                padding-bottom: 80px !important;
            }

            .content-grid {
                margin-bottom: 30px !important;
            }

            .card {
                margin-bottom: 25px !important;
                page-break-inside: avoid !important;
            }

            .reference {
                position: absolute !important;
                bottom: 20px !important;
                left: 20px !important;
                right: 20px !important;
            }
        </style>
    </head>"""

        fixed_content = fixed_content.replace('</style>\n    </head>', css_fix)

        # Salvar arquivo corrigido
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        return True

    except Exception as e:
        print(f"❌ Erro ao corrigir {html_file}: {e}")
        return False

def convert_fixed_slide(html_file, png_file):
    """Converte slide corrigido para PNG"""

    html_path = os.path.abspath(html_file)
    output_path = os.path.abspath(png_file)

    # Chrome com configurações para captura completa
    chrome_cmd = [
        '/usr/bin/google-chrome',
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--window-size=1920,1800',
        '--virtual-time-budget=3000',
        '--hide-scrollbars',
        '--force-device-scale-factor=1',
        f'--screenshot={output_path}',
        f'file://{html_path}'
    ]

    try:
        result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 5000:  # Pelo menos 5KB
                return True
            else:
                print(f"   ⚠️  Arquivo muito pequeno: {file_size} bytes")
                return False
        else:
            print(f"   ❌ Erro Chrome: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    """Função principal"""

    print("🔧 Corrigindo slides para captura COMPLETA...")

    # Criar diretórios
    os.makedirs('slides_corrigidos', exist_ok=True)
    os.makedirs('slide_images_full', exist_ok=True)

    # Encontrar slides
    slide_files = glob.glob('slides_individuais/slide_*.html')
    slide_files.sort()

    if not slide_files:
        print("❌ Nenhum slide encontrado!")
        return

    print(f"📊 Processando {len(slide_files)} slides...")

    successful = 0
    failed = 0

    for i, html_file in enumerate(slide_files, 1):
        basename = os.path.basename(html_file)
        slide_name = basename.replace('.html', '')

        print(f"🔧 [{i}/{len(slide_files)}] {slide_name}...")

        # Corrigir HTML
        fixed_html = f'slides_corrigidos/{slide_name}_fixed.html'
        if not fix_slide_html(html_file, fixed_html):
            print(f"   ❌ Falha na correção")
            failed += 1
            continue

        # Converter para PNG
        png_file = f'slide_images_full/{slide_name}.png'
        if convert_fixed_slide(fixed_html, png_file):
            size_mb = os.path.getsize(png_file) / (1024*1024)
            print(f"   ✅ {slide_name}.png ({size_mb:.1f}MB)")
            successful += 1
        else:
            print(f"   ❌ Falha na conversão")
            failed += 1

        # Pequena pausa
        time.sleep(0.3)

    print(f"\n🎯 Processamento concluído!")
    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📁 Imagens completas: slide_images_full/")

    if successful > 0:
        # Calcular estatísticas
        png_files = glob.glob('slide_images_full/*.png')
        total_size = sum(os.path.getsize(f) for f in png_files) / (1024*1024)  # MB

        print(f"\n📈 Estatísticas:")
        print(f"   • {len(png_files)} imagens geradas")
        print(f"   • Tamanho total: {total_size:.1f}MB")
        print(f"   • Média: {total_size/len(png_files):.1f}MB por slide")

        print(f"\n🎬 Para usar no Canva:")
        print(f"   1. Use pasta 'slide_images_full/'")
        print(f"   2. Importe todas as imagens")
        print(f"   3. Redimensione para preencher slide")
        print(f"   4. TODO o conteúdo estará visível!")

        print(f"\n✨ Problema de corte RESOLVIDO!")

if __name__ == "__main__":
    main()