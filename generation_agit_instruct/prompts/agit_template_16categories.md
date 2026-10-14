# Generic Agent Instruction Template (AGIT)

This file is a **repository-agnostic** instruction template derived from
high-coverage real AGENTS/CLAUDE/Copilot/SKILL files in the AGIT corpus.
It captures *what each section should contain*, not project-specific facts.
When generating or reviewing an instruction file, keep this structure and
fill facts only from the target repository evidence (README, manifests, CI).

## Project overview / purpose

- State what the project does in 2–4 sentences for an agent that has never seen the repo.
- Name the primary users (contributors, SDK consumers, operators) and the main workflows.
- Point to the canonical docs entry (README, docs site) without inventing product claims.
- Prefer facts that appear in the repository README over marketing language.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Project Overview)

Dis na wan educational curriculum repository wey dem dey use teach web development fundamentals to beginners. Di curriculum na big 12-week course wey Microsoft Cloud Advocates make, get 24 hands-on lessons covering JavaScript, CSS, and HTML.

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Common shellcheck Directives in nvm)

- `# shellcheck disable=SC2039` - Allow bash extensions in POSIX mode
- `# shellcheck disable=SC2016` - Allow literal `$` in single quotes
- `# shellcheck disable=SC2001` - Allow sed usage instead of parameter expansion
- `# shellcheck disable=SC3043` - Allow `local` keyword (bash extension)

</details>

## Repository structure

- Summarize the top-level layout: apps/, packages/, src/, docs/, tests/, scripts/, .github/.
- Say where agents should look first for application code vs libraries vs tooling.
- Call out monorepo workspace roots if present (pnpm-workspace, cargo workspace, solutions).
- Keep paths accurate to this repository; do not invent folders.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Monorepo Structure)

While not a traditional monorepo, this repository contains multiple independent projects:
- Each lesson is self-contained
- Projects don't share dependencies
- Work on individual projects without affecting others
- Clone entire repo for the full curriculum experience

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Disclaimer**:
This document has been translated using AI translation service [Co-op Translator](<REPO_URL>). While we strive for accuracy, please be aware that automated translations may contain errors or inaccuracies. The original document in its native language should be considered the authoritative source. For critical information, professional human translation is recommende
…

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: `install.sh`)

Handles nvm installation via curl/wget/git:
- Downloads nvm from GitHub
- Sets up directory structure
- Configures shell integration
- Supports both git clone and script download methods

</details>

## Build / run / install

- Document the package manager and install command used by this repo (npm/pnpm/yarn/pip/uv/cargo/dotnet/…).
- Give the exact local build and run commands from README, Makefiles, or package scripts.
- Note toolchain prerequisites (language version, Node/.NET/Python, Docker) only if evidenced.
- Prefer copy-pasteable shell blocks; do not invent solution names or scripts that are not in the tree.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Common Issues)

**Quiz app fails to start**:
- Check Node.js version (v14+ recommended)
- Delete `node_modules` and `package-lock.json`, run `npm install` again
- Check for port conflicts (default: Vite uses port 5173)

**API server won't start**:
- Verify Node.js version meets minimum (node >=10)
- Check if port is already in use
- Ensure all dependencies installed with `npm install`

**Browser extension won't load**:
- Verify manifest.json is properly formatted
- Check browser console for errors
- Follow browser-specific extension installation instructions

**Python chat project issues**:
- Ensure OpenAI package installed: `pip install openai`
- Verify GITHUB_TOKEN environment variable is set
- Check GitH
…

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Common Gotchas)

1. **PATH modification**: nvm modifies PATH extensively; be careful with restoration
2. **Shell sourcing**: nvm must be sourced, not executed as a script
3. **Version resolution**: Aliases, partial versions, and special keywords interact complexly
4. **Platform differences**: Handle differences between Linux, macOS, and other Unix systems
5. **Network dependencies**: Many operations require internet access for version lists
6. **Concurrent access**: Multiple shells can conflict when installing versions simultaneously

</details>

## Test / CI commands

