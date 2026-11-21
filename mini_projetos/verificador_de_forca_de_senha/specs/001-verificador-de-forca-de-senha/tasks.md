---
feature: Verificador de força de senha via terminal, com nota, entropia estimada e sugestões
status: em andamento
date: 2026-11-20
related:
  - 001-verificador-de-forca-de-senha/requirements.md
  - 001-verificador-de-forca-de-senha/design.md
origin: concepção
---

# 001 — Verificador de Força de Senha — Tasks

O portão de qualidade de cada etapa roda, dentro de `mini_projetos/verificador_de_forca_de_senha/`,
nesta ordem: `uv run ruff check .`, `uv run black --check .`, `uv run mypy` e `uv run pytest`.

## Etapa 1 — Ambiente, regras e nota

- [x] `pyproject.toml`: manifesto gerenciado pelo `uv`, no formato do `validador_de_cpf`
      (`requires-python = ">=3.12"`, `package = false`, `exclude-newer = "7 days"`), sem
      dependência de execução e com o grupo `dev` (ruff, black, mypy, pytest) nos mesmos pisos
      dele. `uv lock` gera o `uv.lock`. — RNF-01
- [x] `tests/__init__.py`: vazio, como nos outros mini-projetos. — RNF-09
- [x] `senhas_comuns.txt`: cópia byte a byte do
      `Passwords/Common-Credentials/Language-Specific/Portugese_Pwdb_common-password-list-top-150.txt`
      do repositório `danielmiessler/SecLists`, no commit
      `fef30127d19485fb91f390a3c8c535aefbd50047`, conferida pelo SHA-256 do design antes de
      versionar. — RF-06, RNF-08, ADR-6
- [x] `main.py`: docstring do módulo com a estrutura do código, reconfiguração de `sys.stdout` para
      UTF-8 no import, o apelido `Leitor` (com o comentário de que o `input` e o `getpass.getpass`
      têm essa assinatura), a `NamedTuple` `Analise` e as constantes `TIPOS`, `SEQUENCIAS`,
      `REPETICAO`, `LIMITES`, `NOMES`, `TAMANHO_MINIMO`, `NOTA_MAXIMA_CURTA`,
      `ARQUIVO_SENHAS_COMUNS` e `OPCOES`. — RF-04, RF-05, RF-07, RNF-05, RNF-06, ADR-1, ADR-2,
      ADR-12
- [x] `main.py`: `classificar(senha)`, com um `any()` por tipo. — RF-04
- [x] `main.py`: `achar_repeticoes(senha)`, com a `REPETICAO` e o comentário que lê o `(.)\1{2,}`
      peça por peça, `achar_sequencias(senha)`, com as janelas de 3 e o `in` contra cada
      sequência e o contrário dela, `juntar_trechos(trechos)` e
      `contar_caracteres(tamanho, trechos)`. — RF-05, ADR-3, ADR-4
- [x] `main.py`: `carregar_senhas_comuns(arquivo)`, com `Path.read_text(encoding="utf-8")` e o
      conjunto das linhas em minúsculas. — RF-06, ADR-6
- [x] `main.py`: `calcular_entropia(quantidade, tamanho_alfabeto)` e
      `descrever_entropia(quantidade, tamanho_alfabeto)`, iguais às do `gerador_de_senhas`, com
      `Entropia estimada:` no começo da linha. — RF-07, RF-08, ADR-7
- [x] `main.py`: `dar_nota(bits, tamanho, comum)`, `analisar(senha, comuns)` e
      `faltam_caracteres(analise)`. — RF-04, RF-05, RF-06, RF-07, RF-09, ADR-5, ADR-8
- [x] `tests/test_main.py`: casos de `classificar` (cada tipo, letra acentuada, espaço), dos
      trechos (`aaa`, `1111`, `abc`, `cba`, `123`, `987`, `qwe`, `asd`, `ABC`, `aAa`, `aa`, `ab`,
      `aaabc`, `aaabbb`) e de `contar_caracteres`, de
      `carregar_senhas_comuns` com o `senhas_comuns.txt` (as 150 linhas e o SHA-256 do arquivo), de
      `calcular_entropia` e `descrever_entropia` (`16 × log2(94) ≈ 104,9 bits` e
      `7 × log2(94) ≈ 45,9 bits`), de `dar_nota` (as fronteiras 27,9 e 28, 35,9 e 36, 59,9 e 60,
      79,9 e 80, a senha comum e a de 7 caracteres), de `analisar` (uma senha da lista em
      maiúsculas e em minúsculas, uma que só contém uma da lista, os espaços contando, a senha
      forte padrão do gerador com nota 4) e de `faltam_caracteres`. — RF-03 a RF-07, RF-09,
      RNF-06, RNF-08
