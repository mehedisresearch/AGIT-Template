# RQ2 Divergent pairs: directory/component scope audit

## Headline

**42 of 64 Divergent pairs are explained by different directory/component scope.**

| Class | n | Meaning |
|---|---:|---|
| **A** Different directory/component scope | **42** | Primary explanation matches frontend/backend / package / skill-vs-general spirit |
| **B** Same repo-wide / same-directory scope | **20** | Both root, same folder, or root↔`.github/copilot` general guides |
| **C** Unclear / edge | **2** | Not forced into A or B |

## Where “59” comes from

In the 150-sample (`manual_coding_sample.csv` / `llm_judge_metrics.json`):

| Source | Divergent count |
|---|---:|
| **Auto labels** (`auto_label`) | **64** |
| LLM judge (`llm_label`) | 23 |
| Auto Contradictory (separate) | 7 |

**No artifact in `interchangeability/` documents “59 Divergent.”**
The figure most likely is a misremembered **64**, or an informal **64 − 5 = 59** if excluding the five same-root `AGENTS.md`↔`CLAUDE.md` content conflicts (`same_dir_root`).
Population Divergent rate for the Security category is 59.8% in `summary.json`, unrelated to the sample count.

This audit uses the exact auto-labeled **64** Divergent pairs.

## Method

- Paths taken from `rq2_pair_scope_audit.csv` (reconstructed source paths for format bags).
- **A** only when different scope is a *plausible primary* explanation for the divergence (component trees, packages/apps/crates/extensions, skill vs general, merged multi-dir bags that mix components).
- **B** when both sides are repo-wide general guides (incl. root ↔ `.github/copilot`) or the same directory — content/role disagreement, not a frontend/backend-style scope split.
- Conservative: same-root format disagreements stay **B**; ambiguous cases stay **C**.

## A — Different directory/component scope (n=42)

