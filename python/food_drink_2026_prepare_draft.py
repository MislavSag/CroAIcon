"""Copy the canonical article to Quarto, preserving its explicit publication state."""
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'drafts/food-drink-2026/article.qmd'
TARGET=ROOT/'posts/2026-10-hrana-pice-iza-naslova/index.qmd'

if __name__=='__main__':
 text=SOURCE.read_text(encoding='utf-8')
 assert re.search(r'^draft: (?:true|false)$',text,re.M) and 'author: []' in text
 assert text.count('[KUT]')<=3
 if 'draft: false' in text:assert '[KUT]' not in text
 TARGET.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(SOURCE,TARGET)
 body=re.sub(r'^---.*?---','',text,count=1,flags=re.S)
 body=re.sub(r'```.*?```','',body,flags=re.S)
 body=re.sub(r'`\{python\}[^`]+`','NUMBER',body)
 body=re.sub(r'\[([^\]]+)\]\([^\)]+\)',r'\1',body)
 print('Approximate draft words:',len(re.findall(r'\S+',body)))
 print(TARGET)