- [x] `../../.github/workflows/ci.yml` e `../../.github/workflows/pip-audit.yml`: acrescenta
      `verificador_de_forca_de_senha` à matriz `projeto` e atualiza a contagem de projetos citada
      no comentário do cache. `../../.github/dependabot.yml`: entrada `uv` para
      `/mini_projetos/verificador_de_forca_de_senha`, no formato das outras. — RNF-01, RNF-09
- [x] Portão de qualidade. — rodado junto com o da Etapa 2, no mesmo `main.py`: 162 passed;
      ruff/black/mypy verdes

## Etapa 2 — Textos, tela, laço principal e atalhos

- [x] `main.py`: `sugerir(analise)`, com a senha comum trocando as outras sugestões e a linha de
      nada a melhorar quando não sobra nenhuma, e `descrever_analise(analise)`, na ordem do quadro
      do design, sem receber a senha. — RF-08, RF-09, ADR-8
- [x] `main.py`: `EXEMPLOS`, com as cinco senhas do design e a explicação de cada uma, e
      `descrever_exemplos(comuns)`, com a nota calculada por `analisar` e as linhas sobre a
      estimativa por regras. — RF-10, ADR-9
- [x] `main.py`: `eh_numero(texto)` e `conferir_opcao(entrada)`, iguais às do gerador. — RF-02,
      RNF-03
- [x] `main.py`: `opcao_verificar(ler_senha, comuns)`, com o pedido que avisa que a senha não
      aparece, o aviso da senha vazia e a senha sem `strip()`. — RF-03, RNF-07, ADR-8
- [x] `main.py`: `limpar_tela()` com `os.system` (`cls` no Windows, `clear` nos outros) e
      `exibir_tela(resultado)`, com o título, o resultado da ação anterior e o menu numerado. —
      RF-01, ADR-10
- [x] `main.py`: `main(ler, ler_senha, comuns)`, com `ler=input` e `ler_senha=getpass.getpass`
      como padrão, a lista carregada quando não é passada, o laço do menu, o `if`/`elif` das
      opções, a opção inválida, o Sair e o `try`/`except (KeyboardInterrupt, EOFError)` com a
      despedida. Guard `if __name__ == "__main__"` chamando `main()`. — RF-01, RF-02, RF-11,
      RNF-04, RNF-06, RNF-07, ADR-2, ADR-11, ADR-13
- [x] `tests/test_main.py`: fixture `autouse` que substitui `limpar_tela`; casos de `sugerir` (cada
      cenário do RF-09, inclusive a nota 4 com sequência), de `descrever_analise` (cada item do
      RF-08, a linha `Falta:` quando falta um tipo, e nenhum trecho de 3 caracteres de uma lista de
      senhas no texto), de `descrever_exemplos` (as notas de 0 a 4 e a explicação), de
      `conferir_opcao` (de 1 a 3, vazia, `0`, `9`, `abc`, `٣`), de `opcao_verificar` (a senha
      vazia, o pedido recebido pelo leitor), da largura máxima de 54 colunas nos textos, no pedido
      da senha e no quadro inteiro, e de `main()` (a ordem do quadro, cada opção, a opção
      inválida, a saída pelo menu, e a saída por `KeyboardInterrupt` e por `EOFError`, no menu e no
      pedido da senha, sem stack trace; o padrão do `ler_senha` é o `getpass.getpass`). Um teste
      com o módulo `ast` confere que o `main.py` só importa `__future__`, `collections.abc`,
      `getpass`, `math`, `os`, `pathlib`, `re`, `string`, `sys` e `typing`, não chama `open`,
      `write_text` nem `write_bytes` e não lê `sys.argv`. — RF-01 a RF-11, RNF-03, RNF-04, RNF-06,
      RNF-07
- [x] `iniciar_verificador.bat` e `iniciar_verificador.sh`: atalhos no formato dos do
      `validador_de_cpf` (`uv run main.py`, com `python`/`python3` como alternativa). — RNF-02
