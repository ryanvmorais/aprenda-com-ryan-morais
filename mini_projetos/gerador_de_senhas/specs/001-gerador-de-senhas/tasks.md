---
feature: Gerador de senhas e frases-senha via terminal, com a entropia de cada uma
status: concluído
date: 2026-11-20
related:
  - 001-gerador-de-senhas/requirements.md
  - 001-gerador-de-senhas/design.md
origin: concepção
---

# 001 — Gerador de Senhas — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/gerador_de_senhas/`, nesta
ordem: `uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, sorteio e entropia

- [x] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `validador_de_cpf`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dele. `uv lock` gera o `uv.lock`. — RNF-01
- [x] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-09
- [x] `palavras.txt`: cópia byte a byte do `bip-0039/portuguese.txt` do repositório
      `bitcoin/bips`, no commit `d353c54154bac64a88eb18cf2d47d15ead083de4`, conferida pelo SHA-256
      do design antes de versionar. — RF-08, RNF-08, ADR-6
- [x] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout`
      para UTF-8 no import, os apelidos `Leitor` e `Escolhedor` (com o comentário de onde vem a
      assinatura) e as constantes `TIPOS`, `PARECIDOS`, os tamanhos e as quantidades de palavras
      (padrão, mínimo e máximo), `SEPARADOR`, `SEMENTE_DEMONSTRACAO`, `ARQUIVO_PALAVRAS` e
      `OPCOES`. — RF-03, RF-06, RF-08, RNF-05, RNF-06, ADR-2, ADR-11
- [x] `main.py`: `montar_grupos(tipos, evitar_parecidos)`, `tem_um_de_cada(senha, grupos)` e
      `gerar_senha(tamanho, grupos, escolher)`, com o novo sorteio da senha inteira quando falta um
      tipo (e o comentário que explica por que não se força a posição). — RF-03, RF-04, RF-05,
      RF-06, ADR-3, ADR-4
- [x] `main.py`: `carregar_palavras(arquivo)`, com `Path.read_text(encoding="utf-8")`, e
      `gerar_frase(quantidade, palavras, escolher)`. — RF-08, ADR-6
- [x] `main.py`: `calcular_entropia(quantidade, tamanho_alfabeto)` e
      `descrever_entropia(quantidade, tamanho_alfabeto)`, com `=` e sem casa decimal no resultado
      inteiro e `≈` com uma casa decimal e vírgula nos outros. — RF-07, ADR-5
- [x] `tests/test_main.py`: casos de `montar_grupos` (cada tipo, os quatro com 94 caracteres, sem
      os parecidos com 88 e nenhum de `PARECIDOS`), de `tem_um_de_cada` (senhas montadas à mão), de
      `gerar_senha` com `random.Random(2026).choice` (milhares de senhas só com caracteres dos
      grupos, pelo menos um de cada e os quatro tipos na primeira posição; um sorteador falso com
      uma senha só de letras e depois uma com número exercita o novo sorteio), de `gerar_frase`
      (a quantidade de palavras, o hífen, toda palavra da lista), de `carregar_palavras` com o
      `palavras.txt` (2048 palavras distintas, todas de `[a-z]`, e o SHA-256 do arquivo) e de
      `calcular_entropia` e `descrever_entropia` (`16 × log2(94) ≈ 104,9 bits`, um alfabeto só de
      números, os alfabetos sem os parecidos e `7 × log2(2048) = 77 bits`). — RF-03, RF-05, RF-06,
      RF-07, RF-08, RNF-06, RNF-08
- [x] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `gerador_de_senhas` à matriz `projeto` e atualiza a contagem de projetos citada no comentário
      do cache. `../../.github/dependabot.yml`: entrada `uv` para
      `/mini_projetos/gerador_de_senhas`, no formato das outras. — RNF-01, RNF-09
