# A stack, e por quê

Cada tecnologia que sustenta o Adivinhe o Número: o que faz, por que foi
escolhida contra a alternativa, e os conceitos que valem a pena estudar
primeiro se forem novos para você.

Não é exaustivo — o grafo completo de versões do grupo de desenvolvimento está
travado no `uv.lock`. Este doc é o mapa: a *forma* do projeto e o raciocínio
por trás de cada peça.

O projeto é um único programa: um script de terminal, sem dependências de
runtime (só a biblioteca padrão do Python), com um grupo de ferramentas de
qualidade por fora.

```
main.py  ──►  biblioteca padrão do Python (random, os, sys, typing, collections.abc)
```

---

## Linguagem e empacotamento

### Python 3.12+

A única linguagem do projeto. 3.12 é o piso (`requires-python`): já tem a
sintaxe moderna de tipos (`X | None`, `dict[str, int]`) e a instrução `type`
(PEP 695), usada nos apelidos `Leitor` e `Sorteador`.

**Por que esta:** o projeto é puramente didático (sorteio, laço, validação de
entrada) — qualquer linguagem serviria, mas Python tem a sintaxe mais direta
para quem está aprendendo esses conceitos por trás de um jogo de terminal.

**Estudar:** `random.randint` (os dois extremos incluídos), `while` com
condição de parada e `return` de dentro do laço, `int()` com `try`/`except
ValueError`, `typing.NamedTuple`, funções como parâmetro (`Callable`), a
instrução `type`, `if __name__ == "__main__"`.

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
(`-> None`, `list[str]`, `str | None`) e garante que elas sejam consistentes
antes mesmo de rodar o código.

**Por que esta:** o projeto é pequeno, mas tipar tudo desde o início é uma boa
prática — evita o hábito de "só ligo o mypy quando o projeto crescer" (nunca
liga).

**Estudar:** sintaxe `X | None` / `list[X]` (não `Optional`/`List`),
`-> None` explícito em método que não retorna nada, `uv run mypy`.

### pytest

O executor de testes. `tests/test_main.py` cobre a lógica do jogo (menu de
níveis, validação dos palpites, partida, recordes, "jogar de novo" e a saída
com Ctrl+C) sem depender de um terminal real.

**Por que esta:** padrão de-facto de testes em Python. Como o teclado e o
sorteio entram por parâmetro, os testes passam um leitor e um sorteador falsos
e escolhem o número secreto e o que foi "digitado", sem `monkeypatch` em
`input` ou `random`. O único `monkeypatch` da suíte troca a limpeza de tela,
para os testes não chamarem `os.system`.

**Estudar:** `@pytest.fixture` (inclusive `autouse=True`),
`@pytest.mark.parametrize` (testar várias entradas sem repetir código), uma
classe com `__call__` como função falsa, `capsys` (capturar o que foi impresso
no terminal), `pytest.raises`.

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
| `random.randint` (stdlib) | sorteia o número secreto na faixa do nível, com os dois extremos incluídos |
| `typing.NamedTuple` (stdlib) | dá nome a cada campo de um nível (`nivel.maximo` em vez de `nivel[2]`) |
| `collections.abc.Callable` (stdlib) | tipa o leitor do teclado e o sorteador que as funções recebem por parâmetro |
| `os.system` (stdlib) | limpa o terminal (`cls` no Windows, `clear` no Unix/Mac) |
| `sys.stdout.reconfigure` (stdlib) | força UTF-8 na saída, evitando `UnicodeEncodeError` com stdout redirecionado no Windows |

---

## O que deliberadamente não está na stack

- **Qualquer dependência de runtime** — o jogo inteiro cabe na biblioteca
  padrão; adicionar uma lib externa só para isso seria peso sem ganho
  pedagógico.
- **Um framework de CLI (Typer/Click)** — o jogo faz três perguntas (nível,
  palpite e "jogar de novo"); `input()` puro já ensina o conceito sem
  introduzir uma dependência nova.
- **Arquivo de recordes** — os recordes ficam num dicionário e valem só
  enquanto o jogo está aberto; gravar em disco traria leitura e escrita de
  arquivo, que não é o assunto deste projeto.
- **`subprocess`** — a limpeza de tela usa `os.system(comando)` com uma string
  fixa (`"cls"`/`"clear"`, nunca entrada do usuário); `subprocess.run(...,
  shell=True)` faria o mesmo com mais código e é o padrão que ferramentas de
  segurança sinalizam por hábito (mesmo sem risco real aqui).
