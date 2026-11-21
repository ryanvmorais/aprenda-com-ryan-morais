![Caesar Cipher in Python: animation of a session that encrypts the sentence "O segredo da mensagem está nas letras." (The secret of the message is in the letters.) with key 7, with the notice that the accents were removed, then breaks the ciphertext through letter frequency, which finds key 7 and shows the sentence back, until it exits](assets/cifra-de-cesar-python-terminal-sessao.svg)

# 🔐 Caesar Cipher in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Run it now:** with [uv](https://docs.astral.sh/uv/) installed, clone the repository and, inside `mini_projetos/cifra_de_cesar`, run `uv run main.py`.

This folder holds the **Caesar Cipher in Python** (Cifra de César), designed as study material for beginner developers. You type a text and a key from 1 to 25, and the program moves each letter that many positions along the alphabet: with key 3, A becomes D, and Z wraps around to C. It also decrypts with the key and breaks a ciphertext without it, in two ways: trying all 25 keys (brute force) or counting the letters and comparing them with the most common ones in Portuguese. The main goal is the hands-on use of **programming fundamentals**: math with the letter codes, the remainder of a division and counting with `Counter`. The typed text is not stored and never leaves the computer. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

> ⚠️ **The Caesar cipher protects nothing:** with only 25 possible keys, any ciphertext falls in seconds, as the program itself shows. It is here to understand how a cipher works and why this one is weak; to protect a real message, use modern encryption software.

### 🎯 Project goal:

Show how to swap letters with **`ord`, `chr` and the remainder of a division (`%`)**, how to apply the swap to the whole text with **`str.maketrans`** and how to break the cipher through **brute force** and **letter frequency**, counted with **`collections.Counter`**, in Python. It is a hands-on project for students who want to understand what a key is, why its size matters and how a pattern of the language gives a ciphertext away.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **Letter codes with `ord` and `chr`:** `ord` returns the number of a letter (`ord("a")` is 97), and `chr` goes the way back, so the letter becomes a calculation.
- **Modular arithmetic with `%`:** the remainder of a division by 26 makes Z wrap around to A, and a negative key walks backwards to decrypt.
- **Translation tables with `str.maketrans`:** all 52 letters swapped at once, with the rest of the text (spaces, digits, punctuation and emoji) going through unchanged.
- **Accents with the `unicodedata` module:** the NFD form splits the letter from its accent, so `ã` becomes `a` before encrypting.
- **Brute force:** a loop that tries all 25 possible keys, and why a real key cannot be tried that way.
- **Counting with `collections.Counter`:** how many times each letter shows up, the three most common with `most_common` and a score that finds the most likely key.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this program:

1. **The Position of a Letter, with `ord` and `chr`:** every character has a number, and the letters from `a` to `z` come in sequence, from 97 to 122. The position of a letter in the alphabet is its number minus that of `a`: `c` is `99 - 97`, position 2. Moving by the key means adding to the position, and `chr` turns the number back into a letter. For uppercase letters, the base is `A` instead of `a`, and the letter comes out uppercase as it went in.
2. **`% 26` and the Wrap from Z to A:** `z` is at position 25, and with key 3 the sum would be 28, outside the alphabet. The remainder of a division by 26 solves it: `(25 + 3) % 26` is 2, the `c`. It is the same math as a clock, where 3 hours after 11 is 2. That is why the key goes from 1 to 25: 0 and 26 leave the text unchanged, and 27 encrypts like 1.
3. **Decrypting Is Walking Backwards:** decrypting uses the same function, with a negative key. `a` with key -3 gives `(0 - 3) % 26`, and in Python the remainder of a negative number by 26 stays between 0 and 25: it gives 23, the `x`. Be careful when taking this math to another language: in C and JavaScript, `%` of a negative number gives a negative result, and the math would need to add 26 first.
4. **The `str.maketrans` Table:** instead of doing the math character by character in a loop, the program does it once for each of the 52 letters, lowercase and uppercase, and keeps the result in a table with `str.maketrans`. `translate` applies the table to the whole text, and everything that is not in it (spaces, digits, punctuation, emoji, a letter from another alphabet such as `ß`) goes through unchanged, with no `if`. `Ola, Mundo!` with key 3 becomes `Rod, Pxqgr!`.
5. **The Accents, with `unicodedata`:** the table only has the 26 unaccented letters, so `ã` would go through unencrypted and give the word away. Before encrypting, the NFD form splits each accented letter into the base letter plus the accent mark (`ã` becomes `a` + `~`, and `ç` becomes `c` + the cedilla), and the marks are dropped from the text. It is the same function as in the Hangman Game. That is why decrypting returns `A acao comecou` instead of `A ação começou`, and the result warns when the accents were removed.
6. **Brute Force, with the 25 Keys:** whoever does not have the key can try all of them. The program decrypts the text with each key from 1 to 25 and shows one line per key, cut to fit the terminal; the right key is the one whose line can be read. This only works because there are few keys. A modern cipher uses a 128-bit key, with 2¹²⁸ possibilities (a 39-digit number): trying a trillion keys per second, it would take more than 10 billion billion years, close to a billion times the age of the universe.
7. **Letter Frequency, with `Counter`:** in Portuguese, A, E and O show up much more than K, W and Y. `Counter` counts the letters of the text, and `most_common(3)` returns the three that show up the most. For each key, the program decrypts the text and gives it a score: each letter is worth its percentage in Portuguese, times how many times it shows up. The right text, full of A, E and O, adds up to more than the wrong ones, full of rare letters, and the key with the highest sum is the most likely:
    ```text
    📊 Mais comuns no texto: L (6), Z (5) e H (5)
       No português, as mais comuns são A, E e O.
    🔓 Chave mais provável: 7
    O segredo da mensagem esta nas letras.
    ```
