# 10X Developer Unicorn

> An agent orchestration system that encodes the "hidden 80%" of software engineering expertise into Claude Code.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-62%20passed-brightgreen.svg)]()
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet.svg)](https://claude.ai)

## What is This?

Most AI coding assistants focus on the visible 20%—writing code, answering syntax questions, generating boilerplate. But real 10X developers spend 80% of their time on skills that are rarely taught:

- **Reading code** strategically (not linearly)
- **Recognizing patterns** across languages and domains
- **Estimating accurately** with risk awareness
- **Self-reviewing** before anyone else sees the code
- **Managing technical debt** deliberately

This system encodes those skills into a coordinated team of specialized agents.

## Architecture

```mermaid
flowchart TB
    subgraph Orchestrator["🎯 ORCHESTRATOR"]
        direction TB
        O[Task Analysis<br/>& Routing]
    end

    subgraph Agents["SPECIALIZED AGENTS"]
        direction LR
        A[🏗️ Architect<br/><i>Design & ADRs</i>]
        D[💻 Developer<br/><i>TDD Implementation</i>]
        Q[🔒 QA-Security<br/><i>Review & Threats</i>]
        V[🚀 DevOps<br/><i>CI/CD & Infra</i>]
        P[🌐 Polyglot<br/><i>Language Learning</i>]
    end

    subgraph Skills["SKILLS MATRIX"]
        direction TB
        S1[Meta Skills]
        S2[Domain Skills]
    end

    O --> A
    O --> D
    O --> Q
    O --> V
    O --> P

    A -.-> S1
    D -.-> S1
    D -.-> S2
    Q -.-> S2
    V -.-> S2
    P -.-> S1
```

### The 5+1 Agent Model

| Agent | Role | Model | Specialty |
|-------|------|-------|-----------|
| **Orchestrator** | Coordination | Fast | Routes tasks, manages context, enforces quality gates |
| **Architect** | Design | Opus | System design, ADRs, API contracts, tradeoff analysis |
| **Developer** | Implementation | Opus | TDD-first coding in Python, JS/TS, Go, Rust |
| **QA-Security** | Quality | Sonnet | Code review, STRIDE threat modeling, security scans |
| **DevOps** | Operations | Sonnet | CI/CD, Docker, Kubernetes, observability |
| **Polyglot** | Learning | Opus | Rapid language acquisition, pattern transfer |

## Workflow

```mermaid
flowchart LR
    subgraph Input
        T[Task]
    end

    subgraph Analysis
        C{Complexity?}
    end

    subgraph Routing
        S[Simple]
        M[Medium]
        H[Complex]
    end

    subgraph Execution
        D1[Direct<br/>Answer]
        D2[Single<br/>Agent]
        D3[Multi-Agent<br/>Parallel]
    end

    subgraph Quality
        QG[Quality<br/>Gates]
    end

    subgraph Output
        R[Result]
    end

    T --> C
    C -->|Low| S
    C -->|Medium| M
    C -->|High| H

    S --> D1
    M --> D2
    H --> D3

    D1 --> QG
    D2 --> QG
    D3 --> QG

    QG --> R
```

## TDD Workflow

Every implementation follows strict Test-Driven Development:

```mermaid
flowchart LR
    subgraph RED["🔴 RED"]
        R1[Write<br/>Failing Test]
        R2[Test MUST<br/>Fail]
    end

    subgraph GREEN["🟢 GREEN"]
        G1[Write Minimum<br/>Code]
        G2[Test MUST<br/>Pass]
    end

    subgraph REFACTOR["🔵 REFACTOR"]
        F1[Improve<br/>Code]
        F2[Tests Still<br/>Pass]
    end

    subgraph VERIFY["✅ VERIFY"]
        V1[Self-Review]
        V2[Coverage ≥80%]
    end

    R1 --> R2
    R2 --> G1
    G1 --> G2
    G2 --> F1
    F1 --> F2
    F2 --> V1
    V1 --> V2
    V2 -->|Next Feature| R1
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/aj-geddes/unicorn-team.git
cd unicorn-team

# Install the system
./scripts/install.sh

# Verify installation
pytest tests/ -v
```

### Prerequisites

- Python 3.10+
- Git
- One of: pytest, npm, go, cargo (depending on your projects)

## Skills Matrix

```mermaid
flowchart TB
    subgraph root["🦄 10X SKILLS"]
        direction TB
        subgraph meta["META SKILLS"]
            M1[Orchestrator]
            M2[Self-Verification]
            M3[Code Reading]
            M4[Pattern Transfer]
            M5[Estimation]
            M6[Technical Debt]
            M7[Language Learning]
        end
        subgraph domain["DOMAIN SKILLS"]
            D1[Python]
            D2[JavaScript]
            D3[Testing]
            D4[Security]
            D5[DevOps]
        end
        subgraph agents["AGENTS"]
            A1[Architect]
            A2[Developer]
            A3[QA-Security]
            A4[DevOps]
            A5[Polyglot]
        end
    end

    style root fill:#1e1e2e,stroke:#cba6f7,stroke-width:2px,color:#ffffff
    style meta fill:#313244,stroke:#89b4fa,stroke-width:2px,color:#ffffff
    style domain fill:#313244,stroke:#a6e3a1,stroke-width:2px,color:#ffffff
    style agents fill:#313244,stroke:#fab387,stroke-width:2px,color:#ffffff

    style M1 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M2 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M3 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M4 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M5 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M6 fill:#45475a,stroke:#89b4fa,color:#ffffff
    style M7 fill:#45475a,stroke:#89b4fa,color:#ffffff

    style D1 fill:#45475a,stroke:#a6e3a1,color:#ffffff
    style D2 fill:#45475a,stroke:#a6e3a1,color:#ffffff
    style D3 fill:#45475a,stroke:#a6e3a1,color:#ffffff
    style D4 fill:#45475a,stroke:#a6e3a1,color:#ffffff
    style D5 fill:#45475a,stroke:#a6e3a1,color:#ffffff

    style A1 fill:#45475a,stroke:#fab387,color:#ffffff
    style A2 fill:#45475a,stroke:#fab387,color:#ffffff
    style A3 fill:#45475a,stroke:#fab387,color:#ffffff
    style A4 fill:#45475a,stroke:#fab387,color:#ffffff
    style A5 fill:#45475a,stroke:#fab387,color:#ffffff
```

### Meta Skills (The Hidden 80%)

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `orchestrator` | Route tasks to appropriate agents | "implement", "build", "create" |
| `self-verification` | Quality check before every commit | "review", "check", "before commit" |
| `code-reading` | Strategic code comprehension | "understand", "how does this work" |
| `pattern-transfer` | Apply patterns across domains | "I've seen this before", "like X but in Y" |
| `estimation` | Risk-aware time estimation | "how long", "estimate" |
| `technical-debt` | Track and manage debt deliberately | "tech debt", "shortcuts", "cleanup" |
| `language-learning` | Rapid language acquisition | "learn", "new language" |

### Domain Skills

| Skill | Coverage |
|-------|----------|
| `python` | Type hints, pytest, async, tooling (ruff, mypy, poetry) |
| `javascript` | TypeScript, React, Node.js, Jest/Vitest |
| `testing` | TDD, mocking strategies, coverage, cross-language patterns |
| `security` | OWASP Top 10, STRIDE, input validation, secrets management |
| `devops` | Docker, Kubernetes, GitHub Actions, observability |

## Project Structure

```
unicorn-team/
├── skills/
│   ├── unicorn/                    # Meta-skills
│   │   ├── orchestrator/SKILL.md
│   │   ├── self-verification/SKILL.md
│   │   ├── code-reading/SKILL.md
│   │   ├── pattern-transfer/SKILL.md
│   │   ├── estimation/SKILL.md
│   │   ├── technical-debt/SKILL.md
│   │   └── language-learning/
│   │       ├── SKILL.md
│   │       └── references/         # Deep-dive docs
│   ├── agents/                     # Agent definitions
│   │   ├── developer.md
│   │   ├── architect.md
│   │   ├── qa-security.md
│   │   ├── devops.md
│   │   ├── polyglot.md
│   │   └── references/
│   └── domain/                     # Domain expertise
│       ├── python/
│       ├── javascript/
│       ├── testing/
│       ├── security/
│       └── devops/
├── hooks/
│   ├── pre-commit                  # Quality gate before commit
│   └── pre-push                    # Full validation before push
├── scripts/
│   ├── install.sh                  # One-command setup
│   ├── tdd.sh                      # TDD workflow helper
│   ├── self-review.sh              # Pre-commit checklist
│   ├── estimate.sh                 # PERT estimation tool
│   └── new-language.sh             # Language learning protocol
├── tests/
│   ├── test_skills_valid.py        # Skill validation
│   ├── test_scripts.py             # Script validation
│   └── test_hooks.py               # Hook validation
└── docs/
    ├── architecture.md             # Full architecture spec
    ├── hidden-skills.md            # The 80% skills deep-dive
    ├── implementation-guide.md     # Quickstart guide
    └── TROUBLESHOOTING.md          # Common issues & fixes
```

## Scripts Reference

### TDD Workflow
```bash
./scripts/tdd.sh user-authentication
```

Guides you through RED → GREEN → REFACTOR with enforcement:
- Creates test file in correct location
- **Fails if tests pass in RED phase** (non-negotiable)
- Runs coverage report in REFACTOR phase

### Self-Review
```bash
./scripts/self-review.sh
```

Interactive pre-commit checklist:
- Shows staged changes
- Checks for TODOs, debug code, secrets
- Runs tests with coverage
- Asks "Would you approve this PR?"

### Estimation
```bash
./scripts/estimate.sh
```

PERT-based estimation helper:
- Breaks down tasks into subtasks
- Collects optimistic/realistic/pessimistic estimates
- Calculates risk buffers
- Outputs: "X hours (±Y hours) assuming Z. Risks: A, B, C."

### Language Learning
```bash
./scripts/new-language.sh rust
```

5-phase protocol (< 4 hours to productive):
1. **Exploration** (30 min) - Hello World, toolchain
2. **Patterns** (60 min) - Map to known patterns
3. **Ecosystem** (30 min) - Package manager, testing
4. **Idioms** (60 min) - Community conventions
5. **Production** (60 min) - Deployment, monitoring

## Quality Gates

```mermaid
flowchart TB
    subgraph PreCommit["PRE-COMMIT HOOK"]
        PC1[Lint Check]
        PC2[Type Check]
        PC3[Tests + Coverage]
        PC4[Security Scan]
        PC5[No Debug Code]
        PC6[No TODO/FIXME]
    end

    subgraph PrePush["PRE-PUSH HOOK"]
        PP1[Full Test Suite]
        PP2[Coverage ≥ 80%]
        PP3[Clean Working Tree]
        PP4[Commit Format]
        PP5[Security Audit]
        PP6[Build Success]
    end

    PC1 --> PC2 --> PC3 --> PC4 --> PC5 --> PC6
    PC6 -->|Commit| PP1
    PP1 --> PP2 --> PP3 --> PP4 --> PP5 --> PP6
    PP6 -->|Push| Remote[(Remote)]
```

### What Gets Checked

| Check | Pre-Commit | Pre-Push |
|-------|:----------:|:--------:|
| Linting (ruff/eslint) | ✅ | ✅ |
| Type checking (mypy/tsc) | ✅ | ✅ |
| Unit tests | ✅ | ✅ |
| Coverage threshold (80%) | ✅ | ✅ |
| Security scan (bandit/npm audit) | ✅ | ✅ |
| No debug code | ✅ | ✅ |
| No TODO/FIXME/HACK | ✅ | ✅ |
| Full test suite | ❌ | ✅ |
| Commit message format | ❌ | ✅ |
| Clean working tree | ❌ | ✅ |

## The 10X Philosophy

### What Makes a 10X Developer?

It's not typing speed. It's not knowing more languages. It's the **invisible skills**:

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryTextColor': '#ffffff', 'pieStrokeColor': '#ffffff', 'pieOuterStrokeColor': '#ffffff'}}}%%
pie showData
    title Where 10X Developers Spend Their Time
    "Reading Code" : 40
    "Pattern Recognition" : 15
    "Debugging" : 15
    "Self-Review" : 10
    "Writing Code" : 10
    "Communication" : 5
    "Estimation" : 5
```

### The Iceberg Model

```
        ┌─────────────────────────┐
        │    VISIBLE (20%)        │
        │  • Writing code         │
        │  • Using frameworks     │
        │  • Syntax knowledge     │
~~~~~~~~│~~~~~~~~~~~~~~~~~~~~~~~~~│~~~~~~~~ Surface
        │    HIDDEN (80%)         │
        │  • Strategic reading    │
        │  • Pattern transfer     │
        │  • Risk estimation      │
        │  • Self-verification    │
        │  • Debt management      │
        │  • Security mindset     │
        │  • Observability design │
        └─────────────────────────┘
```

This system encodes the 80% that's usually learned through years of experience.

## Contributing

### Development Rules

1. **TDD Always**: RED → GREEN → REFACTOR. No exceptions.
2. **Self-Review**: Run `./scripts/self-review.sh` before every commit.
3. **Quality Gates**: All hooks must pass.
4. **Skill Standards**: SKILL.md files must be < 500 lines (use references/).

### Commit Convention

```
type(scope): description

Types: feat, fix, docs, skill, script, test, refactor
Scope: orchestrator, developer, qa, devops, hooks, etc.

Examples:
- feat(orchestrator): add delegation matrix
- skill(code-reading): implement strategic reading protocol
- script(tdd): add coverage threshold check
```

### Adding a New Skill

1. Create `skills/<category>/<skill-name>/SKILL.md`
2. Add YAML frontmatter with `name` and `description`
3. Keep body under 500 lines
4. Add detailed content to `references/` if needed
5. Run `pytest tests/test_skills_valid.py -v`

## Documentation

| Document | Purpose |
|----------|---------|
| [Architecture](docs/architecture.md) | Full system specification |
| [Hidden Skills](docs/hidden-skills.md) | Deep-dive into the 80% |
| [Implementation Guide](docs/implementation-guide.md) | Quickstart and examples |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |

## Statistics

- **61 files** in the system
- **39,000+ lines** of content
- **12 skills** with **25 reference documents**
- **5 automation scripts**
- **2 git hooks**
- **62 validation tests** (all passing)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>Built with the 10X methodology using Claude Code</i>
</p>
