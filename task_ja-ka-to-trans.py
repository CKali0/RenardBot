import pywikibot as pwb
import wikitextparser as parser
import pykakasi as kks
import unicodedata
import re

pwb._config.put_throttle = 0
site = pwb.Site()


pages = pwb.Category(site, title='Catégorie:Verbes godan en japonais')
testpage = pwb.Page(site, '萌える')
filename = 'japflexion_data_ichi_ru.txt'
kks = kks.kakasi()
# regexkana=re.compile(r'[\u4e00-\u9fff]+')


non_kana_regex = re.compile(r'[^\u3040-\u309f\u30A0-\u30FF\u31F0-\u31FF]')

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join(c for c in nfkd_form if not unicodedata.combining(c))

def log_processed(infinitive, filename="processed_pages.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(infinitive + "\n")

toggle_first_tab = True
new_total = 0



for page in pages.linkedPages():
    for line in page.text.splitlines():
        if line.startswith("{{ja-ka}}"):
            if non_kana_regex.search(page.title()):










#   new_total = increment_counter()
#print(new_total)