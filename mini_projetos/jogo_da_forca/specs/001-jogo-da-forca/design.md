---
feature: Jogo da Forca via terminal
status: concluído
date: 2026-11-20
related:
  - 001-jogo-da-forca/requirements.md
origin: concepção
---

# 001 — Jogo da Forca — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade: sortear a palavra,
tirar os acentos, mascarar a palavra, desenhar a tela, jogar uma partida, perguntar se o jogador
quer jogar de novo e mostrar o placar. A lista de palavras e os desenhos da forca ficam em
constantes de módulo (`PALAVRAS` e `FORCA`). O estado que atravessa partidas (as palavras já
sorteadas e o placar) mora em `main()`, que o cria e o passa adiante, e é o único ponto que trata
o Ctrl+C.

O coração do jogo são dois conjuntos: o das letras da palavra, já sem acento, e o das letras
tentadas. A vitória é "as letras da palavra estão todas entre as tentadas", e os erros são "as
tentadas que não estão na palavra". As duas regras saem de operações de conjunto, sem contador
separado.

As funções que leem o teclado recebem a leitura por parâmetro (`ler`, que vale `input` por
padrão), e o sorteio entra da mesma forma (`sortear`, que vale `random.choice`). O jogo roda igual
para quem só executa `main.py`, e os testes passam leitores e sorteadores falsos, sem
`monkeypatch`.

Não há camadas (persistência, rede, interface gráfica), e é de propósito: o fluxo precisa caber na
cabeça numa leitura de cima para baixo.

## Layout de módulos

```
main.py            # constantes, funções do jogo e main() (ponto de entrada)
tests/test_main.py # suíte pytest
```

## Modelo de dados

Constante de módulo `PALAVRAS: dict[str, list[str]]`, do tema para as 8 palavras dele, todas em
minúsculas e com a grafia acentuada:

| Tema              | Palavras                                                                         |
| ----------------- | -------------------------------------------------------------------------------- |
| `frutas`          | banana, maçã, abacaxi, morango, limão, melancia, maracujá, pêssego               |
| `animais`         | cachorro, elefante, girafa, tartaruga, jacaré, onça, coruja, borboleta           |
| `países`          | brasil, argentina, japão, canadá, portugal, méxico, alemanha, egito              |
| `profissões`      | médico, professor, bombeiro, músico, cozinheiro, engenheiro, jornalista, padeiro |
| `objetos da casa` | cadeira, travesseiro, geladeira, fogão, sofá, espelho, relógio, lençol           |

Constante `ERROS_MAXIMOS = 6` e constante `FORCA: list[str]`, com 7 desenhos em ASCII, em que o
índice é o número de erros: o `FORCA[0]` é só o poste, e cada erro acrescenta uma parte (cabeça,
tronco, braço esquerdo, braço direito, perna esquerda, perna direita). O `FORCA[6]`:

```
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========
```

Constante `ALFABETO = string.ascii_lowercase`: as 26 letras que a entrada pode ter depois de
perder o acento.

Estado de uma partida, local a `jogar_partida`: `letras_da_palavra: set[str]` (as letras da
palavra sem acento, sem repetição) e `tentadas: set[str]` (as letras já tentadas, também sem
acento). Estado da sessão, local a `main()`: `ja_sorteadas: set[str]` (as palavras que já saíram)
e `placar: dict[str, int]`, com as chaves `"vitórias"` e `"derrotas"`.

