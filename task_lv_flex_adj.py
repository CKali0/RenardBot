import pywikibot as pwb
import wikitextparser as parser
import pykakasi as kks
import unicodedata

pwb._config.put_throttle = 0
site = pwb.Site()


laterpages = pwb.Category(site, title='Catégorie:Adjectifs en letton')
testpage = pwb.Page(site, '狩る')
filename = 'lvadjflex_data.txt'
kks = kks.kakasi()

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

def makepage(ns, root, flex, definitions):
    lines = [
        "== {{langue|lv}} ==",
        "=== {{S|adjectif|lv|flexion}} ===",
        f"'''{flex}''' {{{{pron||lv}}}}"
    ]
    for definition in definitions:
        lines.append("# " + definition + " [[" + ns + "]].")
        lines.append("#* {{exemple|lang=lv}}")

    lines.append("")
    lines.append("==== {{S|déclinaison}} ====")
    lines.append(f"{{{{lv-décl-adj-s|{root}}}}}")
    return lines

def log_processed(infinitive, filename="processed_pages.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(infinitive + "\n")

def increment_counter(filename="lvadjflexcounter.txt"):
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

page = pwb.Page(site, "fanātisks")
ns = page.title()
for line in page.text.splitlines():
    if line.startswith("{{lv-décl-adj-s") or line.startswith("{{lv-décl-adj-š"):
        template = parser.Template(line)
        root = template.get_arg("1").value
        declensions = load_conjugations(filename)
        for(suffix, definitions) in declensions.items():
            suffixed_page = pwb.Page(site, root + suffix)
            if not suffixed_page.exists():
                definitions = declensions[suffix]
                lines = makepage(ns, root, suffixed_page.title(), definitions)
                suffixed_page.text = "\n".join(lines)
                suffixed_page.save("Création d'une flexion en letton")
                new_total = increment_counter()
print(new_total)
