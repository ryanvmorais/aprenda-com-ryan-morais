---
feature: Jogo da Forca via terminal
status: aprovado
date: 2026-11-20
related:
  - 001-jogo-da-forca/requirements.md
  - 001-jogo-da-forca/design.md
origin: concepção
---

# 001 — Jogo da Forca — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/jogo_da_forca/`, nesta ordem:
`uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, palavras e funções puras

- [ ] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `adivinhe_o_numero`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dele. `uv lock` gera o `uv.lock`. — RNF-01
- [ ] `.gitignore` e `.gitattributes`: cópias dos do `adivinhe_o_numero` (LF fixo no `.sh`).
      — RNF-02
- [ ] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-07
- [ ] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout`
      para UTF-8 no import, apelidos `Leitor` e `Sorteador` e as constantes `PALAVRAS`,
      `ERROS_MAXIMOS`, `FORCA` e `ALFABETO`. — RF-01, RNF-05, RNF-06, ADR-2, ADR-6, ADR-9
- [ ] `main.py`: `sortear_palavra(ja_sorteadas, sortear)`, sem repetir palavra e recomeçando a
      lista quando ela acaba. — RF-01, RF-02, ADR-4, ADR-6
- [ ] `main.py`: `remover_acentos(texto)`, com `unicodedata.normalize("NFD", ...)` e
      `unicodedata.combining`. — RF-04, ADR-3
- [ ] `main.py`: `mascarar_palavra(palavra, tentadas)` e `contar_erros(letras_da_palavra,
      tentadas)`. — RF-04, RF-05, ADR-4
- [ ] `main.py`: `Conferencia` (`NamedTuple`) e `conferir_entrada(entrada, tentadas)`, com o
      tamanho conferido antes do `in ALFABETO`. — RF-03, RNF-03, ADR-5
- [ ] `main.py`: `perguntar_jogar_de_novo(ler)`, com `s`/`n` sem diferenciar maiúscula e
      minúscula, e `exibir_placar(placar)`. — RF-07, RNF-03
- [ ] `tests/test_main.py`: casos da forma de `PALAVRAS` (5 temas, 8 palavras por tema, só letras
      minúsculas depois de tirar o acento, sem palavra repetida, com acento e com "ç") e de
      `FORCA` (7 desenhos), de `sortear_palavra` (a palavra sorteada entra em `ja_sorteadas` e
      sai das opções seguintes, a lista recomeça quando acaba), de `remover_acentos` (vogais
      acentuadas, "ç", texto sem acento), de `mascarar_palavra` (nenhuma letra, parte, todas, com
      a grafia original em maiúsculas), de `contar_erros`, de `conferir_entrada` (minúscula,
      maiúscula, acentuada, "ç", com espaços, vazia, duas letras, número, símbolo, repetida com e
      sem acento), de `perguntar_jogar_de_novo` (`s`, `S`, `n`, `N`, inválida) e de
      `exibir_placar`, com leitor e sorteador falsos por parâmetro. — RF-01, RF-02, RF-03, RF-04,
      RF-05, RF-07, RNF-03, RNF-06
- [ ] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `jogo_da_forca` à matriz `projeto` e atualiza a contagem de projetos citada no comentário
      do cache. `../../.github/dependabot.yml`: entrada `uv` para `/mini_projetos/jogo_da_forca`,
      no formato das outras. — RNF-01
- [ ] Portão de qualidade. —

## Etapa 2 — Partida, laço principal e atalhos

- [ ] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros).
      — RF-08, ADR-7
- [ ] `main.py`: `exibir_jogo(tema, palavra, tentadas, mensagem)`, com o tema, o desenho, a
      palavra mascarada, as letras tentadas em ordem alfabética, os erros restantes e a mensagem
      da tentativa anterior. — RF-05, RF-08
- [ ] `main.py`: `jogar_partida(tema, palavra, ler)`, com o laço `while` que limpa a tela,
      redesenha, lê e confere a entrada, e o último quadro com a vitória ou a derrota que revela
      a palavra. — RF-03, RF-04, RF-06, RF-08, ADR-4
- [ ] `main.py`: `main(sortear, ler)`, com o conjunto das palavras sorteadas, o placar, o "jogar
      de novo", o placar final e o `try`/`except (KeyboardInterrupt, EOFError)` com a despedida.
      Guard `if __name__ == "__main__"` chamando `main()`. — RF-02, RF-07, RNF-04, ADR-1, ADR-8,
      ADR-10
- [ ] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de
      `exibir_jogo` (sem tentativa, com letras tentadas fora de ordem, com mensagem) e de
      `jogar_partida` (vitória sem erro, vitória com erros, derrota no sexto erro que revela a
      palavra, letra repetida e entrada inválida que não contam como erro, letra sem acento que
      revela a acentuada, "c" que revela o "ç") e de `main()` (sessão de duas partidas sem
      repetir palavra, placar final, saída por `KeyboardInterrupt` e por `EOFError` sem stack
      trace). — RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-08, RNF-04
- [ ] `iniciar_jogo.bat` e `iniciar_jogo.sh`: atalhos no formato dos do `adivinhe_o_numero`
      (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [ ] Conferência manual: duas partidas no terminal (uma vitória e uma derrota), a limpeza de
      tela a cada jogada e a saída redirecionada para arquivo sem `UnicodeEncodeError`. — RF-08,
      RNF-05
- [ ] Portão de qualidade. —

## Etapa 3 — Documentação do projeto

- [ ] `tests/test_impessoalidade.py` e `tests/test_readme_en.py`: cópias dos do
      `adivinhe_o_numero`. — RNF-07
- [ ] `assets/jogo-da-forca-python-terminal-sessao.svg`: animação de uma sessão real do
      `main.py`, com as entradas de um roteiro e o sorteio fixo, no visual das outras animações e
      na largura de 52 colunas (ou na menor acima disso em que a linha mais longa caiba sem
      quebrar); quem pede movimento reduzido vê a última tela parada. — RNF-07
- [ ] `README.md`: mesmas seções e na mesma ordem do `README.md` do `adivinhe_o_numero`, abrindo
      com a animação e os badges, com "Atividades para praticar" e "Continue praticando", que
      aponta para os outros mini-projetos. — RF-01 a RF-08
- [ ] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-07
- [ ] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `adivinhe_o_numero` (visão geral, comandos,
      arquitetura e convenções). — RNF-07
- [ ] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-07
- [ ] `LICENSE`, `CODE_OF_CONDUCT.md` e `SECURITY.md`: cópias dos do `adivinhe_o_numero`.
      `CONTRIBUTING.md`: no formato do `adivinhe_o_numero`, com o nome deste projeto. — RNF-07
- [ ] Portão de qualidade. —

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [ ] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (strings, conjuntos e acentos com `unicodedata`). — RNF-07
- [ ] `specs/001-jogo-da-forca/`: `Desvios` e `Notas de implementação` no `design.md`, se houver
      o que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`. — RNF-07
- [ ] Portão de qualidade. —
