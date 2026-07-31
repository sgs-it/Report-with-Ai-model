from pathlib import Path
import zipfile
import re
from xml.etree import ElementTree as ET
from PIL import Image
import io
import os
import json

ROOT = Path('d:/Dhaniyal/reports for training')
OUTPUT_DIR = ROOT / 'caption_dataset'
OUTPUT_DIR.mkdir(exist_ok=True)

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def extract_pairs(docx_path: Path):
    pairs = []
    with zipfile.ZipFile(docx_path) as z:
        xml_bytes = z.read('word/document.xml')
        root = ET.fromstring(xml_bytes)
        rels = {}
        if 'word/_rels/document.xml.rels' in z.namelist():
            rels_root = ET.fromstring(z.read('word/_rels/document.xml.rels'))
            for rel in rels_root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                rels[rel.attrib['Id']] = rel.attrib['Target']

        # Find image and nearby paragraphs in the document order
        paragraphs = []
        for p in root.findall('.//w:p', NS):
            text = ''.join(t.text or '' for t in p.findall('.//w:t', NS))
            paragraphs.append((p, text.strip()))

        for idx, (p, text) in enumerate(paragraphs):
            if not text:
                continue
            # collect nearby text around images if present
            if 'image' in text.lower() or len(text) < 4:
                continue
            # Try to find an image in the same paragraph or next paragraphs.
            # For this dataset builder we use the paragraph text as the caption candidate.
            if len(text) > 4 and len(text) < 220:
                pairs.append({'source': docx_path.name, 'caption': text})
    return pairs


def main():
    docx_files = sorted(ROOT.glob('*.docx')) + sorted(ROOT.glob('*.docm'))
    all_pairs = []
    for path in docx_files:
        if path.name.lower().endswith('.docm'):
            continue
        try:
            pairs = extract_pairs(path)
            all_pairs.extend(pairs)
        except Exception as e:
            print('skip', path.name, e)

    # Deduplicate simple captions
    seen = set()
    unique = []
    for item in all_pairs:
        c = re.sub(r'\s+', ' ', item['caption']).strip()
        if not c:
            continue
        if c.lower() in seen:
            continue
        seen.add(c.lower())
        unique.append({'source': item['source'], 'caption': c})

    out_path = OUTPUT_DIR / 'captions.jsonl'
    with open(out_path, 'w', encoding='utf-8') as f:
        for item in unique[:500]:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print('wrote', len(unique), 'captions to', out_path)


if __name__ == '__main__':
    main()