Apelidos de tipo para os parâmetros injetáveis, com a instrução `type` (Python 3.12) e `Callable`
de `collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado,
  como o `input`.
- `type Sorteador = Callable[[list[tuple[str, str]]], tuple[str, str]]`: recebe a lista de pares
  `(tema, palavra)` e devolve um deles, como o `random.choice`.

## Componentes

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `jogar_partida` a chama antes de cada redesenho (RF-08).

### `sortear_palavra(ja_sorteadas, sortear)`

Monta a lista de pares `(tema, palavra)` de `PALAVRAS` cuja palavra não está em `ja_sorteadas`.
Se a lista sai vazia, porque todas as 40 já saíram, esvazia `ja_sorteadas` com `clear()` e monta
a lista de novo. Sorteia um par com `sortear(opcoes)`, acrescenta a palavra em `ja_sorteadas` e
devolve o par (RF-01, RF-02). A lista segue a ordem de `PALAVRAS`, o que deixa o teste escolher o
par pelo sorteador falso.

### `remover_acentos(texto)`

Função pura: decompõe o texto com `unicodedata.normalize("NFD", texto)`, que separa cada letra
acentuada na letra base mais a marca do acento ("ã" vira "a" + "~", e "ç" vira "c" + cedilha), e
junta com `"".join(...)` só os caracteres em que `unicodedata.combining(caractere)` é zero, ou
seja, descarta as marcas (RF-04, ADR-3).

### `mascarar_palavra(palavra, tentadas)`

Função pura: percorre a palavra caractere por caractere e troca por `_` cada letra cuja versão sem
acento não está em `tentadas`. As letras descobertas ficam com a grafia original, em maiúsculas.
Junta o resultado com `" ".join(...)`, para cada posição ficar visível: `maçã` com `{"a"}` vira
`_ A _ Ã` (RF-04, RF-05).

### `contar_erros(letras_da_palavra, tentadas)`

Função pura: devolve `len(tentadas - letras_da_palavra)`, o tamanho da diferença entre os
conjuntos, que são as letras tentadas que a palavra não tem (RF-04, ADR-4).

### `conferir_entrada(entrada, tentadas)`

Função pura: tira os espaços, converte para minúscula e remove o acento da entrada. Devolve a
letra pronta, ou uma mensagem de recusa: "digite uma letra só, de A a Z" quando o resultado não
tem exatamente um caractere de `ALFABETO`, ou "a letra já foi tentada" quando ela está em
`tentadas` (RF-03, ADR-5). O retorno é uma `NamedTuple` `Conferencia(letra, recusa)`, em que só um
dos dois campos vem preenchido e o outro é `""`.

### `exibir_jogo(tema, palavra, tentadas, mensagem)`

Imprime, nesta ordem: o tema, o desenho `FORCA[erros]`, a palavra mascarada, as letras tentadas
em maiúsculas e em ordem alfabética (`sorted(tentadas)`, ou um traço quando ainda não há
nenhuma), os erros restantes e, por último, a mensagem da tentativa anterior, se houver (RF-05,
RF-08).

### `jogar_partida(tema, palavra, ler)`

Cria `letras_da_palavra = set(remover_acentos(palavra))` e `tentadas` vazio. Laço
`while contar_erros(...) < ERROS_MAXIMOS and not letras_da_palavra.issubset(tentadas)`: limpa a
tela, exibe o jogo com a mensagem da rodada anterior, lê a entrada e a confere. A recusa vira a
mensagem da próxima rodada, sem mudar `tentadas`. A letra aceita entra em `tentadas`, e a mensagem
diz se a palavra tem ou não a letra (RF-03, RF-04). Ao sair do laço, limpa a tela, exibe o jogo uma
última vez e anuncia a vitória, com a palavra e o número de erros, ou a derrota, com a palavra
revelada (RF-06). Devolve `True` na vitória e `False` na derrota.

### `perguntar_jogar_de_novo(ler)`

Lê a resposta, tira os espaços e converte para minúscula. Devolve `True` para `s` e `False` para
`n`; outra resposta gera uma mensagem de erro e a pergunta se repete (RF-07).

### `exibir_placar(placar)`

Imprime as vitórias e as derrotas da sessão (RF-07).

### `main(sortear, ler)`

Cria `ja_sorteadas` vazio e o placar zerado e repete: sorteia a palavra, joga a partida, soma no
placar e pergunta se o jogador quer jogar de novo. Na saída, mostra o placar e se despede. O laço
inteiro fica dentro de um `try` que captura `KeyboardInterrupt` e `EOFError`, e a despedida sai em
uma linha, sem stack trace (RNF-04).

## Interfaces

Nenhuma: é um programa de terminal, sem rede, arquivo ou API. A única "interface" é a entrada e a
saída pelo terminal, descrita nos requisitos funcionais. Como a tela é limpa a cada jogada, o
terminal mostra sempre um quadro só. O quadro ilustrativo abaixo é o da palavra "maçã", depois das
tentativas `a`, `e` e `r` (o texto exato de cada mensagem fica no `main.py`):

```
Tema: frutas

  +---+
  |   |
  O   |
  |   |
      |
      |
