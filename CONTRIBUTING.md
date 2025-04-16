# 🧑‍💻 Contributing to HIPAah

First off, thanks for your interest in contributing! HIPAah is an open-source project built to make HIPAA-compliant development easier, safer, and more accessible for everyone.

Whether you’re fixing a bug, building a new feature, improving documentation, or suggesting ideas — we welcome your contributions.

---

## 🛠️ Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/hipaah.git
cd hipaah
poetry install
```

### 2. Run the Dev Server

```bash
uvicorn api.main:app --reload
```

### 3. Run Tests

```bash
pytest
```

---

## 🧩 How You Can Contribute

- 🔧 Fix bugs or file new issues
- ✨ Implement features from the roadmap or issues
- 🧪 Write unit/integration tests
- 📚 Improve or clarify documentation
- 🎨 Help design UI/CLI/UX for tooling
- 🔍 Review pull requests

---

## 🧃 Branch & PR Guidelines

- Create feature branches from `main`:  
  `git checkout -b feature/your-feature-name`
- Write clear, descriptive commit messages.
- Link issues in your PR when applicable.
- Run tests before submitting.
- Use `black` or `prettier` for code formatting (we’ll add hooks soon).

---

## 📁 Project Structure

```plaintext
api/        # FastAPI endpoints
core/       # Access control engine
sdk/        # SDKs (Python, JS)
cli/        # Command-line tool
utils/      # Helpers: masking, logging, etc.
data/       # Audit logs
config/     # Sample schemas/policies
```

---

## 📋 Code of Conduct

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) — we’re building a kind, respectful, and inclusive community.

---

## 💬 Questions?

- Open an [issue](https://github.com/YOUR_USERNAME/hipaah/issues)
- Ping us in Discussions
- Or email jeff@hipaah.com

Thanks again — we’re glad you’re here. Let's build the future of privacy-first healthtech.
