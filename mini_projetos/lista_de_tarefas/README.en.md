![To-Do List in Python: animation of a session that opens the list saved on previous days, adds "Comprar pão" (buy bread) with today's date, rejects the number 7 in a three-task list, completes "Estudar pathlib" (study pathlib) and removes "Revisar o README" (review the README) after confirming, until it quits](assets/lista-de-tarefas-python-terminal-sessao.svg)

# 📝 To-Do List in Python | Programming Logic Exercise

**English** · [Português (Brasil)](README.md)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Run it now:** with [uv](https://docs.astral.sh/uv/) installed, clone the repository and, inside `mini_projetos/lista_de_tarefas`, run `uv run main.py`.

This folder holds the **To-Do List in Python** (Lista de Tarefas), designed as study material for beginner developers. You add, complete, edit and remove tasks in a terminal menu, and the list is still there when you close the program and open it again, because every change is saved to a JSON file. The main goal is the hands-on use of **programming fundamentals**: reading and writing a file, keeping the data in a list of dictionaries and handling what can go wrong with the file. The program's on-screen text is in Brazilian Portuguese, and so are the identifiers in the code.

### 🎯 Project goal:

Show the use of **JSON files**, **paths with `pathlib`** and **atomic writes** in Python. It is a practical project for students who want to understand how a program keeps what the user did between one run and the next, without losing the list when the file goes missing, gets corrupted or the program crashes in the middle of a write.

---

### 📚 What will you learn from this project?

This exercise was designed to consolidate essential algorithm concepts:

- **JSON files (`json`):** `json.dumps` turns the list into text and `json.loads` goes the other way; with `ensure_ascii=False` and `indent=2`, the file is readable in an editor, with accents written as letters.
- **Paths with `pathlib`:** `Path(__file__).parent / "tarefas.json"` builds the file's path with each system's separator, and `read_text`, `write_text`, `exists`, `rename` and `replace` do the rest, always with `encoding="utf-8"`.
- **List of dictionaries:** each task is a dictionary with the text, the status and the creation date, and the whole list is the program's "database". The `TypedDict` tells `mypy` which keys each task has.
- **Error handling:** a single `except ValueError` catches the invalid JSON, the file that is not UTF-8 and the list with the wrong shape, because the three errors belong to the same family.
- **Atomic writes:** the text first goes to a temporary file, which then replaces the real file in a single operation.
- **Cross-platform OS interaction:** using `os.system` to detect the operating system (`cls` on Windows or `clear` on Unix/Mac) and keep the terminal interface clean and professional.

---

### 🧠 Implementation Guide (The Logic behind the Code):

For beginners, the biggest challenge is not the syntax but **building the reasoning**. Here is the step-by-step construction of this program:

1. **The task (typed dictionary):** each task is a dictionary with three keys: `texto` (what to do, from 1 to 80 characters), `concluida` (`False` for pending, `True` for completed) and `criada_em` (the creation date). The task list is a plain `list`, and the number shown on screen is the position in the list plus 1.
2. **Where the file lives (`pathlib`):** the list is saved to `tarefas.json`, in the same folder as `main.py`. The path comes from `Path(__file__).parent`, not from `Path("tarefas.json")`: with the relative path, running the program from another folder would create a second, empty list. `tarefas.json` is in `.gitignore`, so your list never ends up in a commit.
3. **The file format (JSON):** a list at the top, one object per task, with the date in ISO 8601 (`YYYY-MM-DD`), which the screen shows as `20/11/2026` (day first, as in Brazil):
    ```json
    [
      {
        "texto": "Comprar pão",
        "concluida": false,
        "criada_em": "2026-11-20"
      }
    ]
    ```
4. **First run and corrupted file:** if the file does not exist, the list starts empty, and the file is only created on the first change. If it exists but is not a task list (invalid JSON, another encoding, one key too many or too few), the program deletes nothing: it renames the file to a copy with the date and time in its name, such as `tarefas.corrompido-20261120-153000.json`, warns about it on the first screen and starts with an empty list. The copy stays there for you to open and recover what you can.
5. **Why the write is atomic:** `write_text` empties the file before writing. If the program crashed in between, the list would be cut in half. That is why the text first goes to `tarefas.json.tmp`, in the same folder, and `Path.replace` swaps one file for the other in a single operation: `tarefas.json` is always the whole old list or the whole new one, never a piece.
6. **The heart of the program (`while` loop):** the menu runs until you choose Quit (Sair). Each turn always follows this order: `clear the screen` -> `show the list, the count and the menu` -> `read the option` -> `perform the action` -> `save the file`. Since every action saves right after changing the list, a `Ctrl+C` or a closed terminal loses nothing.
7. **Protection against errors (validated input):** what if the user types "7" in a three-task list, "abc" in the menu or an empty text? The `conferir_*` functions reject it and explain why, and the program asks again without clearing the screen. Notice the `isdecimal()` before `int()`: `isdigit()` would accept "²", which `int()` rejects with an error. Removing is the only action that deletes saved data, so it asks first (`s`/`n`, for yes/no).
8. **Keyboard, clock and file as parameters:** `main` receives what reads the keyboard (`ler`), what gives the date and time (`agora`) and the file's path, with `input`, `datetime.now` and `tarefas.json` as the defaults. Users notice no difference, but the tests pass a fake keyboard, a fake clock and a temporary folder, and never touch your list.

> 💡 **Study tip:** after adding a few tasks, open `tarefas.json` in a text editor. Change a `false` to `true`, save and open the program: the task shows up as completed. Now delete a comma and open it again, to see the corrupted-file warning and the copy it leaves behind.

---

### 🛠️ Technologies and Tools:

To give you the best learning experience, the project uses the following technologies:

| Tool | Description |
| :--- | :--- |
| **Python 3.12+** | The project's main language. The program uses only the standard library (`json`, `pathlib`, `datetime`), with no external dependencies. |
| **uv** | Dependency and virtual environment manager: creates the environment and runs the program with a single command. |
| **Terminal** | The interface where the list shows up and receives the user's choices (CMD, PowerShell or the VS Code/PyCharm terminal). |

The quality tools (Ruff, Black, Mypy and Pytest) are in [Quality and tests](#quality-and-tests). For the reasoning behind each choice, see [docs/stack.md](docs/stack.md) (in Portuguese).

---

### ⚙️ How to run the project locally:

**Prerequisites:** [Python 3.12+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/). To check, run `python --version` and `uv --version`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/lista_de_tarefas
    ```
2.  **Run the program:** in the terminal (CMD, PowerShell or the VS Code/PyCharm one), inside the project folder. `uv` creates the virtual environment by itself on the first run.
    ```bash
    uv run main.py
    ```
3.  **Prefer two clicks? Use the shortcut:** on Windows, open `iniciar_lista.bat`; on Linux/macOS, run `iniciar_lista.sh` in the terminal. The scripts detect whether you have `uv` (preferred) or `python`/`python3` installed before opening the list.

> ⚠️ **Note:** without `uv`, `python main.py` works just the same, because the program has no external dependencies. It also detects whether you are on Windows, Linux or macOS to clear the screen the right way. To quit, choose option 5 or press `Ctrl+C` at any moment: what you already did is saved.

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

1. **🔎 Filter the List:** add an option that shows only the pending tasks or only the completed ones, keeping each task's number the same as in the full list.
   - **What you learn:** numbering with `enumerate` before filtering, so the number does not change, and building the filtered list with a list comprehension.
2. **📅 Task Deadline:** let a task have an optional deadline, shown next to the text, without the lists saved before the change being treated as corrupted.
   - **What you learn:** evolving a file format without breaking the old files: accepting the new key as optional in `validar_tarefas` and reading it with `tarefa.get("prazo")`.
3. **↕️ Pending First:** add an option that reorders the list, with the pending tasks before the completed ones and the creation order kept inside each group.
   - **What you learn:** `list.sort(key=...)` with a `bool` key (`False` comes before `True`) and Python's stable sort, which does not shuffle equal items.

---

### 🧭 Keep practicing:

This project is part of a trail of programming logic exercises in Python. After this one, try:

- **[Hangman in Python](../jogo_da_forca/README.en.md):** strings, sets and accents with `unicodedata`.
- **[Snake Game in Python](../jogo_da_cobrinha/README.en.md):** dynamic lists and a game loop with the `curses` library.

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
