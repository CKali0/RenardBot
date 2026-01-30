import pywikibot as pwb
import wikitextparser as parser
import pykakasi as kks
import unicodedata

from task_japconj_ru import suffixed_page

pwb._config.put_throttle = 0
site = pwb.Site()
filename = "plflex_noun_mi_i_data.txt"


def load_conjugations(filename):
    conjugations = {}
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # allow comments / blank lines
                continue
            suffix, defs = line.split("|", 1)
            suffix = suffix.strip()
            # preserve the double apostrophes exactly as in the file
            definitions = [d.strip() for d in defs.split(",")]
            conjugations[suffix] = definitions
    return conjugations

def makepage(ns, flex, definitions):
    lines = [
        "== {{langue|pl}} ==",
        "=== {{S|nom|pl|flexion}} ===",
        f"{{{{pl-décl-nom-mi-i|{ns}}}}}",
        f"'''{flex}''' {{{{pron||pl}}}} {{{{m|i}}}}"
    ]
    for definition in definitions:
        lines.append("# " + definition + " [[" + ns + "]].")
        lines.append("#* {{exemple|lang=pl}}")
    return lines

def log_processed(infinitive, filename="processed_pages.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(infinitive + "\n")

def increment_counter(filename="plflexcounter.txt"):
    # Try to read the current count, if the file exists
    try:
        with open(filename, "r", encoding="utf-8") as f:
            count = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        count = 0

    # Increment
    count += 1

    # Save back
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(count))

    return count

template = pwb.Page(site, 'Modèle:pl-décl-nom-mi-i')
for page in template.embeddedin():
    ns = page.title()
    if "{{S|nom|pl|flexion}}" not in page.text and "{{S|nom commun|pl|flexion}}" not in page.text:
        for line in page.text.splitlines():
            if line.startswith("{{pl-décl-nom-mi-i"):
                declensions = load_conjugations(filename)
                for(suffix, definitions) in declensions.items():
                    suffixed_page = pwb.Page(site, ns + suffix)
                    if not suffixed_page.exists():
                        definitions = declensions[suffix]
                        lines = makepage(ns, suffixed_page.title(), definitions)
                        suffixed_page.text = "\n".join(lines)
                        suffixed_page.save("Création d'une flexion en polonais")
                        new_total = increment_counter()
print(new_total)