- Document how to run unit, integration, and lint checks locally.
- Reference the CI system and what must be green before merge (GitHub Actions, Azure DevOps, …).
- Include filters or package-scoped test commands when the repo uses them.
- Do not invent coverage thresholds or workflow names that are not in `.github/workflows` or docs.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Related Resources)

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub resources](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) dey recommended for learners
- Other courses: Generative AI, Data Science, ML, IoT curricula dey available

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Individual Test Execution)

```bash
./test/fast/Unit\ tests/nvm_get_arch     # Run single test (WARNING: This will exit/terminate your current shell session)
./node_modules/.bin/urchin test/fast/                        # Run fast test suite
./node_modules/.bin/urchin 'test/fast/Unit tests/nvm_get_arch'  # Run single test safely without shell termination
./node_modules/.bin/urchin test/slow/                        # Run slow test suite
./node_modules/.bin/urchin test/sourcing/                    # Run sourcing test suite
./node_modules/.bin/urchin test/install_script/              # Run install script test suite
./node_modules/.bin/urchin test/installation_node/           # Run Node installation test suite
./node_module
…

</details>

## Code style / formatting

- Name the formatter/linter stack (eslint, prettier, ruff, black, editorconfig, dotnet format, …).
- State naming and formatting rules that contributors must follow.
- Point to config files (`.eslintrc`, `pyproject.toml`, `.editorconfig`) rather than restating every rule.
- Prefer “run the project formatter” over invented style guides.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Required Checks)

提交 PR 前：

1. <strong>程式碼品質</strong>：
   - 在受影響的專案資料夾執行 `npm run lint`
   - 修正所有 lint 錯誤及警告

2. <strong>建置驗證</strong>：
   - 執行 `npm run build`（如適用）
   - 確認無建置錯誤

3. <strong>連結驗證</strong>：
   - 測試所有 Markdown 連結
   - 確認圖片參照正常

4. <strong>內容審核</strong>：
   - 校對拼字與文法
   - 確保程式碼範例正確且具教育意義
   - 驗證翻譯保持原意

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Linting and Docs Checks)

```bash
npm run eclint               # Checks EditorConfig compliance
npm run doctoc:check         # Verifies README table of contents
npm run dockerfile_lint      # Lints the Dockerfile
npm run test:check-exec      # Checks test files have executable permission
npm run test:check-nonexec   # Checks non-test files don't have executable permission
npm run markdown-link-check  # Validates markdown links (requires markdown-link-check)
```

</details>

## Architecture / design constraints

- Describe major layers/modules and allowed dependency directions.
- State non-negotiable design rules (no cross-layer imports, prefer composition, keep APIs stable).
- Reference architecture docs or ADRs when they exist.
- Avoid generic SOLID boilerplate that is not enforced in this repo.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Key Components)

- **Educational Content**: 24 structured lessons wey dem organize inside project-based modules
- **Practical Projects**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, and AI Chat Assistant
- **Interactive Quizzes**: 48 quizzes wey get 3 questions each (pre/post-lesson assessments)
- **Multi-language Support**: Automated translations for 50+ languages through GitHub Actions
- **Technologies**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (for AI projects)

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Core Architecture)

- **Main script**: `nvm.sh` - Contains all core functionality and the main `nvm()` function
- **Installation script**: `install.sh` - Handles downloading and installing nvm itself
- **Execution wrapper**: `nvm-exec` - Allows running commands with specific Node.js versions
- **Bash completion**: `bash_completion` - Provides tab completion for bash users
- **Tests**: Comprehensive test suite in `test/` directory using the [urchin](https://www.npmjs.com/package/urchin) test framework

</details>

## Domain models / key abstractions

- Define the core domain types/entities agents will touch.
- Explain how data flows between those abstractions.
- Point to canonical model packages or schema locations.
- Do not invent entities that do not appear in the codebase.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Common Issues)

<strong>測驗應用無法啟動</strong>：
- 檢查 Node.js 版本（建議 v14+）
- 刪除 `node_modules` 及 `package-lock.json`，重新執行 `npm install`
- 檢查埠號衝突（預設：Vite 使用埠5173）

**API 伺服器無法啟動**：
- 確認 Node.js 版本符合要求（node >=10）
- 確定埠號未被占用
- 確保已執行 `npm install` 安裝所有相依套件

<strong>瀏覽器擴充功能無法載入</strong>：
- 確認 manifest.json 格式正確
- 檢查瀏覽器主控台錯誤訊息
- 遵循瀏覽器特定的擴充功能安裝指示

**Python 聊天專案問題**：
- 確認已安裝 OpenAI 套件：`pip install openai`
- 確保 GITHUB_TOKEN 環境變數設定正確
- 檢查 GitHub Models 存取權限

**Docsify 文件無法啟動**：
- 全域安裝 docsify-cli：`npm install -g docsify-cli`
- 於資源庫根目錄執行
- 檢查 `docs/_sidebar.md` 是否存在

**Exemplar 2** (`Stirling-Tools_Stirling-PDF` / `AGENTS.md` / heading: Python Typing and Models)

- Deserialize into Pydantic models as early as possible.
- Serialize from Pydantic models as late as possible.
- Do not pass raw `dict[str, Any]` or `dict[str, object]` across important boundaries when a typed model can exist instead.
- Avoid `Any` wherever possible.
- Avoid `cast()` wherever possible (reconsider the structure first).
- All shared models should subclass `stirling.models.ApiModel` so the service behaves consistently.
- Do not use string literals for any type annotations, including `cast()`.

</details>

## API / interface contracts

- Document public APIs, CLI entrypoints, or RPC/HTTP contracts agents must respect.
- Note versioning / compatibility expectations for public surfaces.
- Point to OpenAPI, proto, or typed interface directories when present.
- Avoid fabricating endpoints or method signatures.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Bank Project API (Node.js + Express))

```bash
cd 7-bank-project/api
npm install
npm start          # Start API server
npm run lint       # Run ESLint
npm run format     # Format with Prettier
```

**Exemplar 2** (`netdata_netdata` / `SKILL.md` / heading: 8. Canonical documentation pointers)

| Topic | Open when | Path |
|---|---|---|
| NIDL framework | designing metrics, labels, charts | `docs/NIDL-Framework.md` |
| Chart types and dimension algorithms | choosing chart shape and metric algorithm | `src/database/rrdset-type.h`, `src/database/rrd-algorithm.h` |
| Chart priorities (C) | dashboard ordering convention | `src/collectors/all.h` |
| Shared metric definitions (C) | reusing common contexts | `src/collectors/common-contexts/` |
| Plugin types and privileges | choosing where to add a collector | `src/collectors/README.md` |
| External plugin protocol | non-Go external plugin | `src/plugins.d/README.md` |
| go.d V2 authoring | adding a `go.d` module | `src/go/plugin/go.d/doc
…

