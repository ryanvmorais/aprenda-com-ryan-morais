![Simple Calculator in Python: real terminal capture calculating 42 + 8](assets/calculadora-simples-python-terminal.svg)

# 🧮 Simple Calculator in Python | Logic and Dictionaries Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![deps](https://img.shields.io/badge/deps-uv-DE5FE9)
[![CI](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml/badge.svg)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![Lint](https://img.shields.io/badge/lint-ruff-261230)
![Format](https://img.shields.io/badge/style-black-000000)
![Types](https://img.shields.io/badge/types-mypy%20strict-2A6DB2)
![License](https://img.shields.io/badge/license-MIT-green)

This folder holds a **Simple Calculator in Python**, built as study material for people who are just starting to program. The main goal is to show how to organize **interactive menus** and **run basic math operations** cleanly. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Practice **dictionaries**, **loops** and **error handling**. It is the ideal project to understand how Python processes user input and returns math results in real time.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **Dictionaries (mapping):** how to map math symbols (`+`, `-`, `*`, `/`) to readable names.
- **Error handling (try/except):** how to keep the program from closing when you divide by zero or type letters.
- **List handling:** turning dictionary keys into lists so options can be picked by number (index).
- **Terminal UX:** using the `os` module to clear the screen and build a dynamic interface.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this calculator:

1. **Operations dictionary:** instead of many `if` statements, we store the operations in a dictionary (`dict`). This lets the program "know" the name of each symbol automatically.
2. **Dynamic menu:** the code walks through the dictionary and builds a numbered menu. If you add an operation later, the menu updates itself.
3. **Safe input:** we use `int(input()) - 1` to turn the user's choice into the right Python index, which always starts at 0.
4. **Shielding (try/except):** if the user types something wrong, the program reports the error politely instead of crashing.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library, with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the project with a single command. |
| **Terminal** | The interface where the program runs and receives the user's input (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/calculadora_simples
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_calculadora.bat`; on Linux/macOS, run `iniciar_calculadora.sh` in the terminal. The scripts check that `uv` is installed before starting.

> ⚠️ **Note:** the program detects whether you are on Windows, Linux or macOS to clear the screen the right way.

---

### Quality and tests

The project has an automated test suite (`pytest`) and a quality gate that runs in CI on every push and every PR:

```bash
# Installs the development dependencies
uv sync

# Lint + import order
uv run ruff check .

# Formatting
uv run black --check .

# Type checking
uv run mypy

# Tests
uv run pytest
```

For the map of each technology in the stack (what it is, why it was chosen, what to study), see [docs/stack.md](docs/stack.md). For the expected behavior of the program and the history of decisions, see [specs/](specs/). For architecture and conventions in detail, see [CLAUDE.md](CLAUDE.md). These three are in Portuguese.

---

### 📋 Practice activities (Evolution Challenges):

To exercise what you learned, try changing the code and implementing these new features:

1. **🏆 Operation History:** create a list (e.g. `historico_calculos`) that stores every result, and a new menu option to show it, so the data does not vanish every time the screen is cleared.
   - **What you learn:** telling single-value variables apart from structures that accumulate data, and keeping information in memory during the session.
2. **📊 New Math Functions:** extend the operations dictionary to include the **Remainder (%)** and the **Square Root (√)**, handling the case where the second value is not needed.
   - **What you learn:** watching the operations dictionary grow without new `if` statements, and dealing with operations that take a different number of inputs.
3. **🎨 Visual Feedback:** use the `colorama` library to show results in **green** and error messages (such as division by zero) in **red**.
   - **What you learn:** installing an external dependency with `uv add` and using it without breaking the rest of the program.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Rock, Paper, Scissors in Python](../pedra_papel_tesoura/README.en.md):** dictionaries and Object-Oriented Programming.
- **[Tic Tac Toe in Python](../jogo_da_velha/README.en.md):** matrices and Object-Oriented Programming.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the project, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in [CONTRIBUTING.md](CONTRIBUTING.md) (in Portuguese).
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. For more details, see the [LICENSE](LICENSE) file.
