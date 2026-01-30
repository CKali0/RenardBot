import pywikibot as pwb
import wikitextparser as parser
import unicodedata

pwb._config.put_throttle = 0
site = pwb.Site()
currLength = 5

scrap = pwb.Category(site, title='Catégorie:anglais')
nList = []

for page in scrap:
    if len(page.title()) == currLength:
        nList.append(page.title())

currID = 0
for title in nList:
    title.strip(currID)