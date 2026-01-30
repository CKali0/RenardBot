import pywikibot as pwb
import wikitextparser as wtp

pwb._config.put_throttle = 0
site = pwb.Site()

cat = pwb.Category(site, 'Catégorie:Formes de noms communs en letton')

for page in cat.articles():
    if "décl=4" not in page.text:
        continue

    new_lines = []
    changed = False

    for line in page.text.splitlines(keepends=True):
        if line.startswith("{{lv-nom") and "vs-complet=oui" in line:
            tpl = wtp.Template(line.strip())
            tpl.del_arg("vs-complet")
            new_line = tpl.string + "\n"
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)

    if changed:
        page.text = "".join(new_lines)
        page.save("Retrait du paramètre vs-complet pour les tableaux de déclinaison des noms de la quatrième déclinaison.")
