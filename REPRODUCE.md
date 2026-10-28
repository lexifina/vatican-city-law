# How this repository was made (Vatican City)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| Governatorato dello Stato della Città del Vaticano: Legislazione e normativa (vaticanstate.va) | <https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa.html> | 2026-10-28 | 15 | Copyright © 2026 by Governatorato dello Stato della Città del Vaticano | Tutti i diritti riservati |
| La Santa Sede (vatican.va) and Sala Stampa della Santa Sede (press.vatican.va) | <https://www.vatican.va/> | 2026-10-28 | 7 | © Dicastero per la Comunicazione - Libreria Editrice Vaticana |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `legge-fondamentale` | Legge fondamentale dello Stato della Città del Vaticano | 4 | 2001-02-22 to 2026-07-31 |
| `legge-fonti-diritto` | Legge sulle fonti del diritto (N. LXXI, 1 ottobre 2008) | 1 | 2009-01-01 to 2009-01-01 |

The build made 5 commits:

| Commits | Kind |
| ---: | --- |
| 2 | first version of an act |
| 3 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `futuro`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 5 laws in the record.
- 10 tags.

## Dates

Each commit is dated at noon (Europe/Vatican) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Legge sulle fonti del diritto, 1 ottobre 2008, n. LXXI, art. 2, n. 2: "Le leggi entrano in vigore il settimo giorno successivo alla loro pubblicazione, salvo che le leggi stesse stabiliscano un diverso termine." Every law used here names its own day or rule of entry into force, which is used. https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa/normativa-generale.html?download=10

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/vatican-city-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `ad226a73e15c54abd774bf94e0da46223e75eacc610b2c51d43ea0b6fdf2bd13` (87381 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `833a2433a3ea96fd87477ccc7a2ed47dc9e24b48` |
| check.py | `426d4cfb32ce103715be6a00865c0a7bca81a56a` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `64045b78a73ea37ff5c9353a44e56e9465345f20` |
| parse.py | `93c7ceea6c353ea4a41e048179d5b33abbcb4d45` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

5 versions of 2 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

Not yet run for this build.

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- The Fundamental Law is one act, legge-fondamentale, whose text is replaced in full by the laws of 13 May 2023 and 31 July 2026; each replacement is a version credited to the replacing law, so blame shows which law wrote each article.
- The first Fundamental Law (7 June 1929, n. I) is not on the official site with a text layer, so the history starts with the law of 26 November 2000 in force 22 February 2001.
- No amendment of the 2000 law was found on the official site; the 2023 law was amended once, by the motu proprio of 19 November 2025 (art. 8, n. 1), applied by replaying it on the 2023 text.
- The motu proprio of 19 November 2025 enters into force on the day of its publication in L'Osservatore Romano; the source gives 21 November 2025 as the day the Holy See Press Office made it public, used as the in-force day (the newspaper's issue date was not checked).
- The law of 31 July 2026 enters into force 'immediatamente' and was published in the Holy See Press Office Bulletin n. 0611 of 31 July 2026, so its in-force day is 31 July 2026.
- Every in-force day comes from the law's own clause (2000: 22 February 2001; 2023: 7 June 2023; 2008 LXXI: 1 January 2009; 2013 VIII: 1 September 2013), which overrides the seven-day rule of LXXI art. 2.
- Units are articles (art-NNN), title headings (titolo-NN), the preamble (preambolo), and the closing promulgation formula with date and signature (formula-finale). The 2000 law's unnumbered final clauses (replacement and entry into force) are the unit disposizione-finale.
- The 2000 law's preamble is left out: the publisher's copy paraphrases it inside a press introduction rather than reproducing it.
- Annexes A-C (flag, coat of arms, seal) are left out of every version: they are drawn models, and only the 2023 copy adds short captions to them.
- Title headings are set in sentence case (TITOLO I / DISPOSIZIONI GENERALI and Titolo I / Disposizioni Generali both read 'Titolo I / Disposizioni generali'), so a change of typesetting is not a change of law.
- Typesetting is normalised: NBSP to space, runs of spaces collapsed, curly quotes and apostrophes to straight ones, em dashes to en dashes, PDF line wraps joined into one paragraph per line, page numbers dropped.
- Character errors in the publisher's own PDF text layer are corrected by hand: 2000 law art. 7 'I1 potere' -> 'Il potere'; LXXI 'Ada Apostolicae' -> 'Acta Apostolicae', 'entrata ih vigore' -> 'entrata in vigore', Cyrillic 'а)' -> 'a)' and 'б)' -> '6)' in art. 12.
- Check against vatican.va (verify.py, verification.json): every line of the 2026 law matches the HTML copy; in the 2023 law one line differs, the preamble's 'Vaticano che, il Trattato' (vaticanstate.va PDF, kept) against 'Vaticano, che il Trattato' (vatican.va HTML).
- The Legge sulle fonti del diritto (LXXI) is built as enacted: the official site lists no amending act and gives no consolidated text.
- Legge n. VIII of 2013 (criminal law) sits in corpus.d/50-legge-viii.json, unverified, because later laws amended it (e.g. N. CCCXXIX/CCCXXXVI of 2019 and N. DXXXI) and those changes are not yet replayed.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote fetch.py and parse.py, chose the sources and made the decisions above. No model wrote or edited legal text; all law text is parsed by code from the official files. No model runs at build time.
