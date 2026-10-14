#!/usr/bin/env python3
"""RQ1 — Prevalence & adoption analysis (writes rq1_*.csv/json).

Inputs (first match wins per cohort):
  - AGIT_STUDY_ROOT/{top,bottom}_500_projects_instruction_files.csv  (packaged slim)
  - AGIT_STUDY_ROOT/{top,bottom}_500_projects_with_files.csv         (full-tree)

Default STUDY is this folder's ../data (packaged). Override with AGIT_STUDY_ROOT / AGIT_RQ_OUT.
"""
from __future__ import annotations
import os
from pathlib import Path as _Path

_PKG_DATA = _Path(__file__).resolve().parents[1] / "data"
_STUDY = _Path(os.environ.get(
    "AGIT_STUDY_ROOT",
    str(_PKG_DATA if (_PKG_DATA / "top_500_projects_instruction_files.csv").exists()
        else "/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files"),
))
_OUT = _Path(os.environ.get(
    "AGIT_RQ_OUT",
    str(_Path(__file__).resolve().parents[1]),
))
BASE = _STUDY
OUT = _OUT


def _inventory(cohort: str) -> _Path:
    slim = BASE / f"{cohort}_500_projects_instruction_files.csv"
    full = BASE / f"{cohort}_500_projects_with_files.csv"
    if slim.exists():
        return slim
    if full.exists():
        return full
    raise FileNotFoundError(f"Missing inventory for {cohort} under {BASE}")

import ast, csv, json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

csv.field_size_limit(10**9)
# BASE from AGIT_STUDY_ROOT
FILE_TYPES = ["AGENTS.md", "CLAUDE.md", "Cursor rules", "Copilot instructions"]

def classify_path(path: str):
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

def load(csv_path, cohort):
    rows = []
    with open(csv_path, newline='', encoding='utf-8', errors='replace') as f:
        for row in csv.DictReader(f):
            try:
                raw = row.get('files') or ''
                files = json.loads(raw) if raw.strip().startswith('[') else (ast.literal_eval(raw) if raw else [])
            except Exception:
                try: files = ast.literal_eval(row['files']) if row.get('files') else []
                except Exception: files = []
            types = set()
            for fp in files:
                types |= classify_path(str(fp))
            rec = {
                'cohort': cohort,
                'full_name': row.get('full_name'),
                'language': row.get('language') or 'Unknown',
                'license': row.get('license') or 'Unknown',
                'stars': float(row['stars']) if row.get('stars') else np.nan,
                'forks': float(row['forks']) if row.get('forks') else np.nan,
                'n_types': len(types),
                'has_any': int(len(types) > 0),
                'types': frozenset(types),
            }
            for t in FILE_TYPES:
                rec[f'has_{t}'] = int(t in types)
            rows.append(rec)
    return pd.DataFrame(rows)

projects = pd.concat([
    load(_inventory('top'), 'top'),
    load(_inventory('bottom'), 'bottom'),
], ignore_index=True)

# --- Prevalence ---
prev = []
for cohort, g in projects.groupby('cohort'):
    row = {'cohort': cohort, 'n': len(g), 'any_n': int(g.has_any.sum()), 'any_pct': round(100*g.has_any.mean(),1)}
    for t in FILE_TYPES:
        col = f'has_{t}'
        row[f'{t}_n'] = int(g[col].sum())
        row[f'{t}_pct'] = round(100*g[col].mean(),1)
    prev.append(row)

# --- Multi-file ---
multi = projects.groupby(['cohort','n_types']).size().unstack(fill_value=0)
multi_pct = projects.assign(multi=projects.n_types>=2).groupby('cohort')['multi'].mean()*100

pair_counts = Counter()
for types in projects.loc[projects.n_types>=2, 'types']:
    for a,b in combinations(sorted(types), 2):
        pair_counts[(a,b)] += 1

# --- Language domain (min 15 repos overall) ---
lang_counts = projects.language.value_counts()
keep_langs = lang_counts[lang_counts >= 15].index.tolist()
lang_rows = []
for lang in keep_langs:
    g = projects[projects.language==lang]
    row = {'language': lang, 'n': len(g), 'any_pct': round(100*g.has_any.mean(),1)}
    for t in FILE_TYPES:
        row[t] = round(100*g[f'has_{t}'].mean(),1)
    # preferred format among adopters
    adopters = g[g.has_any==1]
    if len(adopters):
        prefs = {t: adopters[f'has_{t}'].mean() for t in FILE_TYPES}
        row['dominant'] = max(prefs, key=prefs.get)
    else:
        row['dominant'] = None
    lang_rows.append(row)
