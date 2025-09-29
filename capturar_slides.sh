#!/bin/bash
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

        wkhtmltoimage \
            --width 1920 \
            --height 1080 \
            --quality 100 \
            --format png \
            --javascript-delay 2000 \
            --enable-local-file-access \
            "$html_file" \
            "slide_images/${filename}.png"
    fi
done

echo "✅ Screenshots salvos em slide_images/"
echo "🎯 Agora você pode importar as imagens PNG no Canva!"
