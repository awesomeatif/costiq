# Contributing to CostIQ

First off, thank you for considering contributing to CostIQ! 🎉 It's people like you that make CostIQ such a great tool for hospital cost optimization.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/costiq.git
   cd costiq
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/buildwithatif/costiq.git
   ```

## 💡 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)

### ✨ Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a **clear and descriptive title**
- Provide a **detailed description** of the proposed feature
- Explain **why this would be useful** to CostIQ users
- Include **mockups or examples** if applicable

### 🔧 Code Contributions

Great areas to contribute:

| Area | Description |
|------|-------------|
| **Rules Engine** | Add new cost detection rules |
| **PDF Reports** | Enhance report formatting and visualizations |
| **API Endpoints** | Add new functionality |
| **Tests** | Improve test coverage |
| **Documentation** | Improve docs and examples |

## 💻 Development Setup

```bash
# Clone and enter directory
cd costiq/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest
```

## 📝 Style Guidelines

### Python Code Style

- Follow **PEP 8** guidelines
- Use **type hints** for function parameters and returns
- Write **docstrings** for all public functions/classes
- Maximum line length: **100 characters**

```python
def calculate_variance(
    prices: list[float],
    threshold: float = 0.1
) -> dict[str, float]:
    """
    Calculate price variance for a list of prices.
    
    Args:
        prices: List of unit prices to analyze
        threshold: Variance threshold for flagging (default: 10%)
        
    Returns:
        Dictionary with mean, std_dev, and flagged items
    """
    pass
```

### File Organization

- One class per file when possible
- Group related functionality in directories
- Keep imports organized (stdlib → third-party → local)

## 💬 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |

### Examples

```
feat(rules): add emergency procurement detection rule

- Detect POs marked as rush/emergency
- Compare pricing vs standard orders
- Calculate premium percentage

Closes #123
```

```
fix(pdf): correct table overflow on findings page

Tables with long descriptions now wrap properly.

Fixes #456
```

## 🔀 Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Confirmation tests pass

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] No merge conflicts

---

## 🙏 Recognition

Contributors will be recognized in our README! Thank you for helping make CostIQ better.

---

<p align="center">
  <sub>Questions? Open an issue or reach out to <a href="https://github.com/awesomeatif">@awesomeatif</a></sub>
</p>
