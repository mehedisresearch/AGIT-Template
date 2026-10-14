#!/usr/bin/env python3
"""RQ3 — Maintenance dynamics on AIDev-pop (writes rq3_*.csv/json).

Inputs: AGIT_STUDY_ROOT/aidev_cache/*.parquet
Default STUDY is this folder's ../data when it contains a full pr_commit_details.parquet;
otherwise the external study root. Slim package cache omits full details — run
../../scripts/fetch_aidev_cache.sh before a full re-derivation.
Override with env AGIT_STUDY_ROOT / AGIT_RQ_OUT.
"""

from __future__ import annotations
import os
from pathlib import Path as _Path

_PKG_DATA = _Path(__file__).resolve().parents[1] / "data"
_PKG_CACHE = _PKG_DATA / "aidev_cache"
_EXT = _Path("/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files")
if (_PKG_CACHE / "pr_commit_details.parquet").exists():
    _DEFAULT_STUDY = _PKG_DATA
elif (_EXT / "aidev_cache" / "pr_commit_details.parquet").exists():
    _DEFAULT_STUDY = _EXT
else:
    _DEFAULT_STUDY = _PKG_DATA  # instruction-row subset + derived CSVs still useful
_STUDY = _Path(os.environ.get("AGIT_STUDY_ROOT", str(_DEFAULT_STUDY)))
_OUT = _Path(os.environ.get(
    "AGIT_RQ_OUT",
    str(_Path(__file__).resolve().parents[1]),
))
BASE = _STUDY
OUT = _OUT
CACHE = _STUDY / "aidev_cache"

"""Finish RQ3: fix human triangulation, persist full results, print summary."""
import json, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

# BASE set from AGIT_STUDY_ROOT above
# CACHE set above
FILE_TYPES = ["AGENTS.md", "CLAUDE.md", "Cursor rules", "Copilot instructions"]

def classify_path(path: str):
    if not isinstance(path, str) or not path: return set()
    p = path.replace('\\','/'); pl=p.lower(); name=Path(pl).name; found=set()
    if name=='agents.md': found.add('AGENTS.md')
    if name=='claude.md': found.add('CLAUDE.md')
    if name=='.cursorrules' or '/.cursor/rules/' in pl or pl.endswith('/.cursor/rules'): found.add('Cursor rules')
    if name=='copilot-instructions.md' or name.endswith('.instructions.md') or '/.github/instructions/' in pl:
        found.add('Copilot instructions')
    return found

