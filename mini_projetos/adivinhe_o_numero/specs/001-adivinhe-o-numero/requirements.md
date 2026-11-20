---
feature: Jogo Adivinhe o Número via terminal
status: em andamento
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Adivinhe o Número

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. O computador sorteia
um número secreto, e o jogador tenta acertá-lo com as dicas "maior" e "menor", dentro de um limite
de tentativas. O jogo exercita três conceitos: o sorteio com `random.randint`, o laço `while` com
condição de parada e a conversão da entrada do teclado com `int()` dentro de `try`/`except`, para
que um "abc" não derrube o programa. O resto (funções, dicionário, `if`/`elif`) fica no nível dos
outros mini-projetos, para o código se ler de cima para baixo.

## Objetivos

- Jogar partidas de adivinhação no terminal, com dicas a cada palpite.
- Oferecer três níveis de dificuldade, cada um com a própria faixa e o próprio limite de
  tentativas.
- Guardar, durante a sessão, o melhor resultado de cada nível.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Ranking ou recorde gravado em arquivo entre execuções.
- Modo de dois jogadores (um escolhe o número, o outro adivinha).
- Nível personalizado (faixa ou limite escolhidos pelo jogador).
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como o
  `while`, o `random` e o `try`/`except` se encaixam num programa de verdade.
- **Jogador casual:** quer abrir o jogo (com duplo clique ou um comando) e jogar algumas partidas
  no terminal.

## Requisitos funcionais

### RF-01 — Escolher o nível da partida

- **Given** uma partida vai começar
  **When** o menu de níveis é exibido
  **Then** ele mostra as três opções com a faixa e o limite de cada uma:
  `1` fácil (1 a 50, 10 tentativas), `2` médio (1 a 100, 8 tentativas) e `3` difícil (1 a 1000,
  10 tentativas).
- **Given** o menu de níveis está visível
  **When** o jogador digita `1`, `2` ou `3`
  **Then** a partida começa no nível correspondente.
- **Given** o menu de níveis está visível
  **When** o jogador digita outra coisa (`4`, `0`, `abc` ou nada)
  **Then** uma mensagem de erro é exibida, sem stack trace, e o menu pede a escolha de novo.

### RF-02 — Sortear o número secreto

- **Given** o jogador escolheu um nível
  **When** a partida começa
  **Then** um número inteiro é sorteado na faixa do nível, com os dois extremos incluídos, e o
  jogo informa a faixa e o limite de tentativas.

### RF-03 — Ler e validar o palpite

- **Given** a partida está em andamento
  **When** o jogador digita um número inteiro dentro da faixa do nível
  **Then** o palpite é aceito e conta como uma tentativa.
- **Given** a partida está em andamento
  **When** o jogador digita algo que não é um número inteiro (`abc`, `3.5` ou nada)
  **Then** uma mensagem de erro é exibida, sem stack trace, o jogo pede o palpite de novo e a
  entrada não conta como tentativa.
- **Given** a partida está em andamento
  **When** o jogador digita um número inteiro fora da faixa do nível (`0` ou `51` no fácil)
  **Then** uma mensagem lembra a faixa, o jogo pede o palpite de novo e a entrada não conta como
  tentativa.

### RF-04 — Dar a dica depois de cada palpite errado

- **Given** um palpite aceito é menor que o número secreto
  **When** o palpite é comparado
  **Then** o jogo diz que o número secreto é maior e mostra quantas tentativas restam.
- **Given** um palpite aceito é maior que o número secreto
  **When** o palpite é comparado
  **Then** o jogo diz que o número secreto é menor e mostra quantas tentativas restam.

### RF-05 — Terminar a partida com vitória ou derrota

- **Given** um palpite aceito é igual ao número secreto
  **When** o palpite é comparado
  **Then** a partida termina com vitória, e o jogo mostra em quantas tentativas o jogador acertou.
- **Given** o jogador errou e não restam tentativas
  **When** a última tentativa é usada
  **Then** a partida termina com derrota, e o jogo revela o número secreto.

### RF-06 — Guardar o melhor resultado de cada nível

- **Given** o jogador venceu num nível que ainda não tinha resultado na sessão
  **When** a partida termina
  **Then** o número de tentativas passa a ser o melhor resultado daquele nível, e o jogo avisa que
  é um novo recorde.
- **Given** o jogador venceu com menos tentativas que o melhor resultado do nível
  **When** a partida termina
  **Then** o melhor resultado do nível é atualizado, e o jogo avisa que é um novo recorde.
- **Given** o jogador venceu com o mesmo número de tentativas do recorde, ou com mais
  **When** a partida termina
  **Then** o recorde do nível não muda.
- **Given** o jogador perdeu
  **When** a partida termina
  **Then** o recorde do nível não muda.
- **Given** o nível escolhido já tem um melhor resultado na sessão
  **When** a partida começa
  **Then** o jogo mostra o recorde do nível, junto da faixa e do limite.

### RF-07 — Jogar de novo ou encerrar

