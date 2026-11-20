---
feature: Jogo Adivinhe o Número via terminal
status: em andamento
date: 2026-11-20
related:
  - 001-adivinhe-o-numero/requirements.md
  - 001-adivinhe-o-numero/design.md
origin: concepção
---

# 001 — Adivinhe o Número — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/adivinhe_o_numero/`, nesta
ordem: `uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, níveis e entrada validada

- [x] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `pedra_papel_tesoura`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dos outros mini-projetos. `uv lock` gera o `uv.lock`. — RNF-01
- [x] `.gitignore` e `.gitattributes`: cópias dos do `pedra_papel_tesoura` (LF fixo no `.sh`).
      — RNF-02
- [x] `tests/__init__.py`: vazio, como nos outros mini-projetos.
- [x] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout`
      para UTF-8 no import, apelidos `Leitor` e `Sorteador`, `Nivel` (`NamedTuple`) e a constante
      `NIVEIS`. — RNF-05, RNF-06, ADR-2, ADR-3, ADR-6
- [x] `main.py`: `escolher_nivel(ler)`, com o menu montado a partir de `NIVEIS`. — RF-01, RNF-03
- [x] `main.py`: `ler_palpite(nivel, tentativa, ler)`, com `int()` em `try`/`except ValueError` e
      a conferência da faixa. — RF-03, RNF-03
- [x] `main.py`: `atualizar_recorde(recordes, nome_nivel, tentativas)` e
      `exibir_recordes(recordes)`. — RF-06, RF-07, ADR-8
- [x] `main.py`: `perguntar_jogar_de_novo(ler)`, com `s`/`n` sem diferenciar maiúscula e
      minúscula. — RF-07, RNF-03
- [x] `tests/test_main.py`: casos de `escolher_nivel` (válidos, fora do menu, texto, vazio),
      `ler_palpite` (válido, texto, decimal, vazio, fora da faixa, sem contar a entrada inválida),
      `atualizar_recorde` (primeiro recorde, recorde batido, empate, pior resultado),
      `exibir_recordes` (com e sem vitória) e `perguntar_jogar_de_novo` (`s`, `S`, `n`, `N`,
      inválida), com leitor falso por parâmetro. — RF-01, RF-03, RF-06, RF-07, RNF-03, RNF-06
- [x] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `adivinhe_o_numero` à matriz `projeto` e atualiza a contagem de projetos citada no
      comentário do cache. `../../.github/dependabot.yml`: entrada `uv` para
      `/mini_projetos/adivinhe_o_numero`, no formato das outras. — RNF-01
- [x] Portão de qualidade. — 30 passed; ruff/black/mypy verdes

## Etapa 2 — Partida, laço principal e atalhos

- [x] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros).
      — RF-08, ADR-4
- [x] `main.py`: `jogar_partida(nivel, recorde, sortear, ler)`, com o sorteio na faixa, o laço
      `while` até o limite, a dica com as tentativas restantes, a vitória e a derrota que revela o
      número. — RF-02, RF-04, RF-05, RF-06
- [x] `main.py`: `main(sortear, ler)`, com o dicionário de recordes, a limpeza de tela antes do
      menu, o aviso de novo recorde, o "jogar de novo", o resumo final e o `try`/`except
      (KeyboardInterrupt, EOFError)` com a despedida. Guard `if __name__ == "__main__"` chamando
      `main()`. — RF-06, RF-07, RF-08, RNF-04, ADR-1, ADR-5, ADR-7
- [x] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de
      `jogar_partida` (extremos do sorteio por nível, dica "maior" e "menor" com as tentativas
      restantes, vitória na primeira e na última tentativa, derrota que revela o número, recorde
      exibido no início) e de `main()` (sessão de duas partidas com recorde, resumo final, saída
      por `KeyboardInterrupt` e por `EOFError` sem stack trace). — RF-02, RF-04, RF-05, RF-06,
      RF-07, RF-08, RNF-04
- [x] `iniciar_jogo.bat` e `iniciar_jogo.sh`: atalhos no formato dos do `pedra_papel_tesoura`
      (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [x] Conferência manual: uma partida por nível no terminal, a limpeza de tela entre partidas e
      a saída redirecionada para arquivo sem `UnicodeEncodeError`. — RF-08, RNF-05
- [x] Portão de qualidade. — 45 passed; ruff/black/mypy verdes

## Etapa 3 — Documentação do projeto

- [ ] `tests/test_impessoalidade.py` e `tests/test_readme_en.py`: cópias dos do
      `pedra_papel_tesoura`.
- [ ] `assets/adivinhe-o-numero-python-terminal-sessao.svg`: animação de uma sessão real do
      `main.py`, com as entradas de um roteiro e o sorteio fixo, no visual e na largura de 52
      colunas das outras animações; quem pede movimento reduzido vê a última tela parada.
- [ ] `README.md`: mesmas seções e na mesma ordem do `README.md` do `pedra_papel_tesoura`,
      abrindo com a animação e os badges, com "Atividades para praticar" e "Continue
      praticando". — RF-01 a RF-08
- [ ] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem.
- [ ] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `pedra_papel_tesoura` (visão geral,
      comandos, arquitetura e convenções).
- [ ] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos.
- [ ] `LICENSE`, `CODE_OF_CONDUCT.md` e `SECURITY.md`: cópias dos do `pedra_papel_tesoura`.
      `CONTRIBUTING.md`: no formato do `pedra_papel_tesoura`, com o nome deste projeto.
- [ ] Portão de qualidade. —

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [ ] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (`random`, laço `while` e validação de entrada).
- [ ] `specs/001-adivinhe-o-numero/`: `Desvios` e `Notas de implementação` no `design.md`, se
      houver o que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`.
- [ ] Portão de qualidade. —
