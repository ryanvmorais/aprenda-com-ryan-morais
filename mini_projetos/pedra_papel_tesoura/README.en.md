![Rock, Paper, Scissors in Python: real terminal capture with the scoreboard and the round result](assets/pedra-papel-tesoura-python-terminal.svg)

# ✂️ Rock, Paper, Scissors in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![deps](https://img.shields.io/badge/deps-uv-DE5FE9)
[![CI](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml/badge.svg)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![Lint](https://img.shields.io/badge/lint-ruff-261230)
![Format](https://img.shields.io/badge/style-black-000000)
![Types](https://img.shields.io/badge/types-mypy%20strict-2A6DB2)
![License](https://img.shields.io/badge/license-MIT-green)

This folder holds the classic **Rock, Paper, Scissors game (Jokenpô) in Python**, designed as study material for beginner developers. The main goal is the hands-on use of **programming fundamentals** and of dictionaries to map business rules in the terminal. The game's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Show the use of **loops**, **collection handling (lists and dictionaries)** and **Object-Oriented Programming (OOP)** in Python. It is a practical project for students who want to understand how to turn real-world rules into efficient algorithms.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **Loops:** controlling the continuous flow of rounds (`while` loop).
- **Dictionaries (mapping):** how to replace many `if/else` statements with a logical win mapping (`key` beats `value`).
- **Error handling:** using `try/except` blocks to validate the user's numeric input.
- **OOP (Object-Oriented Programming):** organizing modular code through the `PedraPapelTesoura` class and using `self`.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this game:

1. **Making the choice easy (lists and indexes):** instead of asking the user to type "pedra" (and risk a mistyped letter breaking the code), we use a list: `['pedra', 'papel', 'tesoura']`. The user only types a number (0, 1 or 2). Python understands that 0 is Rock, 1 is Paper and 2 is Scissors. This avoids errors and makes the game faster.
2. **The dictionary "trick" (win rules):** you know that pile of `if` and `else` we usually write? Here we use a **dictionary**. It works like a table: we say that Rock beats Scissors, Paper beats Rock, and so on. The code only needs to look at this "table" to know who won. It is much cleaner and easier to read!
3. **Organizing the house (classes and that `self` thing):** we use a **class** called `PedraPapelTesoura`. Think of it as a box that holds everything the game needs: the score, the rules and the moves. `self` lets the game know it is changing its *own* score and not something outside. This avoids the mess of variables scattered around the code.
4. **The heart of the game (game loop):** the game runs inside a *loop* that does not stop until you ask. It always follows this order: `clear the screen` -> `ask for your move` -> `draw the computer's move` -> `show who won` -> `ask if you want to play again`. That is how almost every game works!
5. **Talking to your computer:** we use a special command (`os.system`) to talk to the operating system (`Windows`, `Mac` or `Linux`). It finds out which system you use and clears the terminal screen automatically, making the game look much nicer and tidier.
6. **Protection against errors (try/except):** what if the game asks for a number and the user types a letter? Normally the program would close with an ugly error. Here we use `try/except`, which "tries" to do something and, if it fails, politely warns the user instead of crashing everything.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The game uses only the standard library, with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the game with a single command. |
| **Terminal** | The interface where the game runs and receives the user's moves (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/pedra_papel_tesoura
    ```
2.  **Run the game:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_jogo.bat`; on Linux/macOS, run `iniciar_jogo.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before starting the match.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the game has no external dependencies. The game also detects whether you are on Windows, Linux or macOS to clear the screen the right way.

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

For the map of each technology in the stack (what it is, why it was chosen, what to study), see [docs/stack.md](docs/stack.md). For the expected behavior of the game and the history of decisions, see [specs/](specs/). For architecture and conventions in detail, see [CLAUDE.md](CLAUDE.md). These three are in Portuguese.

---

### 📋 Practice activities (Evolution Challenges):

To exercise what you learned, try changing the code and implementing these new features:

1. **🏆 Running Scoreboard:** create a counter that does not reset when a match restarts. Add control variables (e.g. `pontos_usuario` and `pontos_computador`) inside the class's `__init__` method and make sure that, when the move loop restarts, they persist and are shown on the scoreboard every new turn.
   - **What you learn:** telling variables that control the **current round** apart from those that control the **user's global history**, keeping data consistent in applications with several execution cycles (game loops).
2. **🤖 "Best of 3" Mode:** make the game end and declare a Grand Champion as soon as the user or the computer reaches 2 wins.
   - **What you learn:** using the state stored in the object (`self`) to decide when the loop ends, instead of relying only on the "play again?" answer.
3. **⏲️ Suspense Effect:** use the `time` module and the `time.sleep(1)` function to show "Pedra...", "Papel..." and "Tesoura!" with pauses before revealing the machine's move.
   - **What you learn:** importing a standard library module and controlling the pace of the interaction in the terminal.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Tic Tac Toe in Python](../jogo_da_velha/README.en.md):** matrices and Object-Oriented Programming.
- **[Snake Game in Python](../jogo_da_cobrinha/README.en.md):** dynamic lists and a game loop with `curses`.

See all the channel's projects and videos at [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Any questions or suggestions?

Learning something new has its challenges, but I'm here to walk the path with you! If you found a mistake, had trouble running the game, or thought of an improvement that would make this material even more instructive:

- **Open an [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** describe your question or suggestion. It is the best way for us to exchange knowledge and help other people who have the same question.
- **Contribute code:** want to propose an improvement? See the step-by-step guide in [CONTRIBUTING.md](CONTRIBUTING.md) (in Portuguese).
- **Email me:** if you prefer something more private, write to [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

I will be very happy to see your progress and get your feedback so we can keep improving our study materials! 🤝

---

### ⚖️ License

This project is under the **MIT License**. That means you can use, copy and modify the code freely, including in your own projects. For more details, see the [LICENSE](LICENSE) file.
