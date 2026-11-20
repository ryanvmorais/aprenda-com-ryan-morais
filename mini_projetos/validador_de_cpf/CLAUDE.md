# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Validador de CPF em Python, via terminal — material de estudo para prática de
um algoritmo de verdade (a soma ponderada com o resto da divisão por 11, que dá
os dois dígitos verificadores), da limpeza e da conferência do texto digitado
(`str.isdigit` com `str.isascii` e list comprehension) e das funções pequenas e
puras. Um modo didático mostra a conta passo a passo, e um gerador monta CPFs
válidos para teste. Um único arquivo (`main.py`), sem dependência de runtime
(só a biblioteca padrão), que não grava arquivo nem usa rede. Projeto
educacional, público no GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o programa
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_calcular_digitos_do_exemplo_da_receita_da_38 -v

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
main.py              # funções do programa + main() (ponto de entrada)
tests/test_main.py   # suíte pytest (117 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md         # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py    # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-validador-de-cpf/
iniciar_validador.bat # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_validador.sh  # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
.gitignore            # o de sempre: o programa não cria arquivo
.gitattributes        # LF fixo nos atalhos .sh (com CRLF o shebang quebra no Linux/macOS)
assets/               # validador-de-cpf-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT
CONTRIBUTING.md       # guia de contribuição (fork, Conventional Commits, portão de qualidade)
CODE_OF_CONDUCT.md    # Contributor Covenant 2.1 (pt-BR); contato: contato@ryanmorais.com.br
SECURITY.md           # política de segurança; relatos pelo Private Vulnerability Reporting
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: o CPF passa de função em função como `str`, e a lista de `int` só
existe dentro da conta. A conta de cada dígito é uma `Conta` (`NamedTuple` com
os algarismos, os pesos, os produtos, a soma, o resto e o dígito), e a
conferência devolve uma `Conferencia` (`NamedTuple` com o CPF aceito ou o
motivo da recusa), sem lançar exceção. Uma função por responsabilidade:

- **Cálculo:** `calcular_digito` (os pesos de `range(10 - len(algarismos), 10)`,
  o resto da soma por 11 e o 10 valendo 0) e `calcular_digitos` (o 1º dígito e o
  2º, com o 1º no fim da base).
- **Conferência:** `limpar_cpf` (descarta os `SEPARADORES`, recusa o caractere
  que não é algarismo de 0 a 9, nada digitado e a quantidade errada, nesta
  ordem), `eh_sequencia_repetida` e `conferir_cpf` (limpeza, sequência repetida e
  dígitos; a recusa pelos dígitos não diz quais seriam os certos).
- **Formatação e gerador:** `formatar_cpf` (`000.000.000-00`),
  `descrever_regiao` (o 9º algarismo em `REGIOES_FISCAIS`) e `gerar_cpf` (sorteia
  a base de novo se os 9 algarismos saírem iguais).
- **Textos:** `descrever_resultado`, `descrever_conta`, `explicar_validacao` e
  `descrever_gerado` devolvem o texto da próxima tela, sem imprimir.
- **Interface:** `conferir_opcao`, `limpar_tela` e `exibir_tela`.

`main()` orquestra o menu e trata `KeyboardInterrupt`/`EOFError` num só lugar.
O teclado (`ler`, tipo `Leitor`) e o sorteio (`sortear`, tipo `Sorteador`)
entram por parâmetro, com `input` e `random.randrange` como padrão: os testes
passam um leitor falso e um sorteio de semente fixa. O resultado de cada opção
só vive na variável `resultado` até a próxima volta. Detalhamento completo
(RF-NN, ADRs) em
[`specs/001-validador-de-cpf/`](specs/001-validador-de-cpf/requirements.md).

> **Cuidado:** `calcular_digito` serve aos dois dígitos só porque o último
> algarismo da conta leva sempre o peso 9 (a forma da Receita Federal, ADR-3).
> Trocar para a forma mais divulgada (pesos de 10 a 2 e 11 menos o resto) muda
> também o modo didático, que mostra os pesos na tela; o teste de equivalência
> entre as duas formas continua valendo.

> **Cuidado:** os exemplos do projeto (código, testes, README e animação) usam
> só o exemplo da Receita Federal (`280.012.389-38`), números inválidos
> montados a partir dele e números gerados com semente fixa, nunca o CPF de
> uma pessoa conhecida. Exemplo novo segue a mesma regra.

> **Cuidado:** o `main.py` só importa `__future__`, `collections.abc`, `os`,
> `random`, `sys` e `typing`, e não chama `open`: é o que garante que nenhum
> CPF sai da tela (RNF-07). O teste
> `test_main_py_so_importa_os_modulos_previstos_e_nao_abre_arquivo` confere a
> lista com o módulo `ast`; um `import` novo muda o teste junto, e um módulo de
> rede ou de arquivo muda a spec antes.

> **Cuidado:** nenhuma linha que o programa imprime passa de 54 colunas, com os
> emojis contando duas; dois testes medem os textos e o quadro inteiro. Texto
> novo cabe nessa largura.

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem e termos técnicos universais (`str`, `int`,
  `ASCII`) e de domínio (`CPF`).
- **Estilo de código:** docstrings em português nas funções, classes e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **Funções puras:** cálculo, conferência, formatação e textos devolvem o
  resultado sem ler o teclado nem imprimir; só `exibir_tela` e `main` tocam no
  terminal.
- **Testes:** o único `monkeypatch` da suíte troca `limpar_tela`; o teclado e o
  sorteio entram por parâmetro.
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
com aprovação de cada fase antes da seguinte. A spec `001-validador-de-cpf`
foi escrita **antes do código** (concepção) — ver
[`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_validador.bat`/`.sh` preferem `uv run main.py`, mas caem
> para `python`/`python3 main.py` puro se o `uv` não estiver instalado — é
> assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o programa.
