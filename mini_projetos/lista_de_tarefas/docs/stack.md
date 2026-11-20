# A stack, e por quê

Cada tecnologia que sustenta a Lista de Tarefas: o que faz, por que foi
escolhida contra a alternativa, e os conceitos que valem a pena estudar
primeiro se forem novos para você.

Não é exaustivo — o grafo completo de versões do grupo de desenvolvimento está
travado no `uv.lock`. Este doc é o mapa: a *forma* do projeto e o raciocínio
por trás de cada peça.

O projeto é um único programa: um script de terminal, sem dependências de
runtime (só a biblioteca padrão do Python), com um grupo de ferramentas de
qualidade por fora. O único estado que sobrevive entre uma execução e outra é
o `tarefas.json`, ao lado do `main.py`.

```
main.py  ──►  biblioteca padrão do Python (json, pathlib, datetime, os, sys, typing,
   │          collections.abc)
   └──►  tarefas.json (UTF-8, fora do Git)
```

---

## Linguagem e empacotamento

### Python 3.12+

A única linguagem do projeto. 3.12 é o piso (`requires-python`): já tem a
sintaxe moderna de tipos (`X | None`, `list[Tarefa]`) e a instrução `type`
(PEP 695), usada nos apelidos `Leitor` e `Relogio`.

**Por que esta:** o projeto é puramente didático (arquivo, lista de
dicionários, laço de menu, validação de entrada) — qualquer linguagem serviria,
mas Python tem a sintaxe mais direta para quem está aprendendo esses conceitos,
e a biblioteca padrão já traz o `json` e o `pathlib`.

**Estudar:** `json.dumps` e `json.loads` (com `ensure_ascii` e `indent`),
`pathlib.Path` (`/`, `__file__`, `read_text`, `write_text`, `exists`,
`with_name`, `rename`, `replace`), `encoding="utf-8"`, a hierarquia de exceções
(`JSONDecodeError` e `UnicodeDecodeError` herdam de `ValueError`), `isinstance`,
`datetime` e `date.fromisoformat`, `strftime`, `str.isdecimal` contra
`str.isdigit`, `enumerate(..., start=1)`, `typing.TypedDict`,
`typing.NamedTuple`, funções como parâmetro (`Callable`), a instrução `type`,
`if __name__ == "__main__"`.

### uv

O gerenciador de pacotes e ambientes virtuais do Python (da Astral, o time do
Ruff). Substitui `pip` + `venv` manual. `uv sync` instala o grupo de
desenvolvimento a partir do `uv.lock`; `uv run <comando>` executa dentro do
ambiente sem precisar ativá-lo.

**Por que esta:** o projeto não tem dependência de runtime (só stdlib), mas as
ferramentas de qualidade (ruff, black, mypy, pytest) precisam de um ambiente
isolado e reprodutível. `uv` é uma ordem de magnitude mais rápido que
`pip`/`venv`, usa o `pyproject.toml` padrão (PEP 621) e gera um lockfile real
(`uv.lock`) — hoje o fluxo padrão em projetos Python novos.

**Estudar:** `uv sync`, `uv run <comando>`, `uv add --dev <pacote>`, `uv lock`,
a diferença entre `[project.dependencies]` (runtime, vazio aqui) e
`[dependency-groups] dev` (ferramentas).

---

## Ferramentas de qualidade

### Ruff

O linter — substitui Flake8 + isort + pyupgrade num binário só, quase
instantâneo. Aqui verifica erros óbvios (`F`), estilo `pycodestyle` (`E`/`W`),
ordena imports (`I`) e sugere sintaxe moderna (`UP`).

**Por que esta:** é um dos linters Python mais usados hoje; um só
comando (`ruff check .`) substitui o que antes precisava de 3-4 ferramentas
separadas.

**Estudar:** `uv run ruff check .`, `uv run ruff check --fix .` (corrige o que
for seguro), a tabela `select` no `pyproject.toml` (cada letra é uma família
de regra).

### Black

O formatador — sem configuração para discutir (mesma filosofia do `gofmt`).
Reescreve o arquivo no estilo canônico do Black; ninguém revisa espaçamento em
code review.

**Por que esta:** padrão de-facto do ecossistema Python; usado em larga escala.

**Estudar:** `uv run black .` (reformata), `uv run black --check .` (só
verifica, usado no CI).

### Mypy

O verificador de tipos estáticos, em modo `strict`. Lê as anotações de tipo
(`-> None`, `list[Tarefa]`, `int | None`) e garante que elas sejam
consistentes antes mesmo de rodar o código. Aqui ele também confere o
`TypedDict`: uma chave com o nome errado (`tarefa["concluido"]`) vira erro de
tipo, e não um `KeyError` em produção.

**Por que esta:** o projeto é pequeno, mas tipar tudo desde o início é uma boa
prática — evita o hábito de "só ligo o mypy quando o projeto crescer" (nunca
liga).

**Estudar:** sintaxe `X | None` / `list[X]` (não `Optional`/`List`),
`TypedDict`, `-> None` explícito em função que não retorna nada, `uv run mypy`.

### pytest

O executor de testes. `tests/test_main.py` cobre a lógica do programa (a forma
do arquivo, a primeira execução, o arquivo corrompido e a cópia dele, a
gravação atômica, a formatação das linhas, a validação das entradas, as quatro
ações e a sessão completa com a saída por Ctrl+C) sem depender de um terminal
real nem da sua lista.

**Por que esta:** padrão de-facto de testes em Python. Como o teclado, o
relógio e o caminho do arquivo entram por parâmetro, os testes passam um leitor
e um relógio falsos e um arquivo dentro do `tmp_path`, a pasta vazia que o
pytest cria para cada teste, sem `monkeypatch` em `input` ou `datetime`. O
único `monkeypatch` da suíte troca a limpeza de tela, para os testes não
chamarem `os.system`.

