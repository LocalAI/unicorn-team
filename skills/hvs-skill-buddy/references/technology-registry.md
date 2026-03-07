# HVS Technology Registry

This file defines **technology ownership** across the HVS skill library.
When creating a new skill, check this registry first. If the technology you
need is already owned by another skill, **reference that skill** — do not
re-implement install logic or usage patterns.

---

## Registry

### Browser / UI Automation

| Technology | Owning Skill | Canonical Install | Notes |
|------------|-------------|-------------------|-------|
| Playwright (Python) | `hvs-e2e-testing` | `pip install playwright pytest-playwright --break-system-packages` | Use exactly this form |
| Playwright (browsers) | `hvs-e2e-testing` | `playwright install --with-deps chromium` | Chromium only unless user specifies otherwise |
| @playwright/cli | `hvs-exploratory-testing` | `npm install -g @playwright/cli@latest` | Optional install; use `2>/dev/null \|\| true` |
| Maestro | `hvs-android-e2e-testing` | `curl -Ls "https://get.maestro.mobile.dev" \| bash` | Mobile only |
| Espresso / UI Automator | `hvs-android-e2e-testing` | via Android SDK | Mobile only |

**Cross-skill protocol:** `hvs-user-journey-skill` discovers journeys; `hvs-e2e-testing` executes them. 
`hvs-exploratory-testing` runs without pre-defined journeys. Skills may call each other in sequence 
but must not duplicate installation logic.

---

### Containers / Images

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| Docker build / Dockerfile | `docker-build-expert` | ALL container image builds go through this skill |
| Docker Hardened Images (DHI) | `docker-build-expert` | Base image selection lives here |
| Multi-stage builds | `docker-build-expert` | Patterns in `references/dockerfile-patterns.md` |
| Container scanning (Trivy, Grype) | `docker-build-expert` | Security scan scripts in `scripts/` |

---

### Kubernetes / Helm

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| Helm (database charts) | `containerized-database` | Pinned chart versions in `references/pinned-versions.md` |
| PostgreSQL on k8s | `containerized-database` | |
| Redis on k8s | `containerized-database` | |
| MongoDB on k8s | `containerized-database` | |
| MySQL / MariaDB on k8s | `containerized-database` | |
| OpenSearch on k8s | `containerized-database` | |
| Raw `kubectl` / k8s manifests | None (ad-hoc) | Reference hvs-context cluster conventions |

---

### CI/CD

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| GitHub Actions workflows | `github-actions-expert` | ALL `.github/workflows/*.yml` generation |
| GHA security hardening | `github-actions-expert` | SHA pinning, OIDC, supply chain |
| GHA reusable workflows | `github-actions-expert` | |
| GHA caching / optimization | `github-actions-expert` | |

---

### Infrastructure as Code

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| Azure Bicep | `azure-bicep-expert` | Includes AVM modules, bicepconfig |
| ARM Templates | `azure-bicep-expert` | Converts to Bicep |
| Terraform | None (ad-hoc) | Future skill candidate |

---

### Mobile

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| React Native / Expo | `mobile-app-builder` | Cross-platform iOS + Android |
| Flutter | `mobile-app-builder` | |
| Android Emulator / ADB | `hvs-android-e2e-testing` | Testing only |
| EAS CLI | `mobile-app-builder` | `npm install -g eas-cli` |

---

### Machine Learning

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| PyTorch / TensorFlow / JAX | `ml-engineering` | |
| scikit-learn / XGBoost / LightGBM | `ml-engineering` | |
| Hugging Face / PEFT / LoRA | `ml-engineering` | |
| MLflow | `ml-engineering` | |
| Decision memory journal | `ml-engineering` | `.ml_decisions.json` per project |

---

### AI / Agent Frameworks

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| Google ADK | `agent-development` | |
| LangGraph / CrewAI / AutoGen | `agent-development` | |
| OpenAI Agents SDK | `agent-development` | |
| FastMCP / MCP servers | `agent-development` | |
| Gemini image generation (Nano Banana) | `nano-banana-prompt` | JSON prompt structure only |

---

### Static Sites / Documentation

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| GitHub Pages / Jekyll | `github-pages-designer` | SEO, performance, custom themes |
| Jekyll themes / Liquid | `github-pages-designer` | |

---

### Business / Process

| Technology | Owning Skill | Notes |
|------------|-------------|-------|
| SOW analysis / bid scoring | `sow-bidding` | HVS-specific pricing model |
| Root cause analysis (5 Whys, FTA) | `root-cause-debugger` | |
| Prompt standardization | `prompt-refactor` | Batch or single prompt cleanup |
| AJ Geddes writing voice | `aj-writing-style` | All content written "as AJ" |

---

## Technology Gaps (No Owning Skill Yet)

These technologies are used in HVS work but have no owning skill. They're candidates
for future skills — do not add ad-hoc patterns to existing skills as a workaround:

| Technology | Notes |
|------------|-------|
| Terraform | Used in hvs-context cluster setup; skill not yet built |
| n8n / workflow automation | Mentioned in clawdbot design; no skill yet |
| Ollama / LiteLLM (local AI) | clawdbot stack; no skill yet |
| Open WebUI | No dedicated skill |
| Kubernetes cluster ops (non-DB) | General k8s ops beyond databases |

---

## Conflict Resolution

If two skills both claim a technology, or you're unsure who should own it:

1. Check which skill has the deeper, more complete implementation
2. Prefer the skill whose **primary purpose** is that technology
3. If genuinely ambiguous, raise it in an audit report as a `BOUNDARY_CONFLICT`
4. The user decides ownership; update this registry accordingly
