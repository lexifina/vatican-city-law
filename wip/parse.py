"""Vatican City State law: cache -> corpus.json (gitlaw-VA).

Reads only .cache/raw (filled by fetch.py from sources.json); no network. Deterministic.
Text comes from the publisher's own PDF text layer (no OCR here) and, for the 2025 motu proprio,
from the Governatorato's HTML page.

    python -X utf8 parse.py            # writes corpus.json and corpus.d/50-legge-viii.json atomically
"""
import hashlib
import html
import json
import os
import re
import sys

import fitz  # PyMuPDF: reads the PDF text layer only

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, ".cache", "raw")
RETRIEVED = "2026-10-28"

with open(os.path.join(HERE, "sources.json"), encoding="utf-8") as f:
    DOCS = {d["id"]: d for d in json.load(f)["documents"]}


def raw(doc_id):
    url = DOCS[doc_id]["url"]
    with open(os.path.join(RAW, hashlib.sha256(url.encode()).hexdigest()), "rb") as f:
        b = f.read()
    return url, b, hashlib.sha256(b).hexdigest()


# Character errors in the publisher's own text layer, corrected by hand (each listed in decisions).
FIXES = {
    "lf-2000": [("I1 potere", "Il potere")],
    "lxxi-2008": [("Ada Apostolicae", "Acta Apostolicae"), ("entrata ih vigore", "entrata in vigore"),
                  ("а)", "a)"), ("б)", "6)")],
}


def norm(s):
    s = s.replace(" ", " ").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"').replace("—", "–")
    s = s.replace("\t", " ")
    return re.sub(r" {2,}", " ", s).strip()


def pdf_lines(doc_id):
    url, b, sha = raw(doc_id)
    d = fitz.open(stream=b, filetype="pdf")
    text = "\n".join(p.get_text() for p in d)
    for a, z in FIXES.get(doc_id, []):
        assert a in text, (doc_id, a)
        text = text.replace(a, z)
    lines = [norm(l) for l in text.split("\n")]
    # drop empty lines and bare page numbers
    lines = [l for l in lines if l and not re.fullmatch(r"\d{1,2}", l)]
    return url, sha, lines


MARK = re.compile(r"^(\d+\.|[a-z]\)|\d+\)|-)(\s|$)")


def paragraphs(lines, numbered=True):
    """Join wrapped PDF lines into one paragraph per line.

    numbered=True: a paragraph starts only at a marker (1. / a) / 1) / -).
    numbered=False (preambles, closing formulas): a paragraph also ends at a line ending in . or :"""
    out = []
    pending_marker = False
    for l in lines:
        starts = bool(MARK.match(l))
        if not out or (starts and not pending_marker) or (not numbered and out and re.search(r"[.:;]$", out[-1])):
            out.append(l)
        else:
            out[-1] = out[-1] + " " + l
        pending_marker = bool(re.fullmatch(r"(\d+\.|[a-z]\)|\d+\)|-)", l))
    return [re.sub(r" {2,}", " ", p).strip() for p in out]


def unit(label, kind, body_lines, heading=None, numbered=True, extra=None):
    paras = paragraphs(body_lines, numbered)
    head = [f"# {heading or label}"] + (extra or [])
    return {"label": label, "kind": kind, "text": "\n".join(head + paras) + "\n"}


ART = re.compile(r"^(?:Art\.|ARTICOLO|Articolo)\s+(\d+)$")
TIT = re.compile(r"^(?:TITOLO|Titolo)\s+([IVXL]+)$")
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman(s):
    n = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        n += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return n


def heading_case(s):
    s = s.strip()
    return s[:1].upper() + s[1:].lower()


