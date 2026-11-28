---
feature: Jogo da Cobrinha (Snake) via terminal com curses
status: concluído
date: 2026-09-11
related: []
origin: engenharia reversa
---

# 001 — Jogo da Cobrinha

## Contexto e problema

Este repositório é material de estudo: um jogo de terminal em tempo real
que exercita lógica de movimento, manipulação de listas dinâmicas e o uso
da biblioteca `curses` para desenhar e capturar teclado sem bloquear o
loop do jogo. O jogo já existe e funciona (`main.py`); esta spec documenta
retroativamente o comportamento implementado, para servir de referência
formal e de modelo para futuras mudanças.

## Objetivos

- Jogar uma partida de Snake no terminal, com dificuldade escolhida pelo
  jogador.
- Crescer a cobra e pontuar ao comer frutas sorteadas dentro do campo.
- Encerrar a partida ao colidir com a borda ou com o próprio corpo,
  mostrando a pontuação final.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Sistema de recorde persistido entre execuções (arquivo, banco de dados).
- Frutas especiais ou modo "atravessar paredes" (ficam como atividades
  propostas no README para quem quiser praticar).
- Multiplayer ou interface gráfica fora do terminal.

## Personas

- **Aprendiz de Python**: quer ler o código e entender como listas
  representam coordenadas, como um game loop em tempo real funciona e como
  a biblioteca `curses` desenha e lê teclado sem bloquear.
- **Jogador casual**: só quer abrir o jogo (com duplo clique ou um
  comando), escolher uma dificuldade e jogar no terminal.

## Requisitos funcionais

### RF-01 — Escolher a dificuldade antes de começar

- **Given** o jogo acabou de iniciar
  **When** o jogador digita um número de `1` a `5`
  **Then** a velocidade correspondente (tempo de espera entre quadros) é
  usada na partida e o campo de jogo é aberto.
- **Given** o jogador digita algo fora de `1`-`5`
  **When** a entrada é validada
  **Then** uma mensagem de aviso é exibida e o jogo pede a dificuldade de
  novo, sem encerrar.

### RF-02 — Desenhar o campo a cada quadro

- **Given** uma partida em andamento
  **When** um novo quadro é desenhado
  **Then** a borda do campo, a cobra (cabeça `@` diferenciada do corpo
  `#`) e a fruta (`*`) aparecem nas coordenadas atuais.

### RF-03 — Mover a cobra pelas setas do teclado

- **Given** a cobra está se movendo numa direção
  **When** o jogador pressiona uma tecla de seta que não é a oposta à
  direção atual, dentro do tempo do quadro
  **Then** a cobra passa a se mover na nova direção a partir do próximo
  quadro.
- **Given** a cobra está se movendo numa direção
  **When** o jogador pressiona a seta exatamente oposta (ex.: para cima
  indo para baixo)
  **Then** a tecla é ignorada e a cobra mantém a direção atual.
- **Given** nenhuma tecla de seta é pressionada dentro do tempo do quadro
  **When** o tempo se esgota
  **Then** a cobra continua na direção atual.

### RF-04 — Comer a fruta e pontuar

- **Given** a cabeça da cobra ocupa a mesma coordenada da fruta
  **When** o quadro é processado
  **Then** a pontuação é incrementada em 1, uma nova fruta é sorteada em
  outra posição e a cobra cresce um segmento (a cauda não é removida
  naquele quadro).

### RF-05 — Detectar colisão e encerrar a partida

- **Given** a cabeça da cobra alcança qualquer coordenada da borda do
  campo
  **When** a colisão é verificada
  **Then** a partida termina.
- **Given** a cabeça da cobra ocupa a mesma coordenada de qualquer gomo do
  próprio corpo
  **When** a colisão é verificada
  **Then** a partida termina.

### RF-06 — Exibir a tela final

- **Given** a partida terminou por colisão
  **When** a tela final é desenhada
  **Then** a mensagem "Fim de Jogo! Frutas coletadas: N" aparece
  centralizada, com destaque visual, e a janela permanece visível por
  alguns segundos antes do programa encerrar.

## Requisitos não funcionais

### RNF-01 — Portabilidade

O mesmo `main.py` deve funcionar sem alteração em Windows, Linux e macOS.
No Windows, a ausência do módulo `curses` na stdlib é suprida pela
dependência `windows-curses`; em Linux/macOS o `curses` da stdlib é usado
diretamente.

### RNF-02 — Seleção de dificuldade nunca deixa o jogador travado

Nenhuma entrada inválida na escolha de dificuldade (fora de `1`-`5`, texto
não numérico) pode lançar uma exceção não tratada — o jogo sempre pede a
entrada de novo.