lang_df = pd.DataFrame(lang_rows).sort_values('n', ascending=False)

# language x cohort for top langs
lang_cohort = []
for lang in lang_counts.head(10).index:
    for cohort in ['top','bottom']:
        g = projects[(projects.language==lang)&(projects.cohort==cohort)]
        if len(g)<5: continue
        row = {'language': lang, 'cohort': cohort, 'n': len(g), 'any_pct': round(100*g.has_any.mean(),1)}
        for t in FILE_TYPES:
            row[t] = round(100*g[f'has_{t}'].mean(),1)
        lang_cohort.append(row)

# --- Stars quartiles ---
projects['star_bin'] = pd.qcut(projects.stars.rank(method='first'), 4, labels=['Q1 low','Q2','Q3','Q4 high'])
star_rows = []
for b, g in projects.groupby('star_bin', observed=True):
    row = {'star_bin': str(b), 'n': len(g), 'median_stars': int(g.stars.median()), 'any_pct': round(100*g.has_any.mean(),1)}
    for t in FILE_TYPES:
        row[t] = round(100*g[f'has_{t}'].mean(),1)
    star_rows.append(row)

# --- Logistic regression (sklearn) for each format + any ---
reg = projects.copy()
top_langs = reg.language.value_counts().head(8).index
reg['lang_group'] = reg.language.where(reg.language.isin(top_langs), 'Other')
reg['log_stars'] = np.log1p(reg.stars.fillna(0))
reg['log_forks'] = np.log1p(reg.forks.fillna(0))
reg['is_top'] = (reg.cohort=='top').astype(int)
lang_dummies = pd.get_dummies(reg['lang_group'], prefix='lang', drop_first=True)
X_base = pd.concat([reg[['log_stars','log_forks','is_top']], lang_dummies], axis=1)

logit_results = {}
for outcome in ['has_any'] + [f'has_{t}' for t in FILE_TYPES]:
    y = reg[outcome].values
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_base)
    clf = LogisticRegression(max_iter=2000, solver='lbfgs')
    clf.fit(Xs, y)
    coefs = dict(zip(X_base.columns, clf.coef_[0].round(3)))
    # odds ratios on standardized scale - also fit unstandardized for interpretability of is_top
    clf2 = LogisticRegression(max_iter=2000)
    clf2.fit(X_base, y)
    or_ = dict(zip(X_base.columns, np.exp(clf2.coef_[0]).round(3)))
    logit_results[outcome] = {
        'intercept': round(float(clf2.intercept_[0]),3),
        'odds_ratios': or_,
        'coef_std': coefs,
        'accuracy': round(float(clf2.score(X_base, y)),3),
        'base_rate': round(float(y.mean()),3),
    }

# Favorite format by language (exclusive preference among single-format repos)
single = projects[projects.n_types==1]
single_pref = Counter()
for types in single.types:
    single_pref[list(types)[0]] += 1

# Domain preference: among multi-lang, which format dominates in each language (share of adopters)
domain_pref = lang_df[['language','n','any_pct','dominant'] + FILE_TYPES].to_dict(orient='records')

out = {
    'n_total': len(projects),
    'prevalence': prev,
    'multi_counts': {c: multi.loc[c].to_dict() if c in multi.index else {} for c in ['top','bottom']},
    'multi_pct': {k: round(float(v),1) for k,v in multi_pct.items()},
    'pairs': [{'a':a,'b':b,'n':n} for (a,b),n in pair_counts.most_common()],
    'languages': domain_pref,
    'lang_cohort': lang_cohort,
    'star_bins': star_rows,
    'logit': {k: {'odds_ratios': v['odds_ratios'], 'accuracy': v['accuracy'], 'base_rate': v['base_rate'],
                  'key_ors': {kk: vv for kk,vv in v['odds_ratios'].items() if kk in ('log_stars','log_forks','is_top') or vv>1.3 or vv<0.77}}
              for k,v in logit_results.items()},
    'single_format_dist': dict(single_pref),
    'n_single': int(len(single)),
    'n_multi': int((projects.n_types>=2).sum()),
}

# Save full results
(OUT/'rq1_results.json').write_text(json.dumps(out, indent=2))
projects.drop(columns=['types']).to_csv(OUT/'rq1_project_format_matrix.csv', index=False)
lang_df.to_csv(OUT/'rq1_language_format.csv', index=False)
print(json.dumps(out, indent=2)[:8000])
print('...')
print('saved rq1_results.json')
