#!/usr/bin/env python3
"""RQ2 — Taxonomy / Jaccard content analysis (writes rq2_*.csv/json).

Inputs: AGIT_STUDY_ROOT/{top,bottom}_repos/ instruction extracts.
Default STUDY is this folder's ../data (packaged symlinks to corpus/instruction_extracts).
Override with env AGIT_STUDY_ROOT / AGIT_RQ_OUT.
"""

from __future__ import annotations
import os
from pathlib import Path as _Path

_PKG_DATA = _Path(__file__).resolve().parents[1] / "data"
_DEFAULT_STUDY = (
    _PKG_DATA if (_PKG_DATA / "top_repos").exists()
    else _Path("/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files")
)
_STUDY = _Path(os.environ.get("AGIT_STUDY_ROOT", str(_DEFAULT_STUDY)))
_OUT = _Path(os.environ.get(
    "AGIT_RQ_OUT",
    str(_Path(__file__).resolve().parents[1]),
))
BASE = _STUDY
OUT = _OUT
CACHE = _STUDY / "aidev_cache"

"""RQ2: Content similarity analysis of agent instruction files."""
import json
import os
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

# BASE set from AGIT_STUDY_ROOT above
# OUT set from AGIT_RQ_OUT above
FILE_TYPES = ["AGENTS.md", "CLAUDE.md", "Cursor rules", "Copilot instructions"]
SKIP = {'.git','node_modules','dist','build','.venv','venv','__pycache__','.tox','target','vendor','.next','coverage'}

HEADING_RE = re.compile(r'^(#{1,3})\s+(.+?)\s*$', re.M)
# Cursor .mdc often has YAML frontmatter description
FRONTMATTER_DESC = re.compile(r'^---\s*\n(.*?)\n---', re.S)
DESC_LINE = re.compile(r'^description:\s*[\'"]?(.*?)[\'"]?\s*$', re.M)

# 16-category taxonomy (from study design) with keyword probes for automated pilot coding
CATEGORIES = {
    "1. Project overview / purpose": [
        r"\boverview\b", r"\bpurpose\b", r"\babout\b", r"\bintroduction\b", r"\bwhat (is|this)\b",
        r"\bproject (summary|description)\b", r"\bmission\b",
    ],
    "2. Repository structure": [
        r"\bstructure\b", r"\bdirectory\b", r"\bfolder\b", r"\blayout\b", r"\bcodebase\b",
        r"\bmonorepo\b", r"\bpackage(s)?\b", r"\bwhere (to find|things live)\b",
    ],
    "3. Build / run / install": [
        r"\bbuild\b", r"\binstall\b", r"\brun\b", r"\bsetup\b", r"\bdev(elopment)?\b",
        r"\bnpm\b", r"\bpip\b", r"\bcargo\b", r"\bmake\b", r"\bdocker\b", r"\bgetting started\b",
    ],
    "4. Test / CI commands": [
        r"\btest\b", r"\bci\b", r"\blint\b", r"\bpytest\b", r"\bjest\b", r"\bcoverage\b",
        r"\bcontinuous integration\b", r"\bgithub actions\b",
    ],
    "5. Code style / formatting": [
        r"\bstyle\b", r"\bformat\b", r"\blinter\b", r"\bprettier\b", r"\beslint\b",
        r"\bruff\b", r"\bblack\b", r"\bconvention\b", r"\bnaming\b", r"\bindent\b",
    ],
    "6. Architecture / design constraints": [
        r"\barchitecture\b", r"\bdesign\b", r"\bconstraint\b", r"\bpattern\b",
        r"\bprinciple\b", r"\blayer\b", r"\bmodular\b", r"\bseparat(e|ion)\b",
    ],
    "7. Domain models / key abstractions": [
        r"\bmodel\b", r"\bdomain\b", r"\bentity\b", r"\babstraction\b", r"\bconcept\b",
        r"\bschema\b", r"\btype(s)?\b", r"\bdata model\b",
    ],
    "8. API / interface contracts": [
        r"\bapi\b", r"\bendpoint\b", r"\binterface\b", r"\bcontract\b", r"\bgrpc\b",
        r"\brest\b", r"\bopenapi\b", r"\broute\b",
    ],
    "9. Do / Don't rules": [
        r"\bdo not\b", r"\bdon't\b", r"\bnever\b", r"\balways\b", r"\bmust not\b",
        r"\bavoid\b", r"\brules?\b", r"\bguidelines?\b", r"\bforbidden\b", r"\brequired\b",
    ],
    "10. Security / secrets": [
        r"\bsecurit(y|ies)\b", r"\bsecret\b", r"\bcredential\b", r"\btoken\b", r"\bauth\b",
        r"\bvulnerabilit\b", r"\bowasp\b", r"\bpii\b", r"\bencrypt\b", r"\bsanitiz\b",
    ],
    "11. Performance": [
        r"\bperformance\b", r"\blatenc(y|ies)\b", r"\bprofil\b", r"\bbenchmark\b",
        r"\boptimiz\b", r"\bthroughput\b", r"\bmemory\b", r"\bcach(e|ing)\b",
    ],
    "12. Git / PR / commit conventions": [
        r"\bgit\b", r"\bpull request\b", r"\b\bpr\b", r"\bcommit\b", r"\bbranch\b",
        r"\bconventional commit\b", r"\bchangelog\b", r"\breview\b",
    ],
    "13. Tooling-specific agent config": [
        r"\bagents?\.md\b", r"\bclaude\b", r"\bcursor\b", r"\bcopilot\b", r"\bwindsurf\b",
        r"\bsubagent\b", r"\bskill\b", r"\btool(s|ing)?\b", r"\bmcps?\b", r"\bhooks?\b",
        r"\bpermission\b", r"\ballowlist\b",
    ],
    "14. Examples / few-shot snippets": [
        r"\bexample\b", r"\bsnippet\b", r"\bsample\b", r"\be\.g\.\b", r"\bfor instance\b",
        r"\bfew[- ]shot\b", r"```",
    ],
    "15. Ownership / contacts": [
        r"\bowner\b", r"\bcontact\b", r"\bmaintainer\b", r"\bcodeowner\b", r"\bteam\b",
        r"\bask\b", r"\bslack\b", r"\bdiscord\b",
    ],
    "16. Maintenance / when to update": [
        r"\bmaintain\b", r"\bstale\b", r"\boutdated\b", r"\bkeep (this )?(file )?updated\b",
        r"\bwhen to update\b", r"\bsync\b", r"\bdrift\b", r"\bthis file\b.*\bupdate\b",
    ],
}