8. **The Measurement and the Table's Source:** the sum of products was chosen through a measurement with excerpts from "Dom Casmurro", by Machado de Assis (in the public domain): it found the key in 96.5% of the 20-letter excerpts, 99.1% of the 30-letter ones and 99.9% of the 50-letter ones. Assuming the most common letter of the ciphertext is A was right between 39% and 59% of the time, because A and E are close in Portuguese. Chi-squared, a common statistical method, stopped between 92% and 96%: it divides by the expected frequency, and a single rare letter, such as the K of a proper name, weighed more than the rest of the text. The 26 percentages come from table 1.2.1 of the study [Análise de Freqüências de Línguas](https://www.lockabit.coppe.ufrj.br/sites/lockabit.coppe.ufrj.br/files/publicacoes/lockabit/analise_freq.pdf) (Language Frequency Analysis, in Portuguese), by Bruno da Rocha Braga (COPPE/UFRJ, 2003), which counted 1.1 MB of texts by Brazilian authors, without accents and with Ç as C, the same treatment the program gives the text.
9. **The Short Text Notice:** with few letters, the count misleads: a short word can have more rare letters than common ones. Below 30 letters, the first length at which the most likely key was right in more than 99% of the excerpts in the measurement, the result warns and suggests checking with brute force. The notice counts only letters, because spaces, digits and punctuation do not help find the key, and `Counter`'s `total()` adds them up. The result also shows the second and third most likely keys, where the right one usually is when the first is wrong. `Ctrl+C` ends the program at any point, including the text or key prompt, with a goodbye and no stack trace.

> 💡 **Study tip:** encrypt `Bom dia` (good morning) with key 3 and break the result, `Erp gld`, through frequency: the most likely key is 11, with `Tge vas`, and the right one only shows up in second place, along with the short text notice. Then break the same text through brute force: the line for key 3 is the only one that can be read. Finally, encrypt a text with key 3 and encrypt the result with key 23: the text goes back to the original, because 3 + 23 is 26, a full turn around the alphabet.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library (`string`, `unicodedata`, `collections`, `os`, `sys`), with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the program with a single command. |
| **Terminal** | The interface where the result shows up and receives the user's choices (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/cifra_de_cesar
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer a double click? Use the shortcut:** on Windows, open `iniciar_cifra.bat`; on Linux/macOS, run `iniciar_cifra.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before opening the cipher.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the program has no external dependencies. It also detects whether you are on Windows, Linux or macOS to clear the screen the right way. To exit, choose option 5 or press `Ctrl+C` at any time.

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

1. **🔑 The Vigenère Cipher:** replace the numeric key with a keyword, where each letter of the word gives the shift of one letter of the text (with the word `cafe`, the first letter moves 2, the second 0, the third 5 and the fourth 4, and the word starts over).
   - **What you learn:** reusing `deslocar_letra` with a different key for each letter, going through the keyword in a circle with `itertools.cycle`, and seeing why the brute force over 25 keys and the count of the whole text stop working.
2. **🔢 Digits Too:** shift the digits from 0 to 9 by the same key, so that a text such as `Encontro às 19h` (meeting at 7 p.m.) does not give the time away.
   - **What you learn:** adding the 10 digits to the `str.maketrans` table, with the same remainder math, now by 10, and adjusting the test that currently checks that digits go through unchanged.
3. **📏 Chi-Squared Side by Side:** write a second score with chi-squared, which adds up `(count - expected)² / expected` letter by letter and picks the smallest sum, and compare the two with sentences that have K, W or Y.
   - **What you learn:** computing the expected count of each letter from the length of the text, comparing two methods with the same texts and understanding why a rare letter weighs so much when the math divides by a small number.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Password Strength Checker in Python](../verificador_de_forca_de_senha/README.en.md):** rules with `any()`, regular expressions and estimated entropy, the same idea of counting possibilities as brute force.
- **[Hangman Game in Python](../jogo_da_forca/README.en.md):** strings, sets and accents removed with `unicodedata`, as here.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the program, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in the repository's [CONTRIBUTING.md](../../CONTRIBUTING.md) (in Portuguese). In this project, `FREQUENCIAS` is the unmodified copy of table 1.2.1 of the COPPE/UFRJ study, and a test checks the 26 letters and the sum; changing the scoring method calls for a new measurement and a review of the 30-letter minimum of the short text notice (ADR-5 and ADR-6 of the spec); and `main.py` does not read or write files, does not use the network and takes no text from the command line, which a test checks.
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. The percentages of the letter frequency table come from the COPPE/UFRJ study cited in the Implementation Guide, with the source recorded in `main.py`. The license details are in the [LICENSE](LICENSE) file.
