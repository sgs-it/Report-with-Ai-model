import os
import json
import zipfile
import xml.etree.ElementTree as ET

base_dir = r"d:\Dhaniyal\Report-Generation-main\neww"
out_dir = r"d:\Dhaniyal\Report-Generation-main\offline_training\dataset"

os.makedirs(out_dir, exist_ok=True)

dataset_path = os.path.join(out_dir, "dataset.json")
dataset = []
if os.path.exists(dataset_path):
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

img_counter = 0
import glob
existing_imgs = glob.glob(os.path.join(out_dir, "img_*.jpg"))
for img in existing_imgs:
    try:
        num = int(os.path.basename(img).replace("img_", "").replace(".jpg", ""))
        if num > img_counter:
            img_counter = num
    except:
        pass

ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'v': 'urn:schemas-microsoft-com:vml'
}

ignore_captions = {
    'agriculture engineer', 'date', 'basem adel', 'tmhe', 'photographs - bayti 40 villas',
    'photographs - bayti 33 villas', 'approved by: designation: signature:', 
    'khidmah sole proprietorship llc', 'khidmah', 'signature:'
}

def get_text_from_cell(cell):
    texts = [t.text.strip() for t in cell.findall('.//w:t', namespaces=ns) if t.text and t.text.strip()]
    return " ".join(texts).strip()

def process_doc(path):
    global img_counter
    print("Processing:", path)
    try:
        with zipfile.ZipFile(path) as z:
            # Get rId mapping
            try:
                rels_xml = z.read('word/_rels/document.xml.rels')
            except KeyError:
                return # No rels
            rels = ET.fromstring(rels_xml)
            rId_map = {}
            for rel in rels.findall('.//rel:Relationship', namespaces=ns):
                rId_map[rel.attrib['Id']] = rel.attrib['Target']
                
            # Get document xml
            try:
                doc_xml = z.read('word/document.xml')
            except KeyError:
                return
            root = ET.fromstring(doc_xml)
            
            # Iterate through all tables
            for tbl in root.findall('.//w:tbl', namespaces=ns):
                rows = tbl.findall('.//w:tr', namespaces=ns)
                for r_idx, row in enumerate(rows):
                    cells = row.findall('.//w:tc', namespaces=ns)
                    for c_idx, cell in enumerate(cells):
                        # Find all images in this cell
                        rIds = []
                        for blip in cell.findall('.//a:blip', namespaces=ns):
                            if '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed' in blip.attrib:
                                rIds.append(blip.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'])
                        for imagedata in cell.findall('.//v:imagedata', namespaces=ns):
                            if '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id' in imagedata.attrib:
                                rIds.append(imagedata.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'])
                                
                        if rIds:
                            caption = ""
                            # Check cell directly below
                            if r_idx + 1 < len(rows):
                                next_row_cells = rows[r_idx + 1].findall('.//w:tc', namespaces=ns)
                                if c_idx < len(next_row_cells):
                                    caption = get_text_from_cell(next_row_cells[c_idx])
                            
                            # If no caption below, check same cell
                            if not caption:
                                caption = get_text_from_cell(cell)
                                
                            caption_clean = caption.replace('\n', ' ').strip()
                            
                            if caption and len(caption_clean) > 2 and len(caption_clean) < 100:
                                if caption_clean.lower() not in ignore_captions and not caption_clean.lower().startswith('photographs -'):
                                    for rid in rIds:
                                        if rid in rId_map:
                                            target = rId_map[rid]
                                            # target is something like 'media/image1.jpeg' or '../media/image1.jpeg'
                                            target = target.replace('../', '')
                                            if not target.startswith('word/'):
                                                target = 'word/' + target
                                            try:
                                                img_data = z.read(target)
                                                img_counter += 1
                                                img_path = os.path.join(out_dir, f"img_{img_counter}.jpg")
                                                with open(img_path, "wb") as f:
                                                    f.write(img_data)
                                                dataset.append({"image": f"img_{img_counter}.jpg", "caption": caption_clean})
                                            except Exception as e:
                                                pass
    except Exception as e:
        print(f"Failed to process {path}: {e}")

def main():
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if (f.endswith('.docx') or f.endswith('.docm')) and not f.startswith('~'):
                process_doc(os.path.join(root, f))
                
    dataset_path = os.path.join(out_dir, "dataset.json")
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4)
    print(f"Extracted {len(dataset)} image-caption pairs.")

if __name__ == "__main__":
    main()