- **Given** uma partida terminou
  **When** o jogador responde `s` (ou `S`) à pergunta "jogar de novo?"
  **Then** o menu de níveis volta, e os recordes da sessão continuam guardados.
- **Given** uma partida terminou
  **When** o jogador responde `n` (ou `N`)
  **Then** o jogo mostra o melhor resultado de cada nível (ou que o nível não teve vitória) e
  termina.
- **Given** uma partida terminou
  **When** o jogador responde outra coisa
  **Then** uma mensagem de erro é exibida e a pergunta se repete.

### RF-08 — Limpar a tela entre partidas

- **Given** uma partida vai começar
  **When** a tela é limpa, antes do menu de níveis
  **Then** o comando `cls` é executado no Windows, e o `clear`, no Linux e no macOS.
- **Given** a partida está em andamento
  **When** o jogador dá um palpite
  **Then** a tela não é limpa, e as dicas anteriores continuam visíveis.

## Requisitos não funcionais

### RNF-01 — Sem dependências externas

O jogo roda com Python puro (só a biblioteca padrão), sem instalar nenhum pacote para jogar. As
ferramentas de desenvolvimento (ruff, black, mypy, pytest) ficam no grupo `dev` do
`pyproject.toml`, gerenciado pelo `uv`.

### RNF-02 — Portabilidade

O mesmo `main.py` funciona, sem alteração, nos terminais do Windows, do Linux e do macOS. Os
atalhos `.bat` e `.sh` cobrem só a conveniência de abrir o jogo.

### RNF-03 — Feedback nunca deixa o usuário travado

Nenhuma entrada do teclado (no menu de níveis, no palpite ou na pergunta "jogar de novo?") lança
exceção não tratada: o jogo sempre explica o erro e pede a entrada de novo.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o jogo está esperando uma entrada do teclado
  **When** o jogador aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o jogo se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive dos emojis das mensagens, não lança `UnicodeEncodeError`, nem
quando a saída padrão não está presa a um console UTF-8 (saída redirecionada para arquivo, pipe ou
executor de CI).

### RNF-06 — Testável sem sorteio nem teclado reais

O sorteio e a leitura do teclado entram nas funções do jogo por parâmetro, para a suíte de testes
ser determinística: o teste escolhe o número secreto e a sequência de entradas sem `monkeypatch`
em `random` ou `input`.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **O nível muda a faixa e o limite de tentativas.** Os limites seguem a busca binária: chutar
   sempre o meio da faixa garante o acerto em até 6 tentativas de 1 a 50, 7 de 1 a 100 e 10 de 1 a
   1000. O fácil tem folga de 4 tentativas, e o médio, de 1. No difícil, só a estratégia ótima
   garante a vitória.
2. **Na derrota, o número secreto é revelado:** com limite de tentativas, a partida tem fim, e o
   jogador quer saber qual era o número.
3. **O nível é escolhido a cada partida, e o recorde é por nível:** 5 tentativas no fácil e 5 no
   difícil não valem a mesma coisa. "Melhor resultado" é o menor número de tentativas numa
   vitória. Empatar com o recorde não conta como recorde novo.
4. **Entrada inválida não gasta tentativa:** texto, número decimal e número fora da faixa só
   repetem o pedido. Palpite repetido dentro da faixa conta como tentativa normal, como no jogo de
   papel e caneta.
5. **A tela é limpa só entre partidas:** durante a partida, as dicas anteriores ficam visíveis e
   ajudam o jogador a estreitar a faixa.
6. **"Jogar de novo?" usa `s`/`n`,** sem diferenciar maiúscula e minúscula.

## Testes

### RF-01, RF-03, RNF-03 — Validação da entrada

`tests/test_main.py` cobre a escolha de nível válida e inválida (fora do menu, texto e vazio) e o palpite
válido, não numérico, decimal, vazio e fora da faixa, conferindo que a entrada inválida não conta
como tentativa. As entradas são simuladas por uma sequência passada por parâmetro (RNF-06).

### RF-02 — Sorteio

Um teste confere que o sorteio é chamado com os extremos da faixa de cada nível, usando um
sorteador falso passado por parâmetro.

### RF-04, RF-05 — Dicas e fim da partida

A suíte cobre a dica "maior" e "menor" com as tentativas restantes, a vitória na primeira
tentativa, a vitória na última, e a derrota que revela o número.

### RF-06, RF-07 — Recordes e "jogar de novo"

A suíte cobre o primeiro recorde de um nível, o recorde batido, o empate e a derrota (que não
mudam o recorde), a resposta `s`/`n` em maiúscula e minúscula, a resposta inválida e o resumo dos
recordes no fim da sessão.

### RNF-04, RNF-05 — Saída do jogo

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o jogo
sem stack trace. A codificação da saída é conferida rodando o jogo com a saída redirecionada.

### RF-08 — Limpeza de tela

Não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de terminal, e não
devolve nada. Fica coberta pela verificação manual ao rodar o jogo e é substituída nos testes dos
outros requisitos.
