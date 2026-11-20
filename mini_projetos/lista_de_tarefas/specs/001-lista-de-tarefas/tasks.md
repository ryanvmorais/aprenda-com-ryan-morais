---
feature: Lista de Tarefas via terminal com arquivo JSON
status: aprovado
date: 2026-11-20
related:
  - 001-lista-de-tarefas/requirements.md
  - 001-lista-de-tarefas/design.md
origin: concepção
---

# 001 — Lista de Tarefas — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/lista_de_tarefas/`, nesta
ordem: `uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, arquivo e funções puras

- [ ] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `jogo_da_forca`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dele. `uv lock` gera o `uv.lock`. — RNF-01
- [ ] `.gitignore` e `.gitattributes`: cópias dos do `jogo_da_forca` (LF fixo no `.sh`); o
      `.gitignore` ganha uma seção para a lista de quem usa o programa, com `tarefas.json`,
      `tarefas.corrompido-*.json` e `tarefas.json.tmp`. — RNF-02, RNF-07, ADR-5
- [ ] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-08
- [ ] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout`
      para UTF-8 no import, o `TypedDict` `Tarefa`, a `NamedTuple` `Conferencia`, os apelidos
      `Leitor` e `Relogio` e as constantes `ARQUIVO_PADRAO` (com o comentário sobre a pasta do
      usuário num programa instalado), `TAMANHO_MAXIMO`, `CAMPOS` e `OPCOES`. — RF-01, RNF-05,
      RNF-06, ADR-2, ADR-4, ADR-8, ADR-11
- [ ] `main.py`: `validar_tarefas(dados)`, que confere a lista, as chaves exatas de `CAMPOS` e o
      tipo de cada campo, e lança `ValueError` com o motivo. — RF-02, ADR-6
- [ ] `main.py`: `guardar_corrompido(arquivo, agora)`, com o nome da cópia pela data e hora e o
      contador quando o nome já existe, e `carregar_tarefas(arquivo, agora)`, com o arquivo
      ausente, o válido e o `except ValueError` único (com o comentário sobre as subclasses).
      — RF-01, RF-02, RNF-05, ADR-6
- [ ] `main.py`: `salvar_tarefas(tarefas, arquivo)`, com `ensure_ascii=False`, `indent=2`,
      `encoding="utf-8"`, o `tarefas.json.tmp` na mesma pasta e o `Path.replace`. — RF-03,
      RNF-05, ADR-3, ADR-5
- [ ] `main.py`: `formatar_data(criada_em)` e `formatar_tarefa(numero, tarefa)`, com o número
      alinhado, a marca, a data e o texto. — RF-04
- [ ] `main.py`: `conferir_opcao(entrada)`, `conferir_texto(entrada)` e
      `conferir_numero(entrada, total)`, com `isdecimal()` antes do `int()` (e o comentário sobre
      o `isdigit()`). — RF-05, RF-06, RF-07, RF-09, RNF-03
- [ ] `tests/test_main.py`: casos, numa pasta `tmp_path` e com um relógio falso, de
      `validar_tarefas` (lista válida, vazia, que não é lista, item que não é dicionário, chave
      faltando, chave a mais, texto vazio, situação que não é `bool`, data inválida), de
      `carregar_tarefas` (arquivo ausente sem criar nada, arquivo válido com acentos, JSON
      inválido, arquivo que não é UTF-8, forma errada, nome da cópia com a data e a hora, cópia
      anterior preservada), de `salvar_tarefas` (gravar e carregar devolve a mesma lista, acentos
      legíveis no arquivo, nenhum temporário sobrando, arquivo anterior intacto quando a gravação
      do temporário falha), de `formatar_data`, de `formatar_tarefa` (pendente, concluída, número
      de um e de dois dígitos) e das três funções `conferir_*` (válida, vazia, só espaços, longa
      demais, fora do intervalo, não numérica, `"²"`). — RF-01, RF-02, RF-03, RF-04, RF-05, RF-06,
      RF-07, RF-09, RNF-03, RNF-05, RNF-06
- [ ] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `lista_de_tarefas` à matriz `projeto` e atualiza a contagem de projetos citada no
      comentário do cache. `../../.github/dependabot.yml`: entrada `uv` para
      `/mini_projetos/lista_de_tarefas`, no formato das outras. — RNF-01, RNF-08
- [ ] Portão de qualidade.

## Etapa 2 — Tela, ações, laço principal e atalhos

- [ ] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros) e
      `exibir_tela(tarefas, mensagem)`, com o título, a lista (ou a linha da lista vazia), a
      contagem de pendentes e concluídas, o menu numerado e a mensagem da ação anterior. — RF-04,
      ADR-9
- [ ] `main.py`: `ler_texto(ler, pedido)`, `ler_numero(ler, total)` e `confirmar(ler, pergunta)`,
      com os laços que imprimem a recusa e pedem de novo sem limpar a tela. — RF-06, RF-07, RF-09,
      RF-10, RNF-03