**Estudar:** `tmp_path` (uma pasta temporária por teste), `@pytest.fixture`
(inclusive `autouse=True`), `@pytest.mark.parametrize` (testar várias entradas
sem repetir código), uma classe com `__call__` como função falsa, `capsys`
(capturar o que foi impresso no terminal), `pytest.raises`.

---

## Automação no GitHub

Tudo roda em `ubuntu-26.04` (rótulo fixo, nunca `ubuntu-latest`) e as Actions
ficam fixadas pelo SHA do commit, com a versão no comentário: uma tag pode ser
movida depois de publicada, o SHA não.

### GitHub Actions (CI)

Roda o mesmo portão que você roda local — `ruff` → `black --check` → `mypy` →
`pytest` — em todo push na `main` e em todo PR, numa matriz de Python 3.12 (o
piso), 3.14 e 3.15. Um check verde no PR significa o mesmo que um clone limpo
passando.

**Por que esta:** o repositório já está no GitHub e o CI é grátis para repo
público; a matriz testa o piso de verdade, em vez de só declarar `>=3.12`.

**Estudar:** `on:` (gatilhos), `strategy.matrix`, `permissions: contents: read`
(o mínimo necessário), fixar `uses:` por SHA.

### CodeQL

Análise estática de segurança (code scanning) do código Python, em push/PR na
`main` e uma vez por semana (domingo) para pegar consultas novas sem mudança no
repositório.

**Por que esta:** é o scanner nativo do GitHub e grátis para repo público. Roda
como workflow do repositório, não como o "default setup", porque o default usa
um rótulo de runner que o repo não controla e seus runs não podem ser
re-executados.

**Estudar:** `github/codeql-action` (`init` + `analyze`), `build-mode: none`
(Python não precisa de build), a aba Security → Code scanning.

### Dependabot

Abre PRs de atualização de `uv` e de `github-actions` aos domingos, um PR
agrupado por ecossistema (minor e patch juntos; major em PR próprio). Uma versão
nova espera 7 dias (`cooldown`) antes de virar PR.

**Por que esta:** é integrado ao GitHub e entende o `uv.lock`. O cooldown evita
adotar uma release que quebrou no dia da publicação.

**Estudar:** `../../.github/dependabot.yml` (`groups`, `cooldown`, `schedule`), e como
revisar um PR de bump (changelog, CI verde).

### pip-audit (semanal)

Toda segunda, 09:00 de São Paulo, exporta o `uv.lock` e procura CVEs conhecidas
nas dependências travadas. Run vermelho = vulnerabilidade no lock.

**Por que esta:** o CI só roda em PR e o Dependabot nem sempre abre PR de
correção; sem esta auditoria, uma CVE nova passaria despercebida até o PR
seguinte. Roda via `uvx`, sem ser dependência do projeto.

**Estudar:** `uv export` (lock → requirements), `uvx` (rodar ferramenta sem
instalar), `--no-deps` (auditar exatamente o conjunto travado).

---

## Peças menores

| Peça | Papel |
|---|---|
| `json` (stdlib) | converte a lista em texto (`dumps`, com `ensure_ascii=False` e `indent=2`) e o texto de volta em lista (`loads`) |
| `pathlib.Path` (stdlib) | monta o caminho ao lado do `main.py` (`Path(__file__).parent`), lê e grava em UTF-8 e troca os arquivos (`rename`, `replace`) |
| `datetime` (stdlib) | a data de criação de cada tarefa (`isoformat` no arquivo, `strftime("%d/%m/%Y")` na tela) e o carimbo do nome da cópia do corrompido |
| `typing.TypedDict` (stdlib) | declara as chaves de cada tarefa sem deixar de ser um `dict`, que o `json` grava como está |
| `typing.NamedTuple` (stdlib) | dá nome aos dois campos da conferência da entrada (`conferencia.valor` e `conferencia.recusa`) |
| `collections.abc.Callable` (stdlib) | tipa o leitor do teclado e o relógio que `main` recebe por parâmetro |
| `os.system` (stdlib) | limpa o terminal (`cls` no Windows, `clear` no Unix/Mac) |
| `sys.stdout.reconfigure` (stdlib) | força UTF-8 na saída, evitando `UnicodeEncodeError` com stdout redirecionado no Windows |

---

## O que deliberadamente não está na stack

- **Qualquer dependência de runtime** — o programa inteiro cabe na biblioteca
  padrão; adicionar uma lib externa só para isso seria peso sem ganho
  pedagógico.
- **Um banco de dados (SQLite)** — o `sqlite3` também está na biblioteca
  padrão, mas a lista cabe inteira na memória e um arquivo JSON se abre num
  editor qualquer; ver o arquivo que o programa grava é parte do que o projeto
  ensina.
- **Um framework de CLI (Typer/Click)** — o menu é numerado e lido com
  `input()`; argumentos de linha de comando seriam outro jeito de usar o
  programa, não o assunto deste projeto.
- **`os.fsync` na gravação** — o `Path.replace` já garante que o arquivo é a
  lista antiga inteira ou a nova inteira quando o programa cai; forçar o disco
  a gravar na hora só protegeria contra a queda de energia do computador, um
  detalhe de sistema operacional que foge do escopo de um exercício.
- **`subprocess`** — a limpeza de tela usa `os.system(comando)` com uma string
  fixa (`"cls"`/`"clear"`, nunca entrada do usuário); `subprocess.run(...,
  shell=True)` faria o mesmo com mais código e é o padrão que ferramentas de
  segurança sinalizam por hábito (mesmo sem risco real aqui).
