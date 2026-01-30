import pywikibot as pwb
import wikitextparser as parser

pwb._config.put_throttle = 0
site = pwb.Site()
source = pwb.Page(site, "Modèle:sv-nom-c-ind")

pages = source.embeddedin()

def makepage(sing, arg, title):
    if arg == "n=":
        temp = f"{{{{sv-nom-c-ind|{arg}|mot={sing}}}}}"
    else:
        temp = f"{{{{sv-nom-c-ind|mot={sing}}}}}"
    lines = [
        "== {{langue|sv}} ==",
        "=== {{S|nom|sv|flexion}} ===",
        temp,
        f"'''{title}''' {{{{pron||sv}}}}",
        f"# ''Singulier défini de'' {{{{lien|{sing}|sv}}}}",
        "#* {{exemple|lang=sv}}"
    ]
    newpage = pwb.Page(site, title)
    newpage.text = "\n".join(lines)
    print(newpage.text)
    #newpage.save("Création d'une flexion en suédois")

canceler = False
for page in pages:
    if page.embeddedin(namespaces=None):
        if "{{S|nom|sv|flexion" not in page.text:
            for line in page.text.splitlines():
                if line.startswith("{{sv-nom-c-ind|"):
                    template = parser.Template(line)
                    if not template.has_arg("mot"):
                        if template.has_arg("2"):
                            suffixed_page = template.get_arg("2")
                            suff = suffixed_page.plain_text().replace(page.title(), "", 1)
                            val = ""
                            if suff == "en":
                                val = "en"
                            elif suff == "n":
                                val = "n"
                            else:
                                print("Error on " + page.title())
                                canceler = True
                            if not canceler:
                                makepage(page.title(), val, suffixed_page)


                        elif template.has_arg("n"):
                            suff = "n"
                            val = "n="
                            sing = page.title()
                            suffixed_page = sing + suff
                            if not pwb.Page(site, suffixed_page).exists():
                                makepage(sing, val, suffixed_page)
                        else:
                            suff = "en"
                            val = "en"
                            sing = page.title()
                            suffixed_page = sing + suff
                            if not pwb.Page(site, suffixed_page).exists():
                                makepage(sing, val, suffixed_page)