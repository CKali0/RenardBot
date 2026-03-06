import pywikibot as pwb
import wikitextparser as parser
import pykakasi as kks
import unicodedata

pwb._config.put_throttle = 0
site = pwb.Site()


laterpages = pwb.Category(site, title='Catégorie:Verbes godan en japonais')
testpage = pwb.Page(site, '泣く')
filename = 'japflexion_data_ku.txt'
kks = kks.kakasi()

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join(c for c in nfkd_form if not unicodedata.combining(c))

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

def makepage(suffix, definitions, infinitive, root_kanji, root_hiragana):
    new_hira = root_hiragana + suffix
    new_page_title = root_kanji + suffix
    lines = [
        "== {{langue|ja}} ==",
        "=== {{S|verbe|ja|flexion}} ===",
        f"{{{{ja-trans|hira={new_hira}}}}}",
        f"{{{{ja-mot|{new_page_title}|{new_hira}}}}} {{{{ja-pron|{new_hira}}}}} {{{{ja-verbe-godan|{infinitive}}}}}"
    ]
    for definition in definitions:
        lines.append("# " + definition + " [[" + infinitive + "]].")
        lines.append("#* {{exemple|lang=ja}}")


    lines.append("\n{{clé de tri|" + remove_accents(new_hira) + "}}")
    return lines

def log_processed(infinitive, filename="processed_pages.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(infinitive + "\n")

def increment_counter(filename="jpflexcounter.txt"):
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

toggle_first_tab = True
new_total = 0

for i, line in enumerate(testpage.text.splitlines()):
    if toggle_first_tab:
        if line.startswith('{{ja-trans'):
            toggle_first_tab = False
            template = parser.Template(line)
            fullhiragana = str(template.get_arg('hira'))
            fullhiragana = fullhiragana.split("=", 1)[1]
            roothiragana = fullhiragana.split("く", 1)[0]
            rootkanji = testpage.title().split("く", 1)[0]

            conjugations = load_conjugations(filename)
            log_processed("\n" + testpage.title())

            for suffix, definitions in conjugations.items():
                suffixed_page = pwb.Page(site, rootkanji + suffix)
                if not suffixed_page.exists():
                    lines = makepage(suffix, definitions, testpage.title(), rootkanji, roothiragana)
                    suffixed_page.text = "\n".join(lines)
                    suffixed_page.save("Création d'une flexion en japonais")
                    new_total = increment_counter()
print(new_total)