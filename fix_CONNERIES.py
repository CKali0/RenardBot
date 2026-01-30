import pywikibot as pwb

pwb._config.put_throttle = 0
site = pwb.Site()

def handle_page(page):
    if page.title().endswith("けれ"):
        new_text = ""
        rem_next_line = False
        for line in page.text.splitlines():
            if "Forme impérative de" in line:
                rem_next_line = True
                continue
            if rem_next_line:
                rem_next_line = False
                continue
            else:
                new_text += (line + "\n")
        return new_text
    return "empty"

allpages = pwb.Category(site, title="Catégorie:Adjectifs variables en japonais")
new_text = ""
rem_next_line = False
for page in allpages.articles(recurse=True):
    new_text = handle_page(page)
    if new_text != "empty":
        page.text = new_text
        page.save("Réparation d'une erreur de RenardBot")
