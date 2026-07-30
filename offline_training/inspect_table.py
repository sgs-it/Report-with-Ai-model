import xml.etree.ElementTree as ET

tree = ET.parse(r'unzipped\word\document.xml')
root = tree.getroot()
ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}

for tbl_idx, tbl in enumerate(root.findall('.//w:tbl', namespaces=ns)):
    print(f"Table {tbl_idx}:")
    for r_idx, row in enumerate(tbl.findall('.//w:tr', namespaces=ns)):
        cells = row.findall('.//w:tc', namespaces=ns)
        print(f"  Row {r_idx} ({len(cells)} cells)")
        for c_idx, cell in enumerate(cells):
            blips = [b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') for b in cell.findall('.//a:blip', namespaces=ns)]
            texts = [t.text for t in cell.findall('.//w:t', namespaces=ns) if t.text and t.text.strip()]
            text_str = "".join(texts)
            if blips or text_str:
                print(f"    R{r_idx}C{c_idx}: {len(blips)} images, text: '{text_str}'")
