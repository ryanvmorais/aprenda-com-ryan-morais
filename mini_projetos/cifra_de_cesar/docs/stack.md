# A stack, e por quê

Cada tecnologia que sustenta a Cifra de César: o que faz, por que foi
escolhida contra a alternativa, e os conceitos que valem a pena estudar
primeiro se forem novos para você.

Não é exaustivo — o grafo completo de versões do grupo de desenvolvimento está
travado no `uv.lock`. Este doc é o mapa: a *forma* do projeto e o raciocínio
por trás de cada peça.

O projeto é um único programa: um script de terminal, sem dependências de
runtime (só a biblioteca padrão do Python), com um grupo de ferramentas de
qualidade por fora. Nada sobrevive entre uma execução e outra: o programa não
lê nem grava arquivo e não usa rede, e o texto digitado só existe na memória
enquanto a opção roda. A tabela de frequência das letras fica no próprio
`main.py`.

```
main.py  ──►  biblioteca padrão do Python (string, unicodedata,
              collections, collections.abc, os, sys)
```

---

## Linguagem e empacotamento

### Python 3.12+

A única linguagem do projeto. 3.12 é o piso (`requires-python`): já tem a
sintaxe moderna de tipos (`X | None`, `list[str]`) e a instrução `type`
(PEP 695), usada no apelido `Leitor`.

**Por que esta:** o projeto é puramente didático (uma conta por letra, um laço
de tentativas, uma contagem) — qualquer linguagem serviria, mas Python traz na
biblioteca padrão o alfabeto pronto (`string.ascii_lowercase`), a tabela de
tradução (`str.maketrans`), a decomposição dos acentos (`unicodedata`) e a
contagem (`collections.Counter`), e o `%` de um número negativo já devolve um
resto entre 0 e 25, o que decifra com a chave negativa sem conta a mais.

**Estudar:** `ord` e `chr`, o operador `%` (inclusive com número negativo),
`str.maketrans` e `str.translate`, `unicodedata.normalize("NFD", ...)` e
`unicodedata.combining`, `collections.Counter` (`most_common` e `total`),
`sorted` com `key` e `reverse=True` (e por que ele mantém a ordem dos
iguais), `range`, generator expressions dentro de `sum`, `any` e `"".join`,
f-strings com alinhamento (`{chave:2}`), `enumerate(..., start=1)`, funções
como parâmetro (`Callable`), a instrução `type`, `if __name__ == "__main__"`.

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
(`-> str`, `list[tuple[int, str]]`, `int | None`) e garante que elas sejam
consistentes antes mesmo de rodar o código. Aqui ele também confere o
`Counter[str]` que `contar_letras` devolve e o `dict[int, int]` da tabela do
`str.maketrans`.

**Por que esta:** o projeto é pequeno, mas tipar tudo desde o início é uma boa
prática — evita o hábito de "só ligo o mypy quando o projeto crescer" (nunca
liga).

**Estudar:** sintaxe `X | None` / `list[X]` (não `Optional`/`List`),
`collections.abc.Callable`, tipos genéricos como `Counter[str]`, `-> None`
explícito em função que não retorna nada, `uv run mypy`.

### pytest

O executor de testes. `tests/test_main.py` cobre a lógica do programa (a
retirada dos acentos, a volta do Z para o A e do A para o Z, a cifra
conhecida de `Ola, Mundo!`, o decifrar que desfaz o cifrar nas 25 chaves, a
força bruta, a contagem e a pontuação conferidas à mão, a chave certa em
primeiro para frases cifradas com cada chave, a tabela de frequência, os
avisos de acentos e de texto curto, a largura das linhas, o menu e a saída por
Ctrl+C) sem depender de um terminal real. `tests/test_readme_en.py` confere
que o `README.en.md` segue a estrutura do `README.md`.

**Por que esta:** padrão de-facto de testes em Python. Como o teclado entra
por parâmetro, os testes passam um leitor falso, sem `monkeypatch` em
`input`. As funções puras se testam chamando-as com um valor. O único
`monkeypatch` da suíte troca a limpeza de tela, para os testes não chamarem
`os.system`. Um teste com o módulo `ast` lê o `main.py` e confere os `import`
e a ausência de leitura e gravação de arquivo.

**Estudar:** `@pytest.mark.parametrize` (testar as 25 chaves sem repetir
código), `@pytest.fixture` (inclusive `autouse=True`), testes de fronteira
(29 e 30 letras), um leitor falso que devolve as respostas de uma lista,
`capsys` (capturar o que foi impresso no terminal), `pytest.approx`
(comparar números com vírgula), o módulo `ast` (ler código sem executá-lo).

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
| `string.ascii_lowercase` (stdlib) | o `ALFABETO`, as 26 letras de `a` a `z` na ordem em que a chave anda |
| `ord` e `chr` (builtins) | a posição da letra no alfabeto e a letra de volta, na conta de `deslocar_letra` |
| `str.maketrans` e `str.translate` (builtins) | a tabela das 52 letras deslocadas, aplicada ao texto inteiro, com o resto passando sem mudança |
| `unicodedata` (stdlib) | a forma NFD e o `combining`, que tiram os acentos e a cedilha antes de cifrar |
| `collections.Counter` (stdlib) | conta as letras do texto; `most_common(3)` dá as três mais comuns e `total()`, quantas letras há |
| `FREQUENCIAS` (COPPE/UFRJ) | os 26 percentuais das letras no português, da tabela 1.2.1 do estudo "Análise de Freqüências de Línguas", copiados sem alteração, com a fonte no comentário |
| `collections.abc.Callable` (stdlib) | tipa o leitor (`ler`) que `main` recebe por parâmetro |
| `os.system` (stdlib) | limpa o terminal (`cls` no Windows, `clear` no Unix/Mac) |
| `sys.stdout.reconfigure` (stdlib) | força UTF-8 na saída, evitando `UnicodeEncodeError` com stdout redirecionado no Windows (os emojis e os acentos das mensagens) |

---

## O que deliberadamente não está na stack

- **Qualquer dependência de runtime** — o programa inteiro cabe na biblioteca
  padrão; adicionar uma lib externa só para isso seria peso sem ganho
  pedagógico.
- **Uma biblioteca de criptografia (como a `cryptography`)** — a cifra de
  César é o assunto, e uma cifra moderna esconderia a conta que o projeto
  ensina; o README avisa que esta cifra não protege nada.
- **O `codecs.encode(texto, "rot13")`** — faz só a chave 13, pronta; a conta
  com `ord`, `chr` e `%` é o que se quer ver.
- **O qui-quadrado (ou o `scipy.stats.chisquare`)** — na medição do design, a
  soma dos produtos acertou mais a chave, e uma letra rara (K, W ou Y) pesava
  demais no qui-quadrado; fica como atividade no README.
- **Um arquivo com a tabela de frequência** — são 26 números, que cabem no
  `main.py` ao lado do código que os usa, e o programa continua sem ler
  arquivo.
- **Um framework de CLI (Typer/Click)** — o menu é numerado e lido com
  `input()`; além disso, um texto passado como argumento ficaria gravado no
  histórico do shell.
- **`subprocess`** — a limpeza de tela usa `os.system(comando)` com uma string
  fixa (`"cls"`/`"clear"`, nunca entrada do usuário); `subprocess.run(...,
  shell=True)` faria o mesmo com mais código e é o padrão que ferramentas de
  segurança sinalizam por hábito (mesmo sem risco real aqui).