- **OrchardCMS_OrchardCore** (`id=3`): `AGENTS.md` ↔ `.agents/skills/orchardcore-admin-edit-views/SKILL.md; .agents/skills/orchardcore-asset-...`
- **modelcontextprotocol_servers** (`id=8`): `src/everything/AGENTS.md` ↔ `CLAUDE.md`
- **bruin-data_bruin** (`id=12`): `CLAUDE.md` ↔ `.agents/skills/humanizer/SKILL.md`
- **getsentry_sentry** (`id=15`): `AGENTS.md; src/AGENTS.md` ↔ `.agents/skills/analytics/SKILL.md`
- **cline_cline** (`id=17`): `sdk/packages/llms/AGENTS.md` ↔ `.agents/skills/cline-sdk/SKILL.md; .agents/skills/create-pull-request/SKILL.md`
- **RSSNext_Folo** (`id=18`): `apps/desktop/AGENTS.md` ↔ `.agents/skills/mobile-release/SKILL.md`
- **supabase_supabase** (`id=19`): `.claude/skills/vercel-composition-patterns/AGENTS.md` ↔ `.agents/skills/vitest/SKILL.md`
- **openai_openai-agents-js** (`id=21`): `AGENTS.md` ↔ `.agents/skills/maintainer-review/SKILL.md`
- **coder_coder** (`id=26`): `site/CLAUDE.md` ↔ `.agents/skills/coder-agents-review/SKILL.md; .agents/skills/deep-review/SKILL.md`
- **Azure_azure-service-operator** (`id=30`): `.agents/skills/migrate-group-versioning/SKILL.md` ↔ `.github/copilot-instructions.md`
- **oxc-project_oxc** (`id=31`): `CLAUDE.md; apps/oxfmt/CLAUDE.md; crates/oxc_formatter/CLAUDE.md; crates/oxc_formatter_c...` ↔ `.github/copilot-instructions.md`
- **getsentry_sentry-dart** (`id=32`): `AGENTS.md` ↔ `.agents/skills/code-guidelines/SKILL.md`
- **mastra-ai_mastra** (`id=34`): `packages/server/CLAUDE.md` ↔ `.agents/skills/testing-core-processors/SKILL.md`
- **vercel_next.js** (`id=39`): `CLAUDE.md` ↔ `.agents/skills/dce-edge/SKILL.md; .agents/skills/insight-error-page/SKILL.md`
- **raycast_extensions** (`id=41`): `extensions/agent-usage/AGENTS.md` ↔ `extensions/anytype/CLAUDE.md`
- **OrchardCMS_OrchardCore** (`id=42`): `AGENTS.md` ↔ `.agents/skills/orchardcore-module-creator/SKILL.md; .agents/skills/orchardcore-theme-cr...`
- **onnx_onnx** (`id=48`): `CLAUDE.md` ↔ `.agents/skills/add-op/SKILL.md; .agents/skills/add-shape-inference/SKILL.md`
- **PostHog_posthog** (`id=57`): `AGENTS.md` ↔ `.agents/skills/clickhouse-migrations/SKILL.md`
- **Arize-ai_openinference** (`id=59`): `AGENTS.md` ↔ `.agents/skills/agent-browser/SKILL.md`
- **NangoHQ_nango** (`id=60`): `CLAUDE.md` ↔ `.agents/skills/agent-builder-skill/SKILL.md; .agents/skills/building-and-verifying/SKIL...`
- **windmill-labs_windmill** (`id=63`): `CLAUDE.md; ai_evals/CLAUDE.md` ↔ `.agents/skills/commit/SKILL.md; .agents/skills/local-review/SKILL.md`
- **yamadashy_repomix** (`id=67`): `.agents/skills/contextual-commit/SKILL.md` ↔ `.github/copilot-instructions.md`
- **PostHog_posthog** (`id=72`): `CLAUDE.md` ↔ `.agents/skills/adding-personhog-rpc/SKILL.md`
- **mastra-ai_mastra** (`id=75`): `.claude/skills/builder-smoke-test/references/agents.md` ↔ `packages/playground-ui/CLAUDE.md`
- **microsoft_onnxruntime** (`id=82`): `AGENTS.md` ↔ `.agents/skills/contrib-op-shape-inference-memory-safety/SKILL.md`
- **mastra-ai_mastra** (`id=83`): `.claude/skills/mastra-smoke-test/references/tests/agents.md; agent-sdks/acp/AGENTS.md` ↔ `.agents/skills/testing-core-processors/SKILL.md`
- **microsoft_teams-ai** (`id=84`): `packages/cli/AGENTS.md` ↔ `.github/copilot-instructions.md`
- **OrchardCMS_OrchardCore** (`id=86`): `AGENTS.md` ↔ `.agents/skills/orchardcore-admin-edit-views/SKILL.md`
- **getsentry_sentry** (`id=87`): `CLAUDE.md; src/CLAUDE.md; static/CLAUDE.md; tests/CLAUDE.md` ↔ `.agents/skills/analytics/SKILL.md; .agents/skills/lint-fix/SKILL.md; .agents/skills/mig...`
- **netz98_n98-magerun2** (`id=89`): `AGENTS.md` ↔ `.agents/skills/magerun-release/SKILL.md`
- **ComposioHQ_composio** (`id=94`): `AGENTS.md; docs/AGENTS.md` ↔ `ts/packages/cli/CLAUDE.md`
- **ant-design_ant-design** (`id=99`): `AGENTS.md` ↔ `.agents/skills/changelog-collect/SKILL.md; .agents/skills/create-pr/SKILL.md; .agents/s...`
- **dotCMS_core** (`id=102`): `core-web/apps/dotcms-ui/AGENTS.md` ↔ `.agents/skills/link-workspace-packages/SKILL.md; .agents/skills/nx-generate/SKILL.md`
- **mono_SkiaSharp** (`id=103`): `AGENTS.md` ↔ `.agents/skills/api-add-review/SKILL.md`
- **NangoHQ_nango** (`id=105`): `docs/AGENTS.md` ↔ `.agents/skills/agent-builder-skill/SKILL.md; .agents/skills/creating-integration-docs/S...`
- **sccn_eeglab** (`id=117`): `AGENTS.md` ↔ `.agents/skills/fix-issue/SKILL.md; .agents/skills/github-pr-review/SKILL.md`
- **bruin-data_bruin** (`id=122`): `CLAUDE.md` ↔ `.agents/skills/humanizer/SKILL.md`
- **dotCMS_core** (`id=129`): `core-web/apps/dotcms-ui/AGENTS.md` ↔ `CLAUDE.md`
- **bruin-data_bruin** (`id=133`): `AGENTS.md` ↔ `.agents/skills/add-ingestr-source/SKILL.md`
- **gronxb_hot-updater** (`id=141`): `plugins/plugin-core/CLAUDE.md` ↔ `.agents/skills/shadcn/SKILL.md`
- **rustfs_rustfs** (`id=144`): `crates/AGENTS.md; crates/ecstore/AGENTS.md; crates/targets/AGENTS.md; rustfs/src/storag...` ↔ `.agents/skills/rust-code-quality/SKILL.md`
- **StarRocks_starrocks** (`id=146`): `AGENTS.md; be/AGENTS.md; be/src/common/AGENTS.md; docs/AGENTS.md; fe/AGENTS.md` ↔ `.github/copilot-instructions.md`

