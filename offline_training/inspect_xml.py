import xml.etree.ElementTree as ET

tree = ET.parse(r'unzipped\word\document.xml')
root = tree.getroot()
tags = []
for elem in root.iter():
    tag = elem.tag.split('}')[-1]
    if tag in ('drawing', 'imagedata', 'blip', 't'):
        val = elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') or \
              elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id') or \
              elem.text
        if val and val.strip():
            tags.append(f'{tag}: {val.strip()}')

print('\n'.join(tags[:50]))