=========

Palavra: _ A _ Ã
Letras tentadas: A, E, R
Erros restantes: 4

❌ A palavra não tem a letra R.
Digite uma letra: c
```

As mensagens evitam concordar com o número ("Erros restantes: 4", "Erros cometidos: 1"), para
nenhuma frase precisar de plural. Na vitória, o último quadro termina com "🎉 Você descobriu a
palavra: MAÇÃ! Erros cometidos: 2."; na derrota, com "💀 A forca completou. A palavra era MAÇÃ.".
No fim da sessão:

```
Jogar de novo? (s/n): n

Placar da sessão:
  Vitórias: 1
  Derrotas: 0
Até a próxima! 👋
```

## ADRs

### ADR-1 — Funções soltas em vez de uma classe

**Decisão.** O jogo é um conjunto de funções no nível do módulo, e o estado da sessão (as
palavras sorteadas e o placar) é passado por parâmetro.

**Alternativas.** (a) uma classe `JogoDaForca` com o estado em `self`, como o
`pedra_papel_tesoura` e o `jogo_da_velha`.

**Porquê.** O centro deste projeto são as strings, os conjuntos e o `unicodedata`, e não a
Orientação a Objetos. Funções com entrada e saída explícitas se leem de cima para baixo e se
testam sem montar um objeto. Segue o projeto anterior da série, o `adivinhe_o_numero`.

**Trade-off.** O estado da sessão passa de função em função, em vez de morar em `self`. Com um
conjunto e um dicionário, o custo é pequeno.

### ADR-2 — `PALAVRAS` como dicionário de tema para lista

**Decisão.** A lista de palavras fica em `PALAVRAS: dict[str, list[str]]`, escrita à mão no
`main.py`, com o tema como chave.

**Alternativas.** (a) uma lista de pares `(tema, palavra)`, com o tema repetido em cada linha.
(b) um arquivo `palavras.txt` lido na abertura. (c) uma lista pronta da internet.

**Porquê.** O dicionário escreve cada tema uma vez e agrupa as palavras dele, o que facilita
conferir as 8 por tema e acrescentar palavras. Descartar (b): o arquivo externo fica fora do
escopo (ver "Não objetivos" no `requirements.md`), e ler arquivo é um conceito a mais para o
iniciante. Descartar (c): a lista pronta traz a
questão da licença.

**Trade-off.** O sorteio precisa achatar o dicionário em pares a cada partida. São 40 itens, então
o custo não aparece.

### ADR-3 — Remover acentos com `unicodedata` (NFD)

**Decisão.** `remover_acentos` decompõe o texto na forma NFD e descarta os caracteres que o
`unicodedata.combining` marca como sinal diacrítico.

**Alternativas.** (a) uma tabela feita à mão com `str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")`.
(b) a forma NFKD.

**Porquê.** A decomposição é o conceito novo do projeto e cobre todo acento do português, inclusive
o "ç", sem uma tabela que pode esquecer uma letra (decisão 1 do `requirements.md`). Descartar (b):
a NFKD também troca caracteres de compatibilidade ("ª" vira "a"), um efeito que o jogo não precisa
e que pede mais explicação.

**Trade-off.** O iniciante precisa entender que "ã" pode ser um caractere ou dois. Um comentário
curto com o exemplo `"ã"` → `"a" + "~"` explica a ideia.