## B — Same repo-wide / same-directory (n=20)

- **Azure_azure-sdk-for-net** (`id=9`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **openops-cloud_openops** (`id=16`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **pixeltable_pixeltable** (`id=29`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **pytorch_pytorch** (`id=43`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **buefy_buefy** (`id=47`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **Humanizr_Humanizer** (`id=56`): `AGENTS.md` ↔ `CLAUDE.md`
- **strapi_documentation** (`id=74`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **AstrBotDevs_AstrBot** (`id=78`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **eyaltoledano_claude-task-master** (`id=79`): `assets/AGENTS.md` ↔ `assets/GEMINI.md`
- **SolidInvoice_SolidInvoice** (`id=85`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **laravel-workflow_laravel-workflow** (`id=88`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **Floorp-Projects_Floorp** (`id=90`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **apache_pinot** (`id=93`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **BeehiveInnovations_zen-mcp-server** (`id=108`): `AGENTS.md` ↔ `CLAUDE.md`
- **mautic_mautic** (`id=110`): `AGENTS.md` ↔ `CLAUDE.md`
- **pixeltable_pixeltable** (`id=118`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **Skyvern-AI_skyvern** (`id=121`): `AGENTS.md` ↔ `CLAUDE.md`
- **Lumiwealth_lumibot** (`id=127`): `AGENTS.md` ↔ `CLAUDE.md`
- **getsentry_sentry-cocoa** (`id=135`): `.github/AGENTS.md; AGENTS.md` ↔ `CLAUDE.md`
- **NewFuture_DDNS** (`id=138`): `AGENTS.md` ↔ `.github/copilot-instructions.md`

## C — Unclear / edge (n=2)

- **tommyxchow_frosty** (`id=49`): `AGENTS.md; web/AGENTS.md` ↔ `.claude/CLAUDE.md; web/.claude/CLAUDE.md`
  - _both formats merge root+web; parallel coverage, not clear fe/be split_
- **SuperClaude-Org_SuperClaude_Framework** (`id=55`): `docs/user-guide/agents.md` ↔ `CLAUDE.md`
  - _docs/user-guide/agents.md looks like user-guide doc vs root CLAUDE; not clear component split_

## Notes for paper wording

- Of auto-labeled Divergent pairs in the 150-sample, **42/64 (66%)** are primarily scope-driven under a conservative manual coding.
- **20/64 (31%)** remain plausible same-scope content conflicts (including root↔Copilot).
- Pairing merges all same-format files per repo before cross-format section matching, so path scope is not controlled by design.

Updated columns in `rq2_pair_scope_audit.csv`: `manual_abc`, `explained_by_diff_scope`, `manual_note`.
