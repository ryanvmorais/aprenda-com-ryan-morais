# A stack, e por quê

Cada tecnologia que sustenta o Verificador de Força de Senha: o que faz, por
que foi escolhida contra a alternativa, e os conceitos que valem a pena estudar
primeiro se forem novos para você.

Não é exaustivo — o grafo completo de versões do grupo de desenvolvimento está
travado no `uv.lock`. Este doc é o mapa: a *forma* do projeto e o raciocínio
por trás de cada peça.

O projeto é um único programa: um script de terminal, sem dependências de
runtime (só a biblioteca padrão do Python), com um grupo de ferramentas de
qualidade por fora. Nada sobrevive entre uma execução e outra: o programa não
grava arquivo nem usa rede, o único arquivo que ele lê é a lista de senhas
comuns, e a senha digitada só existe na memória durante a verificação.

```
main.py  ──►  biblioteca padrão do Python (getpass, re, string, math,
   │          pathlib, os, sys, collections.abc, typing)
   └──►  senhas_comuns.txt (lista portuguesa do SecLists, lida uma vez)
```

---

## Linguagem e empacotamento

### Python 3.12+

A única linguagem do projeto. 3.12 é o piso (`requires-python`): já tem a
sintaxe moderna de tipos (`X | None`, `list[str]`) e a instrução `type`
(PEP 695), usada no apelido `Leitor`.

**Por que esta:** o projeto é puramente didático (regras, uma conta, laço de
menu) — qualquer linguagem serviria, mas Python traz na biblioteca padrão a
leitura sem eco (`getpass`), as expressões regulares (`re`), os alfabetos
prontos (`string`) e o logaritmo (`math.log2`), e cada regra de tipo de
caractere cabe numa linha com `any`.

**Estudar:** `any` com generator expressions, `str.islower`, `str.isupper` e
`str.isdigit`, as expressões regulares (grupos, a referência `\1`, os
quantificadores `{2,}`, `re.IGNORECASE`, `re.finditer` e `Match.span`), o
operador `in` entre strings, o fatiamento `[::-1]`, `getpass.getpass`,
`typing.NamedTuple`, `set` para busca rápida, `math.log2` e `math.ceil`,
`pathlib.Path` e `Path(__file__).parent`, f-strings com formatação (`:.1f`),
`enumerate(..., start=1)`, funções como parâmetro (`Callable`), a instrução
`type`, `if __name__ == "__main__"`.

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
(`-> str`, `list[str]`, `int | None`) e garante que elas sejam consistentes
antes mesmo de rodar o código. Aqui ele também confere os dois leitores: o
`input` e o `getpass.getpass` precisam caber no mesmo `Leitor`, e cada campo
da `Analise` tem o tipo conferido, o que um `dict` comum não daria.

**Por que esta:** o projeto é pequeno, mas tipar tudo desde o início é uma boa
prática — evita o hábito de "só ligo o mypy quando o projeto crescer" (nunca
liga).

**Estudar:** sintaxe `X | None` / `list[X]` (não `Optional`/`List`),
`collections.abc.Callable`, `typing.NamedTuple`, `-> None` explícito em função
que não retorna nada, `uv run mypy`.

### pytest

O executor de testes. `tests/test_main.py` cobre a lógica do programa (cada
tipo de caractere, as repetições e sequências descontadas, a lista de senhas
comuns e o SHA-256 dela, a entropia, as fronteiras de cada nota e as duas
travas, as sugestões, o resultado sem nenhum trecho da senha, os exemplos com
as notas de 0 a 4, a largura das linhas, o menu e a saída por Ctrl+C) sem
depender de um terminal real. `tests/test_readme_en.py` confere que o
`README.en.md` segue a estrutura do `README.md`.

