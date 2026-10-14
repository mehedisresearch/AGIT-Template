"""Shared automated metrics for instruction-file generation evaluation."""

import re
from rouge_score import rouge_scorer as rouge_lib
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score

GAP_KEYWORDS = [
    "security",
    "secret",
    "api key",
    "credential",
    "never commit",
    "performance",
    "latency",
    "throughput",
    "optimize",
    "maintenance",
    "when to update",
    "update this file",
    "overview",
    "purpose",
    "about this project",
    "owner",
    "contact",
    "maintainer",
]

REQUIRED_KEYWORDS = {
    "Build": ["install", "build", "pnpm", "npm", "maven", "pip", "yarn", "make"],
    "Test": ["test", "jest", "pytest", "junit", "coverage", "ci"],
    "Style": ["style", "lint", "naming", "convention", "format"],
    "Architecture": ["architecture", "design", "pattern", "module"],
    "Rules": ["do not", "never", "always", "must", "avoid", "don't"],
    "Structure": ["structure", "directory", "folder", "src/", "layout"],
    "Models": ["model", "entity", "schema", "abstraction", "class"],
    "API": ["api", "interface", "contract", "endpoint", "graphql"],
    "Examples": ["example", "snippet", "```"],
    "Tooling": ["agent", "skill", "tool", "relay", "cursor"],
}


def lexical_and_structure_metrics(reference, hypothesis):
    rscorer = rouge_lib.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    smoother = SmoothingFunction().method1

    rouge = rscorer.score(reference, hypothesis)
    bleu = corpus_bleu(
        [[reference.split()]],
        [hypothesis.split()],
        smoothing_function=smoother,
    )
    met = meteor_score([reference.split()], hypothesis.split())

    h_lower = hypothesis.lower()
    coverage = sum(
        1
        for kws in REQUIRED_KEYWORDS.values()
        if any(kw in h_lower for kw in kws)
    )
    has_gap = int(any(kw in h_lower for kw in GAP_KEYWORDS))
    headings = len(re.findall(r"^#{1,3}\s+\S", hypothesis, re.MULTILINE))
    valid_fmt = int(headings >= 3 and "```" in hypothesis)

    return {
        "rouge1": round(rouge["rouge1"].fmeasure, 4),
        "rougeL": round(rouge["rougeL"].fmeasure, 4),
        "bleu": round(bleu, 4),
        "meteor": round(met, 4),
        "coverage": coverage,
        "has_gap": has_gap,
        "valid_fmt": valid_fmt,
    }


def add_bertscore(scores, bert_f1):
    scores["bertscore_f1"] = round(float(bert_f1), 4)
    return scores


def aggregate(scores, skip_keys=("repo", "format", "tier", "mode", "idx")):
    n = len(scores)
    if n == 0:
        return {}
    keys = [k for k in scores[0] if k not in skip_keys]
    return {k: round(sum(s[k] for s in scores) / n, 4) for k in keys}


def print_results_table(results_dict):
    print("\n" + "=" * 95)
    print(
        f"{'Model':<32} {'R1':>6} {'RL':>6} {'BLEU':>6} "
        f"{'METEOR':>7} {'BERT':>6} {'Cov':>5} {'Gap%':>6} {'Fmt%':>6}"
    )
    print("-" * 95)
    for model_name, agg in results_dict.items():
        print(
            f"{model_name:<32} "
            f"{agg.get('rouge1', 0):>6.3f} "
            f"{agg.get('rougeL', 0):>6.3f} "
            f"{agg.get('bleu', 0):>6.3f} "
            f"{agg.get('meteor', 0):>7.3f} "
            f"{agg.get('bertscore_f1', 0):>6.3f} "
            f"{agg.get('coverage', 0):>5.1f} "
            f"{agg.get('has_gap', 0) * 100:>6.1f} "
            f"{agg.get('valid_fmt', 0) * 100:>6.1f}"
        )
    print("=" * 95)