- [x] Portão de qualidade. — 2026-11-20, rodado uma vez para as Etapas 1 e 2, implementadas
      juntas: `ruff check`, `black --check` e `mypy` limpos; `pytest` com 128 casos verdes.

## Etapa 2 — Perguntas, textos, tela, laço principal e atalhos

- [x] `main.py`: `conferir_opcao(entrada)`, `conferir_numero(entrada, padrao, minimo, maximo)` e
      `conferir_sim_nao(entrada, padrao)`, com `isascii()` e `isdecimal()` antes do `int()`. —
      RF-02, RF-04, RF-08, RNF-03
- [x] `main.py`: `perguntar_numero(ler, pedido, padrao, minimo, maximo)` e
      `perguntar_sim_nao(ler, pedido, padrao)`, que repetem a pergunta com a mensagem da recusa
      até a resposta ser aceita. — RF-04, RF-08, RNF-03, ADR-8
- [x] `main.py`: `descrever_gerada(titulo, gerada, quantidade, tamanho_alfabeto)`, com a senha ou
      a frase sozinha na linha, e `explicar_random(escolher)`, com dois `random.Random` novos na
      `SEMENTE_DEMONSTRACAO`, as duas senhas do `escolher`, a explicação do RF-09 e o comentário
      que mostra a forma com `random.seed`; nenhuma linha, fora as das senhas e da frase, acima de
      54 colunas. — RF-03, RF-07, RF-08, RF-09, ADR-7
- [x] `main.py`: `opcao_senha_forte(escolher)`, `opcao_senha_personalizada(ler, escolher)`, com a
      recusa quando nenhum tipo é escolhido, e `opcao_frase_senha(ler, escolher, palavras)`. —
      RF-03, RF-04, RF-05, RF-06, RF-08
- [x] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros) e
      `exibir_tela(resultado)`, com o título, o resultado da ação anterior e o menu numerado. —
      RF-01, ADR-9
- [x] `main.py`: `main(ler, escolher, palavras)`, com `ler=input` e `escolher=secrets.choice` como
      padrão, a lista carregada quando não é passada, o laço do menu, o `if`/`elif` das opções, a
      opção inválida, o Sair e o `try`/`except (KeyboardInterrupt, EOFError)` com a despedida.
      Guard `if __name__ == "__main__"` chamando `main()`. — RF-01, RF-02, RF-10, RNF-04, RNF-06,
      RNF-07, ADR-1, ADR-2, ADR-10, ADR-12
- [x] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de
      `conferir_opcao` (de 1 a 5, vazia, `0`, `9`, `abc`, `٣`), de `conferir_numero` (Enter, os
      limites 8 e 64 e 5 e 12, `7`, `65`, `4`, `13`, `abc`, `12.5`), de `conferir_sim_nao` (Enter
      com cada padrão, `s`, `sim`, `n`, `não`, `nao`, em maiúsculas e minúsculas, e uma resposta
      inválida), das perguntas (a recusa com a mensagem e a pergunta repetida, sem perder as
      respostas anteriores), de `descrever_gerada` e `explicar_random` (as duas senhas do `random`
      iguais, as do `escolher` diferentes, a explicação), de cada `opcao_*` (a senha forte com 16
      caracteres e os quatro tipos, a personalizada com os tipos escolhidos e sem os parecidos, a
      recusa sem nenhum tipo, a frase com a quantidade pedida), da largura máxima de 54 colunas nos
      textos, e de `main()` (a ordem do quadro, cada opção, a opção inválida, a saída pelo menu, e
      a saída por `KeyboardInterrupt` e por `EOFError`, no menu e no meio das perguntas, sem stack
      trace; o padrão do `escolher` é o `secrets.choice`). Um teste com o módulo `ast` confere que
      o `main.py` só importa `__future__`, `collections.abc`, `math`, `os`, `pathlib`, `random`,
      `secrets`, `string` e `sys`, não chama `open`, `write_text` nem `write_bytes` e não lê
      `sys.argv`. — RF-01 a RF-10, RNF-03, RNF-04, RNF-06, RNF-07
