# n=386 LLM consistency sample: directory/component scope audit

## Headline

| Subset | n | **A** (diff scope) | **B** (same scope) | **C** (unclear) |
|---|---:|---:|---:|---:|
| **Full sample** | **386** | **193 (50.0%)** | **186 (48.2%)** | **7 (1.8%)** |
| **LLM label = Divergent** | **62** | **50 (80.6%)** | **11 (17.7%)** | **1 (1.6%)** |
| **Auto label = Divergent** | **160** | **117 (73.1%)** | **41 (25.6%)** | **2 (1.2%)** |

**50 of 62 LLM-Divergent pairs** and **117 of 160 auto-Divergent pairs** are explained by different directory/component scope under the same conservative A/B/C scheme as the n=150 audit.

## Comparison to n=150 Divergent audit

| Audit | Divergent definition | A | B | C | A rate |
|---|---|---:|---:|---:|---:|
| n=150 (`rq2_divergent_scope_report.md`) | auto Divergent | **42** | **20** | **2** | **65.6%** (42/64) |
| n=386 (this audit) | auto Divergent | **117** | **41** | **2** | **73.1%** (117/160) |
| n=386 (this audit) | LLM Divergent | **50** | **11** | **1** | **80.6%** (50/62) |

Auto-Divergent A-rate is in the same ballpark as n=150 (65.6% → 73.1%). LLM-Divergent A-rate is **higher** (80.6%), i.e. when the judge calls Divergent, scope mismatch is even more often the primary explanation. Same-scope content conflicts (B) remain a minority of Divergent cases.

## Method

- Paths resolved from `unified_files/<repo>.json` with the same contributor-matching logic used for `rq2_pair_scope_audit.csv` (format bags merge all same-format files; category text matched back to contributing `source_path`s).
- CSV `path_a`/`path_b` in `sample_n386_llm_judge.csv` are single representative files; audit `path_a`/`path_b` list **all matched contributors** (semicolon-separated).
- **A** — different directory/component scope (component trees, packages/apps/crates/extensions, skill vs general, skill vs copilot, merged multi-dir bags that mix scopes).
- **B** — same repo-wide / same-directory (both root, same folder, root ↔ `.github/copilot` or `.github` general guides).
- **C** — unclear / parallel mirrored bags / docs-user-guide edges.
- All **64** n=150 Divergent pairs present in this sample reuse the prior manual `manual_abc` labels for consistency.

Artifact: `scope_audit_n386.csv`.

## Scope-class distribution (path resolution)

| scope_class | full n=386 | LLM Divergent | auto Divergent |
|---|---:|---:|---:|
| `same_dir_root` | 98 | 4 | 12 |
| `same_dir_nested` | 11 | 0 | 1 |
| `root_vs_github_copilot` | 72 | 7 | 27 |
| `root_or_general_vs_skill` | 64 | 20 | 44 |
| `different_component_trees` | 24 | 5 | 13 |
| `merged_cross_dir` | 115 | 25 | 62 |
| `other_cross_path` | 2 | 1 | 1 |

## LLM Divergent — A (n=50)