</details>

## Do / Don't rules

### Do
- Follow existing patterns in neighboring code before inventing new ones.
- Run the project’s lint/tests before submitting changes.
- Keep diffs focused; update docs/instruction files when behavior changes.
- Prefer shared utilities over copy-pasted logic.

### Don't
- Do not commit secrets, credentials, or `.env` files.
- Do not bypass CI checks or disable failing tests without discussion.
- Do not introduce a second package manager or build system.
- Do not add large unrelated refactors to bugfix PRs.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Contribution Requirements)

- Agree to Microsoft CLA (automated check on first PR)
- Follow the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines
- Reference issue numbers in PR description if applicable

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Fixing shellcheck Issues)

1. **Quoting**: Always quote variables: `"${VAR}"` instead of `$VAR`
2. **POSIX compliance**: Avoid bash-specific features in portable sections
3. **Array usage**: Use `set --` for positional parameters instead of arrays, which are not supported in POSIX
4. **Local variables**: Declared with `local FOO` and then initialized on the next line (the latter is for ksh support)

</details>

## Git / PR / commit conventions

- Follow the repository’s branch naming and PR template.
- Use the commit style this project already uses (conventional commits if configured).
- Keep PRs reviewable; link issues when applicable.
- Do not invent a commit format that conflicts with existing history or bots.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Working with Specific Projects)