COMPILED = {k: [re.compile(p, re.I) for p in v] for k, v in CATEGORIES.items()}

def classify_path(path: str) -> set[str]:
    p = path.replace('\\', '/')
    pl = p.lower()
    name = Path(pl).name
    found = set()
    if name == 'agents.md': found.add('AGENTS.md')
    if name == 'claude.md': found.add('CLAUDE.md')
    if name == '.cursorrules' or '/.cursor/rules/' in pl or pl.endswith('/.cursor/rules'):
        found.add('Cursor rules')
    if name == 'copilot-instructions.md' or name.endswith('.instructions.md') or '/.github/instructions/' in pl:
        found.add('Copilot instructions')
    return found

def normalize_heading(h: str) -> str:
    h = h.lower().strip()
    h = re.sub(r'`+', '', h)
    h = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', h)  # markdown links
    h = re.sub(r'[^a-z0-9 /+_.-]+', ' ', h)
    h = re.sub(r'\s+', ' ', h).strip()
    return h

def extract_headings(text: str) -> list[str]:
    heads = []
    fm = FRONTMATTER_DESC.match(text)
    if fm:
        for m in DESC_LINE.finditer(fm.group(1)):
            d = normalize_heading(m.group(1))
            if d:
                heads.append(d)
    for m in HEADING_RE.finditer(text):
        h = normalize_heading(m.group(2))
        if h and h not in ('table of contents', 'toc'):
            heads.append(h)
    return heads

def categorize_text(text: str) -> set[str]:
    hits = set()
    # sample first 50k chars for speed
    sample = text[:50000]
    for cat, pats in COMPILED.items():
        if any(p.search(sample) for p in pats):
            hits.add(cat)
    return hits

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

# ---------- Collect ----------
# Per-file records; also aggregate headings/categories by type and by (repo, type)
records = []
headings_by_type = {t: Counter() for t in FILE_TYPES}
cats_by_type = {t: Counter() for t in FILE_TYPES}
# repo -> type -> {headings set, cats set, texts concat for within-repo}
repo_type_heads = defaultdict(lambda: defaultdict(set))
repo_type_cats = defaultdict(lambda: defaultdict(set))
repo_cohort = {}

n_read = 0
n_err = 0
for cohort in ['top_repos', 'bottom_repos']:
    root = BASE / cohort
    if not root.exists():
        continue
    for repo in sorted(root.iterdir()):
        if not repo.is_dir():
            continue
        repo_key = f"{cohort}/{repo.name}"
        repo_cohort[repo_key] = 'top' if cohort == 'top_repos' else 'bottom'
        for dirpath, dirnames, filenames in os.walk(repo):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            for fn in filenames:
                full = Path(dirpath) / fn
                rel = str(full.relative_to(repo)).replace('\\', '/')
                types = classify_path(rel)
                if not types:
                    continue
                try:
                    text = full.read_text(encoding='utf-8', errors='replace')
                except Exception:
                    n_err += 1
                    continue
                n_read += 1
                heads = extract_headings(text)
                cats = categorize_text(text)
                for t in types:
                    headings_by_type[t].update(heads)
                    cats_by_type[t].update(cats)
                    repo_type_heads[repo_key][t].update(heads)
                    repo_type_cats[repo_key][t].update(cats)
                records.append({
                    'cohort': repo_cohort[repo_key],
                    'repo': repo.name,
                    'path': rel,
                    'types': sorted(types),
                    'n_headings': len(heads),
                    'n_chars': len(text),
                    'categories': sorted(cats),
                    'headings': heads,
                })

