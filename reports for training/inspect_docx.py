from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

p = Path('Landscaping Monthly Report - AFRE -  Al Dhiyafa Village - 22A10601- June 2026.docx')
print('file exists', p.exists())
with zipfile.ZipFile(p) as z:
    names = [n for n in z.namelist() if n.startswith('word/media/')]
    print('media files', len(names))
    for n in names[:10]:
        print(n)
    print('document.xml exists', 'word/document.xml' in z.namelist())
    if 'word/document.xml' in z.namelist():
        xml = z.read('word/document.xml').decode('utf-8')
        print(xml[:2000])
