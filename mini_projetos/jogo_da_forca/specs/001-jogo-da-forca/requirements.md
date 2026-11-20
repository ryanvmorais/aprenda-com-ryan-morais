---
feature: Jogo da Forca via terminal
status: aprovado
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Jogo da Forca

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. O computador sorteia
uma palavra em português, mostra o tema dela como dica, e o jogador tenta descobri-la letra por
letra antes que o desenho da forca se complete. O jogo exercita três conceitos: strings
(indexação, `in`, `join`), conjuntos (`set`) para as letras tentadas e para saber quando a palavra
fechou, e a remoção de acentos com `unicodedata`, para que o jogador digite "a" e acerte o "á"
enquanto a palavra continua aparecendo acentuada. O resto (funções, dicionário, laço `while`,
validação da entrada) fica no nível dos outros mini-projetos, para o código se ler de cima para
baixo.

## Objetivos

- Jogar partidas de forca no terminal, com o desenho da forca em ASCII, a palavra com as letras
  descobertas e as letras já tentadas.
- Sortear palavras em português de uma lista escrita à mão, com o tema como dica.
- Aceitar a letra sem acento para a letra acentuada da palavra, e o "c" para o "ç".
- Guardar, durante a sessão, o placar de vitórias e derrotas, sem repetir palavra.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Palavras vindas de arquivo externo ou de API.
- Modo de dois jogadores (um escolhe a palavra, o outro adivinha).
- Chutar a palavra inteira de uma vez.
- Escolha de tema ou de dificuldade pelo jogador.
- Placar gravado em arquivo entre execuções.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como as
  strings, os conjuntos e o `unicodedata` se encaixam num programa de verdade.
- **Jogador casual:** quer abrir o jogo (com duplo clique ou um comando) e jogar algumas partidas
  no terminal.

## Requisitos funcionais

### RF-01 — Sortear a palavra e mostrar o tema

- **Given** uma partida vai começar
  **When** a palavra é sorteada
  **Then** ela sai de uma lista embutida no código, com 5 temas (frutas, animais, países,
  profissões e objetos da casa) e 8 palavras por tema, e o jogo mostra o tema da palavra como
  dica.
- **Given** a lista de palavras
  **When** ela é lida
  **Then** cada palavra é uma só, em minúsculas, só com letras (sem espaço, hífen nem número), e
  a lista tem palavras com acento e com "ç".

### RF-02 — Não repetir palavra na sessão

- **Given** uma palavra já saiu numa partida da sessão
  **When** a partida seguinte sorteia a palavra
  **Then** o sorteio é feito só entre as palavras que ainda não saíram.
- **Given** todas as 40 palavras já saíram na sessão
  **When** a partida seguinte sorteia a palavra
  **Then** a lista recomeça, e qualquer palavra pode sair de novo.

### RF-03 — Ler e validar a letra

- **Given** a partida está em andamento
  **When** o jogador digita uma letra, maiúscula ou minúscula, com ou sem acento
  **Then** a letra é aceita como tentativa.
- **Given** a partida está em andamento
  **When** o jogador digita algo que não é uma letra só (nada, `ab`, `3` ou `?`)
  **Then** uma mensagem de erro é exibida, sem stack trace, o jogo pede a letra de novo e a
  entrada não conta como erro.
- **Given** o jogador já tentou uma letra na partida
  **When** ele digita a mesma letra de novo, com ou sem acento (`a` depois de `á`)
  **Then** o jogo avisa que a letra já foi tentada, pede outra e a entrada não conta como erro.

### RF-04 — Comparar a letra sem acento

- **Given** a palavra sorteada tem a letra tentada, comparada sem acento e com "ç" igual a "c"
  **When** a tentativa é conferida
  **Then** todas as ocorrências dela são reveladas, com a grafia original: `a` em "maçã" revela
  o "a" e o "ã", e `c` revela o "ç".
- **Given** a palavra sorteada não tem a letra tentada
  **When** a tentativa é conferida
  **Then** conta como um erro, e a forca ganha mais uma parte.

### RF-05 — Mostrar a forca, a palavra e as letras tentadas

- **Given** a partida está em andamento
  **When** o jogo pede a próxima letra
  **Then** a tela mostra o tema, o desenho da forca correspondente ao número de erros (de 0 a 6),
  a palavra em maiúsculas com `_` no lugar de cada letra escondida, as letras já tentadas em
  ordem alfabética e quantos erros ainda restam.

### RF-06 — Terminar a partida com vitória ou derrota

- **Given** a tentativa revelou a última letra escondida
  **When** a tentativa é conferida
  **Then** a partida termina com vitória, e o jogo mostra a palavra completa e quantos erros o
  jogador cometeu.
- **Given** a tentativa foi o sexto erro
  **When** a tentativa é conferida
  **Then** a partida termina com derrota, o jogo mostra a forca completa e revela a palavra.

### RF-07 — Jogar de novo ou encerrar

- **Given** uma partida terminou
  **When** o jogador responde `s` (ou `S`) à pergunta "jogar de novo?"
  **Then** uma nova partida começa, e o placar e as palavras já sorteadas na sessão continuam
  guardados.
- **Given** uma partida terminou
  **When** o jogador responde `n` (ou `N`)
  **Then** o jogo mostra o placar da sessão (vitórias e derrotas) e termina.
- **Given** uma partida terminou
  **When** o jogador responde outra coisa
  **Then** uma mensagem de erro é exibida e a pergunta se repete.

### RF-08 — Limpar a tela a cada jogada