def split_act(lines, start, end_markers, rubrics=False):
    """lines[start:] -> units for titles and articles, up to the first line starting with an end marker.
    Returns (units, index of the end line)."""
    units = {}
    cur = None
    i = start
    while i < len(lines):
        l = lines[i]
        if any(l.startswith(m) for m in end_markers):
            break
        m = ART.match(l)
        t = TIT.match(l)
        if m:
            n = int(m.group(1))
            cur = {"key": f"art-{n:03d}", "label": f"Art. {n}", "lines": [], "extra": []}
            units[cur["key"]] = cur
            if rubrics and i + 1 < len(lines) and lines[i + 1].startswith("("):
                rub = lines[i + 1]
                i += 1
                while not rub.endswith(")"):
                    i += 1
                    rub += " " + lines[i]
                cur["extra"] = [rub]
        elif t:
            n = roman(t.group(1))
            name = lines[i + 1]
            i += 1
            units[f"titolo-{n:02d}"] = {"key": f"titolo-{n:02d}", "label": f"Titolo {t.group(1)}",
                                        "text": f"# Titolo {t.group(1)}\n{heading_case(name)}\n"}
            cur = None
        elif cur is not None:
            cur["lines"].append(l)
        i += 1
    out = {}
    for k, u in units.items():
        if "text" in u:
            out[k] = {"label": u["label"], "kind": "heading", "text": u["text"]}
        else:
            out[k] = unit(u["label"], "art", u["lines"], extra=u["extra"])
    return out, i


