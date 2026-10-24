#!/usr/bin/env python3
"""Mechanical checks for manuscripts written under the book-writer editorial standard.

It catches what is easy to miss by eye in long text. It does not judge quality: every
WARN is a prompt for editorial judgment (dialogue, period voice, or an intentional motif
can justify a flagged item), while every ERROR breaks a hard rule of the standard.

Usage:
    python3 check_manuscript.py FILE [FILE ...] [--lang auto|bn|en] [--json]
    cat chapter.md | python3 check_manuscript.py -

With several files (e.g. all chapters), a book-wide pass also checks repetition and
spelling consistency across them (§11.4, §10.2). Exit code is 1 if any ERROR is found.
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter

BN = "ঀ-৿"
BN_LETTER = "ঀ-৥ৰ-৿"  # Bengali block minus the digits ০-৯
NB = f"(?<![{BN}])"  # Bengali-aware word boundaries (\b does not treat vowel signs as word chars)
NA = f"(?![{BN}])"

# ---------------------------------------------------------------- word lists

# §10.5, §21.10: no em dash. The look-alikes people substitute for it are flagged too.
# Spaced dashes count only mid-line (not list bullets); "--" only inside text (not table rules like |---|).
DASH_RE = re.compile(r"[—―⸺⸻﹘]|(?<=[^\s|][ \t])[–-]{1,2}(?=[ \t])|(?<=[^\s|:-])--(?=[^\s|:-])|(?<=[^\W\d])–(?=[^\W\d])")

# §6.2 (verbatim list) plus common additions. Patterns tolerate small wording variations.
CLICHES_BN = [
    r"আজকের দ্রুত পরিবর্তনশীল (বিশ্বে|পৃথিবীতে)", r"(বিষয়টি|এটি) অত্যন্ত গুরুত্বপূর্ণ",
    r"চলুন[^।?!\n]{0,40}(বুঝে|জেনে|দেখে) নে(ওয়া|য়া) যাক", r"চলুন[^।?!\n]{0,20}(জেনে|দেখে) নিই",
    r"আসুন[^।?!\n]{0,20}(জেনে|দেখে|বুঝে)", r"মনে রাখা জরুরি", r"(সবশেষে|পরিশেষে|শেষ পর্যন্ত|সুতরাং|অতএব) বলা যায়",
    r"এই অধ্যায়ে আমরা (দেখলাম|জানলাম)", r"যতটা[^।?!\n]{0,25}মনে হয়,? (আসলে )?ততটা নয়", r"এখানেই শেষ নয়",
    r"প্রশ্ন (হলো|হচ্ছে),? কেন", r"এক কথায় (বলতে গেলে|বলা যায়)", r"নিঃসন্দেহে বলা যায়", r"এই যাত্রায়",
    r"(নতুনভাবে|নতুন করে) ভাবতে শেখায়",
    # additions: nonfiction filler
    r"বর্তমান (যুগে|সময়ে|বিশ্বে)", r"আধুনিক বিশ্বে", r"বলাই বাহুল্য", r"উল্লেখ্য (যে|,)", r"সর্বোপরি",
    r"(গুরুত্বপূর্ণ|অপরিসীম|অগ্রণী) ভূমিকা (পালন করে|রাখে)", r"অনস্বীকার্য", r"মুদ্রার (এপিঠ|অপর পিঠ)",
    # additions: fiction stock phrases
    r"এক অদ্ভুত (অনুভূতি|শিহরণ)", r"সময় যেন থমকে", r"গভীর (একটা |একটি )?(শ্বাস|নিঃশ্বাস) (নিল|নিলেন|ফেলল|ফেললেন)",
    r"শিরদাঁড়া (বেয়ে|দিয়ে)[^।?!\n]{0,20}স্রোত", r"বুকের ভেতরটা[^।?!\n]{0,12}(মোচড়|ধক|কেঁপে)",
    r"ঠোঁটের কোণে[^।?!\n]{0,12}(এক চিলতে|একচিলতে|এক টুকরো|মৃদু) হাসি", r"নিস্তব্ধতা যেন", r"এক অজানা (আশঙ্কা|ভয়|শঙ্কা)",
    r"জীবন (আসলে|মানেই) (এক|একটা|একটি)", r"রহস্যময় (এক )?হাসি",
]
CLICHES_EN = [
    r"in today's (fast-paced|ever-changing|modern) world", r"\bdelve(s|d)? into\b", r"\btapestry\b", r"\ba testament to\b",
    r"\bnavigat(e|ing) the (complexities|challenges|world)\b", r"\bit(’|')?s (important|worth|crucial) (to note|noting)\b",
    r"\bit is (important|worth|crucial) (to note|noting)\b", r"\bplays? an? (crucial|vital|pivotal|key) role\b",
    r"\ba myriad of\b", r"\bembark(ed|ing)? on (a|this|the|your) journey\b", r"\bunlock(ing)? (the|your) (full )?potential\b",
    r"\bever-evolving\b", r"\bgame[- ]changer\b", r"\bin conclusion\b", r"\bat the end of the day\b",
    r"\blittle did (he|she|they|I|we) know\b", r"\b(chill|shiver)s? (ran|went|crept) (down|up) (his|her|their|my) spine\b",
    r"\bbreath (he|she|they|I) didn(’|')?t know\b", r"\bthe air (was|hung) thick with\b", r"\bpalpable\b",
    r"\bcouldn(’|')?t help but\b", r"\bwhispered softly\b", r"\bsomething shifted\b", r"\band that(’|')?s okay\b",
    r"\bhere(’|')?s the (thing|kicker)\b", r"\bsymphony of\b", r"\bin the realm of\b", r"\bsent shivers\b",
]

# §6.2: contrast templates that make prose read as generated when they recur.
CONTRAST_BN = [
    rf"{NB}শুধু(মাত্র)?{NA}[^।?!\n]{{1,60}}?{NB}নয়{NA}[,;]", rf"{NB}নয়{NA},\s*বরং",
    r"একদিকে[^\n]{1,120}?অন্যদিকে", rf"{NB}কখনো{NA}[^।?!\n]{{1,40}},\s*কখনো{NA}",
    r"প্রশ্ন(টা)?[^।?!\n]{1,40}নয়,?\s*প্রশ্ন(টা)?",
]
CONTRAST_EN = [
    r"\bnot (just|only|merely|simply)\b[^.?!\n]{1,60}\bbut\b",
    r"\b(it|this|that)(’|')?s not\b[^.?!\n]{1,60}[,;.]\s*(it|this|that)(’|')?s\b",
    r"\bisn(’|')?t (just )?about\b[^.?!\n]{1,60}\b(it(’|')?s|but)\b",
    r"\bon (the )?one hand\b[^\n]{1,160}?\bon the other\b",
]

# §5.5: transitions used as automatic paragraph glue.
TRANSITIONS_BN = ["অন্যদিকে", "এছাড়াও", "এছাড়া", "তবে", "ফলে", "সুতরাং", "অতএব", "পাশাপাশি", "এবার আসা যাক",
                  "এখন প্রশ্ন হলো", "এখানে লক্ষণীয়", "তাছাড়া", "মোটকথা"]
TRANSITIONS_EN = ["Moreover", "Furthermore", "Additionally", "In addition", "However", "Therefore", "Thus",
                  "On the other hand", "Consequently", "Ultimately", "Notably", "Importantly", "Interestingly"]

# §6.4: intensifiers that should not carry the weight of an argument.
INTENSIFIERS_BN = ["অত্যন্ত", "অবিশ্বাস্য", "ভয়াবহ", "অসাধারণ", "যুগান্তকারী", "গুরুত্বপূর্ণ", "গভীর", "শক্তিশালী", "অভূতপূর্ব", "অনন্য"]
INTENSIFIERS_EN = ["very", "incredibly", "truly", "deeply", "profoundly", "remarkable", "extraordinary", "unprecedented",
                   "powerful", "crucial", "vital", "significant", "essential", "pivotal", "unique"]

# §13.2: pressure phrasing in guidance writing.
PRESSURE_BN = ["আপনাকে অবশ্যই", "আজ থেকেই", "এখনই", "মনে রাখবেন", "কখনোই করবেন না", "আপনি যদি সফল হতে চান", "আপনার জীবন বদলে যাবে"]
PRESSURE_EN = [r"\byou must\b", r"\bstarting today\b", r"\bright now\b", r"\bremember,", r"\bnever ever\b",
               r"\bif you want to succeed\b", r"\byour life will change\b", r"\byou need to\b"]

# §10.1/§10.2: সাধু forms inside চলিত prose (গুরুচণ্ডালী).
SADHU_PRONOUNS = ["তাহার", "তাহাকে", "তাহারা", "তাহাদের", "তাহাতে", "যাহা", "যাহার", "যাহাকে", "যাহারা", "ইহা", "ইহার",
                  "ইহাতে", "উহা", "উহার", "কাহার", "কাহাকে", "কাহারও", "সেইরূপ", "এইরূপ"]
SADHU_STEMS = ["কর", "বল", "দেখ", "আস", "পার", "থাক", "লিখ", "পড়", "শুন", "চল", "ফির", "উঠ", "বস", "রাখ", "ধর", "খুঁজ", "ভাব", "জান"]
SADHU_SUFFIXES = ["িয়া", "িল", "িলেন", "িলাম", "িতে", "িয়াছে", "িয়াছিল", "িয়াছিলেন", "িবে", "িতেছে", "িতেছিল"]
SADHU_OTHER = ["হইল", "হইয়া", "হইতে", "হইবে", "হইয়াছে", "হইয়াছিল", "যাইতে", "যাইবে", "গিয়াছে", "গিয়াছিল", "খাইয়া", "লইয়া", "দিয়াছে", "দিয়াছিল"]
SADHU_RE = re.compile(NB + "(" + "|".join(SADHU_PRONOUNS + SADHU_OTHER + [s + x for s in SADHU_STEMS for x in SADHU_SUFFIXES]) + ")" + NA)

# Bangla Academy প্রমিত: non-tatsama words take ই/উ. These ঈ spellings are non-standard (suffixes allowed).
NONSTANDARD_II = ["বাড়ী", "গাড়ী", "শাড়ী", "সরকারী", "দাবী", "তৈরী", "খুশী", "দেশী", "বিদেশী", "জানুয়ারী", "ফেব্রুয়ারী",
                  "পাখী", "ইংরেজী", "আরবী", "ফারসী", "জাপানী", "বাঙালী", "বাঙ্গালী", "কাহিনী", "রানী", "হাতী", "বেশী", "কোম্পানী"]
NONSTANDARD_RE = re.compile(NB + "(" + "|".join(NONSTANDARD_II) + ")")

# §10.2: one spelling per word across the manuscript. (left, right) pairs; neither is wrong alone.
# House defaults (see SKILL.md): করল, বলল, গেল, এল, দিল, নিল, পেল, এখনো, তখনো, কখনো, দেওয়া, নেওয়া.
VARIANT_PAIRS = [
    ("করল", "করলো"), ("বলল", "বললো"), ("গেল", "গেলো"), ("এল", "এলো"), ("দিল", "দিলো"), ("নিল", "নিলো"),
    ("পেল", "পেলো"), ("থাকল", "থাকলো"), ("এখনো", "এখনও"), ("তখনো", "তখনও"), ("কখনো", "কখনও"),
    ("ওপর", "উপর"), ("দেওয়া", "দেয়া"), ("নেওয়া", "নেয়া"), ("ভেতর", "ভিতর"), ("জন্য", "জন্যে"), ("সঙ্গে", "সাথে"),
]

# §20, §18.4: no placeholders or editorial notes inside the manuscript.
PLACEHOLDER_RE = re.compile(r"\[(TODO|TK|TBD|PLACEHOLDER|insert[^\]]*|[^\]]*লিখুন[^\]]*|\.\.\.|…)\]|\bTODO\b|\bTBD\b|\bXXX\b|\?\?\?|<insert", re.I)
NOTE_RE = re.compile(r"^\s*[\(\[]?\s*(note|editor(’|')?s note|editorial note|নোট|সম্পাদকীয় নোট|সম্পাদকের নোট|লেখকের নোট)\s*[:：]", re.I | re.M)

# Abbreviations that legitimately end in "." in Bengali (ড. মো. সা. রা. ...).
BN_ABBREV = {"ড", "ডা", "মো", "মুহা", "মোহা", "মোছা", "মোসা", "পৃ", "দ্র", "সং", "ইং", "খ্রি", "বি", "রা", "সা", "আ", "রহ", "আলাই", "লি", "কো"}


# ---------------------------------------------------------------- helpers

def strip_non_prose(text):
    """Blank out frontmatter, fenced code and inline code, keeping offsets and line numbers intact."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"\A---\n.*?\n---\n", blank, text, flags=re.S)
    text = re.sub(r"```.*?```", blank, text, flags=re.S)
    return re.sub(r"`[^`\n]+`", blank, text)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def excerpt(text, start, end, pad=30):
    s = text[max(0, start - pad):min(len(text), end + pad)].replace("\n", " ")
    return s.strip()


