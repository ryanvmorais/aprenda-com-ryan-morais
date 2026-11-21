---
feature: Cifra de César via terminal, com cifrar, decifrar e quebrar por força bruta e por frequência
status: concluído
date: 2026-11-21
related:
  - 001-cifra-de-cesar/requirements.md
  - 001-cifra-de-cesar/design.md
origin: concepção
---

# 001 — Cifra de César — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/cifra_de_cesar/`, nesta ordem:
`uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, cifra e quebra

- [x] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do
      `verificador_de_forca_de_senha` (`requires-python = ">=3.12"`, `package = false`,
      `exclude-newer = "7 days"`), sem dependência de execução e com o grupo `dev` (ruff, black,
      mypy, pytest) nos mesmos pisos dele. `uv lock` gera o `uv.lock`. — RNF-01
- [x] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-09
- [x] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout` para
      UTF-8 no import, o apelido `Leitor` e as constantes `ALFABETO`, `CHAVES`, `MINIMO_LETRAS`,
      `LARGURA` e `OPCOES`. — RF-05, RF-06, RNF-05, RNF-06, ADR-1, ADR-11
- [x] `main.py`: `FREQUENCIAS`, com os 26 percentuais da tabela 1.2.1 do estudo, conferidos contra
      o PDF antes de versionar, e o comentário com o título, o autor, a instituição, a data e o
      endereço do estudo. — RF-09, RNF-08, ADR-7
- [x] `main.py`: `remover_acentos(texto)`, igual à do `jogo_da_forca`. — RF-04, ADR-4
- [x] `main.py`: `deslocar_letra(letra, chave)`, com o comentário que lê o `% 26` e o docstring
      sobre o resto de um número negativo no Python e em outras linguagens, `montar_tabela(chave)`,
      `deslocar(texto, chave)`, `cifrar(texto, chave)` e `decifrar(texto, chave)`. — RF-04, RF-06,
      RF-07, ADR-2, ADR-3
- [x] `main.py`: `tem_letras(texto)` e `forca_bruta(texto)`. — RF-03, RF-08
- [x] `main.py`: `contar_letras(texto)`, com o `Counter`, `pontuar(texto)` e
      `ordenar_chaves(texto)`. — RF-09, ADR-5
- [x] `tests/test_main.py`: casos de `remover_acentos` (cada vogal acentuada do português, o `ç`,
      as maiúsculas, e espaço, número, pontuação e emoji passando sem mudança), de `deslocar_letra`
      (a volta do `z` para o `a`, e do `a` para o `z` com a chave negativa), de `cifrar`
      (`Ola, Mundo!` com a chave 3 vira `Rod, Pxqgr!`, as maiúsculas mantidas, `ß` passando sem
      mudança), de `decifrar` (desfaz `cifrar` para as 25 chaves, devolvendo o texto sem acentos),
      de `tem_letras` (vazio, `2026!`, `ç`), de `forca_bruta` (25 tentativas, da chave 1 à 25, e a
      da chave certa igual ao texto original), de `contar_letras` e `pontuar` (valores conferidos à
      mão), de `ordenar_chaves` (frases de 30 letras ou mais, cifradas com cada uma das 25 chaves,
      com a chave certa em primeiro; o empate com a chave menor antes) e de `FREQUENCIAS` (as 26
      letras de `ALFABETO`, A 14,64, E 12,70 e O 10,78, a soma entre 99,9 e 100,1). — RF-03, RF-04,
      RF-06 a RF-09, RNF-06, RNF-08
- [x] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `cifra_de_cesar` à matriz `projeto` e atualiza a contagem de projetos citada no comentário do
      cache. `../../.github/dependabot.yml`: entrada `uv` para `/mini_projetos/cifra_de_cesar`, no
      formato das outras. — RNF-01, RNF-09
- [x] Portão de qualidade. — 130 passed; ruff/black/mypy verdes

## Etapa 2 — Textos, tela, laço principal e atalhos

- [x] `main.py`: `cortar(linha)` e `aviso_acentos(texto)`. — RF-04, RF-08, RF-09, ADR-8
- [x] `main.py`: `descrever_cifra(texto, chave)` e `descrever_decifra(texto, chave)`, com a chave,
      o texto inteiro e o aviso de acentos. — RF-04, RF-06, RF-07
- [x] `main.py`: `descrever_forca_bruta(texto)`, com as 25 linhas cortadas e a explicação no fim. —
      RF-08, ADR-8
- [x] `main.py`: `descrever_frequencia(texto)`, com as três letras mais comuns, a linha das mais
      comuns do português, a chave mais provável com o texto inteiro, as duas alternativas cortadas
      e o aviso de texto curto abaixo de `MINIMO_LETRAS`. — RF-09, ADR-5, ADR-6, ADR-8
- [x] `main.py`: `eh_numero(texto)` e `conferir_opcao(entrada)`, iguais às do verificador, e
      `conferir_chave(entrada)`. — RF-02, RF-05, RNF-03
- [x] `main.py`: `pedir_texto(ler)`, sem `strip()`, e `opcao_cifrar(ler)`, `opcao_decifrar(ler)`,
      `opcao_forca_bruta(ler)` e `opcao_frequencia(ler)`, com as mensagens do texto sem letras e da
      chave inválida. — RF-03, RF-05 a RF-09, RNF-07
- [x] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros) e
      `exibir_tela(resultado)`, com o título, o resultado da ação anterior e o menu numerado. —
      RF-01, ADR-9
