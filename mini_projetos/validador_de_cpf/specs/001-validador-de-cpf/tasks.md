---
feature: Validador de CPF via terminal, com a conta passo a passo
status: em andamento
date: 2026-11-20
related:
  - 001-validador-de-cpf/requirements.md
  - 001-validador-de-cpf/design.md
origin: concepção
---

# 001 — Validador de CPF — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/validador_de_cpf/`, nesta
ordem: `uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, cálculo e conferência

- [x] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `lista_de_tarefas`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dele. `uv lock` gera o `uv.lock`. — RNF-01
- [x] `.gitignore` e `.gitattributes`: cópias dos do `lista_de_tarefas` (LF fixo no `.sh`), sem a
      seção dos arquivos da lista, porque este programa não cria arquivo. — RNF-02, RNF-07
- [x] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-08
- [x] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout`
      para UTF-8 no import, as `NamedTuple` `Conta` e `Conferencia`, os apelidos `Leitor` e
      `Sorteador` e as constantes `SEPARADORES`, `TAMANHO_CPF`, `REGIOES_FISCAIS`, `AVISO_GERADO` e
      `OPCOES`. — RF-06, RF-08, RNF-05, RNF-06, ADR-4, ADR-9
- [x] `main.py`: `calcular_digito(algarismos)`, com os pesos de `range(10 - len(algarismos), 10)`,
      os produtos por list comprehension, o resto e o 10 valendo 0 (e o comentário que mostra a
      equivalência com a forma mais divulgada), e `calcular_digitos(base)`. — RF-04, ADR-2, ADR-3,
      ADR-4
- [x] `main.py`: `limpar_cpf(entrada)`, com os `SEPARADORES` descartados, o `isascii()` e o
      `isdigit()` (e o comentário com os exemplos `²` e `٣`), e as recusas na ordem do design, e
      `eh_sequencia_repetida(cpf)`. — RF-03, RF-05, RNF-03, ADR-5
- [x] `main.py`: `conferir_cpf(entrada)`, `formatar_cpf(cpf)` e `descrever_regiao(cpf)`. — RF-04,
      RF-05, RF-06, ADR-2
- [x] `main.py`: `gerar_cpf(sortear)`, com a base sorteada de novo quando os 9 algarismos saem
      iguais. — RF-08, ADR-6
- [x] `tests/test_main.py`: casos de `calcular_digito` e `calcular_digitos` (o exemplo da Receita
      Federal, com a base `280012389` e os dígitos `38`; restos 0, 1 e 10), da equivalência com a
      forma mais divulgada em 10.000 bases de `random.Random(2026)`, de `limpar_cpf` (com e sem
      pontuação, com espaços, letra, barra, `²`, `٣`, 10 e 12 algarismos, vazio e só pontuação, com
      o motivo de cada recusa), de `eh_sequencia_repetida` e `conferir_cpf` (as dez sequências
      repetidas, cada dígito verificador errado, o motivo sem os dígitos certos), de `formatar_cpf`,
      de `descrever_regiao` (os 10 valores do 9º dígito) e de `gerar_cpf` (cada CPF gerado passa
      em `conferir_cpf`; um sorteador falso com nove `7` seguidos de outra base exercita o novo
      sorteio). — RF-03, RF-04, RF-05, RF-06, RF-08, RNF-03, RNF-06
- [x] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `validador_de_cpf` à matriz `projeto` e atualiza a contagem de projetos citada no comentário
      do cache. `../../.github/dependabot.yml`: entrada `uv` para `/mini_projetos/validador_de_cpf`,
      no formato das outras. — RNF-01, RNF-08
- [x] Portão de qualidade. — 67 passed; ruff/black/mypy verdes.

## Etapa 2 — Textos, tela, laço principal e atalhos

- [x] `main.py`: `descrever_resultado(entrada)` e `descrever_gerado(cpf)`, com o CPF válido em
      uma linha e a região na seguinte, o inválido em duas linhas (o resultado e o motivo) e o
      `AVISO_GERADO`, sem nenhuma linha acima de 54 colunas. — RF-05, RF-06, RF-08
- [x] `main.py`: `descrever_conta(conta, digitado, ordem)` e `explicar_validacao(entrada)`, com as
      colunas de largura fixa, a linha da soma, da divisão, do resto e do dígito, a marca de que o
      dígito digitado confere ou não e a entrada recusada sem conta. — RF-05, RF-07, ADR-4
- [x] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros),
      `exibir_tela(resultado)`, com o título, o resultado da ação anterior e o menu numerado, e
      `conferir_opcao(entrada)`, com `isdecimal()` antes do `int()`. — RF-01, RF-02, ADR-7
