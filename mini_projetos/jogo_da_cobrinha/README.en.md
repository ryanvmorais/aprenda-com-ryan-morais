![Snake Game in Python: real terminal capture with the snake moving](assets/jogo-da-cobrinha-python-terminal.svg)

# 🐍 Snake Game in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![deps](https://img.shields.io/badge/deps-uv-DE5FE9)
[![CI](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml/badge.svg)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![Lint](https://img.shields.io/badge/lint-ruff-261230)
![Format](https://img.shields.io/badge/style-black-000000)
![Types](https://img.shields.io/badge/types-mypy%20strict-2A6DB2)
![License](https://img.shields.io/badge/license-MIT-green)

This folder holds the classic **Snake Game (Jogo da Cobrinha) in Python**, designed as study material for beginner developers. The main goal is the hands-on use of **movement logic**, dynamic list handling and the `curses` library for terminal interfaces. The game's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Show the use of **data structures (lists)**, **real-time event handling** and **function modularization**. It is a practical project for students who want to understand how games based on coordinates and update cycles (*game loops*) work.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **List handling:** using `insert` and `pop` to simulate the snake's movement and the growth of its body.
- **Flow and time control:** managing the game speed and reading keys without halting execution (`timeout`).
- **Coordinate logic:** how to manage `[y, x]` positions inside a Cartesian plane limited by borders.
- **The curses library:** advanced terminal handling to create windows, borders and draw characters at specific positions.
- **Modularization:** organizing the code into functions with single responsibilities (S.O.L.I.D. for beginners).

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this game:

1. **Dynamic body modeling:** the snake is not a single object but a **list of coordinates** `[[y, x], [y, x]]`. The "head" is always the first item (index `0`), and the rest of the list forms the trail we call the body.
2. **The math of movement:** instead of "pushing" each segment of the snake, we use a logic trick: on every turn, we compute and insert a **new head** in the chosen direction. If the snake eats nothing, we remove the last item of the list (the tail). This constant swap creates the illusion of movement.
3. **Collision detection:** the system watches the head's coordinate in real time. If it equals the border limits (`y <= 0` or `x >= width`) or matches any coordinate already in the body list, the game detects the impact and ends the match.
4. **Ecosystem and feeding:** we use the `random` library to draw positions for the fruit. When the head occupies the same position as the fruit, the system increments the score and **does not remove the tail** on that turn, so the snake grows naturally.
5. **Preventing opposite movement:** to avoid "logical suicide", we implement a lock that keeps the snake from turning 180° instantly (e.g. trying to go up when it is already going down). The command is only accepted if it is a side turn.
6. **The heart of the game (game loop):** a `while True` loop coordinates the game's time. It clears the screen, draws the actors (`ASCII` characters), reads the keyboard input and waits a few milliseconds before repeating everything, so the game does not run too fast for the human eye.
7. **Abstraction with functions:** the code is split into specialist functions (such as `mover_cobra` and `verificar_colisoes`), which makes maintenance easier and lets you understand the role of each piece in how the whole system works.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. |
| **curses** | Python standard library for drawing windows, borders and characters at specific terminal positions. On Windows, it comes from the `windows-curses` package. |
| **uv** | Dependency and virtual environment manager: creates the environment, installs `windows-curses` on Windows and runs the game with a single command. |
| **Terminal** | The interface where the game runs and receives the player's keys (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/jogo_da_cobrinha
    ```
2.  **Run the game:** in the system terminal (Command Prompt or PowerShell), inside the project folder, for a better visual experience. `uv` creates the virtual environment and installs `windows-curses` on Windows by itself.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_jogo.bat`; on Linux/macOS, run `iniciar_jogo.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before starting the match.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same. On Windows, first install `windows-curses` with `pip install windows-curses`; on Linux/macOS, `curses` already ships with Python.

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

1. **🏆 High Score System:** today the score resets every time the program closes. Create a "permanent memory": on start, the game reads the `recorde.txt` file; if the match score beats the value read, overwrite the file with the new high score before exiting.
   - **What you learn:** handling files (`open`, `read`, `write`) to save data on the computer (`HD/SSD`) and make the high score persist even after the machine is turned off.
2. **🍎 Special Fruits:** create a "golden" fruit that rarely appears and gives 5 points at once.
   - **What you learn:** using the `random` module for rare events (probability) and giving one type of item its own rule without duplicating the collision logic.
3. **🔳 Walking Through Walls:** change the collision logic so that, when hitting the right border, the snake reappears on the left border.
   - **What you learn:** working with coordinate limits (for example, with the `%` operator) and seeing how a game rule becomes a condition in the code.

---

### 🧭 Keep practicing:

This project is part of a Python study trail. After this one, the next step is to leave the terminal and build web applications with Django:

- **[Dynamic Portfolio with Django](https://github.com/ryanvmorais/django-fullstack-portfolio):** advanced security (honeypot, rate limit, CSP) and query optimization.
- **[Culinary Blog in Django](https://github.com/ryanvmorais/django-blog-culinario):** domain modeling, authentication, admin and security.

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
