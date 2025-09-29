#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criador de Template PowerPoint - Apresentação Arboviroses
Cria arquivo CSV para importação no PowerPoint/Canva
"""

import re
import html
import csv

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

        # Extrair título principal
        title_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', slide_content, re.DOTALL)
        if title_match:
            title = html.unescape(re.sub(r'<[^>]+>', '', title_match.group(1)))
            title = clean_text(title)
        else:
            title = f"Slide {slide_num}"

        # Extrair cabeçalho do aluno
        aluno_match = re.search(r'<div class="aluno-header"[^>]*>(.*?)</div>', slide_content, re.DOTALL)
        aluno_info = ""
        if aluno_match:
            aluno_info = html.unescape(re.sub(r'<[^>]+>', '', aluno_match.group(1)))
            aluno_info = clean_text(aluno_info)

        # Coletar todo o conteúdo textual
        content_sections = []

        # Cards
        card_pattern = r'<div class="card"[^>]*>(.*?)</div>'
        cards = re.findall(card_pattern, slide_content, re.DOTALL)

        for card in cards:
            card_text = extract_card_content(card)
            if card_text:
                content_sections.append(card_text)

        # Destaques
        highlight_patterns = [
            r'<div class="danger[^"]*"[^>]*>(.*?)</div>',
            r'<div class="highlight[^"]*"[^>]*>(.*?)</div>',
            r'<div class="stat-box[^"]*"[^>]*>(.*?)</div>',
            r'<div class="success[^"]*"[^>]*>(.*?)</div>'
        ]

        for pattern in highlight_patterns:
            highlights = re.findall(pattern, slide_content, re.DOTALL)
            for highlight in highlights:
                highlight_text = clean_text(html.unescape(re.sub(r'<[^>]+>', ' ', highlight)))
                if highlight_text and len(highlight_text) > 5:
                    content_sections.append(f"DESTAQUE: {highlight_text}")

        # Juntar conteúdo
        main_content = "\n\n".join(content_sections)

        # Extrair referências
        ref_match = re.search(r'<div class="reference"[^>]*>(.*?)</div>', slide_content, re.DOTALL)
        reference = ""
        if ref_match:
            reference = clean_text(html.unescape(re.sub(r'<[^>]+>', '', ref_match.group(1))))

        slides_data.append({
            'slide_number': slide_num,
            'title': title,
            'presenter': aluno_info,
            'content': main_content,
            'notes': reference
        })

    return slides_data

def clean_text(text):
    """Limpa texto removendo caracteres problemáticos"""
    if not text:
        return ""

    # Remover caracteres especiais mantendo apenas essenciais
    text = re.sub(r'[^\w\s:.,;!?%()+-→°><=]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_card_content(card_html):
    """Extrai conteúdo estruturado de um card"""
    # Título do card
    h3_match = re.search(r'<h3[^>]*>(.*?)</h3>', card_html, re.DOTALL)
    card_title = ""
    if h3_match:
        card_title = clean_text(html.unescape(re.sub(r'<[^>]+>', '', h3_match.group(1))))

    # Conteúdo do card
    content_parts = []

    # Lista de itens
    li_pattern = r'<li[^>]*>(.*?)</li>'
    items = re.findall(li_pattern, card_html, re.DOTALL)

    if items:
        for item in items:
            clean_item = clean_text(html.unescape(re.sub(r'<[^>]+>', '', item)))
            if clean_item:
                content_parts.append(f"• {clean_item}")
    else:
        # Divs com conteúdo
        div_pattern = r'<div[^>]*>(.*?)</div>'
        divs = re.findall(div_pattern, card_html, re.DOTALL)
        for div in divs:
            clean_div = clean_text(html.unescape(re.sub(r'<[^>]+>', '', div)))
            if clean_div and len(clean_div) > 3:
                content_parts.append(f"• {clean_div}")

    # Montar conteúdo final
    if card_title and content_parts:
        return f"{card_title}:\n" + "\n".join(content_parts)
    elif card_title:
        return card_title
    elif content_parts:
        return "\n".join(content_parts)
    else:
        return ""

def create_csv_for_powerpoint(slides_data, output_file):
    """Cria CSV para importação no PowerPoint"""

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Slide', 'Title', 'Presenter', 'Content', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for slide in slides_data:
            writer.writerow({
                'Slide': slide['slide_number'],
                'Title': slide['title'],
                'Presenter': slide['presenter'],
                'Content': slide['content'],
                'Notes': slide['notes']
            })

def create_markdown_output(slides_data, output_file):
    """Cria arquivo Markdown para fácil visualização"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Apresentação Arboviroses\n\n")
        f.write("## Estrutura da Apresentação\n")
        f.write("**Duração Total:** 15 minutos (2,5 min por aluno)\n\n")

        for slide in slides_data:
            f.write(f"## Slide {slide['slide_number']}: {slide['title']}\n\n")

            if slide['presenter']:
                f.write(f"**Apresentador:** {slide['presenter']}\n\n")

            if slide['content']:
                f.write(f"{slide['content']}\n\n")

            if slide['notes']:
                f.write(f"*Fonte: {slide['notes']}*\n\n")

            f.write("---\n\n")

def main():
    """Função principal"""
    html_file = "apresentação_v3.html"

    print("🔄 Criando templates para PowerPoint/Canva...")

    try:
        # Extrair dados
        slides_data = extract_slides_from_html(html_file)
        print(f"📊 Processados {len(slides_data)} slides")

        # Criar arquivos
        create_csv_for_powerpoint(slides_data, "slides_powerpoint.csv")
        create_markdown_output(slides_data, "apresentacao_arboviroses.md")

        print("✅ Templates criados com sucesso!")
        print("\n📁 Arquivos gerados:")
        print("  • slides_powerpoint.csv - Para importação no PowerPoint")
        print("  • apresentacao_arboviroses.md - Visualização em Markdown")

        print("\n🎯 Como usar:")
        print("  1. Abra o PowerPoint")
        print("  2. Vá em Inserir > Objeto > Criar do arquivo")
        print("  3. Selecione slides_powerpoint.csv")
        print("  4. Ou copie conteúdo do .md para slides individuais")

        # Estatísticas
        total_cards = sum(len(slide['content'].split('\n\n')) for slide in slides_data if slide['content'])
        presenters = set(slide['presenter'] for slide in slides_data if slide['presenter'])

        print(f"\n📈 Estatísticas:")
        print(f"  • {len(slides_data)} slides totais")
        print(f"  • {len(presenters)} apresentadores")
        print(f"  • ~{total_cards} seções de conteúdo")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()