print(f"Read {n_read} files ({n_err} errors)")

# ---------- Type-level Jaccard on heading vocabulary ----------
type_head_sets = {t: set(headings_by_type[t]) for t in FILE_TYPES}
type_cat_sets = {t: set(cats_by_type[t]) for t in FILE_TYPES}

heading_jaccard = []
for a, b in combinations(FILE_TYPES, 2):
    heading_jaccard.append({
        'type_a': a, 'type_b': b,
        'jaccard_headings': round(jaccard(type_head_sets[a], type_head_sets[b]), 4),
        'jaccard_categories': round(jaccard(type_cat_sets[a], type_cat_sets[b]), 4),
        'intersect_headings': len(type_head_sets[a] & type_head_sets[b]),
        'union_headings': len(type_head_sets[a] | type_head_sets[b]),
        '|A|_heads': len(type_head_sets[a]),
        '|B|_heads': len(type_head_sets[b]),
    })

# ---------- Shared core / unique / gaps on headings ----------
heading_types = defaultdict(set)
for t, s in type_head_sets.items():
    for h in s:
        heading_types[h].add(t)

shared_core = sorted([h for h, ts in heading_types.items() if len(ts) >= 3])
shared_all4 = sorted([h for h, ts in heading_types.items() if len(ts) == 4])
in_exactly_2 = sorted([h for h, ts in heading_types.items() if len(ts) == 2])
unique = {t: sorted([h for h, ts in heading_types.items() if ts == {t}]) for t in FILE_TYPES}

# Frequency-weighted shared core: headings in ≥3 types AND appearing often
shared_core_freq = []
for h in shared_core:
    total = sum(headings_by_type[t][h] for t in FILE_TYPES)
    shared_core_freq.append((h, total, len(heading_types[h])))
shared_core_freq.sort(key=lambda x: -x[1])

# ---------- Category prevalence by type (% of files) ----------
# Count files per type
files_per_type = Counter()
cat_file_counts = {t: Counter() for t in FILE_TYPES}
for r in records:
    for t in r['types']:
        files_per_type[t] += 1
        for c in r['categories']:
            cat_file_counts[t][c] += 1

cat_prevalence = []
for cat in CATEGORIES:
    row = {'category': cat}
    present_in = 0
    for t in FILE_TYPES:
        pct = 100 * cat_file_counts[t][cat] / files_per_type[t] if files_per_type[t] else 0
        row[t] = round(pct, 1)
        if pct >= 5:  # present if ≥5% of files of that type
            present_in += 1
    row['n_types_ge5pct'] = present_in
    cat_prevalence.append(row)

# Gaps: categories with low prevalence across ALL types
gaps = [r for r in cat_prevalence if max(r[t] for t in FILE_TYPES) < 25]
# Shared strong: high in ≥3 types
shared_cats = [r for r in cat_prevalence if sum(1 for t in FILE_TYPES if r[t] >= 40) >= 3]
# Unique: high in one, low in others
unique_cats = []
for r in cat_prevalence:
    vals = [(t, r[t]) for t in FILE_TYPES]
    vals.sort(key=lambda x: -x[1])
    if vals[0][1] >= 40 and vals[1][1] < 25:
        unique_cats.append({**r, 'unique_to': vals[0][0]})

# ---------- Within-repo pairwise Jaccard (multi-format repos) ----------
within_repo = []
for repo_key, type_map in repo_type_heads.items():
    types_present = [t for t in FILE_TYPES if type_map[t]]
    if len(types_present) < 2:
        continue
    for a, b in combinations(types_present, 2):
        within_repo.append({
            'repo': repo_key,
            'cohort': repo_cohort[repo_key],
            'type_a': a, 'type_b': b,
            'jaccard_headings': jaccard(type_map[a], type_map[b]),
            'jaccard_categories': jaccard(repo_type_cats[repo_key][a], repo_type_cats[repo_key][b]),
            'n_heads_a': len(type_map[a]),
            'n_heads_b': len(type_map[b]),
        })

