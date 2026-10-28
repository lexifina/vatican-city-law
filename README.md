# Vatican City: law history in git

The law of Vatican City State as a git history: one file per provision, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to a provision; `tools/on.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `va/`. The texts are the official files published by the Governatorato dello Stato della Città del Vaticano on [vaticanstate.va](https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa.html), in Italian, the language of the State's laws.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `legge-fondamentale/` | Legge fondamentale dello Stato della Città del Vaticano (the Fundamental Law, the State's constitution) | 4 | 2001-02-22 to 2026-07-31 |
| `legge-fonti-diritto/` | Legge sulle fonti del diritto, N. LXXI of 1 October 2008 (the law on the sources of law) | 1 | 2009-01-01, as enacted |

**Legge fondamentale**

| In force | Author | What happened |
| --- | --- | --- |
| 2001-02-22 | Legge fondamentale of 26 November 2000 (John Paul II) | Replaced the first Fundamental Law of 7 June 1929 |
| 2023-06-07 | Legge fondamentale of 13 May 2023 (Francis) | Replaced the 2000 law in full |
| 2025-11-21 | Motu proprio of 19 November 2025 (Leo XIV) | Art. 8, n. 1: the President of the Pontifical Commission need no longer be a Cardinal |
| 2026-07-31 | Legge fondamentale of 31 July 2026 (Leo XIV) | Replaced the 2023 law in full, in force immediately |

A Fundamental Law is replaced whole rather than amended, so each new law is one commit that rewrites the act's files; blame then shows, article by article, which law last wrote each paragraph. Each folder's `README.md` lists every provision, how often it changed and when.

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did Art. 8 say on 1 January 2025? | `python tools/on.py 2025-01-01 legge-fondamentale art-008` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2025-01-01T23:59:59Z" main -- legge-fondamentale/art-008.md):legge-fondamentale/art-008.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2025-01-01T23:59:59Z" main -- legge-fondamentale/art-008.md; git show "$($r):legge-fondamentale/art-008.md"` |
| Which law wrote each line? | `git blame legge-fondamentale/art-008.md` |
| Every change, word by word | `git log -p --word-diff legge-fondamentale/art-008.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one law changed | `git show law/mp-2025-11-19` (tags `law/<key>` mark each law's commit) |
| The whole Fundamental Law on a date | `python tools/on.py 2010-06-01 legge-fondamentale` |
| Which law gave a provision its wording on a date | `python tools/on.py --law 2024-01-01 legge-fondamentale art-008` |

Article numbers are those of the law in force on the day: the 2000 law has 20 articles, the 2023 law 24 and the 2026 law 25, so `art-008.md` is a different provision under each law. Read it together with the version's tag (`legge-fondamentale/<date>`). After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Europe/Vatican, on the day the change took effect**. The day is also in the `In-force:` trailer, which the tools read; the day of promulgation (`Enacted:`) and, where known, of publication (`Published:`) are trailers too.
- **Every day comes from the law itself.** The 2000 law took effect on 22 February 2001 and the 2023 law on 7 June 2023, as their final clauses say; LXXI on 1 January 2009 (its art. 13). The 2026 law took effect "immediatamente" (art. 25, n. 3) and was published that day, 31 July 2026, in the Holy See Press Office Bulletin. The motu proprio of 19 November 2025 took effect on the day of its publication in L'Osservatore Romano; the record uses 21 November 2025, the day the Press Office made it public (the newspaper's issue date was not checked).
- Without such a clause, a Vatican law takes effect on the seventh day after its publication (LXXI, art. 2, n. 2).
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- **Against a second official copy:** every paragraph of the 2023 and 2026 laws was compared with the HTML text on vatican.va. All of the 2026 law matches; in the 2023 law one comma differs, in the preamble ("Vaticano che, il Trattato" in the Governatorato's PDF, kept here, against "Vaticano, che il Trattato" on vatican.va).
- **The 2025 change was replayed:** the new art. 8, n. 1 is taken word for word from the motu proprio as the Governatorato printed it and applied to the 2023 text.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist, so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- The first commit of each act is the act as enacted.
- A replacement Fundamental Law is credited with every provision it changed, inserted or removed. A provision whose words did not change keeps its earlier author: Art. 1 to 3 and 5, for example, still read as the 2023 law wrote them.
- Blame credits whole lines (one paragraph per line). Use `git log -p --word-diff` to see exactly which words each change made.

## What it does not show

- **The first Fundamental Law (7 June 1929, n. I)** and the 2000 law's preamble: the official site has no text of them (its copy of the 2000 law gives the preamble only as a press summary).
- **Annexes A to C** (the models of the flag, coat of arms and seal) are drawings and are left out.
- **Amendments of LXXI:** the official site publishes it as enacted and lists no amending act. If one exists, it is not here.
- **Other laws.** Vatican City applies Italian codes as received (civil, criminal and their procedures, under LXXI arts. 4 to 8) with its own amending laws; those are not in this record yet. Law n. VIII of 2013 (complementary criminal provisions) is parsed but not yet published here, because the laws that later amended it have not yet been replayed.
- **No OCR.** Every text comes from the publisher's own text layer. Five character errors in that layer were corrected and are listed in REPRODUCE.md (for example "Ada Apostolicae" for "Acta Apostolicae").

## How it is built

`tools/fetch.py` downloads each official file once with curl, cached by the sha256 of its URL, and logs every request. `tools/parse.py` reads only that cache: it takes the text layer of each PDF (PyMuPDF), joins the printed lines into one paragraph per line, splits the law into its preamble, title headings, articles and closing formula, applies the 2025 motu proprio, and writes `corpus.json`. `tools/verify.py` compares the result with the vatican.va copies. The shared builder `tools/build.py` turns `corpus.json` into the commits. `REPRODUCE.md` lists every source, command, tool version and decision, and the result of the hash-for-hash rebuild.

## Sources

| Source | What it gives | Used for |
| --- | --- | --- |
| [Governatorato, Legislazione e normativa](https://www.vaticanstate.va/it/stato-e-governo/legislazione-e-normativa.html) | Official PDFs of each law as promulgated; the Governatorato's page carrying the motu proprio of 19 November 2025. No consolidated texts and no dated versions. | The text of every version |
| [vatican.va](https://www.vatican.va/) | HTML copies of the 2023 and 2026 Fundamental Laws | Checking the parsed text |
| [Sala Stampa della Santa Sede](https://press.vatican.va/content/salastampa/it/bollettino/pubblico/2026/07/31/0611.pdf) | Bulletin n. 0611 of 31 July 2026 | The publication day of the 2026 law |

The State's laws are published in the Supplemento per le leggi e disposizioni dello Stato della Città del Vaticano of the Acta Apostolicae Sedis, and recent ones first in L'Osservatore Romano. The world sources register notes that publication on vaticanstate.va has had legal effect since 2024; this was not confirmed from a legal text.

## Licence

See [LICENSE](LICENSE). The legal texts come from the Governatorato dello Stato della Città del Vaticano (vaticanstate.va), whose site states "Copyright © 2026 by Governatorato dello Stato della Città del Vaticano | Tutti i diritti riservati". This repository is private. Lexifina's arrangement, messages, tables and tools are CC0.

This repository is not legal advice.

## In italiano

Questo repository contiene la storia della legislazione dello Stato della Città del Vaticano in git: un file per ogni disposizione e un commit per ogni legge, datato al giorno della sua entrata in vigore e attribuito alla legge che ha introdotto la modifica. Contiene la Legge fondamentale (testi del 26 novembre 2000, del 13 maggio 2023 e del 31 luglio 2026, e il motu proprio del 19 novembre 2025 che ha sostituito l'art. 8, n. 1) e la Legge sulle fonti del diritto n. LXXI del 1° ottobre 2008 nel testo originario. I testi sono quelli pubblicati dal Governatorato su vaticanstate.va. `python tools/on.py <data> legge-fondamentale` restituisce il testo vigente in una data. Non costituisce consulenza legale.
