import pywikibot as pwb
import re

pwb._config.put_throttle = 0
site = pwb.Site()

template = pwb.Page(site, "Modèle:ja-exemple")
pages = template.embeddedin()
pattern = re.compile(r"(?s)\{\{ja-exemple(.*?)\}\}")
for page in pages:
    if page.title() != "私" and page.title() != "俺" and page.namespace().id == 0:
        page.text = pattern.sub(r"#* {{exemple\1|lang=ja}}", page.text)
        page.save("Remplacement du modèle ja-exemple par le modèle exemple")





    #newlines = []  # reset per page
    #for line in page.text.splitlines():
    #    if line.strip() in ("{{ja-exemple}}", "{{ja-exemple|}}"):
    #        line = "#* {{exemple|lang=ja}}"
    #    newlines.append(line)
    #newtext = "\n".join(newlines)
    #if newtext != page.text:
    #    page.text = newtext
    #    page.save("Remplacement du modèle ja-exemple par le modèle exemple")