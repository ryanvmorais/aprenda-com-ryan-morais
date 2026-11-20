# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral do projeto

Lista de Tarefas em Python, via terminal — material de estudo para prática de
leitura e gravação de arquivo com `json` e `pathlib` (sempre em UTF-8), da
lista de dicionários como "banco de dados" e do tratamento do arquivo ausente,
corrompido ou gravado pela metade. Um único arquivo (`main.py`), sem
dependência de runtime (só a biblioteca padrão). Projeto educacional, público
no GitHub.

## Comandos comuns

```bash
# Sincronizar o ambiente (.venv) a partir do uv.lock
uv sync

# Rodar o programa
uv run main.py

# Rodar a suíte de testes
uv run pytest

# Rodar um teste específico
uv run pytest tests/test_main.py::test_main_sessao_grava_e_reabre_com_a_mesma_lista -v

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
tests/test_main.py   # suíte pytest (89 casos)
tests/test_readme_en.py # confere que README.en.md segue a estrutura do README.md
README.en.md         # versão em inglês do README (mesmas seções, mesma ordem)
tests/__init__.py    # torna tests/ um pacote (vazio)
docs/stack.md         # o que cada peça da stack faz e por quê
specs/                # spec-driven development (ver specs/README.md)
  001-lista-de-tarefas/
iniciar_lista.bat     # atalho Windows: uv run main.py (fallback: python main.py)
iniciar_lista.sh      # atalho Linux/macOS: uv run main.py (fallback: python3 main.py)
pyproject.toml        # gerenciado por uv — sem deps de runtime, grupo dev com
                       # ruff/black/mypy/pytest
uv.lock               # lock do grupo dev — nunca editar à mão
.gitignore            # só os dados de quem usa: tarefas.json, tarefas.corrompido-*.json e tarefas.json.tmp
../../.gitattributes  # LF fixo nos atalhos .sh e CRLF nos .bat; vale para o repositório inteiro, na raiz
assets/               # lista-de-tarefas-python-terminal-sessao.svg: animação de uma sessão no topo do README
LICENSE               # licença MIT
../../CONTRIBUTING.md # com CODE_OF_CONDUCT.md e SECURITY.md: valem para o repositório inteiro, na raiz
tarefas.json          # gerado na primeira alteração; dado de quem usa, fora do Git
../../.github/   # CI, CodeQL, pip-audit, Dependabot, templates e o script de impessoalidade
                 # (scripts/conferir_impessoalidade.py, para o repositório inteiro): ficam na raiz
```

### Funções (em `main.py`)

Sem classe: a lista de tarefas vive em `main()` e é passada às ações, que a
alteram no lugar. Cada tarefa é um `Tarefa` (`TypedDict` com `texto`,
`concluida` e `criada_em`, a data em ISO 8601), e o arquivo é o
`ARQUIVO_PADRAO`, `Path(__file__).parent / "tarefas.json"`, ao lado do
`main.py` de onde quer que o programa seja chamado. Uma função por
responsabilidade:

- **Arquivo:** `validar_tarefas` (confere a forma e lança `ValueError` com o
  motivo), `guardar_corrompido` (renomeia para
  `tarefas.corrompido-AAAAMMDD-HHMMSS.json`, com `-2`, `-3` se o nome existir),
  `carregar_tarefas` (arquivo ausente → lista vazia; inválido → cópia e aviso) e
  `salvar_tarefas` (gravação atômica: `tarefas.json.tmp` na mesma pasta e
  `Path.replace`).
- **Tela e entrada:** `formatar_data`, `formatar_tarefa`, as três `conferir_*`
  (sem lançar exceção: `conferir_opcao` devolve o número ou `None`, e
  `conferir_texto` e `conferir_numero` devolvem uma `Conferencia`, a
  `NamedTuple` com o valor aceito ou o motivo da recusa), `limpar_tela`,
  `exibir_tela` e os
  leitores `ler_texto`, `ler_numero` e `confirmar`, que pedem de novo sem limpar
  a tela.
