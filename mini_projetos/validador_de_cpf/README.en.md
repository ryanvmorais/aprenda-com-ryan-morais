![CPF Validator in Python: animation of a session that validates the Receita Federal example with punctuation, rejects the same number with the last digit changed, generates a CPF for testing with the warning and shows the math of the two check digits in the step-by-step mode, until it quits](assets/validador-de-cpf-python-terminal-sessao.svg)

# 🔢 CPF Validator in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Run it now:** with [uv](https://docs.astral.sh/uv/) installed, clone the repository and, inside `mini_projetos/validador_de_cpf`, run `uv run main.py`.

This folder holds the **CPF Validator in Python** (Validador de CPF), designed as study material for beginner developers. The CPF is the Brazilian individual taxpayer number. You type a CPF, with or without punctuation, and the program tells you whether it is valid by computing its two check digits, shows the number in the `000.000.000-00` format and the tax region. A step-by-step mode shows the math, and a generator builds valid numbers to test forms. The main goal is the hands-on use of **programming fundamentals**: a real algorithm, cleaning up the typed text and small, pure functions. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Show the use of the **weighted sum with the remainder of a division**, **text checks with `str.isdigit`** and **pure functions** in Python. It is a practical project for students who want to understand how a document number checks itself, without asking any service, and why keeping the math apart from the screen makes the code easy to test.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **Weighted sum and remainder (`%`):** each digit is multiplied by a weight, the products are added up, and the remainder of the sum divided by 11 gives the check digit.
- **List comprehension:** `[algarismo * peso for algarismo, peso in zip(algarismos, pesos)]` builds the products in one line, and another list comprehension drops the punctuation from the typed CPF.
- **Text checks (`str.isdigit` and `str.isascii`):** `isdigit()` alone accepts characters that are not the digits 0 to 9, and `isascii()` next to it closes that door.
- **Pure functions:** the math and check functions take a value and return another, without reading the keyboard or printing anything, so each one is tested with a single line.
- **`NamedTuple`:** the `Conta` keeps every step of the math (digits, weights, products, sum, remainder and digit), and the step-by-step mode shows on screen the same math that decided the result.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this program:

1. **The CPF Is Text, Not a Number:** a CPF has 11 digits, the 9 of the base and the 2 check digits. It stays a `str` from start to finish because, stored as an `int`, it would lose its leading zero: `int("01234567890")` becomes `1234567890`. The list of `int` only exists inside the math, and that is why 10 digits do not turn into a CPF with a zero in front: the program asks for all 11.
2. **Cleaning Up What Was Typed:** a list comprehension drops the dots, the hyphen and the spaces, in any position, so whoever types does not need to get the mask right. Every character left must be a digit from 0 to 9. Notice the `isascii()` next to `isdigit()`: on its own, `isdigit()` accepts "²", which `int()` rejects with an error, and digits from other scripts, such as the Arabic "٣", which `int()` reads as 3. Any other character rejects the CPF, and the result shows which one it was.
3. **The 1st Digit's Math (Weighted Sum):** each digit of the base, from left to right, is multiplied by the weights 1 to 9, the products are added up, and the digit is the remainder of the sum divided by 11 (a remainder of 10 counts as 0, because the digit is a single digit). This is the method published by the Receita Federal (Brazil's federal revenue service) in Annex II of the Ato Declaratório Executivo Cofis nº 41/2017, which includes a worked example with the base `280012389`. The step-by-step mode shows it like this:
    ```text
    1º dígito verificador
    Algarismos   2   8   0   0   1   2   3   8   9
    Pesos        1   2   3   4   5   6   7   8   9
    Produtos     2  16   0   0   5  12  21  64  81
    Soma 201 ÷ 11 = 18, resto 3 → dígito 3
    ```
