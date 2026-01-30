import pywikibot as pwb
import re

pwb._config.put_throttle = 0
site = pwb.Site()
pattern = r"^'''(.+?)'''$"
handled_language = "néerlandais"
handled_language_code = "nl"

pages = pwb.Category(site, "Catégorie:" + handled_language)


def handle_page(page):
    page_text = page.text
    page_lines = page_text.splitlines()
    in_section = False
    in_main = False
    level_four = False
    new_page_lines = []
    for i, line in enumerate(page_lines):
        if line == f"== {{{{langue|{handled_language_code}}}}} ==":
            in_section = True
        elif in_section and line.startswith("== ") and not line == f"== {{{{langue|{handled_language_code}}}}} ==":
            in_section = False

        if in_section:
            if line.startswith("=== "):
                in_main = True
            if line.startswith("==== "):
                in_main = False
            if re.match(pattern, line) and in_main:
                new_page_lines.append(line + f" {{{{pron||{handled_language_code}}}}}")
                continue

            if line.startswith("# "):
                if len(page_lines) <= i + 1 or ("{{exemple" not in page_lines[i + 1] and "#*" not in page_lines[i + 1]):
                    new_page_lines.append(line)
                    new_page_lines.append(f"#* {{{{exemple|lang={handled_language_code}}}}}")
                    continue

                if not line.endswith("."):
                    new_page_lines.append(line + ".")
                    continue

        new_page_lines.append(line)
    page.text = '\n'.join(new_page_lines)
    page.save('Formattage de la section en ' + handled_language)

good_place = False
#good_place = True
for page in pages.articles():

    if page.title().startswith("deb"):
        good_place = True

    if good_place:
        if "{{S|symbole" not in page.text and "{{S|lettre" not in page.text:
            handle_page(page)