For detailed instructions on individual projects, refer to the README files in:
- `quiz-app/README.md` - Vue 3 quiz application
- `7-bank-project/README.md` - Banking application with authentication
- `5-browser-extension/README.md` - Browser extension development
- `6-space-game/README.md` - Canvas-based game development
- `9-chat-project/README.md` - AI chat assistant project

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Git Bash (MSYS2))

- Comes with Git for Windows
- Limited functionality compared to full Linux environment
- Some features may not work due to path translation issues, including:
  - Binary extraction paths may be incorrectly translated
  - Symlink creation may fail
  - Some shell-specific features may behave differently
  - File permissions handling differs from Unix systems

</details>

## Tooling-specific agent config

- Describe how this instruction file relates to sibling formats (AGENTS.md, CLAUDE.md, Copilot, Cursor rules).
- Note any agent permissions, MCP tools, or skill files that must be loaded first.
- Prefer repo-local agent config over generic assistant advice.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`nvm-sh_nvm` / `AGENTS.md` / heading: WSL2 (Windows Subsystem for Linux))

- Full nvm functionality available
- **Important**: Ensure you're using WSL2, not WSL1 - see [Microsoft's WSL2 installation guide](https://docs.microsoft.com/en-us/windows/wsl/install) for up-to-date instructions
- Install Ubuntu or other Linux distribution from Microsoft Store
- Follow Linux installation instructions within WSL2

**Exemplar 2** (`netdata_netdata` / `SKILL.md` / heading: AI Fast Path)

For implementation agents, route to the concrete workflow first and use the
rest of this skill as background:

- New go.d collector: read `src/go/AGENTS.md`, then
  `src/go/plugin/go.d/docs/how-to-write-a-collector.md`,
  `.agents/skills/project-writing-go-modules-framework-v2/SKILL.md`, and
  `.agents/skills/integrations-lifecycle/recipes/add-go-collector.md`.
- Existing go.d collector update: read `src/go/AGENTS.md`, the collector's
  local files, `.agents/skills/integrations-lifecycle/consistency.md`, and
  `.agents/skills/integrations-lifecycle/recipes/update-collector.md`.
- V1-to-V2 migration: read `src/go/AGENTS.md`,
  `src/go/plugin/go.d/docs/migrate-v1-to-v2.md`, and the V2 skill be
…

</details>

## Examples / few-shot snippets

- Provide short, real examples of preferred command invocations or API usage from this repo.
- Use fenced code blocks matching the project’s language.
- Examples must be runnable or clearly illustrative — not placeholder `foo/bar` samples.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: For Learners)

1. Fork or clone the repository
2. Navigate to lesson directories sequentially
3. Read README files for each lesson
4. Complete pre-lesson quizzes at https://ff-quizzes.netlify.app/web/
5. Work through code examples in lesson folders
6. Complete assignments and challenges
7. Take post-lesson quizzes

**Exemplar 2** (`netdata_netdata` / `SKILL.md` / heading: 3.4 OTEL mappings — per-metric YAML routing)

Netdata's OTEL plugin (`src/crates/otel-plugin/`) accepts any OTLP gRPC metric. Mapping is **generic by default** — all resource attributes, scope attributes, and data point attributes become chart labels — but the operator controls routing via per-metric YAML files at `/etc/netdata/otel.d/v1/metrics/*.yaml`. Key knobs:

- `instrumentation_scope.name` / `version` — regex match to scope an entry to a specific OTel instrumentation
- `dimension_attribute_key` — which data point attribute becomes the dimension name (default: `"value"`); other attributes become chart labels
- `interval_secs`, `grace_period_secs` — per-metric timing overrides

Aggregation temporality drives the chart algorithm: Ga
…

</details>

## Security / secrets

- Never commit API keys, tokens, private keys, or customer data.
- Load secrets from the project’s approved mechanism (env vars, secret manager, CI secrets).
- Do not log credentials; redact sensitive fields in traces.
- Follow security docs or CODEOWNERS for auth-related changes.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`nvm-sh_nvm` / `AGENTS.md` / heading: Utility Functions)