def index_of(lines, pred, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise ValueError("not found")


# ------------------------------------------------------------------ Legge fondamentale

def lf_2000():
    url, sha, L = pdf_lines("lf-2000")
    a1 = index_of(L, lambda l: l == "Art. 1")
    units, end = split_act(L, a1, ["La presente Legge fondamentale sostituisce"])
    form = index_of(L, lambda l: l.startswith("Comandiamo"), end)
    units["disposizione-finale"] = unit("Disposizione finale", "final", L[end:form], numbered=False)
    units["formula-finale"] = unit("Formula di promulgazione", "final", L[form:], numbered=False)
    return url, sha, units


def lf_new(doc_id, sovereign):
    url, sha, L = pdf_lines(doc_id)
    p0 = index_of(L, lambda l: l == sovereign) + 1
    t1 = index_of(L, lambda l: bool(TIT.match(l)), p0)
    units, end = split_act(L, t1, ["Comando che"])
    stop = next((i for i in range(end, len(L)) if L[i] == "ALLEGATI"), len(L))
    units["preambolo"] = unit("Preambolo", "preamble", L[p0:t1], numbered=False)
    units["formula-finale"] = unit("Formula di promulgazione", "final", L[end:stop], numbered=False)
    return url, sha, units


def mp_2025_text():
    """The new art. 8, n. 1 as printed in the motu proprio of 19 November 2025 (Governatorato page)."""
    url, b, sha = raw("mp-2025-11-19")
    t = html.unescape(re.sub(r"<[^>]+>", " ", b.decode("utf-8")))
    t = norm(" ".join(t.split()))
    m = re.search(r'"Art\. 8, n\. 1: (La Pontificia Commissione per lo Stato della Città del Vaticano è composta '
                  r'[^"]+?quinquennio)"', t)
    assert m, "motu proprio wording not found"
    return url, sha, m.group(1) + "."


# ------------------------------------------------------------------ Legge sulle fonti del diritto (LXXI)

def lxxi():
    url, sha, L = pdf_lines("lxxi-2008")
    p0 = index_of(L, lambda l: l == "BENEDETTO PP. XVI") + 1
    a1 = index_of(L, lambda l: l == "Art. 1", p0)
    units, end = split_act(L, a1, ["Comandiamo"], rubrics=True)
    units["preambolo"] = unit("Preambolo", "preamble", L[p0:a1], numbered=False)
    units["formula-finale"] = unit("Formula di promulgazione", "final", L[end:], numbered=False)
    return url, sha, units


# ------------------------------------------------------------------ Legge VIII (2013)

def viii():
    url, sha, L = pdf_lines("viii-2013")
    p0 = index_of(L, lambda l: l.startswith("LA PONTIFICIA COMMISSIONE"))
    p1 = index_of(L, lambda l: l == "LEGGE", p0)
    t1 = index_of(L, lambda l: bool(TIT.match(l)), p1)
    units, end = split_act(L, t1, ["Il testo della presente legge"], rubrics=True)
    units["preambolo"] = unit("Preambolo", "preamble", L[p0:p1 + 1], numbered=False)
    units["formula-finale"] = unit("Formula di promulgazione", "final", L[end:], numbered=False)
    return url, sha, units


def diff_credits(prev, cur, law):
    keys = set(prev) | set(cur)
    return {k: [law] for k in sorted(keys) if prev.get(k) != cur.get(k)}


COUNTRY = {
    "code": "VA", "name": "Vatican City", "slug": "vatican-city", "lang": "it",
    "tz": "Europe/Vatican", "future_branch": "futuro",
    "publisher": {"name": "Governatorato dello Stato della Città del Vaticano (vaticanstate.va)",
                  "email": "governatorato@vaticanstate.invalid"},
    "default_in_force_rule": {
        "text": "Legge sulle fonti del diritto, 1 ottobre 2008, n. LXXI, art. 2, n. 2: \"Le leggi entrano in vigore "
                "il settimo giorno successivo alla loro pubblicazione, salvo che le leggi stesse stabiliscano un "
                "diverso termine.\" Every law used here names its own day or rule of entry into force, which is used.",
        "source": DOCS["lxxi-2008"]["url"]},
    "licence_note": "Texts: Governatorato dello Stato della Città del Vaticano, vaticanstate.va (\"Copyright © 2026 by "
                    "Governatorato dello Stato della Città del Vaticano | Tutti i diritti riservati\"); check copies "
                    "from vatican.va (© Dicastero per la Comunicazione - Libreria Editrice Vaticana).",
}

LAWS = {
    "lf-2000": {"label": "Legge fondamentale 26.11.2000", "kind": "law",
                "title": "Legge fondamentale dello Stato della Città del Vaticano (Giovanni Paolo II, 26 novembre 2000)",
                "enacted": "2000-11-26", "published": None, "url": DOCS["lf-2000"]["url"],
                "temporary_until": None, "restores": None, "note": None},
    "lf-2023": {"label": "Legge fondamentale 13.5.2023", "kind": "law",
                "title": "Legge fondamentale dello Stato della Città del Vaticano (Francesco, 13 maggio 2023)",
                "enacted": "2023-05-13", "published": None, "url": DOCS["lf-2023"]["url"],
                "temporary_until": None, "restores": None, "note": None},
    "mp-2025-11-19": {"label": "Motu proprio 19.11.2025", "kind": "law",
                      "title": "Lettera apostolica in forma di motu proprio sulla composizione e presidenza della "
                               "Pontificia Commissione per lo Stato della Città del Vaticano (Leone XIV, 19 novembre 2025)",
                      "enacted": "2025-11-19", "published": "2025-11-21", "url": DOCS["mp-2025-11-19"]["url"],
                      "temporary_until": None, "restores": None, "note": None},
    "lf-2026": {"label": "Legge fondamentale 31.7.2026", "kind": "law",
                "title": "Legge fondamentale dello Stato della Città del Vaticano (Leone XIV, 31 luglio 2026)",
                "enacted": "2026-07-31", "published": "2026-07-31", "url": DOCS["lf-2026"]["url"],
                "temporary_until": None, "restores": None, "note": None},
    "lxxi-2008": {"label": "Legge n. LXXI (2008)", "kind": "law",
                  "title": "N. LXXI - Legge sulle fonti del diritto (1 ottobre 2008)",
                  "enacted": "2008-10-01", "published": None, "url": DOCS["lxxi-2008"]["url"],
                  "temporary_until": None, "restores": None, "note": None},
}

LAWS_VIII = {
    "viii-2013": {"label": "Legge n. VIII (2013)", "kind": "law",
                  "title": "Legge n. VIII - Norme complementari in materia penale (11 luglio 2013)",
                  "enacted": "2013-07-11", "published": None, "url": DOCS["viii-2013"]["url"],
                  "temporary_until": None, "restores": None, "note": None},
}


def build():
    u0, s0, v2000 = lf_2000()
    u1, s1, v2023 = lf_new("lf-2023", "FRANCESCO")
    um, sm, art8_1 = mp_2025_text()
    u2, s2, v2026 = lf_new("lf-2026", "LEONE XIV")

    v2025 = dict(v2023)
    old = v2023["art-008"]["text"].split("\n")
    assert old[1].startswith("1. "), old
    new8 = "\n".join([old[0], "1. " + art8_1] + old[2:])
    v2025["art-008"] = {**v2023["art-008"], "text": new8}

    lf = {
        "slug": "legge-fondamentale", "short": "LF",
        "title": "Legge fondamentale dello Stato della Città del Vaticano",
        "url": "https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa/leggi-fondamentali-dello-stato.html",
        "first_law": "lf-2000", "earlier_laws": [],
        "versions": [
            {"from": "2001-02-22", "source_url": u0, "sha256": s0, "units": v2000, "credits": {},
             "note": "Legge fondamentale of 26 November 2000, in force 22 February 2001 by its own final clause. "
                     "The publisher's copy does not reproduce the preamble verbatim, so this version has no preamble."},
            {"from": "2023-06-07", "source_url": u1, "sha256": s1, "units": v2023,
             "credits": diff_credits(v2000, v2023, "lf-2023"),
             "note": "Legge fondamentale of 13 May 2023 replaces the 2000 law in full (art. 24, n. 1) and enters "
                     "into force on 7 June 2023 (art. 24, n. 3)."},
            {"from": "2025-11-21", "source_url": um, "sha256": sm, "units": v2025,
             "credits": diff_credits(v2023, v2025, "mp-2025-11-19"),
             "note": "Art. 8, n. 1 replaced by the motu proprio of 19 November 2025, in force on the day of its "
                     "publication in L'Osservatore Romano; the Holy See Press Office made it public on 21 November 2025."},
            {"from": "2026-07-31", "source_url": u2, "sha256": s2, "units": v2026,
             "credits": diff_credits(v2025, v2026, "lf-2026"),
             "note": "Legge fondamentale of 31 July 2026 replaces the 2023 law in full (art. 25, n. 1) and enters "
                     "into force immediately (art. 25, n. 3); published that day in the Holy See Press Office "
                     "Bulletin n. 0611."},
        ],
    }

    ul, sl, vl = lxxi()
    fonti = {
        "slug": "legge-fonti-diritto", "short": "LFD",
        "title": "Legge sulle fonti del diritto (N. LXXI, 1 ottobre 2008)",
        "url": DOCS["lxxi-2008"]["url"], "first_law": "lxxi-2008", "earlier_laws": [],
        "versions": [{"from": "2009-01-01", "source_url": ul, "sha256": sl, "units": vl, "credits": {},
                      "note": "As enacted; in force 1 January 2009 by its own art. 13. The publisher lists no "
                              "amending act and offers no consolidated text."}],
    }

    uv, sv, vv = viii()
    leggeviii = {
        "slug": "legge-viii-2013", "short": "L. VIII/2013",
        "title": "Legge n. VIII - Norme complementari in materia penale (11 luglio 2013)",
        "url": DOCS["viii-2013"]["url"], "first_law": "viii-2013", "earlier_laws": [],
        "versions": [{"from": "2013-09-01", "source_url": uv, "sha256": sv, "units": vv, "credits": {},
                      "note": "As enacted; in force 1 September 2013 by its own art. 55. Later amending laws are "
                              "not yet applied (see the README)."}],
    }

    sources = [
        {"name": "Governatorato dello Stato della Città del Vaticano: Legislazione e normativa (vaticanstate.va)",
         "url": "https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa.html",
         "retrieved": RETRIEVED, "requests": None,
         "licence": "Copyright © 2026 by Governatorato dello Stato della Città del Vaticano | Tutti i diritti riservati",
         "notes": "Official PDFs of each law (publisher's own text layer) and the Governatorato news page carrying "
                  "the motu proprio of 19 November 2025. No consolidated texts and no point-in-time versions."},
        {"name": "La Santa Sede (vatican.va) and Sala Stampa della Santa Sede (press.vatican.va)",
         "url": "https://www.vatican.va/",
         "retrieved": RETRIEVED, "requests": None,
         "licence": "© Dicastero per la Comunicazione - Libreria Editrice Vaticana",
         "notes": "HTML copies of the 2023 and 2026 Fundamental Laws, used only to check the parsed text; Bulletin "
                  "n. 0611 of 31 July 2026 for the publication day of the 2026 law."},
    ]
    with open(os.path.join(HERE, ".cache", "requests.jsonl"), encoding="utf-8") as f:
        reqs = [json.loads(l) for l in f if l.strip()]
    sources[0]["requests"] = sum(1 for r in reqs if "vaticanstate.va" in r["url"])
    sources[1]["requests"] = sum(1 for r in reqs if "vatican.va" in r["url"] and "vaticanstate" not in r["url"])

    decisions = [
        "The Fundamental Law is one act, legge-fondamentale, whose text is replaced in full by the laws of 13 May 2023 "
        "and 31 July 2026; each replacement is a version credited to the replacing law, so blame shows which law "
        "wrote each article.",
        "The first Fundamental Law (7 June 1929, n. I) is not on the official site with a text layer, so the history "
        "starts with the law of 26 November 2000 in force 22 February 2001.",
        "No amendment of the 2000 law was found on the official site; the 2023 law was amended once, by the motu "
        "proprio of 19 November 2025 (art. 8, n. 1), applied by replaying it on the 2023 text.",
        "The motu proprio of 19 November 2025 enters into force on the day of its publication in L'Osservatore "
        "Romano; the source gives 21 November 2025 as the day the Holy See Press Office made it public, used as "
        "the in-force day (the newspaper's issue date was not checked).",
        "The law of 31 July 2026 enters into force 'immediatamente' and was published in the Holy See Press Office "
        "Bulletin n. 0611 of 31 July 2026, so its in-force day is 31 July 2026.",
        "Every in-force day comes from the law's own clause (2000: 22 February 2001; 2023: 7 June 2023; 2008 LXXI: "
        "1 January 2009; 2013 VIII: 1 September 2013), which overrides the seven-day rule of LXXI art. 2.",
        "Units are articles (art-NNN), title headings (titolo-NN), the preamble (preambolo), and the closing "
        "promulgation formula with date and signature (formula-finale). The 2000 law's unnumbered final clauses "
        "(replacement and entry into force) are the unit disposizione-finale.",
        "The 2000 law's preamble is left out: the publisher's copy paraphrases it inside a press introduction "
        "rather than reproducing it.",
        "Annexes A-C (flag, coat of arms, seal) are left out of every version: they are drawn models, and only "
        "the 2023 copy adds short captions to them.",
        "Title headings are set in sentence case (TITOLO I / DISPOSIZIONI GENERALI and Titolo I / Disposizioni "
        "Generali both read 'Titolo I / Disposizioni generali'), so a change of typesetting is not a change of law.",
        "Typesetting is normalised: NBSP to space, runs of spaces collapsed, curly quotes and apostrophes to "
        "straight ones, em dashes to en dashes, PDF line wraps joined into one paragraph per line, page numbers "
        "dropped.",
        "Character errors in the publisher's own PDF text layer are corrected by hand: 2000 law art. 7 'I1 potere' "
        "-> 'Il potere'; LXXI 'Ada Apostolicae' -> 'Acta Apostolicae', 'entrata ih vigore' -> 'entrata in vigore', "
        "Cyrillic 'а)' -> 'a)' and 'б)' -> '6)' in art. 12.",
        "Check against vatican.va (verify.py, verification.json): every line of the 2026 law matches the HTML copy; "
        "in the 2023 law one line differs, the preamble's 'Vaticano che, il Trattato' (vaticanstate.va PDF, kept) "
        "against 'Vaticano, che il Trattato' (vatican.va HTML).",
        "The Legge sulle fonti del diritto (LXXI) is built as enacted: the official site lists no amending act and "
        "gives no consolidated text.",
        "Legge n. VIII of 2013 (criminal law) sits in corpus.d/50-legge-viii.json, unverified, because later laws "
        "amended it (e.g. N. CCCXXIX/CCCXXXVI of 2019 and N. DXXXI) and those changes are not yet replayed.",
    ]
    ai_use = ["Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote fetch.py and parse.py, chose the sources and "
              "made the decisions above. No model wrote or edited legal text; all law text is parsed by code from "
              "the official files. No model runs at build time."]

    corpus = {"country": COUNTRY, "sources": sources, "laws": LAWS, "acts": [lf, fonti], "applies": [],
              "decisions": decisions, "ai_use": ai_use}
    part = {"laws": LAWS_VIII, "acts": [leggeviii]}
    return corpus, part


def write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


if __name__ == "__main__":
    corpus, part = build()
    write_atomic(os.path.join(HERE, "corpus.json"), corpus)
    if "--no-viii" not in sys.argv:
        write_atomic(os.path.join(HERE, "corpus.d", "50-legge-viii.json"), part)
    for a in corpus["acts"] + part["acts"]:
        print(a["slug"], [(v["from"], len(v["units"])) for v in a["versions"]])
