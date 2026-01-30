import pywikibot as pwb
import pywikibot.config as config
import wikitextparser as parser
import re

config.put_throttle = 0

site = pwb.Site()

page = pwb.Page(site, "Utilisateur:CKali/test2")
pagecontent = page.text

non_kana_regex = re.compile(r'[^\u3040-\u309f\u30A0-\u30FF\u31F0-\u31FF]')
mot1 = "集める"
mot2 = "影響"
mot3 = "よりも"

print(non_kana_regex.search(mot1))
print(non_kana_regex.search(mot2))
print(non_kana_regex.search(mot3))

    #with open("ja_complicated_cases.txt", "a", encoding="utf-8") as f:
        #f.write(page.title() + "\n")