- [ ] `main.py`: `adicionar(tarefas, arquivo, ler, hoje)` e `alternar_conclusao(tarefas, arquivo,
      ler)`, cada uma gravando logo depois de alterar. — RF-03, RF-06, RF-07, RF-08, ADR-7
- [ ] `main.py`: `editar(tarefas, arquivo, ler)` e `remover(tarefas, arquivo, ler)`, com a
      confirmação `s`/`n` antes do `pop` e sem gravar no `n`. — RF-03, RF-07, RF-09, RF-10, ADR-7
- [ ] `main.py`: `main(ler, agora, arquivo)`, com a carga da lista, o aviso de arquivo corrompido
      como primeira mensagem, o laço do menu com o `if`/`elif` das opções, a opção inválida, o
      Sair e o `try`/`except (KeyboardInterrupt, EOFError)` com a despedida. Guard `if __name__ ==
      "__main__"` chamando `main()`. — RF-01, RF-02, RF-05, RF-11, RNF-04, ADR-1, ADR-7, ADR-10,
      ADR-12
- [ ] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de
      `exibir_tela` (lista com tarefas e contagem, lista vazia, com e sem mensagem), dos três
      leitores (recusa seguida de entrada válida; `s`, `S`, `n`, `N` e inválida), das ações
      (adicionar com a data de hoje e pendente, concluir e reabrir, editar sem mudar a situação
      nem a data, remover com `s` e com `n`, ação com a lista vazia sem pedir número nem criar o
      arquivo, cada alteração gravada no arquivo) e de `main()` (sessão que adiciona, conclui e
      sai, e abre de novo com a mesma lista; arquivo corrompido com o aviso na primeira tela;
      opção inválida; saída por `KeyboardInterrupt` e por `EOFError` sem stack trace e sem
      alterar o arquivo). — RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-08, RF-09, RF-10,
      RF-11, RNF-03, RNF-04, RNF-06
- [ ] `iniciar_lista.bat` e `iniciar_lista.sh`: atalhos no formato dos do `jogo_da_forca`
      (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [ ] Conferência manual: uma sessão no terminal que adiciona, conclui, reabre, edita e remove
      tarefas, fecha e abre de novo com a lista igual; um `tarefas.json` estragado à mão, que vira
      cópia com o aviso; a limpeza de tela a cada volta do menu; o programa chamado de outra pasta
      (`python mini_projetos/lista_de_tarefas/main.py`), usando o mesmo arquivo; e a saída
      redirecionada para arquivo sem `UnicodeEncodeError`. — RF-01, RF-02, RF-04, RNF-02, RNF-05,
      ADR-4
- [ ] Portão de qualidade.

## Etapa 3 — Documentação do projeto

- [ ] `tests/test_impessoalidade.py` e `tests/test_readme_en.py`: cópias dos do `jogo_da_forca`.
      — RNF-08
- [ ] `assets/lista-de-tarefas-python-terminal-sessao.svg`: animação de uma sessão real do
      `main.py`, com as entradas de um roteiro, a data fixa e uma pasta temporária, no visual das
      outras animações e na largura de 52 colunas (ou na menor acima disso em que a linha mais
      longa caiba sem quebrar); quem pede movimento reduzido vê a última tela parada. — RNF-08
- [ ] `README.md`: mesmas seções e na mesma ordem do `README.md` do `jogo_da_forca`, abrindo com a
      animação e os badges; o "Guia de Implementação" explica onde fica o `tarefas.json`, o
      formato dele, o que acontece com o arquivo corrompido e o porquê da gravação atômica, e diz
      que o arquivo fica fora do Git; com "Atividades para praticar" e "Continue praticando", que
      aponta para os outros mini-projetos. — RF-01 a RF-11, RNF-07
- [ ] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-08
- [ ] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `jogo_da_forca` (visão geral, comandos,
      arquitetura e convenções), com o cuidado do formato do `tarefas.json` (uma chave nova faz os
      arquivos antigos serem tratados como corrompidos). — RNF-08, ADR-6
- [ ] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-08
- [ ] `LICENSE`, `CODE_OF_CONDUCT.md` e `SECURITY.md`: cópias dos do `jogo_da_forca`.
      `CONTRIBUTING.md`: no formato do `jogo_da_forca`, com o nome deste projeto. — RNF-08
- [ ] Portão de qualidade.

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [ ] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (arquivo JSON, `pathlib` e gravação atômica). — RNF-08
- [ ] `specs/001-lista-de-tarefas/`: `Desvios` e `Notas de implementação` no `design.md`, se
      houver o que registrar; `status: concluído` nos três arquivos e na linha do índice do
      `specs/README.md`. — RNF-08
- [ ] Portão de qualidade.