- **mastra-ai_mastra** (`id=25`): `packages/server/CLAUDE.md` ↔ `.agents/skills/testing-core-processors/SKILL.md`
- **gronxb_hot-updater** (`id=28`): `CLAUDE.md; plugins/plugin-core/CLAUDE.md` ↔ `.agents/skills/agent-device/SKILL.md; .agents/skills/e2e/SKILL.md`
- **ant-design_ant-design** (`id=29`): `CLAUDE.md` ↔ `.agents/skills/commit-msg/SKILL.md; .agents/skills/create-pr/SKILL.md`
- **block_goose** (`id=41`): `AGENTS.md` ↔ `evals/harbor/.agents/skills/compare_tasks/SKILL.md`
- **bruin-data_bruin** (`id=49`): `CLAUDE.md` ↔ `.agents/skills/humanizer/SKILL.md`
- **Humanizr_Humanizer** (`id=50`): `CLAUDE.md` ↔ `.agents/skills/add-locale/SKILL.md`
- **coder_coder** (`id=51`): `site/CLAUDE.md` ↔ `.agents/skills/coder-agents-review/SKILL.md; .agents/skills/deep-re...`
- **dotCMS_core** (`id=66`): `CLAUDE.md; core-web/apps/mcp-server/CLAUDE.md; core-web/libs/sdk/cl...` ↔ `.agents/skills/link-workspace-packages/SKILL.md`
- **ant-design_ant-design** (`id=82`): `AGENTS.md` ↔ `.agents/skills/changelog-collect/SKILL.md; .agents/skills/create-pr...`
- **supabase_supabase** (`id=85`): `.claude/skills/vercel-composition-patterns/AGENTS.md` ↔ `.agents/skills/vitest/SKILL.md`
- **PostHog_posthog** (`id=87`): `common/CLAUDE.md; ee/hogai/eval/sandboxed/CLAUDE.md; frontend/src/s...` ↔ `.agents/skills/adding-personhog-rpc/SKILL.md; .agents/skills/adding...`
- **PostHog_posthog** (`id=89`): `CLAUDE.md` ↔ `.agents/skills/adding-personhog-rpc/SKILL.md; .agents/skills/clickh...`
- **Significant-Gravitas_AutoGPT** (`id=92`): `.claude/skills/vercel-react-best-practices/AGENTS.md` ↔ `classic/CLAUDE.md; classic/direct_benchmark/CLAUDE.md; classic/forg...`
- **ant-design_ant-design** (`id=93`): `CLAUDE.md` ↔ `.agents/skills/changelog-collect/SKILL.md; .agents/skills/commit-ms...`
- **gronxb_hot-updater** (`id=94`): `.agents/skills/vercel-react-best-practices/AGENTS.md` ↔ `.agents/skills/agent-device/SKILL.md; .agents/skills/shadcn/SKILL.md`
- **activepieces_activepieces** (`id=95`): `packages/pieces/CLAUDE.md` ↔ `.agents/skills/agent-browser/SKILL.md`
- **scalar_scalar** (`id=104`): `AGENTS.md` ↔ `.agents/skills/cloud-agents-starter/SKILL.md; .agents/skills/openap...`
- **bruin-data_bruin** (`id=116`): `AGENTS.md` ↔ `.agents/skills/add-ingestr-source/SKILL.md`
- **oxc-project_oxc** (`id=135`): `AGENTS.md` ↔ `crates/oxc_minifier/docs/CLAUDE.md`
- **calcom_cal.com** (`id=162`): `.opencode/skill/vercel-react-best-practices/AGENTS.md; agents/skill...` ↔ `CLAUDE.md`
- **RSSNext_Folo** (`id=165`): `apps/desktop/AGENTS.md` ↔ `.agents/skills/mobile-release/SKILL.md`
- **dotnet_dotnet** (`id=178`): `src/diagnostics/AGENTS.md` ↔ `src/msbuild/.github/copilot-instructions.md`
- **netz98_n98-magerun2** (`id=183`): `AGENTS.md` ↔ `.agents/skills/magerun-release/SKILL.md`
- **dotCMS_core** (`id=184`): `core-web/apps/dotcms-ui/AGENTS.md` ↔ `.agents/skills/link-workspace-packages/SKILL.md; .agents/skills/nx-...`
- **grafana_loki** (`id=190`): `vendor/github.com/go-playground/validator/v10/CLAUDE.md; vendor/git...` ↔ `vendor/modernc.org/libc/GEMINI.md`
- **PostHog_posthog** (`id=199`): `posthog/clickhouse/migrations/AGENTS.md` ↔ `.agents/skills/depot-container-builds/SKILL.md; .agents/skills/depo...`
- **getsentry_sentry** (`id=202`): `AGENTS.md` ↔ `.agents/skills/cell-architecture/SKILL.md; .agents/skills/generate-...`
- **mixpanel_mixpanel-android** (`id=214`): `CLAUDE.md; analytics/src/androidTest/CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **vercel_next.js** (`id=230`): `CLAUDE.md` ↔ `.agents/skills/dce-edge/SKILL.md; .agents/skills/insight-error-page...`
- **comet-ml_opik** (`id=232`): `.agents/skills/analytics-instrumentation/SKILL.md` ↔ `.github/copilot-instructions.md`
- **supabase_supabase** (`id=237`): `.claude/skills/vercel-composition-patterns/AGENTS.md` ↔ `.claude/CLAUDE.md`
- **ruvnet_claude-flow** (`id=238`): `CLAUDE.md; v3/@claude-flow/cli/CLAUDE.md; v3/@claude-flow/mcp/CLAUD...` ↔ `.agents/skills/agent-agent/SKILL.md; .agents/skills/agent-coder/SKI...`
- **dotCMS_core** (`id=241`): `core-web/apps/dotcms-ui/AGENTS.md` ↔ `CLAUDE.md`
- **yamadashy_repomix** (`id=245`): `.agents/skills/contextual-commit/SKILL.md` ↔ `.github/copilot-instructions.md`
- **Arize-ai_openinference** (`id=248`): `CLAUDE.md; js/CLAUDE.md; python/CLAUDE.md` ↔ `.agents/skills/agent-browser/SKILL.md; .agents/skills/java-code-rev...`
- **vercel_next.js** (`id=250`): `.github/CLAUDE.md` ↔ `.agents/skills/create-pr/SKILL.md`
- **mastra-ai_mastra** (`id=254`): `.claude/skills/builder-smoke-test/references/agents.md` ↔ `packages/playground-ui/CLAUDE.md`
- **gronxb_hot-updater** (`id=262`): `.agents/skills/vercel-react-best-practices/AGENTS.md` ↔ `CLAUDE.md`
- **getsentry_sentry-dart** (`id=264`): `AGENTS.md` ↔ `.agents/skills/code-guidelines/SKILL.md`
- **zauberzeug_nicegui** (`id=293`): `AGENTS.md` ↔ `website/CLAUDE.md`
- **sccn_eeglab** (`id=295`): `AGENTS.md` ↔ `.agents/skills/fix-issue/SKILL.md; .agents/skills/github-pr-review/...`
- **BerriAI_litellm** (`id=297`): `litellm-rust/crates/ai-gateway/src/routes/AGENTS.md; litellm/proxy/...` ↔ `CLAUDE.md; litellm-rust/CLAUDE.md`
- **getsentry_sentry** (`id=306`): `CLAUDE.md; src/CLAUDE.md; static/CLAUDE.md; tests/CLAUDE.md` ↔ `.agents/skills/analytics/SKILL.md; .agents/skills/lint-fix/SKILL.md...`
- **mastra-ai_mastra** (`id=312`): `.claude/skills/mastra-smoke-test/references/tests/agents.md; agent-...` ↔ `.agents/skills/testing-core-processors/SKILL.md`
- **Uniswap_interface** (`id=326`): `AGENTS.md` ↔ `.agents/skills/argent-create-flow/SKILL.md`
- **kyegomez_swarms** (`id=332`): `docs/swarms_rs/agents.md` ↔ `CLAUDE.md`
- **OrchardCMS_OrchardCore** (`id=352`): `AGENTS.md` ↔ `.agents/skills/orchardcore-admin-edit-views/SKILL.md; .agents/skill...`
- **vercel_next.js** (`id=356`): `.github/AGENTS.md` ↔ `.agents/skills/create-pr/SKILL.md`
- **stack-auth_stack-auth** (`id=371`): `CLAUDE.md` ↔ `.agents/skills/roids/SKILL.md`
- **bruin-data_bruin** (`id=383`): `CLAUDE.md` ↔ `.agents/skills/humanizer/SKILL.md`

## LLM Divergent — B (n=11)

- **chrxh_alien** (`id=73`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **Azure_azure-sdk-for-net** (`id=118`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **elsa-workflows_elsa-core** (`id=151`): `AGENTS.md` ↔ `CLAUDE.md`
- **livingbio_typed-ffmpeg** (`id=174`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **Floorp-Projects_Floorp** (`id=192`): `AGENTS.md` ↔ `CLAUDE.md`
- **python-cachier_cachier** (`id=258`): `AGENTS.md` ↔ `CLAUDE.md`
- **BeehiveInnovations_zen-mcp-server** (`id=289`): `AGENTS.md` ↔ `CLAUDE.md`
- **owncast_owncast** (`id=291`): `AGENTS.md` ↔ `.github/copilot-instructions.md`
- **meshtastic_firmware** (`id=304`): `CLAUDE.md` ↔ `.github/copilot-instructions.md`
- **oven-sh_bun** (`id=349`): `AGENTS.md` ↔ `.github/workflows/CLAUDE.md`
- **JanDeDobbeleer_oh-my-posh** (`id=357`): `AGENTS.md` ↔ `.github/copilot-instructions.md`

## LLM Divergent — C (n=1)

- **SuperClaude-Org_SuperClaude_Framework** (`id=26`): `docs/user-guide/agents.md` ↔ `CLAUDE.md`
  - _[n150 manual] docs/user-guide/agents.md looks like user-guide doc vs root CLAUDE; not clear component split (auto_scope=other_cross_path, n150_scope=different_component_trees)_

## Remaining C in full sample (n=7)

- **SuperClaude-Org_SuperClaude_Framework** (`id=26`): `docs/user-guide/agents.md` ↔ `CLAUDE.md` — auto=Divergent, llm=Divergent
  - _[n150 manual] docs/user-guide/agents.md looks like user-guide doc vs root CLAUDE; not clear component split (auto_scope=other_cross_path, n150_scope=different_component_trees)_
- **Arize-ai_openinference** (`id=61`): `AGENTS.md; js/AGENTS.md; python/AGENTS.md` ↔ `CLAUDE.md; js/CLAUDE.md; python/CLAUDE.md` — auto=Equivalent, llm=Equivalent
  - _parallel multi-dir bags; not clear component split_
- **StarRocks_starrocks** (`id=229`): `AGENTS.md; be/AGENTS.md; fe/AGENTS.md; gensrc/AGENTS.md` ↔ `CLAUDE.md; be/CLAUDE.md; fe/CLAUDE.md; gensrc/CLAUDE.md` — auto=Equivalent, llm=Equivalent
  - _parallel multi-dir bags; not clear component split_
- **tommyxchow_frosty** (`id=341`): `AGENTS.md; web/AGENTS.md` ↔ `.claude/CLAUDE.md; web/.claude/CLAUDE.md` — auto=Divergent, llm=Complementary
  - _[n150 manual] both formats merge root+web; parallel coverage, not clear fe/be split_
- **netdata_netdata** (`id=359`): `AGENTS.md; src/go/AGENTS.md` ↔ `GEMINI.md; src/go/GEMINI.md` — auto=Equivalent, llm=Equivalent
  - _parallel multi-dir bags; not clear component split_
- **tinacms_tinacms** (`id=361`): `AGENTS.md; examples/AGENTS.md` ↔ `CLAUDE.md; examples/CLAUDE.md` — auto=Equivalent, llm=Equivalent
  - _parallel multi-dir bags; not clear component split_
- **dailydotdev_apps** (`id=380`): `AGENTS.md; packages/playwright/AGENTS.md; packages/shared/src/compo...` ↔ `CLAUDE.md; packages/playwright/CLAUDE.md` — auto=Equivalent, llm=Equivalent
  - _parallel multi-dir bags; not clear component split_

## Notes for paper wording

- Pairing is **same-repo, cross-format, same-category**; paths are **not** constrained to the same directory/component.
- A large share of Divergent labels (auto and LLM) are **scope-driven** rather than same-scope instruction conflicts.
- Root ↔ `.github/copilot-instructions.md` is coded **B** (same logical repo-wide scope), matching the n=150 audit.