- [x] Conferência manual: uma sessão no terminal que verifica uma senha comum, uma com sequência e
      uma forte, com a senha sem aparecer ao digitar, uma opção inválida e a senha vazia no meio,
      mostra os exemplos comentados e sai; o Ctrl+C no pedido da senha, com o terminal voltando a
      mostrar o que se digita; a limpeza de tela a cada volta do menu; o programa chamado de outra
      pasta (`python mini_projetos/verificador_de_forca_de_senha/main.py`), que acha o
      `senhas_comuns.txt`; a saída redirecionada para arquivo sem `UnicodeEncodeError`; e o
      `git status` limpo depois da sessão, sem arquivo criado. — RF-01, RF-03, RF-10, RNF-02,
      RNF-04, RNF-05, RNF-07
      Conferido no cmd do Windows 11, com Python 3.15.
- [x] Portão de qualidade. — 162 passed; ruff/black/mypy verdes

## Etapa 3 — Documentação do projeto

- [ ] `tests/test_readme_en.py`: cópia do arquivo do `validador_de_cpf`. — RNF-09
- [ ] `assets/verificador-de-forca-de-senha-python-terminal-sessao.svg`: animação de uma sessão real
      do `main.py`, com as entradas de um roteiro, no visual das outras animações e na largura de 54
      colunas (ou na menor acima de 52 em que a linha mais longa caiba sem quebrar); o pedido da
      senha aparece sem o que se digita, como no terminal, e quem pede movimento reduzido vê a
      última tela parada. As senhas da sessão são só as dos exemplos do design ou inventadas. —
      RNF-07, RNF-09
- [ ] `README.md`: mesmas seções e na mesma ordem do `README.md` do `gerador_de_senhas`, abrindo
      com a animação e os badges e com o aviso de que a nota é uma estimativa didática, não uma
      auditoria, citando o zxcvbn; o "Guia de Implementação" explica as regras com `any()` e os
      métodos de string, a expressão `(.)\1{2,}` e as janelas das sequências, o desconto dos
      trechos previsíveis, a entropia estimada com a conta do gerador, as faixas da nota e as duas
      travas, a lista de senhas comuns com a origem e a licença, o `getpass` e o que acontece num
      terminal que não esconde a senha, e diz que nenhuma senha é guardada nem mostrada; a dica de
      estudo compara `Senha@123` com uma frase-senha e mostra `Flamengo@2026` tirando 4 nas regras,
      um limite que o zxcvbn pega; com "Atividades para praticar" e "Continue praticando", que
      aponta para os outros mini-projetos; a linha "Contribua com código" aponta para o
      `CONTRIBUTING.md` da raiz e traz as regras próprias do projeto. — RF-01 a RF-11, RNF-07,
      RNF-08, RNF-09, ADR-2, ADR-3, ADR-4, ADR-5
- [ ] `README.en.md`: versão em inglês, com as mesmas seções e na mesma ordem. — RNF-09
- [ ] `CLAUDE.md`: mesma estrutura do `CLAUDE.md` do `gerador_de_senhas` (visão geral, comandos,
      arquitetura e convenções), com os cuidados da senha que não passa de `analisar` (a `Analise`
      não a guarda, e o teste confere que nenhum trecho aparece no resultado), do
      `senhas_comuns.txt` que não se edita (o teste confere o SHA-256), das notas dos exemplos
      calculadas, nunca escritas à mão, e da lista de `import` que o teste do RNF-07 confere. —
      RNF-07, RNF-08, RNF-09, ADR-6, ADR-8, ADR-9
- [ ] `docs/stack.md`: mapa da stack (Python, uv, ruff, black, mypy, pytest), no formato dos
      outros mini-projetos. — RNF-09
- [ ] `LICENSE`: a licença MIT do `gerador_de_senhas`, seguida da seção da lista de senhas comuns,
      com a origem (repositório, arquivo e commit) e as licenças MIT do SecLists e do Pwdb-Public,
      com os avisos de copyright dos dois. — RNF-08, RNF-09
- [ ] Portão de qualidade. —

## Etapa 4 — Integração na pasta `mini_projetos/` e fechamento da spec

- [ ] `../README.md` e `../README.en.md`: uma linha na tabela de projetos, com o que se pratica
      (regras com `any()`, expressões regulares, `getpass` e a entropia estimada). — RNF-09
- [ ] `specs/001-verificador-de-forca-de-senha/`: `Desvios` e `Notas de implementação` no
      `design.md`, se houver o que registrar; `status: concluído` nos três arquivos e na linha do
      índice do `specs/README.md`. — RNF-09
- [ ] Portão de qualidade. —
