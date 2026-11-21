# A stack, e por quê

Cada tecnologia que sustenta o Gerador de Senhas: o que faz, por que foi
escolhida contra a alternativa, e os conceitos que valem a pena estudar
primeiro se forem novos para você.

Não é exaustivo — o grafo completo de versões do grupo de desenvolvimento está
travado no `uv.lock`. Este doc é o mapa: a *forma* do projeto e o raciocínio
por trás de cada peça.

O projeto é um único programa: um script de terminal, sem dependências de
runtime (só a biblioteca padrão do Python), com um grupo de ferramentas de
qualidade por fora. Nada sobrevive entre uma execução e outra: o programa não
grava arquivo nem usa rede, o único arquivo que ele lê é a lista de palavras, e
a senha gerada só existe na tela.

```
main.py  ──►  biblioteca padrão do Python (secrets, random, string, math,
   │          pathlib, os, sys, collections.abc)
   └──►  palavras.txt (lista portuguesa do BIP-39, lida uma vez)
```

---

## Linguagem e empacotamento

### Python 3.12+

A única linguagem do projeto. 3.12 é o piso (`requires-python`): já tem a
sintaxe moderna de tipos (`X | None`, `list[str]`) e a instrução `type`
(PEP 695), usada nos apelidos `Leitor` e `Escolhedor`.

**Por que esta:** o projeto é puramente didático (um sorteio, uma conta,
laço de menu) — qualquer linguagem serviria, mas Python traz na biblioteca
padrão o sorteio seguro (`secrets`), os alfabetos prontos (`string`) e o
logaritmo (`math.log2`), e a regra "um de cada tipo" cabe numa linha com `all`
e `any`.

**Estudar:** o módulo `secrets` contra o `random`, a semente de um gerador
pseudoaleatório (`random.Random(semente)`), as constantes de `string`,
`math.log2`, generator expressions dentro de `"".join(...)`, `all` e `any`,
`str.isdecimal` contra `str.isascii`, `str.join` e `str.split`,
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
antes mesmo de rodar o código. Aqui ele também confere o sorteador: o
`secrets.choice` e o `choice` de um `random.Random` precisam caber no mesmo
`Escolhedor`, e uma função com outra assinatura vira erro de tipo antes de
chegar ao menu.

**Por que esta:** o projeto é pequeno, mas tipar tudo desde o início é uma boa
prática — evita o hábito de "só ligo o mypy quando o projeto crescer" (nunca
liga).

**Estudar:** sintaxe `X | None` / `list[X]` (não `Optional`/`List`),
`collections.abc.Callable` e `Sequence`, `-> None` explícito em função que não
retorna nada, `uv run mypy`.

### pytest

O executor de testes. `tests/test_main.py` cobre a lógica do programa (os
alfabetos de cada tipo e sem os parecidos, a regra "um de cada tipo" em
milhares de senhas sorteadas e o novo sorteio quando falta um tipo, a
frase-senha, a lista de palavras e o SHA-256 dela, a entropia com `=` e `≈`,
as perguntas e as recusas, a demonstração do `random`, a largura das linhas, o
menu e a saída por Ctrl+C) sem depender de um terminal real.
`tests/test_readme_en.py` confere que o `README.en.md` segue a estrutura do
`README.md`.

**Por que esta:** padrão de-facto de testes em Python. Como o teclado e o
sorteio entram por parâmetro, os testes passam um leitor falso e um
`random.Random(2026).choice`, sem `monkeypatch` em `input` ou `secrets`. As
funções puras se testam chamando-as com um valor. O único `monkeypatch` da
suíte troca a limpeza de tela, para os testes não chamarem `os.system`. Um
teste com o módulo `ast` lê o `main.py` e confere os `import` e a ausência de
gravação de arquivo.

**Estudar:** `@pytest.mark.parametrize` (testar várias entradas sem repetir
código), `@pytest.fixture` (inclusive `autouse=True`), teste de propriedade
(conferir uma regra em milhares de senhas sorteadas), um sorteador falso que
devolve uma sequência escolhida, `capsys` (capturar o que foi impresso no
terminal), `hashlib.sha256` (conferir que um arquivo não mudou), o módulo
`ast` (ler código sem executá-lo).

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
| `secrets.choice` (stdlib) | sorteia cada caractere da senha e cada palavra da frase-senha; entra em `main` por parâmetro, como `escolher` |
| `random.Random` (stdlib) | só na demonstração da opção 4, com a semente fixa, para mostrar a repetição; e nos testes, para o sorteio ser reproduzível |
| `string` (stdlib) | `ascii_lowercase`, `ascii_uppercase`, `digits` e `punctuation`: os 94 caracteres dos quatro tipos |
| `math.log2` (stdlib) | a conta da entropia: quantos bits vale cada caractere ou palavra |
| `pathlib.Path` (stdlib) | acha e lê o `palavras.txt` ao lado do `main.py`, de qualquer pasta de onde o programa for chamado |
| `palavras.txt` (BIP-39) | as 2048 palavras da frase-senha, cópia sem alteração da lista portuguesa do BIP-39 (Licença MIT; origem e autores no `LICENSE`) |
| `collections.abc.Callable` e `Sequence` (stdlib) | tipam o leitor do teclado e o sorteador que `main` recebe por parâmetro |
| `os.system` (stdlib) | limpa o terminal (`cls` no Windows, `clear` no Unix/Mac) |
| `sys.stdout.reconfigure` (stdlib) | força UTF-8 na saída, evitando `UnicodeEncodeError` com stdout redirecionado no Windows (os emojis, o `×` e o `≈` da conta) |

---

## O que deliberadamente não está na stack

- **Qualquer dependência de runtime** — o programa inteiro cabe na biblioteca
  padrão; adicionar uma lib externa só para isso seria peso sem ganho
  pedagógico.
- **Uma biblioteca de geração de senhas** — existem pacotes prontos, mas o
  sorteio, a regra "um de cada tipo" e a entropia são o assunto do projeto;
  usar um deles esconderia justamente o que se quer aprender.
- **Uma biblioteca de área de transferência** — copiar a senha para o
  clipboard pediria uma dependência por sistema operacional; a senha fica
  sozinha na linha, para ser selecionada e copiada com o mouse.
- **O módulo `locale`** — a vírgula decimal da entropia é trocada com
  `replace`; o `locale` depende da configuração do sistema, e o mesmo programa
  mostraria ponto num terminal e vírgula em outro.
- **A lista de palavras baixada da internet** — o programa não usa rede; a
  lista fica no projeto, conferida pelo SHA-256.
- **Um framework de CLI (Typer/Click)** — o menu é numerado e lido com
  `input()`; além disso, uma opção passada como argumento ficaria gravada no
  histórico do shell.
- **`subprocess`** — a limpeza de tela usa `os.system(comando)` com uma string
  fixa (`"cls"`/`"clear"`, nunca entrada do usuário); `subprocess.run(...,
  shell=True)` faria o mesmo com mais código e é o padrão que ferramentas de
  segurança sinalizam por hábito (mesmo sem risco real aqui).