- [x] `main.py`: `main(ler)`, com `ler=input` como padrão, o laço do menu, o `if`/`elif` das
      opções, a opção inválida, o Sair e o `try`/`except (KeyboardInterrupt, EOFError)` com a
      despedida. Guard `if __name__ == "__main__"` chamando `main()`. — RF-01, RF-02, RF-10,
      RNF-04, RNF-06, RNF-07, ADR-10, ADR-12
- [x] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de `cortar` (no
      limite de `LARGURA` e um caractere acima), de `aviso_acentos` (com e sem acento), dos textos
      `descrever_*` (cada item do RF-06 ao RF-09, as três letras e as três chaves, o aviso de texto
      curto com 29 letras e não com 30), de `conferir_opcao` (de 1 a 5, vazia, `0`, `9`, `abc`,
      `٣`), de `conferir_chave` (de 1 a 25, vazia, `0`, `26`, `-3`, `três`, ` 3 `), das opções (o
      texto vazio e o sem letras nas quatro, a chave inválida, os espaços do começo e do fim
      mantidos), da largura máxima de 54 colunas nos textos do programa, nos pedidos e no quadro
      inteiro com um texto curto, e de `main()` (a ordem do quadro, cada opção, a opção inválida, a
      saída pelo menu, e a saída por `KeyboardInterrupt` e por `EOFError`, no menu, no texto e na
      chave, sem stack trace). Um teste com o módulo `ast` confere que o `main.py` só importa
      `__future__`, `collections`, `collections.abc`, `os`, `string`, `sys` e `unicodedata`, não
      chama `open`, `read_text`, `write_text`, `read_bytes` nem `write_bytes` e não lê `sys.argv`.
      — RF-01 a RF-10, RNF-03, RNF-04, RNF-06, RNF-07
- [x] `iniciar_cifra.bat` e `iniciar_cifra.sh`: atalhos no formato dos do
      `verificador_de_forca_de_senha` (`uv run main.py`, com `python`/`python3` como
      alternativa). — RNF-02
- [x] Conferência manual: uma sessão no terminal que cifra um texto com acentos, decifra com a
      chave, quebra o texto cifrado pela força bruta e pela frequência (um texto longo e um curto,
      com o aviso), com uma opção inválida, uma chave inválida e um texto sem letras no meio, e
      sai; o Ctrl+C no pedido do texto e no da chave; a limpeza de tela a cada volta do menu; a
      saída redirecionada para arquivo sem `UnicodeEncodeError`; e o `git status` limpo depois da
      sessão, sem arquivo criado. — RF-01, RF-03 a RF-09, RNF-02, RNF-04, RNF-05, RNF-07
- [x] Portão de qualidade. — 259 passed; ruff/black/mypy verdes

## Etapa 3 — Documentação do projeto

- [x] `tests/test_readme_en.py`: cópia do arquivo do `verificador_de_forca_de_senha`. — RNF-09
- [x] `assets/cifra-de-cesar-python-terminal-sessao.svg`: animação de uma sessão real do `main.py`,
      com as entradas de um roteiro, no visual das outras animações e na largura de 54 colunas (ou
      na menor acima de 52 em que a linha mais longa caiba sem quebrar), com textos que caibam
      nessa largura; quem pede movimento reduzido vê a última tela parada. — RNF-09
- [x] `README.md`: mesmas seções e na mesma ordem do `README.md` do
      `verificador_de_forca_de_senha`, abrindo com a animação e os badges e com o aviso de que a
      cifra de César não protege nada; o "Guia de Implementação" explica o `ord`, o `chr` e o
      `% 26` com a volta do Z para o A, a chave negativa para decifrar, a tabela do
      `str.maketrans`, a retirada dos acentos com o `unicodedata`, a força bruta sobre as 25 chaves
      (e por que uma chave de 128 bits não se testa assim), o `Counter` e a pontuação pela
      frequência, com a medição que a escolheu e a fonte da tabela, e o aviso de texto curto; com
      "Atividades para praticar" e "Continue praticando", que aponta para os outros mini-projetos;
      a linha "Contribua com código" aponta para o `CONTRIBUTING.md` da raiz e traz as regras
      próprias do projeto. — RF-01 a RF-10, RNF-07, RNF-08, RNF-09, ADR-2, ADR-3, ADR-5, ADR-6
- [x] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-09
- [x] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `verificador_de_forca_de_senha` (visão geral,
      comandos, arquitetura e convenções), com os cuidados da `FREQUENCIAS` copiada do estudo sem
      alteração (o teste confere as 26 letras e a soma), da troca de método de pontuação, que muda
      o ADR-5 e o `MINIMO_LETRAS` junto, e da lista de `import` que o teste do RNF-07 confere. —
      RNF-07, RNF-08, RNF-09, ADR-5, ADR-6, ADR-7
- [x] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-09
- [x] `LICENSE`: a licença MIT do `verificador_de_forca_de_senha`, sem a seção da lista de senhas
      comuns. — RNF-09
- [x] Portão de qualidade. — 2026-11-21: `ruff check`, `black --check` e `mypy` limpos;
      `pytest` com 265 casos verdes (259 do `test_main.py` e 6 do `test_readme_en.py`).

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [x] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (`ord` e `chr`, aritmética modular, força bruta e frequência das letras com `Counter`). —
      RNF-09
- [x] `specs/001-cifra-de-cesar/`: `Desvios` e `Notas de implementação` no `design.md`, se houver o
      que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`. — RNF-09
- [x] Portão de qualidade. — 2026-11-21: `ruff check`, `black --check` e `mypy` limpos;
      `pytest` com 265 casos verdes.
