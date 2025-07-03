# Vibe Coders

**Vibe Coders** is an AI-powered documentation generator for coding projects. It analyzes your codebase hierarchically using [Tree-sitter](https://github.com/tree-sitter/tree-sitter) and generates comprehensive, readable Markdown documentation for every level of your project — from functions to the entire repository.

---

## 📚 Table of Contents

* [Overview](#overview)
* [How It Works](#how-it-works)
* [Features](#features)
* [Supported Languages](#supported-languages)
* [Example Usage](#example-usage)
* [Configuration](#configuration)
* [Contributing](#contributing)
* [License](#license)

---

## 🧠 Overview

Vibe Coders is designed with the idea that:

> A project can be described by a set of modules,
> each module by its packages,
> each package by its files,
> and each file by its functions and methods.

This tool helps automate documentation for any structured project — ideal for teams, solo developers, and open-source maintainers who want clean, consistent, and useful docs.

---

## ⚙️ How It Works

1. **Function-Level Analysis:**
   Each function/method is parsed using Tree-sitter and summarized using an OpenAI-like API. Results are cached locally for efficiency.

2. **File-Level Summary:**
   Using the cached descriptions, each file is described as a whole based on its function contents.

3. **Package/Directory-Level Documentation:**
   Individual file summaries are aggregated into a single `README.md` for the directory.

4. **Project-Level Overview:**
   A top-level `README.md` is generated summarizing the entire project.

5. **Auto Commit & PR (Optional):**
   If configured with your credentials, the tool can commit, push, and even open a Pull Request for the generated docs.

---

## ✨ Features

* **Multi-Language Support:**
  Built on Tree-sitter, supports multiple languages out-of-the-box.

* **Token-Efficient:**
  Uses smart local caching to reduce token usage and cost for large codebases.

* **Modular & Extensible:**
  Easy to customize models, prompts, and add support for new languages.

---

## 🧪 Supported Languages

* Python
* C++
* JavaScript
* Go
* Rust
  
*(More can be added with minimal effort.)*

---

## 🚀 Example Usage

To generate documentation for an example project:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Run the tool
python3 main.py --dir examples
```

---

## 🛠️ Configuration

You can easily tweak the following:

* LLM API endpoints (e.g. OpenAI-compatible)
* Prompt templates
* Cache location
* Tree-sitter grammars for additional languages
* Optional GitHub integration for auto PRs

> Configuration is designed to be readable and developer-friendly.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request.

---

## 📄 License

MIT License. See `LICENSE` for more details.