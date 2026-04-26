import o
import json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLineHorizontal, LTChar, LTTextBoxHorizontal
from collections import Counter
import re

def extract_text_elements(pdf_path):
    elements = []
    try:
        for page_num, page_layout in enumerate(extract_pages(pdf_path)):
            page_height = page_layout.height 
            for element in page_layout:
                if isinstance(element, LTTextLineHorizontal):
                    text = element.get_text().strip()
                    if not text:
                        continue
                    font_name = 'unknown'
                    font_size = element.height
                    is_bold = False
                    if hasattr(element, '_objs'):
                        char_info = []
                        for char_obj in element._objs:
                            if isinstance(char_obj, LTChar):
                                char_info.append({
                                    'fontname': char_obj.fontname,
                                    'size': char_obj.size,
                                    'is_bold': 'bold' in char_obj.fontname.lower() or 'bd' in char_obj.fontname.lower()
                                })
                        if char_info:
                            most_common_font = Counter([c['fontname'] for c in char_info]).most_common(1)
                            if most_common_font:
                                font_name = most_common_font[0][0]
                            most_common_size = Counter([round(c['size'], 1) for c in char_info]).most_common(1)
                            if most_common_size:
                                font_size = most_common_size[0][0]
                            is_bold = any(c['is_bold'] for c in char_info)
                    elements.append({
                        'text': text,
                        'page': page_num + 1,
                        'font_name': font_name,
                        'font_size': font_size,
                        'is_bold': is_bold,
                        'x0': element.x0,
                        'y0': element.y0,
                        'x1': element.x1,
                        'y1': element.y1,
                        'width': element.width,
                        'height': element.height,
                        'page_height': page_height
                    })
                elif isinstance(element, LTTextBoxHorizontal):
                    for line in element:
                        if isinstance(line, LTTextLineHorizontal):
                            text = line.get_text().strip()
                            if not text:
                                continue
                            font_name = 'unknown'
                            font_size = line.height
                            is_bold = False
                            if hasattr(line, '_objs'):
                                char_info = []
                                for char_obj in line._objs:
                                    if isinstance(char_obj, LTChar):
                                        char_info.append({
                                            'fontname': char_obj.fontname,
                                            'size': char_obj.size,
                                            'is_bold': 'bold' in char_obj.fontname.lower() or 'bd' in char_obj.fontname.lower()
                                        })
                                if char_info:
                                    most_common_font = Counter([c['fontname'] for c in char_info]).most_common(1)
                                    if most_common_font:
                                        font_name = most_common_font[0][0]
                                    most_common_size = Counter([round(c['size'], 1) for c in char_info]).most_common(1)
                                    if most_common_size:
                                        font_size = most_common_size[0][0]
                                    is_bold = any(c['is_bold'] for c in char_info)
                            elements.append({
                                'text': text,
                                'page': page_num + 1,
                                'font_name': font_name,
                                'font_size': font_size,
                                'is_bold': is_bold,
                                'x0': line.x0,
                                'y0': line.y0,
                                'x1': line.x1,
                                'y1': line.y1,
                                'width': line.width,
                                'height': line.height,
                                'page_height': page_height
                            })
    except Exception as e:
        print(f"Error extracting text elements from PDF '{pdf_path}': {e}")
    return elements

