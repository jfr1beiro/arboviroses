#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de Slides HTML para PNG usando Chrome Headless
"""

import os
import subprocess
import time
import glob

def convert_slide_to_png(html_file, output_file):
    """Converte um slide HTML para PNG usando Chrome headless"""

    # Obter caminho absoluto do arquivo HTML
    html_path = os.path.abspath(html_file)
    output_path = os.path.abspath(output_file)

    # Comando do Chrome em modo headless
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
        '--window-size=1920,1080',
        '--virtual-time-budget=3000',  # Aguardar 3 segundos para animações
        f'--screenshot={output_path}',
        f'file://{html_path}'
    ]

    try:
        # Executar comando
        result = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"❌ Erro ao converter {html_file}: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout ao converter {html_file}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao converter {html_file}: {e}")
        return False

def main():
    """Função principal"""

    print("🔄 Convertendo slides HTML para PNG usando Chrome...")

    # Criar diretório para imagens
    os.makedirs('slide_images', exist_ok=True)

    # Encontrar todos os arquivos de slide
    slide_files = glob.glob('slides_individuais/slide_*.html')
    slide_files.sort()

    if not slide_files:
        print("❌ Nenhum arquivo de slide encontrado na pasta slides_individuais/")
        return

    print(f"📊 Encontrados {len(slide_files)} slides para converter")

    successful = 0
    failed = 0

    for html_file in slide_files:
        # Extrair número do slide do nome do arquivo
        basename = os.path.basename(html_file)
        slide_name = basename.replace('.html', '')
        png_file = f'slide_images/{slide_name}.png'

        print(f"📸 Convertendo {basename}...")

        if convert_slide_to_png(html_file, png_file):
            print(f"✅ {basename} → {slide_name}.png")
            successful += 1
        else:
            print(f"❌ Falha ao converter {basename}")
            failed += 1

        # Pequena pausa entre conversões
        time.sleep(0.5)

    print(f"\n🎯 Conversão concluída!")
    print(f"✅ Sucessos: {successful}")
    print(f"❌ Falhas: {failed}")
    print(f"📁 Imagens salvas em: slide_images/")

    if successful > 0:
        print(f"\n🎬 Próximos passos:")
        print(f"1. Abra o Canva")
        print(f"2. Crie nova apresentação (16:9)")
        print(f"3. Faça upload das {successful} imagens PNG")
        print(f"4. Adicione uma imagem por slide")
        print(f"5. Configure transições e exporte como vídeo")

        # Mostrar tamanho das imagens
        if os.path.exists('slide_images'):
            png_files = glob.glob('slide_images/*.png')
            if png_files:
                total_size = sum(os.path.getsize(f) for f in png_files)
                avg_size = total_size / len(png_files) / (1024*1024)  # MB
                print(f"\n📈 Estatísticas:")
                print(f"   • {len(png_files)} imagens geradas")
                print(f"   • Tamanho médio: {avg_size:.1f} MB por imagem")
                print(f"   • Resolução: 1920x1080 (Full HD)")

if __name__ == "__main__":
    main()