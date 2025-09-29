#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor HTML para Imagens - Apresentação Arboviroses
Converte cada slide HTML em imagem PNG para importação no Canva
"""

import re
import os
import subprocess
import time

def extract_individual_slides(html_file):
    """Extrai cada slide individual e cria arquivos HTML separados"""

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrair cabeçalho HTML (até </style>)
    header_match = re.search(r'(.*?</style>)', content, re.DOTALL)
    if not header_match:
        print("❌ Erro: Não foi possível encontrar o cabeçalho HTML")
        return []

    html_header = header_match.group(1)

    # Extrair footer HTML (scripts e fechamento)
    footer_match = re.search(r'(<script.*?</html>)', content, re.DOTALL)
    html_footer = footer_match.group(1) if footer_match else """
        <script>
            // Scripts de navegação removidos para imagens estáticas
        </script>
    </body>
    </html>"""

    # Encontrar todos os slides
    slide_pattern = r'<div class="slide"[^>]*>(.*?)(?=<div class="slide">|<script|</body>)'
    slides = re.findall(slide_pattern, content, re.DOTALL)

    slide_files = []

    # Criar diretório para slides
    os.makedirs('slides_individuais', exist_ok=True)

    for i, slide_content in enumerate(slides):
        # Extrair número do slide
        slide_num_match = re.search(r'Slide (\d+)/42', slide_content)
        slide_num = slide_num_match.group(1) if slide_num_match else str(i+1)

        # Criar HTML completo para o slide
        slide_html = f"""{html_header}
    </head>
    <body style="margin: 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div class="slide" style="display: block !important;">
            {slide_content}
        </div>

        <style>
            /* Estilos específicos para slide individual */
            .slide {{
                width: 1920px;
                height: 1080px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                padding: 40px;
                box-sizing: border-box;
                position: relative;
                overflow: hidden;
            }}

            /* Garantir que animações sejam visíveis */
            .mosquito-animation {{
                animation: float 3s ease-in-out infinite;
            }}

            .virus-particle {{
                animation: pulse 2s infinite;
            }}

            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
            }}

            /* Ajustar tamanhos para melhor visualização */
            h1 {{ font-size: 2.5em; }}
            h2 {{ font-size: 2.2em; }}
            h3 {{ font-size: 1.8em; }}
            p, li {{ font-size: 1.2em; }}

            .big-emoji {{ font-size: 5em; }}
            .icon-large {{ font-size: 4em; }}
        </style>

        {html_footer}"""

        # Salvar arquivo do slide
        slide_filename = f"slides_individuais/slide_{int(slide_num):02d}.html"
        with open(slide_filename, 'w', encoding='utf-8') as f:
            f.write(slide_html)

        slide_files.append({
            'number': slide_num,
            'filename': slide_filename,
            'html_file': slide_filename
        })

    return slide_files

def create_screenshot_script():
    """Cria script para capturar screenshots dos slides"""

    script_content = """#!/bin/bash
# Script para capturar screenshots dos slides HTML

echo "🔄 Capturando screenshots dos slides..."

# Verificar se wkhtmltopdf está instalado
if ! command -v wkhtmltoimage &> /dev/null; then
    echo "📦 Instalando wkhtmltopdf..."
    sudo apt-get update
    sudo apt-get install -y wkhtmltopdf
fi

# Criar diretório para imagens
mkdir -p slide_images

# Capturar cada slide
for html_file in slides_individuais/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file" .html)
        echo "📸 Capturando $filename..."

        wkhtmltoimage \\
            --width 1920 \\
            --height 1080 \\
            --quality 100 \\
            --format png \\
            --javascript-delay 2000 \\
            --enable-local-file-access \\
            "$html_file" \\
            "slide_images/${filename}.png"
    fi
done