within_df = pd.DataFrame(within_repo)
pair_summary = []
if len(within_df):
    for (a, b), g in within_df.groupby(['type_a', 'type_b']):
        pair_summary.append({
            'type_a': a, 'type_b': b,
            'n_repos': len(g),
            'mean_jaccard_headings': round(g.jaccard_headings.mean(), 3),
            'median_jaccard_headings': round(g.jaccard_headings.median(), 3),
            'mean_jaccard_categories': round(g.jaccard_categories.mean(), 3),
            'median_jaccard_categories': round(g.jaccard_categories.median(), 3),
        })
    pair_summary.sort(key=lambda x: -x['n_repos'])

# ---------- Top headings per type ----------
top_headings = {
    t: [{'heading': h, 'count': int(c)} for h, c in headings_by_type[t].most_common(30)]
    for t in FILE_TYPES
}

# ---------- Heading length / file stats ----------
file_stats = []
for t in FILE_TYPES:
    subset = [r for r in records if t in r['types']]
    chars = [r['n_chars'] for r in subset]
    heads = [r['n_headings'] for r in subset]
    file_stats.append({
        'type': t,
        'n_files': len(subset),
        'median_chars': int(np.median(chars)) if chars else 0,
        'mean_chars': int(np.mean(chars)) if chars else 0,
        'median_headings': float(np.median(heads)) if heads else 0,
        'vocab_heads': len(type_head_sets[t]),
        'mean_categories': round(float(np.mean([len(r['categories']) for r in subset])), 2) if subset else 0,
    })

# ---------- Save ----------
results = {
    'n_files': n_read,
    'files_per_type': dict(files_per_type),
    'file_stats': file_stats,
    'heading_jaccard_vocabulary': heading_jaccard,
    'within_repo_pair_summary': pair_summary,
    'within_repo_n_pairs': len(within_df),
    'shared_core_n': len(shared_core),
    'shared_all4_n': len(shared_all4),
    'shared_core_top50': [
        {'heading': h, 'count': cnt, 'n_types': nt} for h, cnt, nt in shared_core_freq[:50]
    ],
    'shared_all4_sample': shared_all4[:40],
    'unique_heading_counts': {t: len(unique[t]) for t in FILE_TYPES},
    'unique_headings_top20': {t: unique[t][:20] for t in FILE_TYPES},
    'category_prevalence': cat_prevalence,
    'shared_strong_categories': shared_cats,
    'unique_categories': unique_cats,
    'gap_categories_max_lt_25pct': gaps,
    'top_headings_per_type': top_headings,
    'notes': {
        'category_coding': 'Automated keyword pilot (not dual-coder); Cohen κ pending human coding',
        'heading_jaccard_vocabulary': 'Jaccard on union of normalized headings across all files of each type',
        'within_repo': 'Jaccard between formats that coexist in the same repository',
    },
}

(OUT / 'rq2_results.json').write_text(json.dumps(results, indent=2))
pd.DataFrame(cat_prevalence).to_csv(OUT / 'rq2_category_prevalence.csv', index=False)
pd.DataFrame(heading_jaccard).to_csv(OUT / 'rq2_heading_jaccard.csv', index=False)
if len(within_df):
    within_df.to_csv(OUT / 'rq2_within_repo_jaccard.csv', index=False)
pd.DataFrame(file_stats).to_csv(OUT / 'rq2_file_stats.csv', index=False)

# Compact print
print('\n=== File stats ===')
for s in file_stats:
    print(s)

print('\n=== Vocabulary Jaccard (headings) ===')
for r in heading_jaccard:
    print(f"  {r['type_a']} × {r['type_b']}: J_head={r['jaccard_headings']:.3f} J_cat={r['jaccard_categories']:.3f} (|A|={r['|A|_heads']}, |B|={r['|B|_heads']}, ∩={r['intersect_headings']})")

print('\n=== Within-repo pair summary ===')
for r in pair_summary:
    print(f"  {r['type_a']} × {r['type_b']}: n={r['n_repos']} mean_Jh={r['mean_jaccard_headings']} med={r['median_jaccard_headings']} mean_Jc={r['mean_jaccard_categories']}")

print(f'\nShared core headings (≥3 types): {len(shared_core)} (all 4: {len(shared_all4)})')
print('Top shared-core headings:')
for h, cnt, nt in shared_core_freq[:25]:
    print(f'  [{nt} types, n={cnt}] {h}')

print('\n=== Category prevalence (pct of files) ===')
print(pd.DataFrame(cat_prevalence).to_string(index=False))

print('\nShared strong cats (≥40% in ≥3 types):', len(shared_cats))
for r in shared_cats:
    print(' ', r['category'])
print('Gaps (max <25%):')
for r in gaps:
    print(' ', r['category'], {t: r[t] for t in FILE_TYPES})
print('Unique cats:')
for r in unique_cats:
    print(' ', r['unique_to'], r['category'])

print('\nUnique heading counts:', {t: len(unique[t]) for t in FILE_TYPES})
print('Saved rq2_*.json/csv')