- [x] `iniciar_gerador.bat` e `iniciar_gerador.sh`: atalhos no formato dos do `validador_de_cpf`
      (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [x] Conferência manual: uma sessão no terminal que gera uma senha forte, uma personalizada só
      com números e minúsculas, sem os parecidos e com uma resposta inválida no meio, uma
      frase-senha de 5 palavras e a demonstração, e sai; a limpeza de tela a cada volta do menu; o
      programa chamado de outra pasta (`python mini_projetos/gerador_de_senhas/main.py`), que acha
      o `palavras.txt`; a saída redirecionada para arquivo sem `UnicodeEncodeError`; e o
      `git status` limpo depois da sessão, sem arquivo criado. — RF-01, RF-04, RF-08, RF-09,
      RNF-02, RNF-05, RNF-07
- [x] Portão de qualidade. — 2026-11-20: `ruff check`, `black --check` e `mypy` limpos;
      `pytest` com 128 casos verdes.

## Etapa 3 — Documentação do projeto

- [x] `tests/test_readme_en.py`: cópia do arquivo do `validador_de_cpf`. — RNF-09
- [x] `assets/gerador-de-senhas-python-terminal-sessao.svg`: animação de uma sessão real do
      `main.py`, com as entradas de um roteiro e um sorteio de semente fixa, no visual das outras
      animações e na largura de 54 colunas (ou na menor acima de 52 em que a linha mais longa caiba
      sem quebrar); quem pede movimento reduzido vê a última tela parada. As senhas da sessão são
      só as do sorteio com semente fixa. — RNF-07, RNF-09
- [x] `README.md`: mesmas seções e na mesma ordem do `README.md` do `validador_de_cpf`, abrindo
      com a animação e os badges; o "Guia de Implementação" explica por que o `secrets` e não o
      `random` (com o aviso da documentação do Python), as constantes do módulo `string`, a regra
      "um de cada tipo" sorteando de novo, a entropia com a conta e a diferença da fórmula para a
      real, e a frase-senha com a lista do BIP-39, com a origem e a licença, e diz que nenhuma
      senha é guardada; com "Atividades para praticar" e "Continue praticando", que aponta para os
      outros mini-projetos; a linha "Contribua com código" aponta para o `CONTRIBUTING.md` da raiz
      e traz as regras próprias do projeto. — RF-01 a RF-10, RNF-07, RNF-08, RNF-09, ADR-3, ADR-5
- [x] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-09
- [x] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `validador_de_cpf` (visão geral, comandos,
      arquitetura e convenções), com os cuidados do sorteio só pelo `escolher` (o `random` só na
      demonstração), da regra "um de cada tipo" que sorteia de novo, do `palavras.txt` que não se
      edita (o teste confere o SHA-256) e da lista de `import` que o teste do RNF-07 confere. —
      RNF-07, RNF-08, RNF-09, ADR-2, ADR-3, ADR-6
- [x] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-09
- [x] `LICENSE`: a licença MIT do `validador_de_cpf`, seguida da seção da lista de palavras, com a
      origem (repositório, arquivo e commit), a licença MIT da BIP-39 e os autores da BIP-39 e da
      lista portuguesa. — RNF-08, RNF-09
- [x] Portão de qualidade. — 2026-11-20: `ruff check`, `black --check` e `mypy` limpos;
      `pytest` com 134 casos verdes (128 do `test_main.py` e 6 do `test_readme_en.py`).

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [x] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (`secrets` x `random`, as constantes de `string` e a entropia). — RNF-09
- [x] `specs/001-gerador-de-senhas/`: `Desvios` e `Notas de implementação` no `design.md`, se
      houver o que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`. — RNF-09
- [x] Portão de qualidade. — 2026-11-20: `ruff check`, `black --check` e `mypy` limpos;
      `pytest` com 134 casos verdes.
