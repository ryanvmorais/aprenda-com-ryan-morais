# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Gerador de senhas em Python, via terminal — material de estudo para prática da
diferença entre o `random` e o `secrets` (o sorteio de toda senha é o
`secrets.choice`), das constantes do módulo `string`, que montam os alfabetos,
e da entropia em bits, calculada com `math.log2` e mostrada com a conta. Gera a
senha forte padrão com um Enter, a senha personalizada (tamanho, tipos de
caractere e os parecidos de fora), a frase-senha com a lista portuguesa do
BIP-39 e uma demonstração de por que o `random` não serve para senha. Um único
arquivo de código (`main.py`) e a lista de palavras (`palavras.txt`), sem
dependência de runtime (só a biblioteca padrão), que não grava arquivo nem usa
rede. Projeto educacional, público no GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o programa
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_gerar_senha_sorteia_de_novo_a_senha_sem_um_tipo -v

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
main.py               # funções do programa + main() (ponto de entrada)
palavras.txt          # as 2048 palavras da lista portuguesa do BIP-39 — cópia exata, nunca editar
tests/test_main.py    # suíte pytest (130 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md          # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py     # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-gerador-de-senhas/
iniciar_gerador.bat   # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_gerador.sh    # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
../../.gitattributes  # LF em tudo (o palavras.txt inclusive) e CRLF nos .bat; vale para o repositório inteiro, na raiz
assets/               # gerador-de-senhas-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT, com a origem, a licença e os autores da lista de palavras
../../CONTRIBUTING.md # com CODE_OF_CONDUCT.md e SECURITY.md: valem para o repositório inteiro, na raiz
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: cada geração recebe o tamanho, os grupos de caracteres e o
sorteador, e devolve o texto. O alfabeto é uma lista de grupos, um texto por
tipo escolhido: a junção é o que se sorteia, e cada grupo é o que a regra "um
de cada tipo" confere. Uma função por responsabilidade:

- **Sorteio:** `montar_grupos` (os `TIPOS` escolhidos, sem os `PARECIDOS` se
  pedido), `tem_um_de_cada`, `gerar_senha` (sorteia a senha inteira de novo
  quando falta um tipo), `carregar_palavras` e `gerar_frase` (com reposição,
  juntando com o `SEPARADOR`).
- **Entropia:** `calcular_entropia` (quantidade vezes o `log2` do alfabeto) e
  `descrever_entropia` (`=` sem casa decimal no resultado inteiro, `≈` com uma
  casa e vírgula nos outros).
- **Perguntas:** `eh_numero` (`isascii()` e `isdecimal()`), `conferir_opcao`,
  `conferir_numero`, `conferir_sim_nao`, `perguntar_numero` e
  `perguntar_sim_nao` (repetem a pergunta até a resposta ser aceita).
- **Textos:** `descrever_gerada` e `explicar_random` devolvem o texto da
  próxima tela, sem imprimir.
- **Opções:** `opcao_senha_forte`, `opcao_senha_personalizada` e
  `opcao_frase_senha`.
- **Interface:** `limpar_tela` e `exibir_tela`.

`main()` orquestra o menu e trata `KeyboardInterrupt`/`EOFError` num só lugar.
O teclado (`ler`, tipo `Leitor`) e o sorteio (`escolher`, tipo `Escolhedor`)
entram por parâmetro, com `input` e `secrets.choice` como padrão, e a lista de
palavras (`palavras`) também, carregada do `ARQUIVO_PALAVRAS` quando não é
passada: os testes passam um leitor falso e um sorteio de semente fixa. O
resultado de cada opção só vive na variável `resultado` até a próxima volta.
Detalhamento completo (RF-NN, ADRs) em
[`specs/001-gerador-de-senhas/`](specs/001-gerador-de-senhas/requirements.md).

> **Cuidado:** todo sorteio de senha passa pelo `escolher`, que vale
> `secrets.choice` no programa. O `random` só aparece em `explicar_random`, com
> um `random.Random(SEMENTE_DEMONSTRACAO)` novo para cada senha da
> demonstração, nunca o `random.seed` do módulo (ADR-2, ADR-7). Função nova que
> sorteia recebe o `escolher` por parâmetro.

> **Cuidado:** a regra "um de cada tipo" sorteia a senha inteira de novo quando
> falta um tipo (ADR-3). Forçar um caractere de cada tipo numa posição, ou
> trocar um caractere sorteado pelo do tipo que faltou, deixa a senha mais
> previsível; o teste `test_gerar_senha_sorteia_de_novo_a_senha_sem_um_tipo`
> confere o novo sorteio.

> **Cuidado:** o `palavras.txt` não se edita: é a cópia exata da lista
> portuguesa do BIP-39 (ADR-6), e o teste
> `test_palavras_txt_e_a_copia_exata_da_lista` confere o SHA-256 dele. O
> `.gitattributes` da raiz mantém o LF no checkout, para o hash valer em
> qualquer sistema. A origem, a licença e os autores ficam no `LICENSE`.

> **Cuidado:** o `main.py` só importa `__future__`, `collections.abc`, `math`,
> `os`, `pathlib`, `random`, `secrets`, `string` e `sys`, não chama `open`,
> `write_text` nem `write_bytes` e, do `os` e do `sys`, só usa `os.name`,
> `os.system` e `sys.stdout` (nada de `sys.argv`): é o que garante que
> nenhuma senha sai da tela (RNF-07). O teste
> `test_main_py_so_importa_os_modulos_previstos_e_nao_grava_arquivo` confere a
> lista com o módulo `ast`; um `import` novo muda o teste junto, e um módulo de
> rede ou de arquivo muda a spec antes.

> **Cuidado:** os exemplos do projeto (código, testes, README e animação) usam
> só senhas e frases geradas com semente fixa, nunca uma senha em uso.

> **Cuidado:** nenhuma linha que o programa imprime passa de 54 colunas, com os
> emojis contando duas, fora a da senha e a da frase-senha, que podem ser mais
> longas; três testes medem os textos, as perguntas e o quadro inteiro. Texto
> novo cabe nessa largura.

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem e termos técnicos universais (`str`, `ASCII`,
  `SHA-256`) e de domínio (`BIP-39`).
- **Estilo de código:** docstrings em português nas funções, classes e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **Funções puras:** sorteio, entropia, conferência, textos e opções devolvem o
  resultado sem imprimir; as perguntas leem o teclado pelo `ler` recebido, e só
  `exibir_tela`, as perguntas (a recusa) e `main` imprimem no terminal.
- **Testes:** o único `monkeypatch` da suíte troca `limpar_tela`; o teclado, o
  sorteio e a lista de palavras entram por parâmetro.
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
com aprovação de cada fase antes da seguinte. A spec `001-gerador-de-senhas`
foi escrita **antes do código** (concepção) — ver
[`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_gerador.bat`/`.sh` preferem `uv run main.py`, mas caem
> para `python`/`python3 main.py` puro se o `uv` não estiver instalado — é
> assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o programa.
