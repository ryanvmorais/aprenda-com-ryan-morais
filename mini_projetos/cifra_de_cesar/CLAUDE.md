# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Cifra de César em Python, via terminal — material de estudo para prática do
`ord`, do `chr` e da aritmética modular (`% 26`), que andam cada letra a chave
de posições no alfabeto, do `str.maketrans`, que aplica a troca ao texto
inteiro, e do `unicodedata`, que tira os acentos antes. O programa cifra e
decifra com uma chave de 1 a 25 e quebra um texto cifrado sem a chave de dois
jeitos: a força bruta, com as 25 tentativas, e a frequência das letras,
contadas com o `collections.Counter` e pontuadas pela tabela do português da
COPPE/UFRJ, com o aviso de texto curto abaixo de 30 letras. Um único arquivo
de código (`main.py`), sem dependência de runtime (só a biblioteca padrão),
que não lê nem grava arquivo e não usa rede. Projeto educacional, público no
GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o programa
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_frequencias_somam_perto_de_100 -v

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
tests/test_main.py    # suíte pytest (259 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md          # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py     # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-cifra-de-cesar/
iniciar_cifra.bat     # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_cifra.sh      # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
assets/               # cifra-de-cesar-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT
../../.gitattributes  # LF em tudo e CRLF nos .bat; vale para o repositório inteiro, na raiz
../../CONTRIBUTING.md # com CODE_OF_CONDUCT.md e SECURITY.md: valem para o repositório inteiro, na raiz
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: cada operação recebe o texto (e a chave) e devolve o texto
(ADR-1). Uma tentativa da força bruta é um `tuple[int, str]`, com a chave e o
texto decifrado. Uma função por responsabilidade:

- **Cifra:** `remover_acentos` (NFD, igual à do `jogo_da_forca`),
  `deslocar_letra` (`ord`, `chr` e `% 26`), `montar_tabela` (a
  `deslocar_letra` feita para as 52 letras, no formato do `str.maketrans`),
  `deslocar`, `cifrar` e `decifrar` (a chave negativa).
- **Quebra:** `tem_letras`, `forca_bruta` (as 25 `CHAVES`), `contar_letras`
  (o `Counter`), `pontuar` (a soma da contagem vezes o percentual de
  `FREQUENCIAS`) e `ordenar_chaves` (da maior pontuação para a menor; no
  empate, a chave menor antes).
- **Textos:** `cortar` (em `LARGURA` colunas, com reticências),
  `aviso_acentos`, `descrever_cifra`, `descrever_decifra`,
  `descrever_forca_bruta` e `descrever_frequencia` devolvem o texto da próxima
  tela, sem imprimir.
- **Perguntas:** `eh_numero` (`isascii()` e `isdecimal()`), `conferir_opcao` e
  `conferir_chave`.
- **Opções:** `pedir_texto` (sem `strip()`), `opcao_cifrar`, `opcao_decifrar`,
  `opcao_forca_bruta` e `opcao_frequencia`.
- **Interface:** `limpar_tela` e `exibir_tela`.

`main()` orquestra o menu e trata `KeyboardInterrupt`/`EOFError` num só lugar.
A leitura do teclado entra por parâmetro (`ler`, do tipo `Leitor`, que vale
`input`): os testes passam um leitor falso. O texto digitado só vive na
variável local de cada opção, e o resultado, na variável `resultado` até a
próxima volta. Detalhamento completo (RF-NN, ADRs) em
[`specs/001-cifra-de-cesar/`](specs/001-cifra-de-cesar/requirements.md).

> **Cuidado:** a `FREQUENCIAS` é a cópia sem alteração da tabela 1.2.1 do
> estudo "Análise de Freqüências de Línguas" (COPPE/UFRJ), com a fonte no
> comentário acima dela (ADR-7). Não arredonde, não normalize para somar 100
> e não troque um valor por outra fonte: os testes
> `test_frequencias_tem_as_26_letras_do_alfabeto`,
> `test_frequencias_tem_os_percentuais_do_estudo` e
> `test_frequencias_somam_perto_de_100` conferem as 26 letras, os três maiores
> percentuais e a soma entre 99,9 e 100,1.

> **Cuidado:** a pontuação pela soma dos produtos (ADR-5) e o
> `MINIMO_LETRAS = 30` do aviso de texto curto (ADR-6) saíram da mesma
> medição. Trocar o método de pontuação (o qui-quadrado, por exemplo) ou a
> tabela muda o ADR-5 e pede medir de novo e rever o `MINIMO_LETRAS` junto,
> numa spec nova.

> **Cuidado:** o `main.py` só importa `__future__`, `collections`,
> `collections.abc`, `os`, `string`, `sys` e `unicodedata`, não chama `open`,
> `read_text`, `write_text`, `read_bytes` nem `write_bytes` e não lê
> `sys.argv`: é o que garante que o texto digitado não sai do computador nem
> fica no histórico do shell (RNF-07). O teste
> `test_main_py_so_importa_os_modulos_previstos_e_nao_le_nem_grava_arquivo`
> confere a lista com o módulo `ast`; um `import` novo muda o teste junto, e
> um módulo de rede ou de arquivo muda a spec antes.

> **Cuidado:** nenhuma linha que o programa escreve passa de 54 colunas
> (`LARGURA`), com os emojis contando duas; três testes medem os textos, os
> pedidos e o quadro inteiro. Texto novo cabe nessa largura. O texto do
> usuário aparece inteiro no resultado de cifrar, de decifrar e na chave mais
> provável; nas linhas da força bruta e nas alternativas da frequência, ele
> passa por `cortar`.

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem e termos técnicos universais (`str`, `ASCII`,
  `NFD`) e de domínio (`COPPE/UFRJ`).
- **Estilo de código:** docstrings em português nas funções e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **Funções puras:** cifra, quebra, textos e opções devolvem o resultado sem
  imprimir; o texto é lido pelo `ler` recebido, e só `exibir_tela` e `main`
  imprimem no terminal.
- **Testes:** o único `monkeypatch` da suíte troca `limpar_tela`; o leitor
  entra por parâmetro.
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
com aprovação de cada fase antes da seguinte. A spec `001-cifra-de-cesar` foi
escrita **antes do código** (concepção) — ver
[`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_cifra.bat`/`.sh` preferem `uv run main.py`, mas caem
> para `python`/`python3 main.py` puro se o `uv` não estiver instalado — é
> assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o programa.