def cliffs_delta(x, y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    if len(x)==0 or len(y)==0: return np.nan
    more=less=0
    for a in x:
        more += np.sum(a>y); less += np.sum(a<y)
    return (more-less)/(len(x)*len(y))

# Reload core tables quickly
details = pd.read_parquet(CACHE/'pr_commit_details.parquet', columns=[
    'sha','pr_id','author','committer','message','filename','status','additions','deletions','changes','patch'])
inst = details.loc[details['filename'].fillna('').map(lambda p: bool(classify_path(p)))].copy()
inst['file_type'] = inst['filename'].map(lambda p: sorted(classify_path(p)))
inst = inst.explode('file_type')

prs = pd.read_parquet(CACHE/'pull_request.parquet')
repos = pd.read_parquet(CACHE/'repository.parquet')
tasks = pd.read_parquet(CACHE/'pr_task_type.parquet')
reviews = pd.read_parquet(CACHE/'pr_reviews.parquet')

inst = inst.merge(prs[['id','agent','created_at','closed_at','merged_at','state','repo_id','title','html_url','user']].rename(
    columns={'id':'pr_id','user':'pr_user','title':'pr_title'}), on='pr_id', how='left')
inst = inst.merge(repos.rename(columns={'id':'repo_id','full_name':'repo_full_name'}), on='repo_id', how='left')
inst = inst.merge(tasks[['id','type']].rename(columns={'id':'pr_id','type':'task_type'}), on='pr_id', how='left')
rev_agg = reviews.groupby('pr_id').agg(
    n_reviews=('id','count'),
    n_changes_requested=('state', lambda s: int((s=='CHANGES_REQUESTED').sum())),
).reset_index()
inst = inst.merge(rev_agg, on='pr_id', how='left')
inst['n_reviews']=inst['n_reviews'].fillna(0).astype(int)
inst['n_changes_requested']=inst['n_changes_requested'].fillna(0).astype(int)
inst['created_at']=pd.to_datetime(inst['created_at'], utc=True, errors='coerce')
inst['merged_at']=pd.to_datetime(inst['merged_at'], utc=True, errors='coerce')
inst['event_at']=inst['merged_at'].fillna(inst['created_at'])
inst['file_key']=inst['repo_full_name'].astype(str)+'::'+inst['filename'].astype(str)

# cochange
sha_stats = details.groupby('sha').size().rename('n_files').reset_index()
sha_inst = inst.groupby('sha').size().rename('n_inst_files').reset_index()
sha_stats = sha_stats.merge(sha_inst, on='sha', how='inner')
sha_stats['n_other_files']=sha_stats['n_files']-sha_stats['n_inst_files']
sha_stats['cochange']=sha_stats['n_other_files']>0
inst=inst.merge(sha_stats[['sha','n_files','n_other_files','cochange']], on='sha', how='left')

REACTIVE_MSG=re.compile(r'\b(fix|bug|fail|broken|regress|ci|lint|error|review|feedback|address|hotfix|revert|typo)\b',re.I)
PROACTIVE_MSG=re.compile(r'\b(add|introduce|create|init|setup|document|improve|enhance|chore|update agents|update claude|rules for)\b',re.I)

def classify_trigger(row):
    msg=str(row.get('message') or '')+' '+str(row.get('pr_title') or '')
    task=str(row.get('task_type') or '').lower()
    r=p=0
    if REACTIVE_MSG.search(msg): r+=2
    if PROACTIVE_MSG.search(msg): p+=1
    if task in {'fix','bugfix','bug'}: r+=2
    if task in {'docs','chore','feat','feature','refactor'}: p+=1
    if row.get('n_changes_requested',0)>0: r+=2
    if str(row.get('status','')).lower()=='added' and r==0: p+=2
    if r>p: return 'reactive'
    if p>r: return 'proactive'
    return 'unclear'

inst['trigger']=inst.apply(classify_trigger, axis=1)
inst.loc[(inst.trigger=='unclear') & (inst.cochange==True), 'trigger']='proactive_cochange'
inst.loc[(inst.trigger=='proactive') & (inst.cochange==True), 'trigger']='proactive_cochange'

# lifecycle
lifecycle_rows=[]
for (file_key, ftype), g in inst.groupby(['file_key','file_type']):
    g=g.sort_values('event_at')
    times=g['event_at'].dropna()
    authors=g['author'].fillna(g['pr_user']).astype(str)
    n=len(g); n_authors=authors.nunique()
    top_share=authors.value_counts().iloc[0]/n if n else 0
    adds=g['additions'].fillna(0).astype(float).sum(); dels=g['deletions'].fillna(0).astype(float).sum()
    churn=dels/adds if adds>0 else (1.0 if dels>0 else 0.0)
    statuses=g['status'].fillna('').str.lower()
    if len(times)>=2:
        span=(times.iloc[-1]-times.iloc[0]).total_seconds()/86400
        gaps=times.diff().dt.total_seconds().dropna()/86400
        mean_gap=float(gaps.mean()) if len(gaps) else np.nan
        cut=times.iloc[0]+(times.iloc[-1]-times.iloc[0])*0.3
        early=float((times<=cut).mean())
    else:
        span=0.0; mean_gap=np.nan; early=1.0
    if n==1: pattern='abandoned'
    elif early>=0.7 and n>=3: pattern='burst-taper'
    elif n>=3 and (mean_gap==mean_gap and mean_gap<=60): pattern='continuous'
    elif n==2: pattern='sparse'
    else: pattern='continuous' if early<0.7 else 'burst-taper'
    lifecycle_rows.append({
        'file_key':file_key,'file_type':ftype,'repo':g['repo_full_name'].iloc[0],
        'language':g['language'].iloc[0],'stars':g['stars'].iloc[0],
        'n_touches':n,'n_prs':g['pr_id'].nunique(),'n_authors':n_authors,
        'owner_top_share':round(top_share,3),'additions':float(adds),'deletions':float(dels),
        'churn_ratio':round(float(churn),3),
        'n_added':int((statuses=='added').sum()),'n_modified':int((statuses=='modified').sum()),
        'n_removed':int(statuses.isin(['removed','deleted']).sum()),
        'span_days':round(float(span),1),
        'mean_gap_days':round(float(mean_gap),1) if mean_gap==mean_gap else None,
        'early_frac':round(float(early),3),'pattern':pattern,
        'first_at':str(times.iloc[0]) if len(times) else None,
        'last_at':str(times.iloc[-1]) if len(times) else None,
    })
life=pd.DataFrame(lifecycle_rows)

# stats
kw_results=[]; cliff_results=[]
for m in ['n_touches','n_authors','owner_top_share','churn_ratio','span_days','n_modified']:
    groups=[life.loc[life.file_type==t,m].dropna().astype(float).values for t in FILE_TYPES]
    groups=[g for g in groups if len(g)>=3]
    H,p=stats.kruskal(*groups)
    kw_results.append({'metric':m,'H':round(float(H),3),'p':float(p)})
    for a,b in [('AGENTS.md','CLAUDE.md'),('AGENTS.md','Copilot instructions'),('CLAUDE.md','Copilot instructions'),('AGENTS.md','Cursor rules')]:
        xa=life.loc[life.file_type==a,m].dropna().astype(float).values
        yb=life.loc[life.file_type==b,m].dropna().astype(float).values
        if len(xa)>=3 and len(yb)>=3:
            cliff_results.append({'metric':m,'a':a,'b':b,'delta':round(float(cliffs_delta(xa,yb)),3),'n_a':len(xa),'n_b':len(yb)})

# heading durability
HEAD_ADD=re.compile(r'^\+\s*#{1,3}\s+(.+)$',re.M)
HEAD_DEL=re.compile(r'^\-\s*#{1,3}\s+(.+)$',re.M)
def norm_h(h):
    h=h.lower().strip(); h=re.sub(r'[^a-z0-9 /+_.-]+',' ',h); return re.sub(r'\s+',' ',h).strip()
added_heads=Counter(); deleted_heads=Counter()
for _,row in inst.iterrows():
    patch=row.get('patch')
    if not isinstance(patch,str): continue
    for m in HEAD_ADD.finditer(patch):
        h=norm_h(m.group(1))
        if h: added_heads[h]+=1
    for m in HEAD_DEL.finditer(patch):
        h=norm_h(m.group(1))
        if h: deleted_heads[h]+=1

durability=[]
for h in set(added_heads)|set(deleted_heads):
    a,d=added_heads[h],deleted_heads[h]
    if a+d<3: continue
    durability.append({'heading':h,'added':a,'deleted':d,'survive_rate':round(a/(a+d),3),'net':a-d})
dur_df=pd.DataFrame(durability).sort_values(['survive_rate','added'],ascending=[False,False])
durable=dur_df[(dur_df.survive_rate>=0.75)&(dur_df.added>=3)].head(40)
ephemeral=dur_df[(dur_df.survive_rate<=0.45)&(dur_df.deleted>=2)].sort_values('deleted',ascending=False).head(40)

CAT_KW={
    'Build / run / install':[r'command',r'build',r'install',r'setup',r'getting started'],
    'Test / CI':[r'test',r'ci',r'lint',r'verif'],
    'Architecture':[r'architecture',r'design',r'structure'],
    'Code style':[r'style',r'format',r'lint',r'convention'],
    'Do / Don\'t rules':[r'rule',r'do not',r"don't",r'guideline',r'never',r'always'],
    'Security':[r'secur',r'secret',r'credential',r'auth'],
    'Performance':[r'perform',r'latency',r'optim'],
    'Maintenance':[r'maintain',r'update this',r'stale',r'sync'],
    'Ownership':[r'owner',r'contact',r'maintainer'],
    'Tooling / agent':[r'agent',r'claude',r'cursor',r'copilot',r'mcp',r'skill'],
    'Overview':[r'overview',r'purpose',r'about'],
    'Git / PR':[r'commit',r'pull request',r'branch',r'pr '],
}
cat_dur=[]
for cat,kws in CAT_KW.items():
    pats=[re.compile(k,re.I) for k in kws]
    a=sum(c for h,c in added_heads.items() if any(p.search(h) for p in pats))
    d=sum(c for h,c in deleted_heads.items() if any(p.search(h) for p in pats))
    rate=a/(a+d) if a+d else None
    cat_dur.append({'category':cat,'heading_adds':a,'heading_dels':d,
                    'survive_rate':round(rate,3) if rate is not None else None,'total_edits':a+d})
cat_dur_df=pd.DataFrame(cat_dur).sort_values('survive_rate',ascending=False)

# human triangulation
human_path=Path('/gpuhome/shanto1/AIDev/output/human_pr_commit_details.csv')
h_hits=[]
usecols=['owner','repo','sha','pr_id','author','message','created_at','filename','status','additions','deletions']
for chunk in pd.read_csv(human_path, usecols=usecols, chunksize=20000):
    m=chunk['filename'].fillna('').map(lambda p: bool(classify_path(p)))
    if m.any(): h_hits.append(chunk.loc[m])
human=pd.concat(h_hits, ignore_index=True)
human['file_type']=human['filename'].map(lambda p: next(iter(classify_path(p))))
human_summary={
    'n_touches':int(len(human)),
    'n_repos':int(human.groupby(['owner','repo']).ngroups),
    'by_type':{str(k):int(v) for k,v in human['file_type'].value_counts().items()},
    'by_status':{str(k):int(v) for k,v in human['status'].value_counts().items()},
    'median_additions':float(human['additions'].median()),
    'median_deletions':float(human['deletions'].median()),
    'mean_churn_proxy':round(float((human['deletions']/(human['additions'].replace(0,np.nan))).median()),3),
}

# summaries
pattern_tab=life.groupby(['file_type','pattern']).size().unstack(fill_value=0)
trigger_tab=inst.groupby(['file_type','trigger']).size().unstack(fill_value=0)
trigger_pct=(trigger_tab.T/trigger_tab.T.sum()).T*100

life_summary=[]
for t in FILE_TYPES:
    g=life[life.file_type==t]
    if not len(g): continue
    life_summary.append({
        'file_type':t,'n_files':len(g),
        'median_touches':float(g.n_touches.median()),'mean_touches':round(float(g.n_touches.mean()),2),
        'median_authors':float(g.n_authors.median()),'mean_owner_top_share':round(float(g.owner_top_share.mean()),3),
        'median_churn_ratio':round(float(g.churn_ratio.median()),3),
        'median_span_days':float(g.span_days.median()),
        'pct_abandoned':round(100*(g.pattern=='abandoned').mean(),1),
        'pct_burst_taper':round(100*(g.pattern=='burst-taper').mean(),1),
        'pct_continuous':round(100*(g.pattern=='continuous').mean(),1),
        'pct_sparse':round(100*(g.pattern=='sparse').mean(),1),
        'pct_ever_removed':round(100*(g.n_removed>0).mean(),1),
    })

# task type among instruction PRs
task_dist=inst['task_type'].value_counts(dropna=False).head(15).to_dict()
task_by_trigger=inst.groupby(['trigger','task_type']).size().unstack(fill_value=0)

# significant cliffs for churn
sig_cliffs=[c for c in cliff_results if abs(c['delta'])>=0.147]  # medium effect heuristic

results={
    'n_instruction_events':int(len(inst)),
    'n_unique_files':int(len(life)),
    'n_repos':int(inst['repo_full_name'].nunique()),
    'n_prs':int(inst['pr_id'].nunique()),
    'events_by_type':{str(k):int(v) for k,v in inst['file_type'].value_counts().items()},
    'events_by_agent':{str(k):int(v) for k,v in inst['agent'].value_counts().items()},
    'events_by_status':{str(k):int(v) for k,v in inst['status'].value_counts().items()},
    'lifecycle_summary':life_summary,
    'pattern_counts':{ft: pattern_tab.loc[ft].to_dict() if ft in pattern_tab.index else {} for ft in FILE_TYPES},
    'trigger_counts':{ft: {str(k):int(v) for k,v in trigger_tab.loc[ft].items()} if ft in trigger_tab.index else {} for ft in FILE_TYPES},
    'trigger_pct':{ft: {str(k):round(float(v),1) for k,v in trigger_pct.loc[ft].items()} if ft in trigger_pct.index else {} for ft in FILE_TYPES},
    'cochange_rate':{str(k):round(float(v),3) for k,v in inst.groupby('file_type')['cochange'].mean().items()},
    'kruskal_wallis':kw_results,
    'cliffs_delta':cliff_results,
    'cliffs_medium_or_larger':sig_cliffs,
    'durable_headings':durable.to_dict(orient='records'),
    'ephemeral_headings':ephemeral.to_dict(orient='records'),
    'category_durability':cat_dur_df.to_dict(orient='records'),
    'task_type_dist':{str(k):int(v) for k,v in task_dist.items()},
    'human_pr_triangulation':human_summary,
    'template_mapping':{
        'REQUIRED_durable_categories':[r['category'] for r in cat_dur_df.to_dict('records') if r['survive_rate'] and r['survive_rate']>=0.80 and r['total_edits']>=50],
        'OPTIONAL_lower_durability':[r['category'] for r in cat_dur_df.to_dict('records') if r['survive_rate'] and r['survive_rate']<0.80],
        'maintenance_guidance_needed':True,
        'reactive_pct_overall':round(100*(inst.trigger=='reactive').mean(),1),
        'proactive_pct_overall':round(100*(inst.trigger=='proactive').mean(),1),
        'proactive_cochange_pct_overall':round(100*(inst.trigger=='proactive_cochange').mean(),1),
        'abandoned_pct_files':round(100*(life.pattern=='abandoned').mean(),1),
    },
    'notes':{
        'source':'AIDev-pop pr_commit_details filtered to instruction paths',
        'timestamps':'PR merged_at (fallback created_at)',
        'trigger_coding':'Automated heuristic; dual-coder κ pending',
        'abandoned_def':'Exactly one touch in AIDev-pop window',
    },
}

(OUT/'rq3_results.json').write_text(json.dumps(results, indent=2, default=str))
life.to_csv(OUT/'rq3_file_lifecycle.csv', index=False)
inst.drop(columns=['patch'], errors='ignore').to_csv(OUT/'rq3_instruction_events.csv', index=False)
cat_dur_df.to_csv(OUT/'rq3_category_durability.csv', index=False)
pd.DataFrame(kw_results).to_csv(OUT/'rq3_kruskal_wallis.csv', index=False)
pd.DataFrame(cliff_results).to_csv(OUT/'rq3_cliffs_delta.csv', index=False)
durable.to_csv(OUT/'rq3_durable_headings.csv', index=False)
ephemeral.to_csv(OUT/'rq3_ephemeral_headings.csv', index=False)

print('=== LIFECYCLE ===')
print(pd.DataFrame(life_summary).to_string(index=False))
print('\n=== PATTERNS ===')
print(pattern_tab)
print('\n=== TRIGGERS % ===')
print(trigger_pct.round(1))
print('\n=== KW ===')
print(pd.DataFrame(kw_results))
print('\n=== Medium+ Cliff δ ===')
print(pd.DataFrame(sig_cliffs).to_string(index=False))
print('\n=== CAT DURABILITY ===')
print(cat_dur_df.to_string(index=False))
print('\n=== TEMPLATE ===')
print(json.dumps(results['template_mapping'], indent=2))
print('\nHuman:', human_summary)
print('DONE')