def find_all(pattern, text, flags=0):
    rx = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
    return list(rx.finditer(text))


def merge_overlaps(matches):
    """Keep one match per overlapping span, so one phrase hit by two patterns counts once."""
    out = []
    for m in sorted(matches, key=lambda x: x.start()):
        if not out or m.start() >= out[-1].end():
            out.append(m)
    return out


def paragraphs(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        b = block.strip()
        if not b or re.match(r"^(#|[-*_]{3,}\s*$|\* \* \*)", b):
            continue
        out.append(b)
    return out


def words(text):
    return re.findall(rf"[{BN}A-Za-z0-9০-৯’']+", text)


def sentences(text, lang):
    enders = r"[।?!]" if lang == "bn" else r"[.?!]"
    parts = re.split(enders + r"+[”’\"']?\s+", re.sub(r"^#.*$", "", text, flags=re.M))
    return [p for p in (s.strip() for s in parts) if len(words(p)) >= 2]


def cv(values):
    if len(values) < 2 or statistics.mean(values) == 0:
        return None
    return statistics.pstdev(values) / statistics.mean(values)


# ---------------------------------------------------------------- checks

class Report:
    def __init__(self, name, lang, text):
        self.name, self.lang, self.text, self.findings = name, lang, text, []

    def add(self, severity, check, message, matches=(), count=None, examples=None):
        ex = examples if examples is not None else [
            {"line": line_of(self.text, m.start()), "excerpt": excerpt(self.text, m.start(), m.end())} for m in matches[:6]
        ]
        self.findings.append({"severity": severity, "check": check, "message": message,
                              "count": count if count is not None else len(matches), "examples": ex})


def check_text(name, raw, lang_opt):
    text = strip_non_prose(raw)
    bn_letters = len(re.findall(f"[{BN_LETTER}]", text))
    en_letters = len(re.findall(r"[A-Za-z]", text))
    lang = lang_opt if lang_opt != "auto" else ("bn" if bn_letters >= en_letters else "en")
    r = Report(name, lang, text)
    paras = paragraphs(text)
    wc = len(words(text))
    sents = sentences(text, lang)
    per_k = lambda n: n * 1000 / max(wc, 1)
    r.stats = {"lang": lang, "words": wc, "sentences": len(sents), "paragraphs": len(paras)}

    # ERRORS: hard rules
    m = find_all(DASH_RE, text)
    if m:
        r.add("ERROR", "em-dash", "Em dash or a dash used like one (§10.5, §21.10). Restructure with comma, colon, "
              "semicolon, parentheses or a new sentence; do not substitute ― – or --.", m)
    m = find_all(PLACEHOLDER_RE, text)
    if m:
        r.add("ERROR", "placeholder", "Placeholder left in the manuscript (§20).", m)

    # Language-specific punctuation and typography
    if lang == "bn":
        stops = [x for x in re.finditer(rf"([{BN_LETTER}]+)\.(?=\s|$|[”’\"')])", text) if x.group(1) not in BN_ABBREV]
        danda = text.count("।")
        if stops:
            sev = "ERROR" if danda >= len(stops) else "WARN"
            r.add(sev, "ascii-full-stop", "English full stop ending Bengali text; use দাঁড়ি (।) consistently (§10.5).", stops)
        m = find_all(rf"(?<=[{BN}])[ \t]+[।,;?!]", text)
        if m:
            r.add("WARN", "space-before-punct", "Space before punctuation; punctuation attaches to the preceding word.", m)
        m = find_all(rf"[।;?!](?=[{BN_LETTER}])|(?<![০-৯]),(?=[{BN_LETTER}])", text)
        if m:
            r.add("WARN", "no-space-after-punct", "Missing space after punctuation.", m)
        m = find_all(r"।।|।\s*।", text)
        if m:
            r.add("WARN", "double-danda", "Double দাঁড়ি.", m)
        # Skip digits inside quoted English (more Latin than Bengali letters nearby), e.g. a ledger entry.
        m = [x for x in find_all(r"(?<![A-Za-z])[0-9]+(?![A-Za-z])", text)
             if len(re.findall(r"[A-Za-z]", text[max(0, x.start() - 20):x.end() + 20]))
             <= len(re.findall(f"[{BN_LETTER}]", text[max(0, x.start() - 20):x.end() + 20]))]
        if m:
            r.add("WARN", "ascii-digits", "English digits in Bengali prose; use ০-৯ unless the context is technical (§10.7).", m)
        m = find_all(SADHU_RE, text)
        if m:
            r.add("WARN", "sadhu-in-cholit", "সাধু forms in চলিত prose (গুরুচণ্ডালী) unless intentional, e.g. period dialogue "
                  "or a quoted older text (§10.2).", m)
        m = find_all(NONSTANDARD_RE, text)
        if m:
            r.add("WARN", "nonstandard-spelling", "Non-standard ঈ spelling in a non-tatsama word; প্রমিত form uses ি "
                  "(বাড়ি, তৈরি, খুশি, সরকারি ...) (§10.2).", m)
    else:
        m = find_all(r"[০-৯]", text)
        if m:
            r.add("WARN", "bengali-digits", "Bengali digits in English text.", m)
        m = find_all(r"(?<=\w)[ \t]+[.,;:?!](?=\s|$)", text)
        if m:
            r.add("WARN", "space-before-punct", "Space before punctuation.", m)

    # Clichés and templates (§6.1, §6.2)
    cl = merge_overlaps([x for p in (CLICHES_BN if lang == "bn" else CLICHES_EN) for x in find_all(p, text, re.I)])
    if cl:
        r.add("WARN", "ai-cliche", "Stock or AI-like expression (§6.2). Replace with a specific observation, or cut.", cl)
    ct = merge_overlaps([x for p in (CONTRAST_BN if lang == "bn" else CONTRAST_EN) for x in find_all(p, text, re.I)])
    if len(ct) >= 2:
        r.add("WARN", "contrast-template", "Repeated contrast template (শুধু X নয়, বরং Y / not X but Y) (§6.2).", ct)
    elif ct:
        r.add("INFO", "contrast-template", "One contrast template; fine once, watch for repetition (§6.2).", ct)

    trans = TRANSITIONS_BN if lang == "bn" else TRANSITIONS_EN
    led = [(i, p) for i, p in enumerate(paras) for t in trans if p.lstrip("“\"'‘").startswith(t)]
    if len(led) >= 3:
        ex = [{"line": None, "excerpt": p[:60]} for _, p in led[:6]]
        r.add("WARN", "transition-led-paragraphs", f"{len(led)} of {len(paras)} paragraphs open with a stock transition (§5.5).",
              count=len(led), examples=ex)

    ints = Counter()
    for w in (INTENSIFIERS_BN if lang == "bn" else INTENSIFIERS_EN):
        n = len(find_all(NB + re.escape(w) if lang == "bn" else rf"\b{w}\b", text, re.I))
        if n:
            ints[w] = n
    heavy = {w: n for w, n in ints.items() if n >= 3}
    if heavy:
        r.add("WARN", "intensifiers", f"Intensifiers doing the work facts should do (§6.4): {heavy}", count=sum(heavy.values()), examples=[])

    pr = [x for p in (PRESSURE_BN if lang == "bn" else PRESSURE_EN) for x in find_all(p if lang == "en" else re.escape(p), text, re.I)]
    if len(pr) >= 3:
        r.add("WARN", "pressure-phrasing", "Repeated pressure phrasing (§13.2).", pr)

    # Punctuation density (§10.5)
    excl = text.count("!")
    ell_u, ell_a = text.count("…"), len(re.findall(r"\.\.\.", text))
    if excl >= 3 and per_k(excl) > 4:
        r.add("WARN", "exclamations", f"{excl} exclamation marks ({per_k(excl):.1f} per 1,000 words) (§10.5).", count=excl, examples=[])
    if ell_u + ell_a >= 3 and per_k(ell_u + ell_a) > 4:
        r.add("WARN", "ellipses", f"{ell_u + ell_a} ellipses ({per_k(ell_u + ell_a):.1f} per 1,000 words) (§10.5).", count=ell_u + ell_a, examples=[])
    if ell_u and ell_a:
        r.add("WARN", "ellipsis-style", f"Mixed ellipsis styles: … ×{ell_u}, ... ×{ell_a}.", count=ell_u + ell_a, examples=[])
    curly, straight = len(re.findall(r"[“”]", text)), text.count('"')
    if curly and straight:
        r.add("WARN", "quote-style", f"Mixed double quotes: curly ×{curly}, straight ×{straight} (§10.6).", count=curly + straight, examples=[])

    # Repetition (§11.4) and rhythm (§5.4, §5.5)
    repetition_checks(r, text, paras)
    lens = [len(words(s)) for s in sents]
    v = cv(lens)
    r.stats["sentence_len_mean"] = round(statistics.mean(lens), 1) if lens else 0
    r.stats["sentence_len_cv"] = round(v, 2) if v is not None else None
    if v is not None and len(lens) >= 15 and v < 0.35:
        r.add("WARN", "uniform-rhythm", f"Sentence lengths are unusually uniform (variation {v:.2f}, typical prose > 0.45) (§5.4).", count=len(lens), examples=[])
    pv = cv([len(words(p)) for p in paras])
    if pv is not None and len(paras) >= 8 and pv < 0.25:
        r.add("WARN", "uniform-paragraphs", f"Paragraph lengths are unusually uniform (variation {pv:.2f}) (§5.5).", count=len(paras), examples=[])

    # Spelling consistency (§10.2)
    if lang == "bn":
        variant_checks(r, text)

    # Formatting (§11.2, §16)
    heads = find_all(r"^#{1,6}\s", text, re.M)
    bullets = find_all(r"^\s*([-*+]|\d+[.)]|[০-৯]+[.)])\s", text, re.M)
    bold = find_all(r"\*\*[^*\n]+\*\*|__[^_\n]+__", text)
    lines = [l for l in text.split("\n") if l.strip()]
    r.stats.update(headings=len(heads), bullet_lines=len(bullets), bold=len(bold))
    if len(heads) >= 3 and per_k(len(heads)) > 3:
        r.add("WARN", "heading-density", f"{len(heads)} headings in {wc} words; reads like a report or blog (§11.2).", heads)
    if lines and len(bullets) / len(lines) > 0.15:
        r.add("WARN", "bullet-prose", f"{len(bullets)} of {len(lines)} lines are list items; keep prose as prose (§16).", bullets)
    if len(bold) > 5:
        r.add("WARN", "bold", f"{len(bold)} bold spans; use emphasis sparingly (§16).", bold)
    m = find_all(NOTE_RE, text)
    if m:
        r.add("WARN", "inline-note", "Editorial note inside the manuscript; move it outside (§18.4).", m)
    return r


def repetition_checks(r, text, paras, label=""):
    toks = [w.lower() for w in words(text)]
    grams = Counter(tuple(toks[i:i + 4]) for i in range(len(toks) - 3))
    rep = [(" ".join(g), n) for g, n in grams.most_common(40) if n >= 3]
    if rep:
        r.add("WARN", "repeated-phrases" + label, "4-word phrases repeated 3+ times (§11.4); intentional motifs are fine.",
              count=len(rep), examples=[{"line": None, "excerpt": f"{g} ×{n}"} for g, n in rep[:8]])
    openings = Counter(" ".join(words(p)[:2]) for p in paras if len(words(p)) >= 2)
    rep = [(o, n) for o, n in openings.most_common(10) if n >= 3 and n / max(len(paras), 1) >= 0.08]
    if rep:
        r.add("WARN", "repeated-openings" + label, "Several paragraphs open the same way (§6.1, §11.3).",
              count=sum(n for _, n in rep), examples=[{"line": None, "excerpt": f"{o} … ×{n}"} for o, n in rep])


def variant_checks(r, text, label=""):
    mixed = []
    for a, b in VARIANT_PAIRS:
        na = len(find_all(NB + a + NA, text))
        nb = len(find_all(NB + b + NA, text))
        if na and nb:
            mixed.append(f"{a} ×{na} / {b} ×{nb}")
    if mixed:
        r.add("WARN", "inconsistent-spelling" + label, "Same word spelled two ways (§10.2). Pick one (house default is the left form "
              "unless the manuscript already settled on the other).", count=len(mixed),
              examples=[{"line": None, "excerpt": s} for s in mixed])


# ---------------------------------------------------------------- output

def print_report(r):
    s = r.stats
    print(f"\n== {r.name}  [{s['lang']}, {s['words']} words, {s['sentences']} sentences, {s['paragraphs']} paragraphs, "
          f"sentence length mean {s.get('sentence_len_mean')} / variation {s.get('sentence_len_cv')}]")
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for f in sorted(r.findings, key=lambda f: order[f["severity"]]):
        print(f"{f['severity']:5s}  {f['check']} ({f['count']}): {f['message']}")
        for e in f["examples"]:
            loc = f"L{e['line']}: " if e.get("line") else ""
            print(f"         {loc}{e['excerpt']}")
    errs = sum(f["severity"] == "ERROR" for f in r.findings)
    warns = sum(f["severity"] == "WARN" for f in r.findings)
    print(f"-- {errs} error(s), {warns} warning(s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="Markdown/text files, or - for stdin")
    ap.add_argument("--lang", choices=["auto", "bn", "en"], default="auto")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    reports, raws = [], []
    for f in args.files:
        raw = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        raws.append(raw)
        reports.append(check_text("stdin" if f == "-" else f, raw, args.lang))

    if len(reports) > 1:  # book-wide pass across all files
        combined = "\n\n".join(strip_non_prose(x) for x in raws)
        book = Report("BOOK-WIDE (all files)", reports[0].lang, combined)
        book.stats = {"lang": book.lang, "words": len(words(combined)), "sentences": 0, "paragraphs": len(paragraphs(combined))}
        repetition_checks(book, combined, paragraphs(combined), label="-book")
        if book.lang == "bn":
            variant_checks(book, combined, label="-book")
        reports.append(book)

    if args.json:
        print(json.dumps([{"file": r.name, "stats": r.stats, "findings": r.findings} for r in reports], ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print_report(r)
    sys.exit(1 if any(f["severity"] == "ERROR" for r in reports for f in r.findings) else 0)


if __name__ == "__main__":
    main()