### RNF-03 — Saída não crasha por codificação

A impressão da mensagem de aviso da seleção de dificuldade (que usa um
emoji) não pode lançar `UnicodeEncodeError`, mesmo quando `stdout` não
está preso a um console UTF-8 (saída redirecionada para arquivo, pipe, ou
executor de CI) — etapa que roda antes do `curses.wrapper` assumir o
terminal.

### RNF-04 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o
`README.en.md`, com as mesmas seções e abertos por uma animação de uma sessão no terminal, que
fica parada na última tela para quem pede movimento reduzido; o `CLAUDE.md`, com os comandos e a
arquitetura; o `docs/stack.md`, com o mapa da stack; e o `LICENSE`, o `CONTRIBUTING.md`, o
`CODE_OF_CONDUCT.md` e o `SECURITY.md`. O portão de qualidade (ruff, black, mypy strict e pytest)
roda no CI, e o Dependabot propõe as atualizações das ferramentas de desenvolvimento.

> Nota (2026-11-20): o `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md` e o `SECURITY.md` passaram a
> valer para o repositório inteiro e ficam na raiz; as regras de contribuição próprias deste
> projeto estão na seção de dúvidas e sugestões do README.

## Perguntas em aberto

Nenhuma — feature pequena e já finalizada; ver "Atividades para praticar"
no `README.md`, com exercícios de extensão (recorde persistido,
fruta dourada, atravessar paredes).

## Testes

### RF-01 — Seleção de dificuldade

`tests/test_main.py` cobre `selecionar_nivel_dificuldade` com cada um dos
cinco níveis (a espera de cada um escrita no teste) e com entrada fora do
intervalo (via `monkeypatch` em `input`), verificando a mensagem de aviso via
`capsys`.

### RF-02 — Desenho do campo

`tests/test_main.py` cobre `desenhar_tela`, `desenhar_ator` e
`desenhar_cobra` contra uma `curses.window` falsa (`_FakeJanela`) que
registra as chamadas de `clear`/`border`/`addch` sem abrir um terminal
real.

### RF-03 — Movimento e direção oposta

`tests/test_main.py` cobre `obter_nova_direcao` (timeout configurado, cada
uma das quatro setas aceita, tecla não direcional ignorada — parametrizado),
`direcao_e_oposta` (as quatro combinações opostas e uma lateral) e
`mover_cobra` (deslocamento da cabeça nas quatro direções e o corpo inteiro
depois do passo).

### RF-04 — Alimentação

`tests/test_main.py` cobre `mover_cobra` com `cobra_comeu_fruta=True`
(cauda preservada, cobra cresce) e `gerar_nova_fruta` com `random.randint`
mockado, verificando os limites passados (`altura-2`, `largura-2`).

### RF-05 — Colisões

`tests/test_main.py` cobre `verificar_colisoes` para os quatro lados da
borda e para a casa logo ao lado de cada um, que ainda é campo livre
(parametrizado), para colisão com o próprio corpo e para o caso sem
colisão.

### RF-06 — Tela final

`tests/test_main.py` cobre `finalizar_jogo` (com `time.sleep` mockado),
verificando a coordenada centralizada, o texto com a pontuação, o
atributo `curses.A_REVERSE` e a chamada a `refresh`.

### `ciclo_do_jogo` — a partida inteira contra a janela falsa

`tests/test_main.py` roda `ciclo_do_jogo` contra a `_FakeJanela`, com
`curses.curs_set` (que exige um terminal real) trocado por um registro e as
frutas fixadas por `random.randint`: numa partida, a cobra come a fruta, a
meia-volta é ignorada e a batida na base vem no 9º quadro; noutra, a curva
lateral é aceita e a batida na borda direita vem no 24º. A janela falsa
falha o teste depois de 200 leituras de tecla, para uma partida sem fim não
travar a suíte. Só o `curses.wrapper`, que prepara e restaura o terminal,
fica de fora, conferido à mão ao rodar o jogo.

### RNF-04 — Documentação conferida

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links), e `tests/test_impessoalidade.py`, que os arquivos
versionados não citam o mantenedor nem apontam para ferramentas que quem clona não tem. A
animação e os arquivos da comunidade são conferidos à mão, antes de cada pull request.

> Nota (2026-11-20): a conferência de impessoalidade passou a valer para o repositório inteiro
> e fica na raiz, em `.github/scripts/conferir_impessoalidade.py`, que o CI roda a cada pull
> request; o `tests/test_impessoalidade.py` saiu deste projeto.