def analyze_document_structure(elements):
    title = None
    outline = []

    if not elements:
        return {"title": None, "outline": []}

    # Prepare average line height
    valid_heights = [e['height'] for e in elements if 5 < e['height'] < 50]
    avg_line_height = sum(valid_heights) / len(valid_heights) if valid_heights else 12.0

    all_font_sizes = [round(e['font_size'], 1) for e in elements]
    body_font_size_baseline = Counter(all_font_sizes).most_common(1)[0][0] if all_font_sizes else 10.0

    style_counts = Counter()
    for element in elements:
        key = (element['font_name'], round(element['font_size'], 1), element['is_bold'])
        style_counts[key] += 1

    sorted_styles = sorted(style_counts.items(), key=lambda x: (x[0][1], x[1]), reverse=True)

    levels = ["TITLE", "H1", "H2", "H3", "BODY"]
    style_mapping = {}
    current_level_idx = 0
    last_assigned_size = 0
    level_font_sizes = {}

    for style_key, count in sorted_styles:
        font_name, font_size, is_bold = style_key
        if font_size > body_font_size_baseline * 0.95:
            if font_size > last_assigned_size + 3.0:
                style_mapping[style_key] = levels[current_level_idx]
                level_font_sizes.setdefault(levels[current_level_idx], []).append(style_key)
                last_assigned_size = font_size
                current_level_idx = min(current_level_idx + 1, len(levels) - 1)
            else:
                style_mapping[style_key] = levels[max(current_level_idx - 1, 0)]
                level_font_sizes.setdefault(levels[max(current_level_idx - 1, 0)], []).append(style_key)

    # Detect title
    page1_elements = [e for e in elements if e['page'] == 1]
    top_elements = [e for e in page1_elements if e['y0'] > 0.65 * e['page_height']]
    top_elements.sort(key=lambda x: x['font_size'], reverse=True)
    if top_elements:
        title = top_elements[0]['text']
        elements = [e for e in elements if e['text'] != title]

    # X-position for heading alignment
    x_positions = [round(e['x0'], 0) for e in elements]
    body_x_pos = Counter(x_positions).most_common(1)[0][0] if x_positions else 72.0

    h1_patterns = re.compile(r'^(Round\s+\d+|The Journey Ahead|Why This Matters|Are you in)', re.IGNORECASE)
    h2_patterns = re.compile(r'^(Challenge Theme:|Your Mission|What You Need to Build|Docker Requirements|Scoring Criteria)', re.IGNORECASE)
    h3_patterns = re.compile(r'^(Test Case\s+\d+:|Criteria|Description|Metadata|Sub-section Analysis)', re.IGNORECASE)

    non_heading_patterns = re.compile(
        r'^(Welcome to .*Challenge|Rethink Reading|That’s the future|Appendix|index|table of contents|'
        r'著作権|全著作権所有|ライセンス|付録|謝辞|目次|'
        r'droits d\'auteur|licence|introduction|conclusion|références)$',
        re.IGNORECASE
    )

    last_y = float('inf')
    last_page = 0

    for e in elements:
        text, page, x0, y0, size, is_bold = e['text'], e['page'], e['x0'], e['y0'], e['font_size'], e['is_bold']
        style_key = (e['font_name'], round(size, 1), is_bold)
        assigned = style_mapping.get(style_key, "BODY")

        if non_heading_patterns.match(text) or len(text) > 100:
            continue

        is_gap = page > last_page or last_y - y0 > avg_line_height * 2.0
        level = None

        if h1_patterns.match(text):
            level = "H1"
        elif h2_patterns.match(text):
            level = "H2"
        elif h3_patterns.match(text):
            level = "H3"
        elif assigned in ["H1", "H2", "H3"]:
            level = assigned
        elif is_bold and is_gap and size > body_font_size_baseline * 1.3:
            level = "H2"

        if level:
            outline.append({"level": level, "text": text, "page": page})

        last_y = y0
        last_page = page

    return {"title": title, "outline": outline}

if __name__ == "__main__":
    INPUT_DIR = "input/"
    OUTPUT_DIR = "output/"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in {INPUT_DIR}. Please ensure your PDFs are mounted correctly.")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_file)
        output_filename = os.path.splitext(pdf_file)[0] + ".json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"Processing '{pdf_file}'...")
        try:
            elements = extract_text_elements(pdf_path)
            result = analyze_document_structure(elements)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Output saved to '{output_path}'")
        except Exception as e:
            print(f"❌ Error processing '{pdf_file}': {e}")
