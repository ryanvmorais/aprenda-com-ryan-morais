![Password Strength Checker in Python: animation of a session that checks Senha@123, scored 2 out of 4 because of its sequence, and a four-word passphrase, scored 4 out of 4, without the password showing up while it is typed, then shows the annotated examples, scored 0 to 4, until it exits](assets/verificador-de-forca-de-senha-python-terminal-sessao.svg)

# 🔎 Password Strength Checker in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Run it now:** with [uv](https://docs.astral.sh/uv/) installed, clone the repository and, inside `mini_projetos/verificador_de_forca_de_senha`, run `uv run main.py`.

This folder holds the **Password Strength Checker in Python** (Verificador de Força de Senha), designed as study material for beginner developers. You type a password, which does not show up on screen, and the program gives it a score from 0 to 4, from very weak to strong. Next to the score, it shows what weighed in: the length, the character types, the repetitions and sequences (such as `aaa` and `123`), whether the password is on a list of common passwords, and the estimated entropy, with the math. Then it suggests what to change to make the password better. The main goal is the hands-on use of **programming fundamentals**: rules written as small functions, regular expressions and reading text without showing it. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

> ⚠️ **The score is a teaching estimate, not an audit:** the program applies simple rules that anyone can read in the code. Estimators such as [zxcvbn](https://github.com/dropbox/zxcvbn), used on many sign-up pages, recognize dictionary words, names, dates and letter-to-number swaps (`s3nh4`), which these rules do not.

### 🎯 Project goal:

Show how to write **rules with `any()` and the string methods**, how to find patterns with the **`re` module** and how to read a password without echo using **`getpass`** in Python. It is a hands-on project for students who want to understand why a password with letters, numbers and symbols can still be weak, and what actually makes it hard to guess.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **Rules with `any()`:** `islower`, `isupper` and `isdigit` each tell, in one line, whether the password has at least one character of each type.
- **Regular expressions with the `re` module:** the expression `(.)\1{2,}` finds a character repeated three times or more, with a backreference to a group (`\1`).
- **Windows and the `in` operator:** each 3-character slice is looked up in the alphabet, the digits and the keyboard rows, forwards and backwards.
- **Estimated entropy with `math.log2`:** the same math as the Password Generator, applied to a password made by hand, and why it needs discounts.
- **The `getpass` module:** the password is read without showing up on screen, and the program never shows it, not even a piece of it.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this program:

1. **The Character Types, with `any()`:** each type is a question about the whole password: "is any character lowercase?". `any()` answers by going through the password and stops at the first one that fits: `any(c.islower() for c in senha)`. The same goes for `isupper` and `isdigit`, and whatever is neither a letter nor a digit counts as a symbol. An accented letter (`é`) counts as a regular letter, and a space, as a symbol. The size of each type comes from the `string` module, as in the Password Generator: 26 lowercase letters, 26 uppercase letters, 10 digits and 32 symbols.
2. **Repetitions, with `(.)\1{2,}`:** read piece by piece, the expression says: `(.)` keeps any character in a group; `\1` is "the same character as group 1"; and `{2,}` asks for it to show up two more times or more. So `aaa` and `1111` match, and `aa` does not. With `re.IGNORECASE`, `aAa` also counts as a repetition. `finditer` returns each match, and the `span()` of each one tells where it starts and ends.
3. **Sequences, with 3-Character Windows:** the program looks at the password 3 characters at a time (`Sen`, `enh`, `nha`…) and checks, with the `in` operator, whether the window is inside one of the known sequences: the alphabet, the digits from 0 to 9 and the keyboard rows (`qwertyuiop`, `asdfghjkl` and `zxcvbnm`). The reverse of each sequence comes from the `[::-1]` slice, so `cba` and `987` are found too. The comparison is in lowercase, so `ABC` counts as `abc`.
4. **Each Predictable Piece Is Worth One Character:** whoever uses `aaaa` or `1234` chose one character and one rule; the rest is guessed almost for free. That is why the pieces found that overlap are merged (the windows `abc` and `bcd` of `abcd` become one piece), and each piece counts as a single character. In `Senha@123`, the 9 characters become 7 in the math: `123` is worth one.
5. **The Estimated Entropy, with the Math:** the formula is the Password Generator's: the number of characters that count times the log2 of the alphabet size, which is the sum of the types present. The program shows the math next to the score:
    ```text
    Entropia estimada: 7 × log2(94) ≈ 45,9 bits
    ```
    The formula assumes each character was drawn at random, which a password made up by a person almost never is. That is why it is called **estimated** entropy, and the repetitions, the sequences and the common password list correct the most predictable cases.
6. **The Score, with Bands and Two Caps:** the score is how many bands the entropy reaches: 28, 36, 60 and 80 bits raise it to 1, 2, 3 and 4. The bands match the Password Generator: its shortest password (8 characters, 52.4 bits) is fair, and its default strong password (16 characters, 104.9 bits) is strong. Two caps apply on top of the math: a password on the common password list scores 0, and a password shorter than 8 characters scores no more than 1.
7. **The Common Password List:** these are the 150 passwords most used by Portuguese speakers, such as `123mudar` and `102030`, taken from real leaks by the Pwdb-Public project. `senhas_comuns.txt` is an unmodified copy of the file `Portugese_Pwdb_common-password-list-top-150.txt` from [SecLists](https://github.com/danielmiessler/SecLists), under the MIT License, and a test checks its SHA-256; the origin, the commit and the copyright notices are in the [LICENSE](LICENSE). The comparison uses the whole password, in lowercase, and the program finds the file through `Path(__file__).parent`, from whatever folder it is called.
8. **The Password Read with `getpass`:** `getpass.getpass` takes the prompt and returns what was typed, like `input`, but without showing anything on screen while you type. A space at the start or at the end counts too, because the password does not go through `strip()`. In an environment that is not a real terminal, such as IDLE, `getpass` cannot hide what is typed: Python warns with a `GetPassWarning` and the password shows up. That is why you should run the program in a terminal. `Ctrl+C` ends the program at any point, including the password prompt, with a goodbye and no stack trace.
9. **No Password Is Stored or Shown:** the password only goes through two functions, the one that asks for it and the one that analyzes it. The analysis returns numbers, type names and true or false, never the typed text, so no message from the program can show the password, nor the sequence found in it. The program does not write files, does not use the network and takes nothing from the command line, which would be saved in the shell history.

> 💡 **Study tip:** check `Senha@123`: it has all four character types and scores only 2, with 45.9 bits, because `123` is a sequence and the length is short. A passphrase such as `girassol-azul`, with only lowercase letters and the hyphen, scores 3. Then check `Flamengo@2026`: it scores 4 under these rules, with 85.2 bits, but it is a well-known name followed by a year and a symbol, exactly the kind of password someone tries early. zxcvbn, for example, recognizes `2026` as a year and looks the word up in dictionaries; these rules only see 13 characters with all four types.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library (`getpass`, `re`, `string`, `math`, `pathlib`, `os`, `sys`), with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the program with a single command. |
| **Terminal** | The interface where the result shows up and receives the user's choices (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/verificador_de_forca_de_senha
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer a double click? Use the shortcut:** on Windows, open `iniciar_verificador.bat`; on Linux/macOS, run `iniciar_verificador.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before opening the checker.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the program has no external dependencies. It also detects whether you are on Windows, Linux or macOS to clear the screen the right way. To exit, choose option 3 or press `Ctrl+C` at any time.

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

For the map of each technology in the stack (what it is, why it was chosen, what to study), see [docs/stack.md](docs/stack.md). For the expected behavior of the program and the history of decisions, see [specs/](specs/). For the details of the architecture and conventions, see [CLAUDE.md](CLAUDE.md). These three are in Portuguese.

---

### 📋 Practice activities (Evolution Challenges):

To exercise what you learned, try changing the code and implementing these new features:

1. **📅 Years as Predictable Pieces:** add a rule that finds years from 1900 to 2099 (`1998`, `2026`) and discounts them like the sequences, each worth one character.
   - **What you learn:** writing a regular expression with alternative groups (`(19|20)\d\d`) and fitting a new rule into the piece format that `juntar_trechos` already handles, without changing the function.
2. **🔤 Letter-to-Number Swaps:** before comparing with the common password list, undo the most common swaps (`4` for `a`, `3` for `e`, `0` for `o`, `1` for `i`, `@` for `a`), so that `s3nh4` is recognized as `senha`.
   - **What you learn:** building a translation table with `str.maketrans` and applying it with `str.translate`, and seeing why swapping letters for numbers barely makes a password harder to guess.
3. **⏱️ The Time to Guess:** show, next to the entropy, how long a computer that tries 10 billion passwords per second would take, in the worst case, to reach the password.
   - **What you learn:** turning bits into guesses with `2 ** bits`, splitting them into years, days and hours with `divmod`, and picking the right unit for a number that goes from seconds to billions of years.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Password Generator in Python](../gerador_de_senhas/README.en.md):** `secrets` versus `random`, the `string` module constants and the same entropy math.
- **[CPF Validator in Python](../validador_de_cpf/README.en.md):** the check digit algorithm, the remainder of a division and pure functions.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the program, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in the repository's [CONTRIBUTING.md](../../CONTRIBUTING.md) (in Portuguese). In this project, the password only goes through `opcao_verificar` and `analisar`, and a new rule returns what it found as a number or a true-or-false in `Analise`, never the piece of the password; `senhas_comuns.txt` is not edited, because it is the exact copy of the SecLists list; the score of the annotated examples is computed, never written by hand; and, in examples, use only made-up passwords or ones from the common password list, never a password in use.
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. The common password list (`senhas_comuns.txt`) comes from SecLists, also under the MIT License, with its origin and copyright notices recorded in the [LICENSE](LICENSE) file, which also has the license details.
