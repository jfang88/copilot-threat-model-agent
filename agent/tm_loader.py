# Loader the agent runs at the start of every session (same code as in agent_instructions.txt).
# Finds an attached tm_generator.txt; otherwise extracts the script from the TM-03 knowledge file if code interpreter can see it.
import glob,re,zipfile,html
def tm_src():
    F=lambda p:[f for d in('/mnt/data','.','/mnt','/tmp','/home')for f in glob.glob(d+'/**/'+p,recursive=True)]
    for f in F('tm_generator*.txt'):return open(f,encoding='utf-8').read()
    for f in F('TM-03*.docx'):
        for p in re.findall(r'<w:p\b.*?</w:p>',zipfile.ZipFile(f).read('word/document.xml').decode(),re.S):
            if 'SourceCode' in p and 'tm_generator.py  v' in p:
                return html.unescape(re.sub(r'<[^>]+>','',re.sub(r'<w:br\s*/>','\n',p)))
    raise FileNotFoundError('tm_generator not found: attach tm_generator.txt')
exec(tm_src())
