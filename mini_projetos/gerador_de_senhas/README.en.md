![Password Generator in Python: animation of a session that generates a strong password with its entropy, rejects a length out of range and builds a custom password without symbols and without the look-alike characters, draws a 5-word passphrase and shows random repeating the same password with the same seed, until it quits](assets/gerador-de-senhas-python-terminal-sessao.svg)

# 🔐 Password Generator in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Run it now:** with [uv](https://docs.astral.sh/uv/) installed, clone the repository and, inside `mini_projetos/gerador_de_senhas`, run `uv run main.py`.

This folder holds the **Password Generator in Python** (Gerador de Senhas), designed as study material for beginner developers. With a single Enter, the program generates a strong 16-character password; in a custom password, you choose the length, the character types and whether to avoid the ones that look alike, such as zero and O. It also draws passphrases with Portuguese words and shows, next to every password, its entropy in bits with the math. The main goal is the hands-on use of **programming fundamentals**: a secure draw, the math behind a password's strength and small functions that are tested without a keyboard or luck. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Show the difference between **`random` and `secrets`**, the use of the **`string` module constants** and the computation of **entropy with `math.log2`** in Python. It is a practical project for students who want to understand why a draw that looks random can be predictable, and what actually makes a password hard to guess.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **The `secrets` module:** the draw made for security, which uses the operating system's source of randomness, and why `random` is not fit for passwords.
- **The `string` module constants:** `ascii_lowercase`, `ascii_uppercase`, `digits` and `punctuation` build the password's 94 characters, with no alphabet typed by hand.
- **Entropy with `math.log2`:** a password's strength in bits, computed from its length and the number of possible characters, and why each extra bit doubles the work of whoever tries to guess it.
- **Functions as parameters:** the draw comes in as `escolher`, and the same function generates the real password (with `secrets`), the one in the demonstration and the ones in the tests (with a fixed-seed `random`).
- **`any` and `all`:** the "at least one of each type" rule fits in one line that combines the two functions.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this program:

1. **Why `secrets`, and Not `random`:** the documentation of the `random` module warns that its generators should not be used for security purposes, and points to `secrets` for that. `random` is a pseudo-random generator: each number comes from a computation on the previous one, starting from a seed. Whoever finds out the seed, or sees consecutive numbers from the same generator, can predict the next ones. `secrets` uses the operating system's source of randomness, made for security. Option 4 of the menu shows the difference on screen: two passwords generated with `random` and the same seed come out identical, and two with `secrets` come out different.
2. **The Draw Comes in as a Parameter:** `secrets.choice` and the `choice` of a `random.Random(seed)` have the same signature: they take a sequence and return one of its items. That is why every function that draws takes `escolher`, which is `secrets.choice` when the program runs. The demonstration and the tests pass a fixed-seed `random`, and the function that builds the password is the same in all three cases: the problem with `random` is not in the password code, but in the generator.
3. **The Alphabets Come from the `string` Module:** `string.ascii_lowercase` (26 letters), `string.ascii_uppercase` (26), `string.digits` (10) and `string.punctuation` (32 symbols) add up to 94 characters. Avoiding the look-alikes (`0 O 1 l I |`) leaves 88. Each chosen type becomes a group: the groups joined together are what is drawn, and each group, on its own, is what the rule in the next step checks.
4. **"One of Each Type" Draws Again:** many sites require at least one uppercase letter, one digit and one symbol. The temptation is to force a character of each type into a position, but that makes the password more predictable. Here, the whole password is drawn and, if a type is missing, it is thrown away and drawn again. This way, every password that meets the rule has the same chance of coming out. The check fits in one line: `all(any(c in grupo for c in senha) for grupo in grupos)`. With 16 characters, about 4 in 5 drawn passwords already work on the first try; with 8, about half.
5. **Entropy, with the Math:** entropy is the password's length times the log2 of the number of possible characters. The log2 tells how many bits each character is worth, and each extra bit doubles the attempts of whoever tries to guess. The program shows the math next to the password (in Portuguese, with a decimal comma):
    ```text
    Entropia: 16 × log2(94) ≈ 104,9 bits
    Cada bit a mais dobra as tentativas de adivinhar.
    ```
    The entropy shown is the formula's, a little above the real one: the "one of each type" rule throws some passwords away, which takes off at most 1.3 bits with 8 characters and 0.4 bits with 16. The difference is small, and the formula is the one you can read and check in your head. The decimal comma is swapped in with `replace`, without the `locale` module, so the result comes out the same on any system.