- **Given** a partida está em andamento
  **When** o jogo vai redesenhar a forca e a palavra
  **Then** a tela é limpa antes (`cls` no Windows, `clear` no Linux e no macOS), e a mensagem da
  tentativa anterior (acerto, erro, letra repetida ou entrada inválida) aparece abaixo do desenho.

## Requisitos não funcionais

### RNF-01 — Sem dependências externas

O jogo roda com Python puro (só a biblioteca padrão), sem instalar nenhum pacote para jogar. As
ferramentas de desenvolvimento (ruff, black, mypy, pytest) ficam no grupo `dev` do
`pyproject.toml`, gerenciado pelo `uv`.

### RNF-02 — Portabilidade

O mesmo `main.py` funciona, sem alteração, nos terminais do Windows, do Linux e do macOS. Os
atalhos `.bat` e `.sh` cobrem só a conveniência de abrir o jogo.

### RNF-03 — Feedback nunca deixa o usuário travado

Nenhuma entrada do teclado (na letra ou na pergunta "jogar de novo?") lança exceção não tratada:
o jogo sempre explica o erro e pede a entrada de novo.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o jogo está esperando uma entrada do teclado
  **When** o jogador aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o jogo se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive das letras acentuadas e dos emojis das mensagens, não lança
`UnicodeEncodeError`, nem quando a saída padrão não está presa a um console UTF-8 (saída
redirecionada para arquivo, pipe ou executor de CI).

### RNF-06 — Testável sem sorteio nem teclado reais

O sorteio da palavra e a leitura do teclado entram nas funções do jogo por parâmetro, para a
suíte de testes ser determinística: o teste escolhe a palavra e a sequência de entradas sem
`monkeypatch` em `random` ou `input`.

### RNF-07 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o
`README.en.md`, com as mesmas seções e abertos por uma animação de uma sessão no terminal, que
fica parada na última tela para quem pede movimento reduzido; o `CLAUDE.md`, com os comandos e a
arquitetura; o `docs/stack.md`, com o mapa da stack; e o `LICENSE`, o `CONTRIBUTING.md`, o
`CODE_OF_CONDUCT.md` e o `SECURITY.md`. O portão de qualidade (ruff, black, mypy strict e pytest)
roda no CI, e o Dependabot propõe as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **O "ç" vale como "c":** a decomposição do `unicodedata` separa o "ç" em "c" mais a cedilha,
   do mesmo jeito que separa o "á" em "a" mais o acento. Uma regra só cobre os dois casos, e quem
   joga num teclado sem "ç" não fica travado. Digitar "ç" também é aceito e vale como "c".
2. **Lista escrita à mão, com 5 temas de 8 palavras:** 40 palavras dão variedade para várias
   partidas e cabem numa tela de código. Escrever à mão evita a questão da licença de uma lista
   pronta.
3. **O tema é sorteado junto com a palavra e serve de dica:** a partida começa direto, sem menu,
   e o foco fica nas strings e nos conjuntos. A validação de um menu já foi o centro do projeto
   anterior.
4. **Placar da sessão e palavra sem repetição:** o conjunto das palavras já sorteadas usa o
   mesmo `set` das letras tentadas, o conceito novo do projeto.
5. **6 erros completam a forca:** cabeça, tronco, dois braços e duas pernas.
6. **Letra repetida e entrada inválida não contam como erro:** só repetem o pedido, com uma
   mensagem que explica o motivo.
7. **Só letra por letra:** chutar a palavra inteira fica fora, para o laço da partida ter uma
   regra só.
8. **A tela é limpa a cada jogada:** o desenho é redesenhado no mesmo lugar, como no jogo da
   velha, e a mensagem da tentativa anterior aparece abaixo dele.
9. **"Jogar de novo?" usa `s`/`n`,** sem diferenciar maiúscula e minúscula.

## Testes

### RF-01, RF-02 — Lista e sorteio

`tests/test_main.py` confere a forma da lista (5 temas, 8 palavras por tema, só letras
minúsculas, sem palavra repetida, com acento e com "ç") e, com um sorteador falso passado por
parâmetro, que a palavra já sorteada sai das opções e que a lista recomeça quando acaba.

### RF-03, RNF-03 — Validação da entrada

A suíte cobre a letra válida em maiúscula, minúscula e acentuada, a entrada vazia, com duas
letras, com número e com símbolo, e a letra repetida com e sem acento, conferindo que nenhuma
dessas conta como erro. As entradas são simuladas por uma sequência passada por parâmetro
(RNF-06).

### RF-04, RF-05 — Comparação e exibição

A suíte cobre a remoção de acentos e da cedilha, a revelação de todas as ocorrências com a
grafia original, a palavra mascarada com `_`, as letras tentadas em ordem alfabética e o desenho
da forca para cada número de erros.

### RF-06, RF-07 — Fim da partida e "jogar de novo"

A suíte cobre a vitória sem erro, a vitória com erros, a derrota que revela a palavra, a
resposta `s`/`n` em maiúscula e minúscula, a resposta inválida e o placar no fim da sessão.

### RNF-04, RNF-05 — Saída do jogo

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o jogo
sem stack trace. A codificação da saída é conferida rodando o jogo com a saída redirecionada.

### RF-08 — Limpeza de tela

Não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de terminal, e não
devolve nada. Fica coberta pela verificação manual ao rodar o jogo e é substituída nos testes dos
outros requisitos.

### RNF-07 — Documentação conferida

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links), e `tests/test_impessoalidade.py`, que os arquivos
versionados não citam o mantenedor nem apontam para ferramentas que quem clona não tem. A
animação e os arquivos da comunidade são conferidos à mão, antes de cada pull request.
