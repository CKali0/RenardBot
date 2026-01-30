# new_lv_flex.py — Latvian declensions with palatalization, vs-complet, template reconstruction, and multi-definition handling

import pywikibot as pwb
import wikitextparser as parser
from collections import defaultdict
import csv
import json
from pathlib import Path

pwb._config.put_throttle = 0
site = pwb.Site()
testpage = pwb.Page(site, "lietotājs")

# ---------- Data loaders ----------

def load_declensions(filename):
    """
    CSV columns (required): decl, number, case, suffix, definition
    Optional column:
      - palatal: "1", "2", "1,2" for which numbers allow palatalization
    """
    declensions = defaultdict(dict)  # (decl, number) -> case -> {suffix, definition, palatal_nums}
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["decl"]), row["number"])
            palatal_raw = row.get("palatal", "").strip()
            if palatal_raw:
                pal_nums = [int(x) for x in palatal_raw.split(",") if x.strip().isdigit()]
            else:
                pal_nums = []
            declensions[key][row["case"]] = {
                "suffix": row["suffix"],
                "definition": row["definition"],
                "palatal_nums": pal_nums,
            }
    return declensions

def load_meta(filename):
    """
    Optional JSON to mirror Lua’s per-variant metadata.
    Example:
    {
      "1-s": { "vsMayDropEnding": true },
      "2-as": { "vsMayDropEnding": false }
    }
    """
    p = Path(filename)
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)

# ---------- Morphology helpers ----------

def decl_key(word: str, decl: int) -> str:
    tail = word[-2:] if decl in (2, 3) else word[-1:]
    return f"{decl}-{tail}"

def compute_root(ns: str, decl: int) -> str:
    if decl in (2, 3):
        return ns[:-2]
    return ns[:-1]

def mutate_root(root: str, modify: bool, palatal: str) -> str:
    if not palatal:
        return root
    if modify:
        return root[:-1] + palatal
    return root + palatal

# ---------- Core generation ----------

def generate_forms(ns, decl, mode, palatal, remplacer, vs_complet, declensions, meta):
    """
    Build dictionary mapping form string -> list of definitions.
    """
    root = compute_root(ns, decl)
    key = decl_key(ns, decl)
    vs_may_drop = bool(meta.get(key, {}).get("vsMayDropEnding", False))

    # sanity / useless param checks
    if remplacer and not palatal:
        print("Paramètre « remplacer » superflu, palatale manquante → ignoré.")
        remplacer = False
    if vs_complet and not vs_may_drop:
        print("Paramètre « vs-complet » superflu pour cette variante → ignoré.")
        vs_complet = False

    want_sg = (mode == "sing") or (mode == "none")
    want_pl = (mode == "plur") or (mode == "none")

    forms = defaultdict(list)
    any_palatal_applied = False

    for number in ("sg", "pl"):
        if number == "sg" and not want_sg:
            continue
        if number == "pl" and not want_pl:
            continue

        num_index = 1 if number == "sg" else 2

        for case, data in declensions[(decl, number)].items():
            suffix = data["suffix"]
            definition = data["definition"]
            form_root = root

            pal_nums = data.get("palatal_nums", [])
            if palatal and (num_index in pal_nums):
                form_root = mutate_root(root, remplacer, palatal)
                any_palatal_applied = True

            if case == "vs" and number == "sg" and (not vs_complet) and vs_may_drop:
                form = root  # drop suffix
            else:
                form = form_root + suffix

            forms[form].append(definition)

    if palatal and not any_palatal_applied:
        print("Paramètre « palatale » superflu pour ces formes → ignoré.")

    return forms

# ---------- Template reconstruction ----------

def build_lv_nom_template(ns, decl, palatal, remplacer, vs_complet, mode):
    """
    Reconstruct {{lv-nom}} with only non-default arguments.
    Defaults from documentation:
      palatale: "" (unspecified)
      remplacer: false
      vs-complet: false
      mode: "none"
    """
    parts = [f"lv-nom|{ns}|décl={decl}"]
    if palatal:
        parts.append(f"palatale={palatal}")
    if remplacer:
        parts.append("remplacer=oui")
    if vs_complet:
        parts.append("vs-complet=oui")
    if mode != "none":
        parts.append(f"mode={mode}")
    return "{{" + "|".join(parts) + "}}"

# ---------- Page plumbing ----------

def handle_page(page):
    vs_complet = False
    decl = 0
    palatale = ""
    remplacer = False
    probleme = False
    mode = "none"
    ns = page.title()

    for line in page.text.splitlines():
        if line.startswith('{{lv-nom'):
            template = parser.Template(line)
            decl_raw = template.get_arg("décl")
            decl = int(decl_raw.value.strip()) if decl_raw is not None else 0

            vs_complet = template.has_arg("vs-complet")
            remplacer = template.has_arg("remplacer")
            palatale = template.get_arg("palatale").value.strip() if template.has_arg("palatale") else ""
            mode = template.get_arg("mode").value.strip() if template.has_arg("mode") else "none"

            if any(template.has_arg(p) for p in ("ns","np","as","ap","gs","gp","ds","dp","is","ip","ls","lp","vs","vp")):
                probleme = True

            if decl not in (1,2,3,4,5,6):
                probleme = True

            if not probleme:
                makepages(ns, decl, mode, palatale, remplacer, vs_complet)

def makepages(ns, decl, mode, palatale, remplacer, vs_complet):
    declensions = load_declensions("lv_flex_data.csv")
    meta = load_meta("lv_decl_meta.json")
    forms = generate_forms(
        ns=ns,
        decl=decl,
        mode=mode,
        palatal=palatale,
        remplacer=remplacer,
        vs_complet=vs_complet,
        declensions=declensions,
        meta=meta
    )

    for form, definitions in forms.items():
        lines = [
            "== {{langue|lv}} ==",
            "=== {{S|nom|lv|flexion}} ===",
            build_lv_nom_template(ns, decl, palatale, remplacer, vs_complet, mode),
            f"'''{form}''' {{{{pron||lv}}}}"
        ]
        for definition in definitions:
            lines.append(f"# {definition} {{{{lien|{ns}|lv}}}}.")
            lines.append("#* {{exemple|lang=lv}}")

        page = pwb.Page(site, form)
        if not page.exists():
            page.text = "\n".join(lines)
            page.save("Création d'une flexion en letton")

# entry
handle_page(testpage)