- `nvm_echo()`, `nvm_err()` - Output functions
- `nvm_has()` - Checks if command exists
- `nvm_sanitize_path()` - Cleans sensitive data from paths
- `nvm_die_on_prefix()` - Validates npm prefix settings
- `nvm_ensure_default_set()` - Ensures default alias is set
- `nvm_auto()` - Automatic version switching from .nvmrc

**Exemplar 2** (`netdata_netdata` / `SKILL.md` / heading: 5.2 Routing by task)

| If you are doing… | Start with |
|---|---|
| New off-the-shelf application integration (no CGO) | `src/go/plugin/go.d/docs/how-to-write-a-collector.md`; primary V2 reference: `src/go/plugin/go.d/collector/cato_networks/` |
| Migrating existing go.d collector to V2 | `src/go/plugin/go.d/docs/migrate-v1-to-v2.md`; V2 mechanics: `.agents/skills/project-writing-go-modules-framework-v2/SKILL.md` |
| New IBM workload integration (CGO) | `src/go/plugin/ibm.d/AGENTS.md`, `src/go/plugin/ibm.d/framework/README.md` |
| New Rust plugin | SDK at `src/crates/netdata-plugin/`; reference: `src/crates/netflow-plugin/` |
| New SNMP profile (no code change) | `src/go/plugin/go.d/collector/snmp/profile-format
…

</details>

## Performance

- Avoid unnecessary work on hot paths; measure before micro-optimizing.
- Respect existing caching, batching, and pagination patterns.
- Do not add unbounded loops over large collections without limits.
- Call out known performance constraints documented in the repo.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Performance Considerations)

- Large number of translated files (50+ languages) means full clones are large
- Use shallow clone if only working on content: `git clone --depth 1`
- Exclude translations from searches when working on English content
- Build processes may be slow on first run (npm install, Vite build)

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Performance)

- Cache expensive operations (like remote version lists)
- Use local variables to avoid scope pollution
- Minimize subprocess calls where possible
- Implement lazy loading for optional features

</details>

## Ownership / contacts

- Point to CODEOWNERS, maintainers list, or team contacts if present.
- Say where to ask questions ( Discussions, Discord, Slack, issues ).
- Do not invent email addresses or owner names.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`nvm-sh_nvm` / `AGENTS.md` / heading: `nvm ls-remote [pattern]`)

- **Internal functions**: `nvm_ls_remote()`, `nvm_download()`, `nvm_ls_remote_index_tab()`
- Lists available Node.js versions from nodejs.org and iojs.org, or the env-var-configured mirrors
- Supports LTS filtering and pattern matching
- Downloads version index on-demand

**Exemplar 2** (`netdata_netdata` / `SKILL.md` / heading: What this skill is)

You are about to add or modify data collection in the Netdata Agent. This skill is a manifesto and a routing map. It tells you the mindset to apply, the principles you cannot violate, the ways the dashboard gets shaped from upstream data, the quality bar that separates a draft from a shippable collector, and where to look for depth. It is not a tutorial — the deep references already exist in the repo. Your job is to know they exist, pick the right one, and produce work that blends with the patterns the maintainers already accept.

The skill is organized as: AI fast path → mental model → best practices → dashboard shaping → quality bar → environment reference → applied per data type → applied
…

</details>

## Maintenance / when to update

- Update this instruction file when build/test commands, structure, or policies change.
- Remove stale commands after toolchain migrations.
- Keep sibling instruction formats in sync when the same policy applies to all agents.

<details><summary>Corpus exemplars (anonymized, for style only)</summary>

**Exemplar 1** (`microsoft_Web-Dev-For-Beginners` / `AGENTS.md` / heading: Repository Maintenance)

- Active community of learners and contributors
- Regular updates to dependencies and content
- Issues and discussions monitored by maintainers
- Translation updates automated via GitHub Actions

**Exemplar 2** (`nvm-sh_nvm` / `AGENTS.md` / heading: Path Management)

- `nvm_change_path()` - Updates PATH for version switching
- `nvm_strip_path()` - Removes nvm paths from PATH
- `nvm_version_path()` - Gets installation path for version
- `nvm_version_dir()` - Gets version directory name
- `nvm_prepend_path()` - Safely prepends to PATH

</details>