### ADR-4 — Conjuntos para as letras: vitória por subconjunto, erros por diferença

**Decisão.** As letras tentadas e as da palavra ficam em `set`, ambas sem acento. A vitória é
`letras_da_palavra.issubset(tentadas)`, e os erros são `len(tentadas - letras_da_palavra)`. O
conjunto `ja_sorteadas` guarda as palavras que já saíram na sessão.

**Alternativas.** (a) uma lista de letras tentadas e um contador de erros incrementado a cada
erro. (b) os operadores `<=` para o subconjunto, além do `-` da diferença.

**Porquê.** O conjunto não guarda repetição, e o `in` responde direto se a letra já foi tentada. A
regra de vitória e a de derrota saem de uma operação cada, sem contador que possa sair de sincronia
com as letras. Descartar (b): o método `issubset` diz em palavras o que o `<=` diz em símbolo, o que
pesa para quem está começando. A diferença fica com `-`, a forma mais comum e com o nome igual ao da
matemática.

**Trade-off.** O conjunto não tem ordem, então a exibição usa `sorted(tentadas)`.

### ADR-5 — Letra válida é um caractere de `ALFABETO`, conferido depois de tirar o acento

**Decisão.** `conferir_entrada` remove o acento antes de validar, e aceita a entrada só se ela
tiver exatamente um caractere e se ele estiver em `ALFABETO` (`string.ascii_lowercase`). O tamanho
é conferido primeiro.

**Alternativas.** (a) `str.isalpha()`. (b) só `entrada in ALFABETO`, sem conferir o tamanho.

**Porquê.** Validar depois de tirar o acento aceita "á" e "ç" como "a" e "c" (RF-03). Descartar
(a): o `isalpha` aceita letras que nenhuma palavra da lista tem, como "ß" e as gregas, e o jogador
perderia uma tentativa por elas. Descartar (b): em string, `in` procura um trecho, e não um
caractere, então `"" in ALFABETO` e `"ab" in ALFABETO` são `True`. Um comentário mostra essa
armadilha, um bom exemplo do `in` com strings.

**Trade-off.** Nenhum relevante: a lista só tem palavras em português, escritas com as 26 letras e
os acentos.

### ADR-6 — Leitura do teclado e sorteio por parâmetro, com padrões reais

**Decisão.** As funções que leem o teclado recebem `ler: Leitor = input`, e `sortear_palavra`
recebe `sortear: Sorteador = random.choice`. `main()` repassa os dois.

**Alternativas.** (a) chamar `input` e `random.choice` direto e substituí-los nos testes com
`monkeypatch`, como fazem os mini-projetos mais antigos.

**Porquê.** Atende o RNF-06: o teste diz qual é a palavra e qual é a sequência de entradas na
própria chamada, sem trocar funções da biblioteca padrão por baixo. Quem só roda o jogo não percebe
diferença, porque os padrões são as funções reais. É o mesmo desenho do `adivinhe_o_numero`.

**Trade-off.** As assinaturas ganham um parâmetro e os apelidos `Leitor` e `Sorteador`. Um
comentário no topo do arquivo explica o motivo.

### ADR-7 — `os.system` em vez de `subprocess.run(..., shell=True)`

**Decisão.** `limpar_tela` usa `os.system(comando)` com uma string fixa (`"cls"` ou `"clear"`).

**Alternativas.** (a) `subprocess.run(comando, shell=True)`. (b) uma biblioteca de terceiros
(`colorama`, `rich`) com uma função de limpar a tela.

**Porquê.** `comando` nunca vem do usuário: é sempre um literal escolhido pelo `os.name`.
`os.system` faz o mesmo com uma linha mais simples e sem o `shell=True` que as ferramentas de
análise estática sinalizam por hábito. Descartar (b): o jogo não tem dependência de execução
(RNF-01).

**Trade-off.** `os.system` não captura a saída do comando, o que não importa aqui: o efeito
desejado é só o do terminal.

