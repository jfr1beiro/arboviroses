#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor HTML para Texto Estruturado - Apresentação Arboviroses
Extrai conteúdo do HTML para formato compatível com importação no Canva/PowerPoint
"""

import re
import html
import json

def extract_slides_from_html(html_file):
    """Extrai conteúdo dos slides do arquivo HTML"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Encontrar todos os slides
    slide_pattern = r'<div class="slide"[^>]*>(.*?)(?=<div class="slide">|</body>)'
    slides = re.findall(slide_pattern, content, re.DOTALL)

    slides_data = []

    for i, slide_content in enumerate(slides):
        # Extrair número do slide
        slide_num_match = re.search(r'Slide (\d+)/42', slide_content)
        slide_num = slide_num_match.group(1) if slide_num_match else str(i+1)

        # Extrair título principal (h1 ou h2)
        title_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', slide_content, re.DOTALL)
        if title_match:
            title = html.unescape(re.sub(r'<[^>]+>', '', title_match.group(1)))
            # Remover emojis para melhor compatibilidade
            title = re.sub(r'[^\w\s:.-]', '', title).strip()
        else:
            title = f"Slide {slide_num}"

        # Extrair cabeçalho do aluno se existir
        aluno_match = re.search(r'<div class="aluno-header"[^>]*>(.*?)</div>', slide_content, re.DOTALL)
        if aluno_match:
            aluno_info = html.unescape(re.sub(r'<[^>]+>', '', aluno_match.group(1)))
            aluno_info = re.sub(r'[^\w\s:.-]', '', aluno_info).strip()
        else:
            aluno_info = ""

        # Extrair conteúdo de cards
        card_pattern = r'<div class="card"[^>]*>(.*?)</div>'
        cards = re.findall(card_pattern, slide_content, re.DOTALL)

        card_contents = []
        for card in cards:
            # Extrair h3 do card
            h3_match = re.search(r'<h3[^>]*>(.*?)</h3>', card, re.DOTALL)
            if h3_match:
                card_title = html.unescape(re.sub(r'<[^>]+>', '', h3_match.group(1)))
                card_title = re.sub(r'[^\w\s:.-]', '', card_title).strip()
            else:
                card_title = ""

            # Extrair lista ou conteúdo
            li_pattern = r'<li[^>]*>(.*?)</li>'
            items = re.findall(li_pattern, card, re.DOTALL)
            if items:
                card_items = []
                for item in items:
                    clean_item = html.unescape(re.sub(r'<[^>]+>', '', item))
                    clean_item = re.sub(r'[^\w\s:.-→+%()]', '', clean_item).strip()
                    if clean_item:
                        card_items.append(clean_item)
            else:
                # Se não há lista, pegar divs com conteúdo
                div_pattern = r'<div[^>]*style="text-align: center[^>]*>(.*?)</div>'
                divs = re.findall(div_pattern, card, re.DOTALL)
                card_items = []
                for div in divs:
                    clean_div = html.unescape(re.sub(r'<[^>]+>', '', div))
                    clean_div = re.sub(r'[^\w\s:.-→+%()]', '', clean_div).strip()
                    if clean_div:
                        card_items.append(clean_div)

            if card_title or card_items:
                card_contents.append({
                    'title': card_title,
                    'items': card_items
                })

        # Extrair conteúdo de destaque (danger, highlight, stat-box)
        highlight_patterns = [
            r'<div class="danger[^"]*"[^>]*>(.*?)</div>',
            r'<div class="highlight[^"]*"[^>]*>(.*?)</div>',
            r'<div class="stat-box[^"]*"[^>]*>(.*?)</div>'
        ]

        highlight_texts = []
        for pattern in highlight_patterns:
            highlights = re.findall(pattern, slide_content, re.DOTALL)
            for highlight in highlights:
                clean_text = html.unescape(re.sub(r'<[^>]+>', ' ', highlight))
                clean_text = re.sub(r'[^\w\s:.-→+%()]', '', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                if clean_text and len(clean_text) > 10:
                    highlight_texts.append(clean_text)

        # Extrair referências
        ref_match = re.search(r'<div class="reference"[^>]*>(.*?)</div>', slide_content, re.DOTALL)
        if ref_match:
            reference = html.unescape(re.sub(r'<[^>]+>', '', ref_match.group(1)))
            reference = re.sub(r'[^\w\s:.-;,()]', '', reference).strip()
        else:
            reference = ""

        slides_data.append({
            'number': int(slide_num),
            'title': title,
            'aluno_info': aluno_info,
            'cards': card_contents,
            'highlights': highlight_texts,
            'reference': reference
        })

    return slides_data

def create_text_output(slides_data, output_file):
    """Cria arquivo de texto estruturado"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("APRESENTAÇÃO ARBOVIROSES - CONTEÚDO ESTRUTURADO\n")
        f.write("=" * 60 + "\n\n")

        for slide in slides_data:
            f.write(f"SLIDE {slide['number']}: {slide['title']}\n")
            f.write("-" * 50 + "\n")

            if slide['aluno_info']:
                f.write(f"APRESENTADOR: {slide['aluno_info']}\n\n")

            # Cards principais
            for i, card in enumerate(slide['cards']):
                if card['title']:
                    f.write(f"TÓPICO {i+1}: {card['title']}\n")

                for item in card['items']:
                    f.write(f"  • {item}\n")
                f.write("\n")

            # Destaques
            if slide['highlights']:
                f.write("DESTAQUES:\n")
                for highlight in slide['highlights']:
                    f.write(f"  ⚠️ {highlight}\n")
                f.write("\n")

            # Referência
            if slide['reference']:
                f.write(f"FONTE: {slide['reference']}\n")

            f.write("\n" + "="*60 + "\n\n")

def create_json_output(slides_data, output_file):
    """Cria arquivo JSON para importação programática"""

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(slides_data, f, ensure_ascii=False, indent=2)

def create_slides_summary(slides_data, output_file):
    """Cria resumo executivo dos slides"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("RESUMO EXECUTIVO - APRESENTAÇÃO ARBOVIROSES\n")
        f.write("=" * 60 + "\n\n")

        # Estrutura da apresentação
        aluno_slides = {}
        for slide in slides_data:
            if slide['aluno_info']:
                aluno_num = re.search(r'ALUNO (\d+)', slide['aluno_info'])
                if aluno_num:
                    aluno_key = f"ALUNO {aluno_num.group(1)}"
                    if aluno_key not in aluno_slides:
                        aluno_slides[aluno_key] = []
                    aluno_slides[aluno_key].append(slide)

        f.write("ESTRUTURA DA APRESENTAÇÃO:\n")
        f.write("-" * 30 + "\n")
        for aluno, slides in aluno_slides.items():
            duration_match = re.search(r'(\d+:\d+\s*-\s*\d+:\d+)', slides[0]['aluno_info'])
            duration = duration_match.group(1) if duration_match else "2:30"
            f.write(f"{aluno} ({duration}): Slides {slides[0]['number']}-{slides[-1]['number']}\n")

        f.write(f"\nTOTAL: {len(slides_data)} slides, 15 minutos\n\n")

        # Tópicos principais
        f.write("TÓPICOS PRINCIPAIS:\n")
        f.write("-" * 30 + "\n")
        for slide in slides_data[:10]:  # Primeiros 10 slides como exemplo
            f.write(f"Slide {slide['number']}: {slide['title']}\n")

def main():
    """Função principal"""
    html_file = "apresentação_v3.html"

    print("🔄 Convertendo HTML para formatos compatíveis...")
    print(f"📁 Arquivo de entrada: {html_file}")

    try:
        # Extrair dados dos slides
        slides_data = extract_slides_from_html(html_file)
        print(f"📊 Encontrados {len(slides_data)} slides")

        # Criar arquivos de saída
        create_text_output(slides_data, "apresentacao_arboviroses.txt")
        create_json_output(slides_data, "apresentacao_arboviroses.json")
        create_slides_summary(slides_data, "resumo_apresentacao.txt")

        print("✅ Conversão concluída com sucesso!")
        print("\n📁 Arquivos gerados:")
        print("  • apresentacao_arboviroses.txt - Conteúdo completo estruturado")
        print("  • apresentacao_arboviroses.json - Dados estruturados (JSON)")
        print("  • resumo_apresentacao.txt - Resumo executivo")
        print("\n🎯 Use estes arquivos para:")
        print("  1. Copiar conteúdo para slides do Canva")
        print("  2. Importar estrutura no PowerPoint")
        print("  3. Referência para criação manual")

    except Exception as e:
        print(f"❌ Erro durante a conversão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()