**Por que esta:** padrão de-facto de testes em Python. Como o menu e a senha
entram por parâmetro, os testes passam dois leitores falsos, sem `monkeypatch`
em `input` ou `getpass`. As funções puras se testam chamando-as com um valor.
O único `monkeypatch` da suíte troca a limpeza de tela, para os testes não
chamarem `os.system`. Um teste com o módulo `ast` lê o `main.py` e confere os
`import` e a ausência de gravação de arquivo, e outro, com o
`inspect.signature`, confere que a senha é lida com o `getpass` por padrão.

**Estudar:** `@pytest.mark.parametrize` (testar várias entradas sem repetir
código), `@pytest.fixture` (inclusive `autouse=True`), testes de fronteira
(27,9 e 28 bits), um leitor falso que devolve as respostas de uma lista,
`capsys` (capturar o que foi impresso no terminal), `hashlib.sha256` (conferir
que um arquivo não mudou), o módulo `ast` (ler código sem executá-lo),
`inspect.signature` (ler o valor padrão de um parâmetro).

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
| `getpass.getpass` (stdlib) | lê a senha sem mostrá-la na tela; entra em `main` por parâmetro, como `ler_senha` |
| `re` (stdlib) | a `REPETICAO`, `(.)\1{2,}`, acha os caracteres repetidos três vezes ou mais |
| `string` (stdlib) | `ascii_lowercase`, `ascii_uppercase`, `digits` e `punctuation`: o tamanho de cada tipo de caractere (26, 26, 10 e 32) |
| `math.log2` e `math.ceil` (stdlib) | a conta da entropia estimada e quantos caracteres faltam para 80 bits |
| `typing.NamedTuple` (stdlib) | a `Analise`, com um nome e um tipo para cada item do resultado |
| `pathlib.Path` (stdlib) | acha e lê o `senhas_comuns.txt` ao lado do `main.py`, de qualquer pasta de onde o programa for chamado |
| `senhas_comuns.txt` (SecLists) | as 150 senhas mais usadas por falantes de português, cópia sem alteração da lista do SecLists (Licença MIT; origem e avisos de copyright no `LICENSE`) |
| `collections.abc.Callable` (stdlib) | tipa os dois leitores (`ler` e `ler_senha`) que `main` recebe por parâmetro |
| `os.system` (stdlib) | limpa o terminal (`cls` no Windows, `clear` no Unix/Mac) |
| `sys.stdout.reconfigure` (stdlib) | força UTF-8 na saída, evitando `UnicodeEncodeError` com stdout redirecionado no Windows (os emojis, o `×` e o `≈` da conta) |

---

## O que deliberadamente não está na stack

- **Qualquer dependência de runtime** — o programa inteiro cabe na biblioteca
  padrão; adicionar uma lib externa só para isso seria peso sem ganho
  pedagógico.
- **Um estimador pronto, como o zxcvbn** — ele reconhece palavras de
  dicionário, datas e trocas de letra por número, mas esconderia as regras,
  que são o assunto do projeto; o README avisa que a nota daqui é uma
  estimativa didática.
- **Consulta a vazamentos na internet (como o Have I Been Pwned)** — o
  programa não usa rede; a lista de senhas comuns fica no projeto, conferida
  pelo SHA-256.
- **O parâmetro `echo_char` do `getpass`** — mostraria um `*` por caractere
  digitado, mas só existe a partir do Python 3.14, e o piso do projeto é o
  3.12.
- **O módulo `locale`** — a vírgula decimal da entropia é trocada com
  `replace`; o `locale` depende da configuração do sistema, e o mesmo programa
  mostraria ponto num terminal e vírgula em outro.
- **Um framework de CLI (Typer/Click)** — o menu é numerado e lido com
  `input()`; além disso, uma senha passada como argumento ficaria gravada no
  histórico do shell.
- **`subprocess`** — a limpeza de tela usa `os.system(comando)` com uma string
  fixa (`"cls"`/`"clear"`, nunca entrada do usuário); `subprocess.run(...,
  shell=True)` faria o mesmo com mais código e é o padrão que ferramentas de
  segurança sinalizam por hábito (mesmo sem risco real aqui).