- [x] `main.py`: `main(ler, sortear)`, com o laço do menu, o `if`/`elif` das opções, a opção
      inválida, o Sair e o `try`/`except (KeyboardInterrupt, EOFError)` com a despedida. Guard
      `if __name__ == "__main__"` chamando `main()`. — RF-01, RF-02, RF-09, RNF-04, RNF-07, ADR-1,
      ADR-8, ADR-10
- [x] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de
      `descrever_resultado` (válido com a região, cada motivo de recusa), de `descrever_conta` e
      `explicar_validacao` (as linhas da conta no exemplo da Receita Federal, o dígito que confere e
      o que não confere, a sequência repetida com a conta e a recusa, a entrada recusada sem conta),
      de `descrever_gerado` (número formatado, região e aviso), de `conferir_opcao` (de 1 a 4,
      vazia, `0`, `9`, `abc`, `²`), da largura máxima de 54 colunas nos textos, e de `main()` (a
      ordem do quadro, cada opção, a opção inválida, a saída pelo menu, e a saída por
      `KeyboardInterrupt` e por `EOFError` sem stack trace). Um teste com o módulo `ast` confere
      que o `main.py` só importa `__future__`, `collections.abc`, `os`, `random`, `sys` e `typing`
      e não chama `open`. — RF-01, RF-02, RF-05, RF-06, RF-07, RF-08, RF-09, RNF-03, RNF-04, RNF-06,
      RNF-07
- [x] `iniciar_validador.bat` e `iniciar_validador.sh`: atalhos no formato dos do
      `lista_de_tarefas` (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [x] Conferência manual: uma sessão no terminal que valida o exemplo da Receita Federal com e sem
      pontuação, um CPF com o dígito errado, uma sequência repetida no modo didático e uma entrada
      com letra, gera dois CPFs e sai; a limpeza de tela a cada volta do menu; o programa chamado de
      outra pasta (`python mini_projetos/validador_de_cpf/main.py`); a saída redirecionada para
      arquivo sem `UnicodeEncodeError`; e o `git status` limpo depois da sessão, sem arquivo criado.
      — RF-01, RF-03, RF-07, RF-08, RNF-02, RNF-05, RNF-07
- [x] Portão de qualidade. — 117 passed; ruff/black/mypy verdes.

## Etapa 3 — Documentação do projeto

- [ ] `tests/test_impessoalidade.py` e `tests/test_readme_en.py`: cópias dos do
      `lista_de_tarefas`. — RNF-08
- [ ] `assets/validador-de-cpf-python-terminal-sessao.svg`: animação de uma sessão real do
      `main.py`, com as entradas de um roteiro e um sorteio de semente fixa, no visual das outras
      animações e na largura de 54 colunas (ou na menor acima de 52 em que a linha mais longa caiba
      sem quebrar); quem pede movimento reduzido vê a última tela parada. Os CPFs da sessão são só
      o exemplo da Receita Federal, variações inválidas dele e o gerado pela semente. — RNF-07,
      RNF-08
- [ ] `README.md`: mesmas seções e na mesma ordem do `README.md` do `lista_de_tarefas`, abrindo
      com a animação e os badges; o "Guia de Implementação" explica a conta dos dois dígitos pela
      forma da Receita Federal, com a fonte, a equivalência com a forma mais divulgada, a sequência
      repetida, o `isascii()` junto do `isdigit()` e a região fiscal do 9º dígito, e diz que o
      número gerado pode coincidir com o CPF de uma pessoa real e que nenhum CPF digitado é
      guardado; com "Atividades para praticar" e "Continue praticando", que aponta para os outros
      mini-projetos. — RF-01 a RF-09, RNF-07, ADR-3, ADR-5
- [ ] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-08
- [ ] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `lista_de_tarefas` (visão geral, comandos,
      arquitetura e convenções), com os cuidados dos pesos que terminam em 9 (a regra que serve aos
      dois dígitos), dos exemplos que só usam o CPF da Receita Federal e da lista de `import` que o
      teste do RNF-07 confere. — RNF-07, RNF-08, ADR-3
- [ ] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-08
- [ ] `LICENSE`, `CODE_OF_CONDUCT.md` e `SECURITY.md`: cópias dos do `lista_de_tarefas`.
      `CONTRIBUTING.md`: no formato do `lista_de_tarefas`, com o nome deste projeto. — RNF-08
- [ ] Portão de qualidade.

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [ ] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (algoritmo dos dígitos verificadores, resto da divisão e funções puras). — RNF-08
- [ ] `specs/001-validador-de-cpf/`: `Desvios` e `Notas de implementação` no `design.md`, se
      houver o que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`. — RNF-08
- [ ] Portão de qualidade.
