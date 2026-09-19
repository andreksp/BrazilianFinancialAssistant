from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
from lxml import etree
import shutil

R=Path(__file__).resolve().parent
B=R/'backups'/('antes_capa_preta_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
B.mkdir(parents=True)
files=['modelo/modelo_sincronizado.docx','Entrega_Final/Monografia_Revisada_para_Orientador.docx']
for file in files+['Entrega_Final/Monografia_Revisada_para_Orientador.pdf']:
    shutil.copy2(R/file,B/Path(file).name)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for file in files:
    path=R/file
    with ZipFile(path) as z:entries=[(i,z.read(i.filename)) for i in z.infolist()]
    new=[]
    for info,data in entries:
        if info.filename=='word/document.xml':
            root=etree.fromstring(data)
            cover=root.find('w:body',ns).find('w:p',ns)
            colors=cover.xpath('.//w:color',namespaces=ns)
            assert len(colors)>0
            for c in colors:
                c.attrib.clear()
                c.set('{'+ns['w']+'}val','000000')
            data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
            print(file,len(colors),'cores ajustadas')
        new.append((info,data))
    with ZipFile(path,'w') as z:
        for info,data in new:z.writestr(info,data)
print('Backup:',B)