6. **The Passphrase and the BIP-39 List:** the passphrase draws words, with replacement, from a list of 2048 words. Since 2048 is 2 to the power of 11, each word is worth 11 bits, and the default 7 words give 77 bits, with a hyphen between them. The list is the Portuguese one from BIP-39, a Bitcoin wallet standard (file `bip-0039/portuguese.txt` of the [bitcoin/bips](https://github.com/bitcoin/bips) repository, under the MIT License): words of 4 to 8 letters, without accents, spelled the same in Brazil and in Portugal. `palavras.txt` is an unmodified copy, and a test checks its SHA-256; the origin, the commit and the authors are in the [LICENSE](LICENSE). The program finds the file through `Path(__file__).parent`, from any folder it is called from.
7. **Checked Answers and a Clean Exit:** each question takes Enter for the default (in brackets) and asks again when the answer does not fit, without going back to the menu. Numbers go through `isascii()` and `isdecimal()` before `int()`, which removes the need for a `try` and rejects digits from other scripts, such as the Arabic "٣". `Ctrl+C` ends the program at any point, with a goodbye and no stack trace.
8. **No Password Is Stored:** the program does not write files, does not use the network and takes nothing from the command line, which would be saved in the shell history. The generated password only stays on screen until the next option, alone on its line, so it can be selected and copied whole.

> 💡 **Study tip:** choose option 4 several times: the two `random` passwords always come out the same, and the `secrets` ones change every time. Then compare the entropy of an 8-character custom password with digits only (`8 × log2(10) ≈ 26.6 bits`) with that of a 5-word passphrase (`5 × log2(2048) = 55 bits`): the passphrase, easier to remember, is worth more than twice as much.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library (`secrets`, `random`, `string`, `math`, `pathlib`, `os`, `sys`), with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the program with a single command. |
| **Terminal** | The interface where the result shows up and receives the user's choices (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/gerador_de_senhas
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_gerador.bat`; on Linux/macOS, run `iniciar_gerador.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before opening the generator.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the program has no external dependencies. It also detects whether you are on Windows, Linux or macOS to clear the screen the right way. To quit, choose option 5 or press `Ctrl+C` at any moment.

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

1. **🔁 Several Passwords at Once:** add a question to the custom password, "how many passwords?", and show one password per line, with the entropy only once at the end.
   - **What you learn:** reusing `gerar_senha` in a loop without changing the function, and seeing that each password's entropy does not change with how many are generated.
2. **🔠 Passphrase with a Capital Letter and a Digit:** give the passphrase the option to draw one word to start with a capital letter and one digit for the end of the phrase, adding the bits of each choice to the entropy.
   - **What you learn:** the entropy of independent choices adds up: drawing which word gets the capital letter is worth `log2(quantidade)` bits, and the digit, `log2(10)`.
3. **🎯 The Exact Entropy:** compute the real entropy of the custom password, counting only the passwords that have a character of each type, and show the difference from the formula's.
   - **What you learn:** the inclusion-exclusion principle, with `itertools.combinations` to go through the groups of types that may be missing, and why the difference shrinks as the password grows.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[CPF Validator in Python](../validador_de_cpf/README.en.md):** the check digit algorithm, the remainder of a division and pure functions.
- **[To-Do List in Python](../lista_de_tarefas/README.en.md):** JSON files, `pathlib` and atomic writes.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the program, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in the repository's [CONTRIBUTING.md](../../CONTRIBUTING.md) (in Portuguese). In this project, every password draw goes through `escolher`, with `secrets.choice` as the default, and `random` only shows up in the demonstration; the "one of each type" rule draws the whole password again, never forcing a position; `palavras.txt` is not edited, because it is the exact copy of the BIP-39 list; and, in examples, use only passwords generated with a fixed seed, never a password in use.
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. The word list (`palavras.txt`) is the Portuguese BIP-39 list, also under the MIT License, with its origin and authors recorded in the [LICENSE](LICENSE) file, which also has the license details.
