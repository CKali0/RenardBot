import pywikibot as pwb
import wikitextparser as parser
from collections import defaultdict
import csv

site = pwb.Site()
testpage = pwb.Page(site, "čehs")

def load_declensions(filename):
    declensions = defaultdict(dict)
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["decl"]), row["number"])
            declensions[key][row["case"]] = {
                "suffix": row["suffix"],
                "definition": row["definition"]
            }
    return declensions

def generate_forms(root, ns, decl, mode, declensions):
    forms = []
    for number in ("sg", "pl"):
        # skip depending on mode
        if mode == "sing" and number != "sg":
            continue
        if mode == "plur" and number != "pl":
            continue
        # mode == "none" → keep both

        for case, data in declensions[(decl, number)].items():
            form = root + data["suffix"]
            definition = data["definition"]
            forms.append({
                "title": form,
                "definition": definition,
                "case": case,
                "number": number
            })
    return forms

def handle_page(page):
    vs_complet = False
    decl = 0
    palatale = ""
    remplacer = False
    probleme = False
    mode = "none"
    root = ""
    ns = testpage.title()
    for line in page.text.splitlines():
        if line.startswith('{{lv-nom'):
            template = parser.Template(line)
            decl = template.get_arg("décl")
            if(template.has_arg("vs-complet")):
                vs_complet = True
            if(template.has_arg("remplacer")):
                remplacer = True
            if(template.has_arg("palatale")):
                palatale = template.get_arg("palatale")
            if(template.has_arg("mode")):
                mode = template.get_arg("mode")

            if any(template.has_arg(p) for p in ("ns","np","as","ap","gs","gp","ds","dp","is","ip","ls","lv","vs","vp")):
                probleme = True

            if(decl==1 or decl==4 or decl==5 or decl==6):
                root = ns[:-1]
            elif(decl==2 or decl==3):
                root = ns[:-2]
            else:
                probleme = True


            if not probleme:
                makepage(root, ns, vs_complet, decl, mode, remplacer, palatale)


def makepage(root, ns, vs_complet, decl, mode, remplacer, palatale):
    declensions = load_declensions("lv_flex_data.csv")
    forms = generate_forms(root, ns, decl, mode, declensions)
    for f in forms:
        lines = [
            "== {{langue|lv}} ==",
            "=== {{S|nom|lv|flexion}} ===",
            f"'''{f['title']}''' {{{{pron||lv}}}}",
            f"# {f['definition']} [[{ns}]].",
            "#* {{exemple|lang=lv}}"
        ]
        page = pwb.Page(site, f["title"])
        if not page.exists():
            page.text = "\n".join(lines)
            page.save("Création d'une flexion en letton")
    


    # For singular / plural, you should maybe make two separate documents. The first one contains singulars, the other, plurals. You can change certain suffixes
    # locally, that wont be an issue. Probably indicate the most standard case each time. Then, to ifs. If mode = sing or none, print sing. Then, if
    # mode = plural or none, print plural. That way if none, both appear, and the other case handles itself.
    # for palatale, look into how palatalization works exactly. I hope it's regular :p













# for ...
handle_page(testpage)