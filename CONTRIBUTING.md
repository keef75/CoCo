# Contributing to CoCo

Welcome, and thank you for your interest in contributing to CoCo! This is an educational agentic AI project that demonstrates how consciousness-oriented AI assistants were built in the early days of the agentic AI movement -- before modern frameworks like LangChain, CrewAI, or AutoGen became mainstream. Contributions of all kinds are valued, whether you are fixing a bug, improving documentation, or exploring new consciousness extensions.

---

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Running Tests](#running-tests)
- [Dependency Tiers](#dependency-tiers)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Code of Conduct](#code-of-conduct)

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/CoCo.git
   cd CoCo
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies** (see [Development Setup](#development-setup)).
5. Make your changes, write tests if applicable, and commit.
6. **Push** your branch and open a Pull Request against `main`.

---

## How to Contribute

There are many ways to contribute:

- **Bug Reports**: Found something broken? Open an issue with steps to reproduce.
- **Feature Requests**: Have an idea for a new consciousness extension or tool? Open a discussion or issue.
- **Code Contributions**: Fix bugs, add features, improve performance, or refactor existing code.
- **Documentation**: Improve the README, add tutorials, or clarify architecture docs.
- **Testing**: Add test coverage, especially for tool integrations and memory systems.
- **Educational Content**: Write guides explaining CoCo's architecture patterns for others learning about agentic AI.

---

## Development Setup

```bash
# Clone and enter the project
git clone https://github.com/<your-username>/CoCo.git
cd CoCo

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"       # Development dependencies
# OR
pip install -e ".[all]"      # All dependencies including optional integrations

# Copy environment template and add your API keys
cp .env.example .env
```

---

## Code Style

- **Python version**: 3.10 or higher is required.
- **No linter is currently configured**. We rely on syntax validation and code review.
- Before submitting, verify your code compiles cleanly:
  ```bash
  python -m py_compile <your_file.py>
  ```
- Follow the existing patterns in the codebase:
  - Use type hints where practical.
  - Write docstrings for public methods and classes.
  - Keep imports organized: standard library, third-party, local.
  - Prefer descriptive variable names over abbreviations.
- The project uses a **monolithic architecture** for the core engine. If you are adding a new tool or consciousness extension, follow the **Three-Part Tool System** pattern documented in `CLAUDE.md`:
  1. Tool definition (JSON schema)
  2. Tool implementation (Python method)
  3. Tool handler (routing in `_execute_tool()`)

---

## Running Tests

```bash
# Run the full test suite
python -m pytest tests/

# Run a specific test file
python -m pytest tests/test_integration.py

# Run with verbose output
python -m pytest tests/ -v

# Syntax validation (quick check)
python -m py_compile cocoa.py
```

Test files follow the `test_*.py` naming convention. When adding new features, include corresponding tests.

---

## Dependency Tiers

CoCo uses a tiered dependency system to keep the minimal install lightweight while supporting full functionality for those who need it:

| Tier | What You Get | Install Command |
|------|-------------|-----------------|
| **Minimal** | Core conversation engine, basic tools, Rich UI | `pip install -e .` |
| **Standard** | Minimal + web search | `pip install -e ".[standard]"` |
| **Full** | All integrations: audio, visual, video, Twitter, Google Workspace | `pip install -e ".[all]"` |
| **Dev** | Full + testing and development tools | `pip install -e ".[dev]"` |

When adding a new dependency:

- Determine which tier it belongs to. Most new dependencies should go in a specific extras group, not the base install.
- Add it to the appropriate section in `pyproject.toml`.
- Document why the dependency is needed in your PR description.

---

## Pull Request Process

1. **Ensure your branch is up to date** with `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. **Run tests** and syntax validation before pushing.
3. **Write a clear PR description** that explains:
   - What the change does and why.
   - Which components are affected (memory, tools, UI, extensions, etc.).
   - Any new dependencies introduced.
   - How to test the change.
4. **Link related issues** if applicable.
5. PRs will be reviewed for:
   - Correctness and completeness.
   - Adherence to the Three-Part Tool System (for new tools).
   - Test coverage for new functionality.
   - Documentation updates if user-facing behavior changes.

---

## Issue Guidelines

When opening an issue, please include:

- **Bug reports**: Python version, OS, steps to reproduce, expected vs. actual behavior, and relevant error output.
- **Feature requests**: Clear description of the proposed feature, the problem it solves, and how it fits into CoCo's architecture.
- **Questions**: Check existing documentation in `docs/` and `CLAUDE.md` first. If your question is not answered there, open an issue.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this standard. Please report unacceptable behavior by opening an issue.

We are committed to providing a welcoming and inclusive experience for everyone, regardless of background or experience level. This is an educational project -- questions are encouraged, and no contribution is too small.

---

## Thank You

CoCo represents an early chapter in the story of agentic AI. Your contributions help preserve and improve this educational resource for the broader community. Whether you are here to learn, to build, or to teach -- welcome aboard.