- **Ações:** `adicionar`, `alternar_conclusao`, `editar` e `remover`, cada uma
  gravando logo depois de alterar e devolvendo a mensagem da próxima tela;
  `remover` pergunta `s`/`n` antes do `pop`.

`main()` orquestra o menu e trata `KeyboardInterrupt`/`EOFError` num só lugar.
O teclado (`ler`, tipo `Leitor`), o relógio (`agora`, tipo `Relogio`) e o
caminho do arquivo entram por parâmetro, com `input`, `datetime.now` e
`ARQUIVO_PADRAO` como padrão: os testes passam versões falsas e uma pasta
`tmp_path`, e nunca tocam no `tarefas.json` de verdade. Detalhamento completo
(RF-NN, ADRs) em
[`specs/001-lista-de-tarefas/`](specs/001-lista-de-tarefas/requirements.md).

> **Cuidado:** o formato do `tarefas.json` é um contrato com os arquivos já
> gravados. `validar_tarefas` exige exatamente as chaves de `CAMPOS`: uma chave
> nova obrigatória faz os arquivos antigos serem tratados como corrompidos (o
> programa os renomeia e começa vazio). Campo novo entra como opcional, e a
> mudança vem com o teste que abre um arquivo no formato antigo.

> **Cuidado:** em `carregar_tarefas`, o `except ValueError` único só funciona
> porque `json.JSONDecodeError` e `UnicodeDecodeError` são subclasses de
> `ValueError`. Uma conferência nova em `validar_tarefas` tem de lançar
> `ValueError` (ou uma subclasse), ou o erro escapa como stack trace.

> **Cuidado:** em `guardar_corrompido`, é `rename`, e não `replace`: o
> `replace` sobrescreveria em silêncio uma cópia anterior com o mesmo nome. Já
> em `salvar_tarefas` é `replace`, que troca o arquivo numa operação só; o
> temporário fica na mesma pasta porque a troca só é atômica no mesmo disco.

## Convenções

- **Idioma do código:** português — projeto educacional em português do Brasil.
  Exceções: keywords da linguagem, termos técnicos universais (`JSON`, `str`,
  `bool`) e as chaves do arquivo, que seguem o nome dos campos de `Tarefa`.
- **Estilo de código:** docstrings em português nas funções, classes e módulos
  públicos, type hints completos (`mypy` em modo `strict`), comentários que
  explicam o *porquê* e não o *quê*, linhas de até 88 caracteres (`black`).
- **Arquivo:** sempre `encoding="utf-8"` na leitura e na gravação, e
  `ensure_ascii=False` com `indent=2` no `json.dumps`, para o arquivo se ler
  num editor.
- **Testes:** todo teste que grava usa `tmp_path`; nenhum toca no
  `ARQUIVO_PADRAO`. O único `monkeypatch` da suíte troca `limpar_tela`.
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
com aprovação de cada fase antes da seguinte. A spec `001-lista-de-tarefas`
foi escrita **antes do código** (concepção), no formato da spec
`001-jogo-da-forca` do `jogo_da_forca` — ver
[`specs/README.md`](specs/README.md).

Antes de abrir o PR, atualize o `README.md` (e o `README.en.md`) e a spec se o
comportamento ou a documentação mudou, e rode o portão de qualidade.

## Gestão de dependências (uv)

O projeto **não tem dependência de runtime** — só a biblioteca padrão do
Python. O `uv` gerencia apenas o grupo `dev` (`ruff`, `black`, `mypy`,
`pytest`), travado em `uv.lock`. Commite `pyproject.toml` **e** `uv.lock`
juntos; nunca edite o lock à mão.

> **Cuidado:** `iniciar_lista.bat`/`.sh` preferem `uv run main.py`, mas caem
> para `python`/`python3 main.py` puro se o `uv` não estiver instalado — é
> assim que alguém sem `uv` (o público educacional do README) ainda consegue
> rodar o programa.