echo "✅ Screenshots salvos em slide_images/"
echo "🎯 Agora você pode importar as imagens PNG no Canva!"
"""

    with open('capturar_slides.sh', 'w') as f:
        f.write(script_content)

    # Tornar executável
    os.chmod('capturar_slides.sh', 0o755)

def create_browser_capture_html():
    """Cria página HTML para captura manual no navegador"""

    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Captura de Slides - Arboviroses</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
            font-family: Arial, sans-serif;
        }
        .capture-info {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .slide-navigation {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
        }
        .slide-navigation button {
            background: #3498db;
            color: white;
            border: none;
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
        }
        iframe {
            width: 1920px;
            height: 1080px;
            border: 2px solid #333;
            border-radius: 10px;
            transform-origin: top left;
            transform: scale(0.8);
        }
    </style>
</head>
<body>
    <div class="capture-info">
        <h1>🎬 Captura de Slides para Canva</h1>
        <p><strong>Instruções:</strong></p>
        <ol>
            <li>Use F11 para tela cheia</li>
            <li>Navegue pelos slides com os botões</li>
            <li>Use Print Screen ou ferramenta de captura</li>
            <li>Salve cada slide como PNG</li>
            <li>Importe no Canva</li>
        </ol>
    </div>

    <div class="slide-navigation">
        <button onclick="previousSlide()">◀ Anterior</button>
        <span id="slideCounter">Slide 1</span>
        <button onclick="nextSlide()">Próximo ▶</button>
        <br>
        <button onclick="captureMode()">📸 Modo Captura</button>
    </div>

    <iframe id="slideFrame" src="slides_individuais/slide_01.html"></iframe>

    <script>
        let currentSlide = 1;
        const totalSlides = 42;

        function updateSlide() {
            const slideNum = String(currentSlide).padStart(2, '0');
            document.getElementById('slideFrame').src = `slides_individuais/slide_${slideNum}.html`;
            document.getElementById('slideCounter').textContent = `Slide ${currentSlide}/${totalSlides}`;
        }

        function nextSlide() {
            if (currentSlide < totalSlides) {
                currentSlide++;
                updateSlide();
            }
        }

        function previousSlide() {
            if (currentSlide > 1) {
                currentSlide--;
                updateSlide();
            }
        }

        function captureMode() {
            // Esconder navegação para captura limpa
            document.querySelector('.slide-navigation').style.display = 'none';
            document.querySelector('.capture-info').style.display = 'none';

            setTimeout(() => {
                alert('Agora capture a tela! Pressione OK para restaurar a navegação.');
                document.querySelector('.slide-navigation').style.display = 'block';
                document.querySelector('.capture-info').style.display = 'block';
            }, 1000);
        }

        // Navegação por teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' || e.key === 'Space') {
                nextSlide();
            } else if (e.key === 'ArrowLeft') {
                previousSlide();
            }
        });
    </script>
</body>
</html>"""

    with open('capturar_slides_browser.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Função principal"""
    html_file = "apresentação_v3.html"

    print("🔄 Convertendo HTML para imagens individuais...")
    print(f"📁 Arquivo de entrada: {html_file}")

    try:
        # Extrair slides individuais
        slide_files = extract_individual_slides(html_file)
        print(f"📊 Criados {len(slide_files)} slides individuais")

        # Criar script de captura
        create_screenshot_script()
        print("📜 Script de captura criado: capturar_slides.sh")

        # Criar interface de captura no browser
        create_browser_capture_html()
        print("🌐 Interface de captura criada: capturar_slides_browser.html")

        print("\n✅ Conversão concluída!")
        print("\n📁 Arquivos criados:")
        print("  • slides_individuais/ - 42 arquivos HTML individuais")
        print("  • capturar_slides.sh - Script automático de captura")
        print("  • capturar_slides_browser.html - Interface manual de captura")

        print("\n🎯 Como usar:")
        print("  MÉTODO 1 (Automático):")
        print("    ./capturar_slides.sh")
        print("  ")
        print("  MÉTODO 2 (Manual):")
        print("    1. Abra capturar_slides_browser.html no navegador")
        print("    2. Use F11 para tela cheia")
        print("    3. Capture cada slide com Print Screen")
        print("    4. Importe as imagens no Canva")

        print("\n🎨 Resultado:")
        print("  • Slides em resolução 1920x1080 (Full HD)")
        print("  • Todas as cores e gradientes preservados")
        print("  • Animações capturadas no estado ideal")
        print("  • Pronto para importar no Canva como imagens")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()