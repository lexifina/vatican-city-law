"""Check parsed units against a second official copy (gitlaw-VA).

The 2023 and 2026 Fundamental Laws are also published as HTML on vatican.va. Every unit body
(paragraphs without the '# ' heading line) must appear word for word in that copy, after the same
typesetting normalisation, with all whitespace and letter case ignored.

    python -X utf8 verify.py      # prints mismatches; writes verification.json
"""
import hashlib
import html
import json
import os
import re

import parse

HERE = os.path.dirname(os.path.abspath(__file__))


def flat(s):
    s = parse.norm(s).replace("–", "-").replace("«", '"').replace("»", '"')
    s = re.sub(r"\s+", "", s)  # HTML tags split words and punctuation arbitrarily: compare without spaces
    return s.lower()


def html_text(doc_id):
    url, b, _ = parse.raw(doc_id)
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return url, flat(t)


def check(units, doc_id):
    url, hay = html_text(doc_id)
    bad = []
    for k, u in sorted(units.items()):
        body = u["text"].split("\n")[1:]
        for line in body:
            if not line.strip():
                continue
            # a lettered or numbered marker may be set as a list item in HTML: compare without it
            probe = flat(re.sub(r"^(\d+\.|[a-z]\)|\d+\))\s+", "", line))
            if probe not in hay:
                bad.append({"unit": k, "line": line[:160]})
    return {"source": url, "units": len(units), "mismatched_lines": bad}


if __name__ == "__main__":
    _, _, v23 = parse.lf_new("lf-2023", "FRANCESCO")
    _, _, v26 = parse.lf_new("lf-2026", "LEONE XIV")
    res = {"lf-2023": check(v23, "lf-2023-va"), "lf-2026": check(v26, "lf-2026-va")}
    for k, r in res.items():
        print(k, r["units"], "units,", len(r["mismatched_lines"]), "mismatched lines")
        for b in r["mismatched_lines"]:
            print("   ", b)
    with open(os.path.join(HERE, "verification.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
