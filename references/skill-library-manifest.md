# Skill Library Manifest

> **Living index of skills available for assignment to swarm agents.**  
> Consult this manifest during **Phase 3 (Skill Discovery)** of the orchestration pipeline. It maps subtask requirements to skill files, specifies how to load and pass each skill, and defines the priority rules for skill selection and conflict resolution.

---

## Table of Contents

1. [How to Use This Manifest](#1-how-to-use-this-manifest)
2. [Built-in Skills](#2-built-in-skills)
3. [User Skills](#3-user-skills)
4. [Security](#4-security)
5. [System Design](#5-system-design)
6. [Documentation & Context](#6-documentation--context)
7. [Tools & Automation](#7-tools--automation)
8. [External Skills](#8-external-skills)
9. [Skill Assignment Matrix](#9-skill-assignment-matrix)
10. [Skill Loading Patterns](#10-skill-loading-patterns)
11. [Custom Skill Integration](#11-custom-skill-integration)
12. [Skill Conflict Resolution](#12-skill-conflict-resolution)
13. [Skill Versioning Notes](#13-skill-versioning-notes)

---

## 1. How to Use This Manifest

Follow this procedure during Phase 3 of the orchestration pipeline:

1. **Read this manifest** to understand available capabilities and their trigger conditions.
2. **Match subtask requirements** to skill trigger conditions using the [Assignment Matrix](#9-skill-assignment-matrix).
3. **Load the matched skill file** from its path (built-in or user-provided).
4. **Pass skill instructions to sub-agents** via task prompts using one of the [Loading Patterns](#10-skill-loading-patterns).
5. **For short skills**: inline the content directly in the task prompt.
6. **For long skills**: pass the file path and instruct the agent to read it first.

Skills are loaded **progressively** -- only assign a skill when the stage that requires it begins. Do not preload all skills at swarm startup.

### Skill Categories at a Glance

| Category | Section | Loading Model |
|----------|---------|---------------|
| Built-in Skills | [Section 2](#2-built-in-skills) | By-reference from `/app/.agents/skills/` |
| User Skills | [Section 3](#3-user-skills) | By-reference from `/app/.user/skills/` |
| Security | [Section 4](#4-security) | Bundled references (merged into `references/security-comprehensive.md`) |
| System Design | [Section 5](#5-system-design) | Bundled reference (`references/system-design-patterns.md`) |
| Documentation & Context | [Section 6](#6-documentation--context) | Bundled references |
| Tools & Automation | [Section 7](#7-tools--automation) | Scripts integrated into `scripts/` |
| External Skills | [Section 8](#8-external-skills) | Read directly from archive paths (not bundled) |

---

## 2. Built-in Skills

All built-in skills are located at `/app/.agents/skills/`. Each skill has a `SKILL.md` file that defines its workflow, constraints, and trigger conditions.

| Skill Name | Path | Trigger Condition | When to Assign |
|------------|------|-------------------|----------------|
| `deep-research-swarm` | `/app/.agents/skills/deep-research-swarm/SKILL.md` | Multi-agent deep research orchestration. Assign when the task requires comprehensive, multi-dimensional, evidence-backed investigation -- competitive intelligence, market analysis, controversy investigation, policy evaluation, academic landscape review, risk assessment, or file-based analysis. Routes: A (wide search), B (focused search), C (file-only), D (file-augmented). | Assign to the research agent (or orchestrator itself) when any research phase is identified. Covers Routes A-D based on user signals. |
| `report-writing` | `/app/.agents/skills/report-writing/SKILL.md` | End-to-end long-form report creation -- outline design, multi-chapter content writing, review, and assembly. Covers industry research, market analysis, policy briefs, technical reports, consulting deliverables. Output: Markdown (`.md`). **Do NOT use for** academic papers (use `paper-writing`), creative fiction, blog posts, or short-form content under 2000 words. | Assign to the writing agent after research is complete. Use the `docx` skill for `.docx` delivery if needed. |
| `paper-writing` | `/app/.agents/skills/paper-writing/SKILL.md` | End-to-end academic paper creation -- outline design, structured content writing, review, and assembly. Covers survey papers, empirical research, technical papers, case studies, literature reviews. Output: Markdown (`.md`). **Do NOT use for** industry reports, consulting deliverables, or policy briefs (use `report-writing`). | Assign to the writing agent for academic outputs. Requires methodology sections, contribution positioning, and rigorous citation. |
| `vibecoding-webapp-swarm` | `/app/.agents/skills/vibecoding-webapp-swarm/SKILL.md` | Build any web-based project: websites, landing pages, web apps, dashboards, browser games, portfolios, and interactive experiences. Design-first React workflow (Node.js 20, Tailwind CSS v3.4.19, Vite v7.2.4, React 19 + TypeScript, shadcn/ui). **Skip** if the user explicitly requests a non-React framework or the task is unrelated to web UI. | Assign to the coding agent for web UI projects. Includes companion files: `design-guide.md`, `react-dev.md`. |
| `vibecoding-general-swarm` | `/app/.agents/skills/vibecoding-general-swarm/SKILL.md` | General-purpose coding orchestration. **Mandatory** for ANY coding task not covered by `vibecoding-webapp-swarm`. Covers Python tools, data pipelines, ML systems, APIs, games, bots, CLI apps, mobile apps. Spec-first workflow with multi-agent (Mode A) and single-agent (Mode B) variants. | Assign to the coding agent for all non-web coding tasks. Mode A for 3+ modules; Mode B for single scripts. |
| `pptx-swarm` | `/app/.agents/skills/pptx-swarm/SKILL.md` | Exclusive skill for all PowerPoint/presentation tasks -- creating, generating, editing, modifying, redesigning, typesetting, beautifying, or converting presentations. Uses `.pptd` domain-specific language. **Strictly prohibited** from using python-pptx, OpenXML SDK, or any other libraries. Main agent must complete visual design, outline, and `.pptd` file construction before delegating. | Assign to the presentation agent. Requires main agent to design before subagents produce `.page` files. |
| `batch-download` | `/app/.agents/skills/batch-download/SKILL.md` | Multi-agent batch download and data collection. Assign when the task requires discovering, validating, and downloading multiple files or datasets -- batch report downloads, multi-source data collection, structured web scraping, file archival. **Do NOT use for** single file download, simple API calls, or tasks without web discovery. | Assign to a download/orchestration agent for multi-file retrieval tasks. Types A (targets unknown) and B (targets known). |
| `docx` | `/app/.agents/skills/docx/SKILL.md` | Create and edit Word documents (.docx) using C# + OpenXML SDK. Covers document creation, editing, comments, revisions, footnotes, TOC, and Markdown-to-Word conversion. Three routes: WIR (edit existing), md2docx (convert subagent output), Create (build from scratch). | Assign to a document agent when `.docx` output is required. Can also convert subagent `.md` output to Word. |
| `pdf` | `/app/.agents/skills/pdf/SKILL.md` | Professional PDF creation and processing. Three routes: HTML (default, for creation), LaTeX (user-explicitly requests .tex), Process (work with existing PDFs -- extract, merge, fill forms). Supports KaTeX math, Mermaid diagrams, three-line tables, citations. | Assign to the output agent for PDF creation or manipulation. Read the appropriate route file before implementation. |
| `xlsx` | `/app/.agents/skills/xlsx/SKILL.md` | Advanced spreadsheet creation, analysis, and manipulation. Core: formula deployment, complex formatting, data visualization, finance-focused modeling (three-statement models, DCF, public comps). Includes CLI tool for validation, recheck, pivot, inspect. | Assign to the data/finance agent when `.xlsx` output, financial modeling, or complex spreadsheet work is required. |
| `skill-creator-swarm` | `/app/.agents/skills/skill-creator-swarm/SKILL.md` | Guide for creating effective skills. Use when users want to create a new skill, update an existing skill, or refine a skill through swarm-style evaluation with subagents, baseline comparisons, grading, and analysis. | Assign when the swarm's output is itself a skill definition, or when the user requests skill creation/refinement. |

### Skill Size and Loading Strategy

| Skill | Est. Size | Loading Pattern | Notes |
|-------|-----------|-----------------|-------|
| `deep-research-swarm` | Medium | By-reference | Routes are self-selected; read SKILL.md before research phase. |
| `report-writing` | Medium | By-reference | Multi-stage (outline -> content -> review -> assembly). |
| `paper-writing` | Medium | By-reference | Academic-specific stages; includes citation management. |
| `vibecoding-webapp-swarm` | Large | By-reference | Has companion files (`design-guide.md`, `react-dev.md`) that subagents read independently. |
| `vibecoding-general-swarm` | Medium | By-reference | Modes A/B selected based on module count. |
| `pptx-swarm` | Large | By-reference | Main agent does design; subagents only produce `.page` files after `.pptd` is ready. |
| `batch-download` | Medium | By-reference | Plan-first; parallel download phase. |
| `docx` | Medium | By-reference | Route selection (WIR/md2docx/Create) determines execution path. |
| `pdf` | Medium | By-reference | Must read route file (`routes/html.md`, `routes/latex.md`, `routes/process.md`) before implementation. |
| `xlsx` | Medium | By-reference | Has sub-skills in `reference/` for financial modeling. |
| `skill-creator-swarm` | Medium | By-reference | Multi-agent evaluation workflow with subagents. |

---

## 3. User Skills

User-provided skills extend or override built-in capabilities.

### Discovery Path

User skills live at:
```
/app/.user/skills/{skill_name}/SKILL.md
```

### Discovery Procedure

1. List the directory: `ls /app/.user/skills/`
2. For each skill found, read `SKILL.md` frontmatter to extract:
   - `name` -- skill identifier
   - `description` -- trigger conditions and scope
   - `type` -- `capability` or `workflow`
3. Index the skill in your working manifest for the current swarm run.

### Assignment Priority

```
User skill > Built-in skill (same capability)
```

If a user skill has the same capability name as a built-in skill (e.g., a user-provided `report-writing` skill), **always prefer the user skill**. The user's version represents their explicit intent to customize or override the default behavior.

### Override Rules

| Scenario | Action |
|----------|--------|
| User skill has same `name` as built-in | Use user skill; ignore built-in |
| User skill has different `name` but overlapping description | Prefer user skill if description match score is higher |
| Multiple user skills match same subtask | Prefer the one with more specific trigger conditions |
| User skill references a built-in skill as a base | Load user skill; it will internally reference the built-in |

---

## 4. Security

> **Loading model:** Bundled references -- content from multiple security skills has been merged into unified reference files within the swarm-orchestrator's `references/` directory. Agents load these by reference like built-in skills.

Security skills provide comprehensive audit checklists, best practices, and threat modeling guidance. They are triggered whenever code involves authentication, payments, databases, API keys, or user data handling.

| Skill Name | Source | Original Path | Trigger Condition | Bundled Form | Notes |
|------------|--------|---------------|-------------------|--------------|-------|
| `vibe-security` | raroque archive | `/mnt/agents/output/Archive_contents/raroque_vibe-security-skill/vibe-security/` | Any code generation involving auth, payments, database, API keys, or user data | `references/security-comprehensive.md` | Comprehensive security audit with 9 topic areas |
| `security-best-practices` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/security-best-practices/` | Language/framework-specific security reviews | `references/security-comprehensive.md` | Merged with `vibe-security` into unified reference |
| `security-threat-model` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/security-threat-model/` | When designing systems that need threat analysis | `references/security-comprehensive.md` | STRIDE, attack trees, threat categorization |

### Security Skill Loading

```
Read references/security-comprehensive.md before implementing any code involving:
- Authentication or authorization
- Payment processing
- Database access or storage
- API keys or secrets management
- User data collection or handling
```

---

## 5. System Design

> **Loading model:** Bundled reference -- content integrated into a unified reference file in `references/`.

System design skills guide architectural decisions, domain decomposition, and API contract design before implementation begins.

| Skill Name | Source | Original Path | Trigger Condition | Bundled Form | Notes |
|------------|--------|---------------|-------------------|--------------|-------|
| `domain-decomposition-api-design-advisor` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/domain-decomposition-api-design-advisor/` | Before implementing large features or services | `references/system-design-patterns.md` | Domain decomposition, bounded contexts, API contracts |

### System Design Skill Loading

```
Read references/system-design-patterns.md before implementing large features or services.
Covers: bounded contexts, service boundaries, API contract design, data ownership.
```

---

## 6. Documentation & Context

> **Loading model:** Bundled references -- integrated into `references/` directory.

These skills guide documentation production and codebase context ingestion when starting work on existing projects.

| Skill Name | Source | Original Path | Trigger Condition | Bundled Form | Notes |
|------------|--------|---------------|-------------------|--------------|-------|
| `doc-coauthoring` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/doc-coauthoring/` | When producing documentation as a swarm output | `references/documentation-workflow.md` | Collaborative documentation patterns |
| `project-context-ingestion` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/project-context-ingestion/` | When starting work on an existing codebase | `references/project-context-ingestion.md` | Codebase analysis and context extraction |

---

## 7. Tools & Automation

> **Loading model:** Scripts integrated -- automation scripts have been copied into the swarm-orchestrator's `scripts/` directory and are invoked as tools rather than read as skills.

These skills provide browser automation and visual verification capabilities used during testing and validation phases.

| Skill Name | Source | Original Path | Trigger Condition | Integrated Form | Notes |
|------------|--------|---------------|-------------------|-----------------|-------|
| `screenshot` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/screenshot/` | When visual verification of output is needed | `swarm-orchestrator/scripts/` | Capture and compare screenshots of rendered output |
| `playwright` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/playwright/` | Browser automation for testing web outputs | `swarm-orchestrator/scripts/` | End-to-end browser automation for web app validation |

### Tools & Automation Usage

These are invoked as shell commands/scripts rather than loaded into agent context:

```bash
# Screenshot verification
./scripts/screenshot-capture.sh [url] [output_path]

# Playwright browser automation
./scripts/playwright-test.sh [test_file]
```

Assign these tools during the **verification phase** of web projects, not during initial development.

---

## 8. External Skills

> **Loading model:** Referenced, not bundled. Agents read these skills directly from their archive paths when needed. They are **not** copied into the swarm-orchestrator directory.

External skills cover platform-specific deployment, database optimization, and specialized workflows. They are loaded by-reference from their original archive locations.

| Skill Name | Source | Path | Trigger Condition | Notes |
|------------|--------|------|-------------------|-------|
| `cloudflare-deploy` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/cloudflare-deploy/` | Deployment to Cloudflare Workers/Pages/R2 | Covers Wrangler CLI, edge functions, KV storage, R2 bindings |
| `netlify-deploy` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/netlify-deploy/` | Deployment to Netlify | Covers CLI deploy, edge functions, build configuration |
| `vercel-deploy` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/vercel-deploy/` | Deployment to Vercel | Covers CLI, serverless functions, edge config |
| `postgres-best-practices` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/postgres-best-practices/` | Database design and optimization with Postgres | Schema design, indexing, query optimization, migrations |
| `jupyter-notebook` | JetBrains archive | `/mnt/agents/output/Archive_contents/JetBrains Skill-repo/jupyter-notebook/` | Creating, editing, or analyzing Jupyter notebooks | Cell management, data visualization, kernel handling |

### External Skill Loading Pattern

```
Read the external skill from its archive path before use:

Read /mnt/agents/output/Archive_contents/JetBrains Skill-repo/{skill_name}/SKILL.md,
then execute the deployment task.
```

External skills are loaded on-demand per deployment task. They are **not** pre-loaded at swarm startup.

---

## 9. Skill Assignment Matrix

This matrix maps common subtask types to recommended skills. Use it as the primary lookup during Phase 3.

| Subtask Type | Primary Skill | Secondary Skill | Notes |
|--------------|--------------|-----------------|-------|
| Research / information gathering | `deep-research-swarm` | -- | Route auto-selected by skill: A (wide), B (focused), C (file-only), D (file-augmented). |
| Report writing (industry, market, policy, technical) | `report-writing` | `deep-research-swarm` (prerequisite) | Report-writing expects research artifacts at `/mnt/agents/output/research/` or triggers pre-stage research. |
| Academic paper writing | `paper-writing` | `deep-research-swarm` (prerequisite) | Includes methodology, citations, literature review. Never use `report-writing` for academic outputs. |
| Web app / website building | `vibecoding-webapp-swarm` | -- | React-first. Use `vibecoding-general-swarm` only if user explicitly requests non-React. |
| General coding (Python, CLI, data pipelines, ML, APIs) | `vibecoding-general-swarm` | -- | Mode A (multi-agent) for 3+ modules; Mode B (single agent) for focused tasks. |
| Presentation / slides creation | `pptx-swarm` | -- | Main agent must design before subagents produce content. Uses `.pptd`/`.page` format. |
| Document -- Word (.docx) | `docx` | `report-writing` (content source) | Route: WIR (edit existing), md2docx (convert .md), or Create (from scratch). |
| Document -- PDF | `pdf` | `report-writing` (content source) | Default: HTML route. Use LaTeX route only on explicit request. |
| Document -- PowerPoint | `pptx-swarm` | -- | See "Presentation / slides creation" row above. |
| Spreadsheet / Excel (.xlsx) | `xlsx` | -- | Includes financial modeling sub-skills. Must deliver `.xlsx` file. |
| Batch file operations / multi-download | `batch-download` | -- | Type A (targets unknown) or Type B (targets provided). |
| Creating a new skill | `skill-creator-swarm` | -- | Multi-agent evaluation with subagents for testing and grading. |
| Converting Markdown to Word | `docx` | -- | Use md2docx route when subagents produce `.md` output. |
| Editing existing Word document | `docx` | -- | Use WIR route; preserves formatting and style. |
| Processing existing PDFs | `pdf` | -- | Use Process route (extract, merge, fill forms, etc.). |
| Financial modeling in Excel | `xlsx` | -- | Use sub-skills: `reference/3_statement_model_skill.md`, `reference/DCF_SKILL.md`, `reference/comps-analysis/Comps_analysis SKILL.md`. |
| **Security audit / auth & data handling** | `security-comprehensive` ([Section 4](#4-security)) | -- | Load from `references/security-comprehensive.md`. Covers auth, payments, DB, API keys, user data. |
| **Threat modeling** | `security-threat-model` ([Section 4](#4-security)) | -- | Integrated into `references/security-comprehensive.md`. Use for system threat analysis. |
| **Domain decomposition / API design** | `domain-decomposition-api-design-advisor` ([Section 5](#5-system-design)) | -- | Load from `references/system-design-patterns.md`. Use before large feature implementation. |
| **Documentation production** | `doc-coauthoring` ([Section 6](#6-documentation--context)) | -- | Load from `references/documentation-workflow.md`. |
| **Existing codebase onboarding** | `project-context-ingestion` ([Section 6](#6-documentation--context)) | -- | Load from `references/project-context-ingestion.md`. |
| **Visual verification / screenshots** | `screenshot` ([Section 7](#7-tools--automation)) | -- | Invoke script from `scripts/`. Use during validation phase. |
| **Browser automation / E2E testing** | `playwright` ([Section 7](#7-tools--automation)) | -- | Invoke script from `scripts/`. Use for web app validation. |
| **Deploy to Cloudflare** | `cloudflare-deploy` ([Section 8](#8-external-skills)) | -- | Read from archive path. Use Wrangler CLI workflow. |
| **Deploy to Netlify** | `netlify-deploy` ([Section 8](#8-external-skills)) | -- | Read from archive path. Use Netlify CLI workflow. |
| **Deploy to Vercel** | `vercel-deploy` ([Section 8](#8-external-skills)) | -- | Read from archive path. Use Vercel CLI workflow. |
| **Postgres design / optimization** | `postgres-best-practices` ([Section 8](#8-external-skills)) | -- | Read from archive path. Schema, indexing, migrations. |
| **Jupyter notebook work** | `jupyter-notebook` ([Section 8](#8-external-skills)) | -- | Read from archive path. Creation, editing, analysis. |

### Multi-Skill Chains

Some tasks require sequential skill application:

| Task | Skill Chain | Notes |
|------|-------------|-------|
| Research + Report | `deep-research-swarm` -> `report-writing` | Research artifacts feed into report pre-stage. |
| Research + Academic Paper | `deep-research-swarm` -> `paper-writing` | Research feeds into paper pre-stage; paper skill handles academic formatting. |
| Research + Report + Word | `deep-research-swarm` -> `report-writing` -> `docx` | Final `.docx` delivery via md2docx route. |
| Research + Report + PDF | `deep-research-swarm` -> `report-writing` -> `pdf` | Final PDF delivery via HTML route. |
| Web app (design + build) | `vibecoding-webapp-swarm` (orchestrator) -> subagents with `design-guide.md` + `react-dev.md` | Main skill orchestrates; companion files guide subagents. |
| Skill creation + evaluation | `skill-creator-swarm` -> subagents for baseline comparison + grading | Swarm evaluates the created skill against baselines. |
| **Secure web app development** | `vibecoding-webapp-swarm` -> `security-comprehensive` | Apply security audit during/after development. Load from `references/security-comprehensive.md`. |
| **System design + build** | `domain-decomposition-api-design-advisor` -> `vibecoding-general-swarm` | Design architecture before implementation. |
| **Documentation + deployment** | `doc-coauthoring` -> `cloudflare-deploy`/`netlify-deploy`/`vercel-deploy` | Produce docs, then deploy to target platform. |
| **Web app + visual validation** | `vibecoding-webapp-swarm` -> `screenshot` + `playwright` | Build, then validate with screenshots and browser automation. |

---

## 10. Skill Loading Patterns

Use the appropriate pattern based on skill size, category, and whether customization is needed.

### a) Inline Loading (Short Skills Under ~100 Lines)

Paste the skill content directly into the task prompt:

```
Read this skill, then execute:

[paste full skill content here]

Task: [specific task description]
```

Use sparingly -- only when the skill is short and the agent has sufficient context budget.

### b) By-Reference Loading (Long Skills -- Default)

Pass the file path and instruct the agent to read it first:

```
First read /app/.agents/skills/{skill}/SKILL.md, then execute the following task:

Task: [specific task description]
```

This is the **preferred pattern** for all built-in skills. It avoids context bloat and ensures the agent reads the latest version.

### c) Bundled Reference Loading (Security, System Design, Documentation Skills)

For skills merged into unified reference files in `references/`:

```
Read references/security-comprehensive.md, then apply its guidelines
to all code involving authentication, payments, or user data.
```

```
Read references/system-design-patterns.md before implementing this service.
Follow its guidance on domain decomposition and API contract design.
```

```
Read references/documentation-workflow.md, then produce documentation
for the completed feature following its patterns.
```

```
Read references/project-context-ingestion.md, then analyze the codebase
at [path] to extract context before implementation.
```

### d) External Skill Loading (Platform-Specific & Referenced Skills)

For skills stored in the archive and read directly (not bundled):

```
Read /mnt/agents/output/Archive_contents/JetBrains Skill-repo/cloudflare-deploy/SKILL.md,
then deploy the application to Cloudflare following its workflow.
```

```
Read /mnt/agents/output/Archive_contents/JetBrains Skill-repo/postgres-best-practices/SKILL.md,
then review the database schema for optimization opportunities.
```

### e) Tool Script Invocation (Automation Skills)

For skills integrated as executable scripts:

```bash
# Visual verification
./scripts/screenshot-capture.sh [url] [output_path]

# Browser automation testing
./scripts/playwright-test.sh [test_file_or_url]
```

These are **invoked**, not read. Use them during the verification phase.

### f) Annotated Loading (Skill Needs Tailoring)

When a skill requires section overrides or additional constraints:

```
Read this skill: /app/.agents/skills/{skill}/SKILL.md

Apply the following overrides:
- Section [X]: Change output format to [specific format]
- Section [Y]: Use [specific library/tool] instead of the default
- Add constraint: [additional requirement not in the skill]

Task: [specific task description]
```

Document any overrides in `plan.md` so the swarm maintains a clear audit trail.

### g) Multi-File Loading (Skill with Companion Files)

Some skills have companion reference files that subagents must read:

```
Read these files in order:
1. /app/.agents/skills/vibecoding-webapp-swarm/SKILL.md
2. /app/.agents/skills/vibecoding-webapp-swarm/design-guide.md
3. /app/.agents/skills/vibecoding-webapp-swarm/react-dev.md

Then execute:
Task: [specific task description]
```

| Skill | Companion Files | Who Reads |
|-------|----------------|-----------|
| `vibecoding-webapp-swarm` | `design-guide.md`, `react-dev.md` | Designer reads #2; implementation agents read #3 |
| `pptx-swarm` | `format/pptd.md` | Main agent reads for .pptd format spec |
| `xlsx` | `reference/*.md` | Financial modeling agents read sub-skills |
| `pdf` | `routes/html.md`, `routes/latex.md`, `routes/process.md` | Route-dependent; read the matched route file |

---

## 11. Custom Skill Integration

Handle skills not present in this manifest using the following rules:

### If the User References a Skill by Name

1. Search built-in path: `/app/.agents/skills/{skill_name}/SKILL.md`
2. Search user path: `/app/.user/skills/{skill_name}/SKILL.md`
3. Search bundled references: `references/{skill_name}.md`
4. Search archive path: `/mnt/agents/output/Archive_contents/*/{skill_name}/SKILL.md`
5. If found in any location, add to the manifest for future reference and proceed with assignment.
6. If **not found**, proceed **without the skill** -- do not fail the swarm for a missing skill. Fall back to general orchestration principles.

### If the User Provides a Skill File (`.skill`)

1. Extract the skill content from the provided file.
2. Save to a working directory (e.g., `/mnt/agents/output/skills/{skill_name}/`).
3. Read the SKILL.md to understand trigger conditions and workflow.
4. Add to the manifest for the current swarm run.
5. Assign to subagents as a user skill with highest priority.

### Discovery Flow

```
User references skill "X"
  |
  +- Found at /app/.agents/skills/X/SKILL.md
  |   -> Load as built-in skill
  |
  +- Found at /app/.user/skills/X/SKILL.md
  |   -> Load as user skill (highest priority)
  |
  +- Found at references/{X}.md (bundled reference)
  |   -> Load as bundled skill (Section 4-6 category)
  |
  +- Found at /mnt/agents/output/Archive_contents/*/{skill_name}/SKILL.md
  |   -> Load as external skill (Section 8 category)
  |
  +- Not found in any location
      -> Proceed without skill; use general orchestration
      -> Log warning in plan.md
```

---

## 12. Skill Conflict Resolution

When multiple skills match a single subtask, resolve using this priority order:

### Resolution Hierarchy

1. **More specific skill > General skill**
   - `paper-writing` beats `report-writing` for academic papers
   - `vibecoding-webapp-swarm` beats `vibecoding-general-swarm` for web UI
   - `xlsx` (with financial sub-skills) beats general data processing for financial modeling
   - `security-comprehensive` beats general coding guidelines for auth/data tasks
   - `domain-decomposition-api-design-advisor` beats general coding for large feature design

2. **User skill > Built-in skill > Bundled skill > External skill**
   - A user-provided `report-writing` overrides the built-in one
   - A bundled security reference overrides external security guidance
   - User skills represent explicit intent -- honor it

3. **More specific description match > Broader description match**
   - When comparing two user skills, prefer the one whose trigger conditions more precisely match the subtask
   - Example: a skill described for "industry market analysis reports" beats one described for "general writing" for a market analysis subtask

### Resolution Procedure

```
Multiple skills match subtask "S"
  |
  +- Is one a user skill?
  |   -> Prefer user skill
  |
  +- Is one more specific to the subtask type?
  |   -> Prefer the more specific skill
  |
  +- Is one bundled vs external for the same capability?
  |   -> Prefer bundled (it's curated into the orchestrator)
  |
  +- Are both user skills?
  |   -> Prefer the one with more specific trigger/description match
  |
  +- Still ambiguous?
      -> Document the conflict and resolution in plan.md
      -> Choose the skill with narrower scope
      -> Monitor output quality; switch if needed
```

### Conflict Logging

Always document skill conflicts and resolutions in `plan.md`:

```markdown
## Skill Assignment
- Subtask: [description]
- Matched skills: [skill A], [skill B]
- Conflict resolution: Chose [skill A] because [reason]
- Override applied: [none / specific override]
```

---

## 13. Skill Versioning Notes

Follow these practices to ensure skill reliability across swarm runs:

### Always Reference by Path

- **Read skills from their file paths every time.** Never embed skill content in agent prompts as a cached string.
- Skill content may change between swarm runs. Path references guarantee the agent reads the current version.

### Verify Before Dispatch

- Before assigning a skill, verify the `SKILL.md` or reference file is readable at the expected path.
- If a skill fails, check:
  1. File exists at the path
  2. File is readable (not corrupted or empty)
  3. File is the current version (check for recent modifications)

### No Hardcoded Content

- Do not hardcode skill instructions, constraints, or workflows in agent prompts.
- Exception: brief inline references (e.g., "Follow the report-writing skill at `/app/.agents/skills/report-writing/SKILL.md`") are acceptable.
- Full skill content should always be read from the skill file, not duplicated in the prompt.

### Version Resilience

| Practice | Rationale |
|----------|-----------|
| Read from path every dispatch | Ensures latest version is always used |
| Verify file exists before referencing | Prevents silent failures from missing skills |
| Log skill versions in plan.md | Enables debugging if behavior changes between runs |
| Do not cache skill content in working memory | Prevents stale skill usage across long swarm runs |
| Check for companion files | Some skills have updated companion references that must also be read |

### Fallback Behavior

If a skill file is unreadable or missing at dispatch time:

1. Log the failure in `plan.md`
2. Attempt to locate the skill in the alternate path (built-in -> user, or user -> built-in)
3. For bundled skills, check if the source archive skill is still available
4. For external skills, attempt the other archive locations
5. If no path has the skill, proceed with general orchestration principles
6. Do not retry indefinitely -- one fallback attempt per category, then proceed without the skill
