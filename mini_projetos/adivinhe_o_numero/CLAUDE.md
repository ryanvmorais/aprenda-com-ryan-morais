# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Jogo Adivinhe o Número em Python, via terminal — material de estudo para
prática do sorteio com `random`, do laço `while` e da validação da entrada com
`int()` dentro de `try`/`except`. Um único arquivo (`main.py`), sem dependência
de runtime (só a biblioteca padrão). Projeto educacional, público no GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o jogo
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_ler_palpite_aceita_inteiro_na_faixa -v

# Lint, formatação e tipos (nesta ordem)
uv run ruff check .          # lint (substitui flake8 + isort)
uv run ruff check --fix .    # corrige automaticamente o que for seguro
uv run black .               # formatação
uv run mypy                  # tipos (arquivos em [tool.mypy] files)

# Gerenciar dependências de desenvolvimento (não há dependências de runtime)
uv add --dev <pacote>
uv remove --dev <pacote>
uv lock --upgrade-package <pacote>
```

## Arquitetura

```
main.py              # funções do jogo + main() (ponto de entrada)
tests/test_main.py   # suíte pytest (45 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md         # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py    # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-adivinhe-o-numero/
iniciar_jogo.bat      # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_jogo.sh       # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
.gitattributes        # LF fixo nos atalhos .sh (com CRLF o shebang quebra no Linux/macOS)
assets/               # adivinhe-o-numero-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT
../../CONTRIBUTING.md # com CODE_OF_CONDUCT.md e SECURITY.md: valem para o repositório inteiro, na raiz
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: o estado da sessão (o dicionário de recordes) vive em `main()`.
Os níveis ficam na constante `NIVEIS` (`dict[str, Nivel]`, com a tecla do menu
como chave; `Nivel` é uma `NamedTuple` com faixa e limite). Uma função por
responsabilidade — `limpar_tela`, `escolher_nivel`, `ler_palpite` (`int()` em
`try`/`except` e conferência da faixa), `jogar_partida` (sorteio e laço
`while`), `atualizar_recorde`, `exibir_recordes` e `perguntar_jogar_de_novo`.
`main()` orquestra as partidas e trata `KeyboardInterrupt`/`EOFError` num só
lugar. O teclado (`ler`, tipo `Leitor`) e o sorteio (`sortear`, tipo
`Sorteador`) entram por parâmetro, com `input` e `random.randint` como padrão:
os testes passam versões falsas em vez de `monkeypatch`. Detalhamento completo
(RF-NN, ADRs) em
[`specs/001-adivinhe-o-numero/`](specs/001-adivinhe-o-numero/requirements.md).

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem, termos técnicos universais (`int`, `str`,
  `bool`).
- **Estilo de código:** docstrings em português nas funções, classes e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **README bilíngue:** o português fica em `README.md` e o inglês em
  `README.en.md`, com as mesmas seções na mesma ordem. Mudou um, muda o outro
  no mesmo PR; o `tests/test_readme_en.py` pega o desalinhamento de estrutura.

## Qualidade e automação

Sequência do portão, sempre nesta ordem: `ruff check .` → `black --check .`
→ `mypy` → `pytest`. O `../../.github/workflows/ci.yml` roda exatamente essa
sequência (Python 3.12, o piso, 3.14 e 3.15) em todo push na `main` e em todo PR — um
check verde no PR significa o mesmo que um clone limpo passando.

Sem hooks de `.claude/` neste projeto (repositório pequeno demais para
justificar automação por evento); rode o portão manualmente antes de
commitar.

## Spec-driven development

Specs em `specs/NNN-nome/` (`requirements.md` → `design.md` → `tasks.md`),
com aprovação de cada fase antes da seguinte. A spec `001-adivinhe-o-numero`
foi escrita **antes do código** (concepção), no formato da spec
`001-jogo-pedra-papel-tesoura` do `pedra_papel_tesoura` — ver
[`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_jogo.bat`/`.sh` preferem `uv run main.py`, mas caem
> para `python`/`python3 main.py` puro se o `uv` não estiver instalado — é
> assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o jogo.