### ADR-8 — `main()` como função, chamada pelo `if __name__ == "__main__"`

**Decisão.** O laço de partidas vive em `main()`, e o guard `if __name__ == "__main__"` só a
chama.

**Alternativas.** (a) escrever o laço direto no bloco do guard.

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes
chamam `main()` com um leitor e um sorteador falsos.

**Trade-off.** Nenhum relevante.

### ADR-9 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e as letras acentuadas da palavra não teriam como sair.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-10 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada função que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do jogo" em qualquer ponto, então um lugar só
basta, e as funções de leitura ficam focadas em validar (RNF-04). Descartar (b): o stack trace
assusta o iniciante e parece erro do programa.

**Trade-off.** Uma partida interrompida não entra no placar, e o placar não é mostrado na saída
por Ctrl+C. Para um jogo de sessão curta, a despedida basta.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/jogo_da_forca/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`). Fora da pasta, ganha uma entrada na matriz `projeto` do
workflow de CI (`ci.yml`) e do `pip-audit.yml` da raiz, e uma linha na tabela do
`mini_projetos/README.md` e do `README.en.md`. Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, sem integração (não há rede nem arquivo). O leitor falso e o sorteador falso são
pequenas classes com `__call__` (`LeitorFalso`, `SorteadorFalso` e `LeitorQueInterrompe`), como no
`adivinhe_o_numero`: o leitor devolve as respostas de uma lista e guarda os pedidos recebidos, e o
sorteador devolve o par escolhido pelo teste e guarda as opções recebidas, para o teste do RF-02
conferir que a palavra já sorteada ficou de fora. As funções puras (`remover_acentos`,
`mascarar_palavra`, `contar_erros`, `conferir_entrada`) são testadas direto, com casos
parametrizados. A saída se confere com o `capsys`. `limpar_tela` é substituída por uma fixture
`autouse` com `monkeypatch`, para os testes não chamarem `os.system`: é o único `monkeypatch` da
suíte (RF-08). Os testes de `main()` também cobrem o Ctrl+C e o fim da entrada, com um leitor que
lança `KeyboardInterrupt` ou `EOFError` (RNF-04). Ver `tests/test_main.py` e a seção "Testes" do
`requirements.md`.

## Notas de implementação

- **Testes:** 58 casos em `tests/test_main.py` (45 na etapa 1, 13 na etapa 2); com o
  `test_impessoalidade.py` e o `test_readme_en.py`, cópias dos do `adivinhe_o_numero`, a suíte
  tem 66. Ruff, black e mypy strict verdes.
- **Conferido à mão:** uma vitória e uma derrota com a entrada roteirizada por stdin e a saída
  redirecionada para arquivo, não num terminal interativo: os acentos e os emojis saem sem
  `UnicodeEncodeError`, e a limpeza de tela a cada jogada aparece no arquivo como o caractere que
  o `cls` emite (`^L`).
- **Animação do README:** gravada rodando o `main()` de verdade, com o sorteio fixo em
  ("frutas", "maçã") e o roteiro de entradas `e` (erro), `a` (revela o A e o Ã), `ab` (recusada
  sem contar erro), `c` (revela o Ç), `r` (erro), `M` (maiúscula, fecha a palavra com 2 erros) e
  `n`, até o placar da sessão. A linha mais longa é a da vitória ("🎉 Você descobriu a palavra:
  MAÇÃ! Erros cometidos: 2."), com 54 colunas: a animação usa 54, como a do
  `adivinhe_o_numero`. São 16 quadros em 12,4 s.
- **README:** nas seções do `adivinhe_o_numero`, o Guia de Implementação fecha com uma dica de
  estratégia (começar pelas vogais). As atividades para praticar partem de decisões deste
  projeto: a dica que custa um erro, o menu de temas (a partida começa direto, sem menu, ver as
  decisões do `requirements.md`) e as palavras compostas (fora da forma de `PALAVRAS`, RF-01).
