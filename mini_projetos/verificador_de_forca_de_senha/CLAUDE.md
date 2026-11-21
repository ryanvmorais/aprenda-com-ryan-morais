# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Verificador de força de senha em Python, via terminal — material de estudo
para prática de regras escritas com `any()` e os métodos de string
(`islower`, `isupper` e `isdigit`), do módulo `re`, que acha as repetições
(`aaa`), ao lado das janelas de 3 que acham as sequências (`abc`, `123`,
`qwe`), e do `getpass`, que lê a senha sem mostrá-la. A nota, de 0 a 4, sai da
entropia estimada (a mesma conta do `gerador_de_senhas`, com os trechos
previsíveis valendo um caractere), com a lista portuguesa de senhas comuns do
SecLists e o tamanho mínimo como travas; o resultado diz o que pesou e o que
melhorar, sem mostrar a senha. Os exemplos comentados mostram notas de 0 a 4.
Um único arquivo de código (`main.py`) e a lista de senhas
(`senhas_comuns.txt`), sem dependência de runtime (só a biblioteca padrão),
que não grava arquivo nem usa rede. Projeto educacional, público no GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o programa
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_o_resultado_nao_mostra_nenhum_trecho_da_senha -v

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
senhas_comuns.txt     # as 150 senhas da lista portuguesa do SecLists — cópia exata, nunca editar
tests/test_main.py    # suíte pytest (162 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md          # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py     # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-verificador-de-forca-de-senha/
iniciar_verificador.bat # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_verificador.sh  # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
../../.gitattributes  # LF em tudo (o senhas_comuns.txt inclusive) e CRLF nos .bat; vale para o repositório inteiro, na raiz
assets/               # verificador-de-forca-de-senha-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT, com a origem e os avisos de copyright da lista de senhas comuns
../../CONTRIBUTING.md # com CODE_OF_CONDUCT.md e SECURITY.md: valem para o repositório inteiro, na raiz
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: a verificação é um caminho só. `analisar` recebe a senha e a lista
de senhas comuns e devolve uma `Analise` (`NamedTuple` com o tamanho, quantos
caracteres contam, os tipos, o alfabeto, a entropia, as três conferências e a
nota), e os textos são montados a partir dela. Um trecho previsível é um
`tuple[int, int]` com o início e o fim, como o `span()` de um `re.Match`. Uma
função por responsabilidade:

- **Regras:** `classificar` (um `any()` por tipo de `TIPOS`),
  `achar_repeticoes` (a `REPETICAO`, `(.)\1{2,}`), `achar_sequencias` (janelas
  de 3 contra as `SEQUENCIAS` e o contrário delas), `juntar_trechos` (junta os
  que se sobrepõem), `contar_caracteres` (cada trecho vale um) e
  `carregar_senhas_comuns` (o conjunto das linhas em minúsculas).
- **Nota:** `calcular_entropia` e `descrever_entropia` (iguais às do
  `gerador_de_senhas`, com `Entropia estimada:` no começo), `dar_nota` (as
  faixas de `LIMITES`, a senha comum dando 0 e menos de `TAMANHO_MINIMO`
  caracteres limitando a `NOTA_MAXIMA_CURTA`), `analisar` e
  `faltam_caracteres` (quantos a mais levam a 80 bits).
- **Textos:** `juntar_nomes`, `sugerir`, `descrever_analise` e
  `descrever_exemplos` devolvem o texto da próxima tela, sem imprimir.
- **Perguntas:** `eh_numero` (`isascii()` e `isdecimal()`) e `conferir_opcao`.
- **Opções:** `opcao_verificar` (o pedido da senha, sem `strip()`).
- **Interface:** `limpar_tela` e `exibir_tela`.

`main()` orquestra o menu e trata `KeyboardInterrupt`/`EOFError` num só lugar.
As duas leituras do teclado entram por parâmetro, com o mesmo tipo `Leitor`:
`ler`, que vale `input`, e `ler_senha`, que vale `getpass.getpass`. A lista de
senhas comuns (`comuns`) também, carregada do `ARQUIVO_SENHAS_COMUNS` quando
não é passada: os testes passam dois leitores falsos e uma lista curta. O
resultado de cada opção só vive na variável `resultado` até a próxima volta.
Detalhamento completo (RF-NN, ADRs) em
[`specs/001-verificador-de-forca-de-senha/`](specs/001-verificador-de-forca-de-senha/requirements.md).

> **Cuidado:** a senha só passa por `opcao_verificar` e `analisar`; a
> `Analise` não a guarda, então nenhuma função de texto consegue mostrá-la
> (ADR-8). Regra nova devolve o que achou como número ou `bool` na `Analise`,
> nunca o trecho da senha. O teste
> `test_o_resultado_nao_mostra_nenhum_trecho_da_senha` confere que nenhum
> trecho de 3 caracteres de uma lista de senhas aparece no resultado.

> **Cuidado:** o `senhas_comuns.txt` não se edita: é a cópia exata da lista
> portuguesa do SecLists (ADR-6), e o teste
> `test_senhas_comuns_txt_e_a_copia_exata_da_lista` confere o SHA-256 e as 150
> linhas. O `.gitattributes` da raiz mantém o LF no checkout, para o hash
> valer em qualquer sistema. A origem e os avisos de copyright ficam no
> `LICENSE`. A lista tem um palavrão, que o programa nunca mostra: os exemplos
> são escolhidos à parte.

> **Cuidado:** a nota dos `EXEMPLOS` é calculada por `analisar` na hora de
> mostrar, nunca escrita à mão (ADR-9); a constante guarda só a senha e a
> explicação. O teste `test_descrever_exemplos_cobre_as_notas_de_0_a_4`
> confere a cobertura. Mudou uma faixa ou uma regra, confira se cada
> explicação ainda descreve o que pesou na nota.

> **Cuidado:** o `main.py` só importa `__future__`, `collections.abc`,
> `getpass`, `math`, `os`, `pathlib`, `re`, `string`, `sys` e `typing`, não
> chama `open`, `write_text` nem `write_bytes` e não lê `sys.argv`: é o que
> garante que nenhuma senha sai do computador (RNF-07). O teste
> `test_main_py_so_importa_os_modulos_previstos_e_nao_grava_arquivo` confere a
> lista com o módulo `ast`; um `import` novo muda o teste junto, e um módulo de
> rede ou de arquivo muda a spec antes.

> **Cuidado:** os exemplos do projeto (código, testes, README e animação) usam
> só senhas inventadas ou da lista de senhas comuns, nunca uma senha em uso.

> **Cuidado:** nenhuma linha que o programa imprime passa de 54 colunas, com os
> emojis contando duas; três testes medem os textos, o pedido da senha e o
> quadro inteiro. Texto novo cabe nessa largura.

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem e termos técnicos universais (`str`, `ASCII`,
  `SHA-256`) e de domínio (`SecLists`, `QWERTY`).
- **Estilo de código:** docstrings em português nas funções, classes e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **Funções puras:** regras, nota, textos e opções devolvem o resultado sem
  imprimir; a senha é lida pelo `ler_senha` recebido, e só `exibir_tela` e
  `main` imprimem no terminal.
- **Testes:** o único `monkeypatch` da suíte troca `limpar_tela`; os dois
  leitores e a lista de senhas comuns entram por parâmetro.
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
com aprovação de cada fase antes da seguinte. A spec
`001-verificador-de-forca-de-senha` foi escrita **antes do código**
(concepção) — ver [`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_verificador.bat`/`.sh` preferem `uv run main.py`, mas
> caem para `python`/`python3 main.py` puro se o `uv` não estiver instalado —
> é assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o programa.