4. **The 2nd Digit's Math (the Same Function):** the 1st digit goes at the end of the base, and the math repeats with the 10 digits and the weights 0 to 9: the sum is 195, the remainder is 8, and the example's CPF becomes `280.012.389-38`. In both sums the last digit gets the weight 9, so `range(10 - len(algarismos), 10)` builds the weights for both digits, and a single function, `calcular_digito`, serves both.
5. **The Better-Known Method Gives the Same Result:** many websites teach the weights 10 to 2 (and 11 to 2 for the 2nd digit), with the digit being 11 minus the remainder, and 10 and 11 counting as 0. Each weight there is 11 minus the weight here, so the sum there leaves the remainder "11 minus the remainder here", and 11 minus that is the remainder here again. A test compares both methods on 10,000 random bases.
6. **The Repeated Sequence:** a CPF with all 11 digits equal passes the math but is rejected anyway: that is the convention of registration validators, because those are the numbers people type to skip the field. The check fits in one line: `len(set(cpf)) == 1`, since a set keeps each digit only once. In the step-by-step mode, the math shows up matching, followed by the rejection.
7. **The Tax Region (9th Digit):** the 9th digit tells the tax region of the first registration, according to the table in the "CPF" leaflet of the Receita Federal's tax education program (in the example, 9 is PR and SC). It says where the CPF was issued, not where the person lives today.
8. **Pure Functions, Keyboard and Drawing by Parameter:** the math, check and text functions take a value and return another, without reading the keyboard or printing; only `main` and `exibir_tela` touch the terminal. `main` receives who reads the keyboard (`ler`) and who draws the numbers (`sortear`), with `input` and `random.randrange` as defaults. Whoever uses the program does not notice the difference, but the tests pass a fake keyboard and a fixed-seed drawing.
9. **The Generator and Privacy:** the generator draws the 9 digits of the base (again, if they all come out equal) and computes the two digits with the same functions as the validation. The number passes the math, but it may match the CPF of a real person, because there are about 1 billion valid combinations and hundreds of millions of issued CPFs: use it only to test a system. And no typed or generated CPF is kept: the program writes no file and uses no network, and the result only stays on screen until the next action.

> 💡 **Study tip:** in the step-by-step mode, type `280.012.389-39`, with the last digit changed: the 1st digit matches and the 2nd does not. Now type `280.012.389-48`: the 1st does not match, and the 2nd does, because its math uses the computed 1st digit, not the typed one. Finally, type the same digit eleven times, to see the math matching and the repeated sequence being rejected.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library (`random`, `os`, `sys`, `typing`), with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the program with a single command. |
| **Terminal** | The interface where the result shows up and receives the user's choices (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/validador_de_cpf
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_validador.bat`; on Linux/macOS, run `iniciar_validador.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before opening the validator.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the program has no external dependencies. It also detects whether you are on Windows, Linux or macOS to clear the screen the right way. To quit, choose option 4 or press `Ctrl+C` at any moment.

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

1. **🏢 Validate a CNPJ:** add an option that validates a numeric CNPJ (the Brazilian company number) with 14 digits, whose weights go from 2 to 9 from right to left and start over at 2, with the digit being 11 minus the remainder (and 0 when the remainder is 0 or 1).
   - **What you learn:** generalizing the weighted sum, with the list of weights passed as a parameter, and seeing what changes and what is reused between two similar algorithms.
2. **📋 Several CPFs at Once:** let the validate option take several CPFs separated by commas and show one result per line.
   - **What you learn:** `str.split` and a loop that reuses `descrever_resultado` without changing any pure function, the proof that they do not depend on where the CPF came from.
3. **🗺️ Generate for a Region:** make the generator ask for the tax region (0 to 9) and fix the 9th digit of the base, drawing only the other eight.
   - **What you learn:** adding an optional parameter to `gerar_cpf` without breaking whoever already calls it, and validating the new input with a `conferir_*` function.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Hangman in Python](../jogo_da_forca/README.en.md):** strings, sets and accents with `unicodedata`.
- **[To-Do List in Python](../lista_de_tarefas/README.en.md):** JSON files, `pathlib` and atomic writes.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the program, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in [CONTRIBUTING.md](CONTRIBUTING.md) (in Portuguese).
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. For more details, see the [LICENSE](LICENSE) file.
