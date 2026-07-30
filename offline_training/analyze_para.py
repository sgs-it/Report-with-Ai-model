import os
from docx import Document

ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}

doc = Document(r'd:\Dhaniyal\Report-Generation-main\New folder\Landscaping Monthly Report - Aramex Logistics - 52A12301- April 2026.docx')

for p_idx, p in enumerate(doc.paragraphs):
    imgs = 0
    for run in p.runs:
        drawings = run.element.findall('.//w:drawing', namespaces=ns)
        imgs += sum(1 for d in drawings for b in d.findall('.//a:blip', namespaces=ns))
    text = p.text.strip().replace('\n', ' ')
    if imgs > 0 or text:
        print(f"P{p_idx}: {imgs} images, text: '{text[:80]}'")
