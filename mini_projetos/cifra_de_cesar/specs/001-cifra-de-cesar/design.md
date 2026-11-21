---
feature: Cifra de César via terminal, com cifrar, decifrar e quebrar por força bruta e por frequência
status: aprovado
date: 2026-11-21
related:
  - 001-cifra-de-cesar/requirements.md
origin: concepção
---

# 001 — Cifra de César — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade, em quatro grupos: a
cifra (tirar os acentos, deslocar uma letra, montar a tabela de tradução, cifrar e decifrar), a
quebra (as 25 tentativas da força bruta, a contagem das letras, a pontuação pela frequência e a
ordem das chaves), os textos (o resultado de cada opção, devolvido sem imprimir) e a tela (limpar,
desenhar o quadro, ler a opção, o texto e a chave). A cifra, a quebra e os textos são funções
puras; só `limpar_tela`, `exibir_tela` e `main()` tocam no terminal.

A cifra é um caminho só: `deslocar` tira os acentos e troca cada letra pela tabela que
`montar_tabela` monta com `deslocar_letra`, a função em que `ord`, `chr` e o resto da divisão por
26 aparecem. Cifrar é deslocar com a chave, e decifrar é deslocar com a chave negativa. As duas
quebras reaproveitam a mesma `decifrar`: a força bruta a chama com as 25 chaves e mostra todas, e
a frequência a chama com as 25 chaves, dá a cada resultado uma pontuação pela tabela de
frequência das letras no português e ordena as chaves da maior pontuação para a menor.

`main()` repete o laço do menu: limpa a tela, mostra o título, o resultado da ação anterior e o
menu, lê a opção e guarda o texto que a opção devolveu para a próxima volta. A leitura do teclado
entra por parâmetro (`ler`, que vale `input`), e o Ctrl+C é tratado num lugar só.

## Layout de módulos

```text
main.py                # constantes, funções da cifra, da quebra, dos textos e da tela, e main()
tests/test_main.py     # suíte pytest
```

O programa não lê nem cria nenhum arquivo: a tabela de frequência fica no próprio `main.py`
(RNF-07, ADR-7).

## Modelo de dados

O texto digitado e o texto cifrado ou decifrado são `str`. Uma tentativa da força bruta é um
`tuple[int, str]`, a chave e o texto decifrado com ela (RF-08). A contagem das letras é um
`Counter[str]`, de cada letra minúscula de `a` a `z` para quantas vezes ela aparece (RF-09). A
tabela de tradução é o `dict[int, int]` que o `str.maketrans` devolve.

Constantes de módulo:

- `ALFABETO = string.ascii_lowercase`: as 26 letras, de `a` a `z`, na ordem em que a chave anda
  (RF-06).
- `CHAVES = range(1, 26)`: as chaves válidas, usadas pela leitura da chave, pela força bruta e
  pela frequência (RF-05, decisão 2 do `requirements.md`).
- `FREQUENCIAS: dict[str, float]`: o percentual de cada letra de `a` a `z` no português, copiado da
  tabela 1.2.1 do estudo da COPPE/UFRJ, com o comentário da fonte em cima (RNF-08, ADR-7).
- `MINIMO_LETRAS = 30`: abaixo dele, o resultado da frequência ganha o aviso de texto curto
  (RF-09, ADR-6).
- `LARGURA = 54`: as colunas de uma linha do programa, usadas para cortar as linhas da força bruta
  e as alternativas da frequência (RF-08, ADR-8).
- `OPCOES = ["Cifrar um texto", "Decifrar com a chave", "Quebrar por força bruta", "Quebrar pela
  frequência das letras", "Sair"]`: o menu, numerado a partir de 1 na exibição.

Apelido de tipo para o parâmetro injetável, com a instrução `type` (Python 3.12) e `Callable` de
`collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado, como
  o `input` (RNF-06).

## Componentes

### `remover_acentos(texto)`

Função pura, igual à do `jogo_da_forca`: a forma NFD do `unicodedata.normalize` separa cada letra
acentuada na letra base mais a marca do acento, e o `join` fica só com os caracteres em que
`unicodedata.combining` dá zero. O `ç` vira `c`, e a maiúscula continua maiúscula (RF-04, ADR-4).

### `deslocar_letra(letra, chave)`

Função pura: anda a letra `chave` posições no alfabeto. A posição da letra é
`ord(letra) - ord(base)`, com a base `a` para as minúsculas e `A` para as maiúsculas; a posição
nova é `(posicao + chave) % 26`, e `chr(ord(base) + nova)` devolve a letra. O resto da divisão faz o
`z` voltar para o `a`, e, com a chave negativa, o `a` voltar para o `z`, porque no Python o resto de
um número negativo por 26 fica entre 0 e 25 (`-3 % 26 == 23`) (RF-06, RF-07, ADR-2, ADR-3).

### `montar_tabela(chave)`

Função pura: o `str.maketrans` das 52 letras (`ALFABETO + ALFABETO.upper()`) para a letra deslocada
de cada uma, montada com `deslocar_letra`. Só as letras de `a` a `z`, minúsculas e maiúsculas,
estão na tabela: todo o resto passa sem mudança no `translate`, inclusive uma letra de outro
alfabeto que o `remover_acentos` não transforma (`ß`) (RF-04, RF-06, ADR-2).

### `deslocar(texto, chave)`

Função pura: `remover_acentos(texto).translate(montar_tabela(chave))` (RF-04, RF-06, ADR-2).

### `cifrar(texto, chave)`

Função pura de uma linha: `deslocar(texto, chave)`. O nome deixa a leitura das opções em português
(RF-06).

### `decifrar(texto, chave)`

Função pura de uma linha: `deslocar(texto, -chave)`. A chave negativa mostra que decifrar é andar
para trás (RF-07, ADR-3).

### `tem_letras(texto)`

Função pura: diz se, depois de tirar os acentos, sobra pelo menos uma letra de `a` a `z`, com um
`any()` sobre o texto em minúsculas (RF-03).

### `forca_bruta(texto)`

Função pura: a lista das 25 tentativas, `[(chave, decifrar(texto, chave)) for chave in CHAVES]`
(RF-08, decisão 4).

### `contar_letras(texto)`

Função pura: o `Counter` das letras de `a` a `z` do texto, depois de tirar os acentos e passar
para minúsculas (RF-09).

### `pontuar(texto)`

Função pura: a soma, para cada letra, de quantas vezes ela aparece no texto vezes o percentual dela
em `FREQUENCIAS`. Um texto em português tem muitos `a`, `e` e `o`, que valem muito, e soma mais que
o mesmo texto decifrado com a chave errada, cheio de letras raras (RF-09, ADR-5).

### `ordenar_chaves(texto)`

Função pura: as 25 chaves ordenadas pela pontuação do texto decifrado com cada uma, da maior para a
menor: `sorted(CHAVES, key=lambda chave: pontuar(decifrar(texto, chave)), reverse=True)`. Num
empate, a chave menor vem antes, porque o `sorted` mantém a ordem original dos iguais (RF-09,
ADR-5).

### `cortar(linha)`

Função pura: devolve a linha inteira quando ela cabe em `LARGURA` caracteres; senão, os primeiros
`LARGURA - 1` mais as reticências (`…`) (RF-08, RF-09, ADR-8).

### `aviso_acentos(texto)`

Função pura: a linha do aviso de que os acentos e o ç foram tirados, numa lista com um item, quando
`remover_acentos(texto)` é diferente do texto; senão, a lista vazia, para o texto do resultado
juntar as listas sem `if` (RF-04).

### `descrever_cifra(texto, chave)`

Função pura: o texto do resultado de cifrar, com a chave usada, o texto cifrado inteiro e o aviso
de `aviso_acentos` (RF-04, RF-06).

### `descrever_decifra(texto, chave)`

Função pura: o mesmo quadro de `descrever_cifra`, com o texto decifrado (RF-04, RF-07).

### `descrever_forca_bruta(texto)`

Função pura: uma linha por tentativa de `forca_bruta`, `Chave  3: A cifra de Cesar cai…`, com a
chave alinhada em duas colunas e a linha passada por `cortar`, e a explicação do RF-08 no fim
(RF-08).

### `descrever_frequencia(texto)`

Função pura: as três letras mais comuns do texto, de `contar_letras(texto).most_common(3)`, em
maiúsculas com a contagem; a linha que lembra as três mais comuns do português; a primeira chave de
`ordenar_chaves` com o texto decifrado inteiro; e a segunda e a terceira como alternativas, cada uma
com o texto passado por `cortar`. Quando o texto tem menos de `MINIMO_LETRAS` letras, o aviso de
texto curto vem no fim (RF-09, ADR-6).

### `eh_numero(texto)`

Função pura, igual à dos outros mini-projetos: confere `isascii()` e `isdecimal()`, para um
algarismo de outra escrita não virar um número (RF-02, RF-05).

### `conferir_opcao(entrada)`

Função pura, igual à dos outros mini-projetos: tira os espaços e devolve o número da opção (de 1 a
`len(OPCOES)`), conferido com `eh_numero`, ou `None` para qualquer outra coisa (RF-02).

### `conferir_chave(entrada)`

Função pura: tira os espaços e devolve a chave como `int` quando ela passa no `eh_numero` e está em
`CHAVES`, ou `None`. O `-3` cai no `None` pelo `eh_numero`, porque o sinal não é algarismo (RF-05).

### `pedir_texto(ler)`

Lê o texto com `ler` e o pedido `Digite o texto: `, sem `strip()`, e devolve o texto quando
`tem_letras` o aceita, ou `None` (RF-03).

### `opcao_cifrar(ler)`

Pede o texto com `pedir_texto` e a chave com `ler` e `conferir_chave`. Sem letra, devolve a mensagem
do RF-03 (`Não há letras para cifrar.`); com a chave inválida, a do RF-05; senão, o texto de
`descrever_cifra`. O texto é uma variável local e some quando a função termina (RF-03, RF-05,
RF-06, RNF-07).

### `opcao_decifrar(ler)`

O mesmo caminho de `opcao_cifrar`, com a mensagem `Não há letras para decifrar.` e o texto de
`descrever_decifra` (RF-03, RF-05, RF-07, RNF-07).

### `opcao_forca_bruta(ler)`

Pede o texto com `pedir_texto`; sem letra, devolve `Não há letras para quebrar.`, e senão o texto
de `descrever_forca_bruta` (RF-03, RF-08, RNF-07).

### `opcao_frequencia(ler)`

O mesmo caminho de `opcao_forca_bruta`, com o texto de `descrever_frequencia` (RF-03, RF-09,
RNF-07).

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama a cada volta do menu (RF-01, ADR-9).

### `exibir_tela(resultado)`

Imprime, nesta ordem: o título, o resultado da ação anterior (se houver) e o menu numerado de
`OPCOES` (RF-01, decisão 10 do `requirements.md`).

### `main(ler)`

Repete: limpa a tela, exibe o quadro, lê a opção e escolhe num `if`/`elif` qual função `opcao_*`
chamar, guardando o texto devolvido; na opção inválida, guarda a mensagem de opção inválida
(RF-02); em Sair, encerra o laço com a despedida (RF-10). O padrão é `ler=input` (RNF-06, ADR-10).
O laço inteiro fica dentro de um `try` que captura `KeyboardInterrupt` e `EOFError` (RNF-04,
ADR-12). O resultado só vive na variável do laço, até a volta seguinte (RNF-07).

## Interfaces

### O terminal

Como a tela é limpa a cada volta do menu, o terminal mostra sempre um quadro só. Os quadros
ilustrativos abaixo saem das funções deste design aplicadas aos textos de exemplo (o texto exato de
cada mensagem fica no `main.py`). Cifrar `A ação começou às três.` com a chave 3:

```text
======== CIFRA DE CÉSAR ========

🔒 Texto cifrado com a chave 3:
D dfdr frphfrx dv wuhv.
📝 Os acentos e o ç foram tirados do texto.

1 : Cifrar um texto
2 : Decifrar com a chave
3 : Quebrar por força bruta
4 : Quebrar pela frequência das letras
5 : Sair

Escolha uma opção:
```

Os pedidos aparecem abaixo do menu:

```text
Escolha uma opção: 1
Digite o texto: A ação começou às três.
Digite a chave (de 1 a 25): 3
```

Decifrar troca a primeira linha por `🔓 Texto decifrado com a chave 3:`. A força bruta de
`D fliud gh Fhvdu fdl hp vhjxqgrv.` (`A cifra de César cai em segundos.` com a chave 3) ocupa o
mesmo lugar, entre o título e o menu:

```text
🔨 As 25 chaves possíveis:
Chave  1: C ekhtc fg Eguct eck go ugiwpfqu.
Chave  2: B djgsb ef Dftbs dbj fn tfhvoept.
Chave  3: A cifra de Cesar cai em segundos.
Chave  4: Z bheqz cd Bdrzq bzh dl rdftmcnr.
...
Chave 25: E gmjve hi Giwev gem iq wikyrhsw.
💡 A chave certa é a da linha que dá para ler.
   Testar todas as chaves é a força bruta.
```

A frequência de `Xblt alt h johcl kljpmyh; xblt uhv alt, jvuah hz slayhz.` (`Quem tem a chave
decifra; quem não tem, conta as letras.` com a chave 7, 43 letras):

```text
📊 Mais comuns no texto: L (7), H (7) e T (4)
   No português, as mais comuns são A, E e O.
🔓 Chave mais provável: 7
Quem tem a chave decifra; quem nao tem, conta as letras.
Outras chaves possíveis:
- Chave 19: Eisa hsa o qvojs rsqwtfo; eisa boc hsa, q…
- Chave 11: Mqai pai w ydwra zayebnw; mqai jwk pai, y…
```

Com menos de 30 letras, o quadro ganha no fim:

```text
💡 Com menos de 30 letras, a contagem pode enganar:
   confira na força bruta.
```

As mensagens de erro ocupam o mesmo lugar: `❌ Opção inválida. Digite um número de 1 a 5.`,
`❌ A chave vai de 1 a 25.` e `❌ Não há letras para cifrar.` (ou decifrar, ou quebrar). O menu
segue o formato do `calculadora_simples` (`1 : Cifrar um texto`). Nenhuma linha escrita pelo
programa passa de 54 colunas, com os emojis contando duas; o texto do usuário, mostrado inteiro no
resultado de cifrar, de decifrar e na chave mais provável, quebra no terminal como qualquer texto
longo.

### A tabela de frequência

Os 26 percentuais da tabela 1.2.1 ("Agrupamento das letras por similaridade das freqüências para
o Português") de "Análise de Freqüências de Línguas", de Bruno da Rocha Braga (Ravel/COPPE/UFRJ, 24
de março de 2003), publicado em
[analise_freq.pdf](https://www.lockabit.coppe.ufrj.br/sites/lockabit.coppe.ufrj.br/files/publicacoes/lockabit/analise_freq.pdf):
A 14,64; B 1,16; C 3,76; D 4,97; E 12,70; F 1,02; G 1,29; H 1,42; I 5,90; J 0,32; K 0,01; L 2,95;
M 4,71; N 4,85; O 10,78; P 2,58; Q 1,09; R 6,88; S 7,97; T 4,26; U 4,42; V 1,68; W 0,01; X 0,23;
Y 0,01; Z 0,42. A soma dá 100,03%, pelo arredondamento de cada letra a duas casas. O estudo conta
1,1 MB de textos de autores brasileiros, sem acentos e com o Ç como C. A tabela 1.1.1 do mesmo
estudo mostra as frequências a cada bloco de 100 KB acrescentado à contagem, em proporção com
quatro casas; a última coluna, com os 11 blocos, difere da 1.2.1 em no máximo 0,01 ponto (R, I e
H) (RNF-08).

## ADRs

### ADR-1 — Funções soltas, sem classe

**Decisão.** O programa é um conjunto de funções no nível do módulo, e a tentativa da força bruta é
um `tuple[int, str]`.

**Alternativas.** (a) uma classe `Cifra` com a chave guardada e os métodos `cifrar` e `decifrar`.
(b) uma `NamedTuple` para a tentativa.

**Porquê.** Cada operação é independente: entram o texto e a chave, e sai o texto. Funções soltas
se leem de cima para baixo e se testam chamando-as com um valor, como nos projetos anteriores da
série. Descartar (a): a chave é o único estado, e ela já entra por parâmetro. Descartar (b): a
tentativa tem só dois campos, desempacotados no próprio `for` (`for chave, texto in …`).

**Trade-off.** Nenhum relevante.

### ADR-2 — A letra com `ord`, `chr` e o resto da divisão; o texto com `str.maketrans`

**Decisão.** `deslocar_letra` faz a conta de uma letra com `ord`, `chr` e `% 26`, e `deslocar`
aplica ao texto inteiro a tabela que `montar_tabela` monta com ela, pelo `str.translate`.

**Alternativas.** (a) só `ord`, `chr` e `%`, num laço que passa por cada caractere do texto. (b) só
o `str.maketrans`, com a tabela montada por fatias do alfabeto
(`ALFABETO[chave:] + ALFABETO[:chave]`).

**Porquê.** A conta de uma letra é onde a aritmética modular aparece, e o `translate` aplica a
troca ao texto inteiro deixando de fora, sem nenhum `if`, tudo o que não está na tabela: espaço,
número, pontuação e emoji (RF-04). Descartar (a): o laço precisaria de um `if` para cada tipo de
caractere que passa sem mudança. Descartar (b): as fatias escondem a conta que o projeto ensina, e
o `%` sumiria do código.

**Trade-off.** Dois jeitos de trocar letras no mesmo programa. O docstring de `montar_tabela` diz
que a tabela é a `deslocar_letra` feita uma vez para cada uma das 52 letras.

### ADR-3 — Decifrar é deslocar com a chave negativa

**Decisão.** `decifrar(texto, chave)` é `deslocar(texto, -chave)`.

**Alternativas.** (a) `deslocar(texto, 26 - chave)`. (b) uma tabela de tradução invertida, com o
`str.maketrans` dos pares trocados.

**Porquê.** Andar para trás é a definição de decifrar, e o `%` do Python já devolve uma posição
entre 0 e 25 para a conta negativa (`(0 - 3) % 26 == 23`, o `x`). Descartar (a): dá o mesmo
resultado, mas o `26 -` pede uma explicação que a chave negativa não pede. Descartar (b): uma
segunda forma de montar a tabela, para a mesma conta.

**Trade-off.** Em outras linguagens, como C e JavaScript, o `%` de um número negativo dá um
resultado negativo, e a conta não funcionaria igual. O docstring de `deslocar_letra` registra a
diferença.

### ADR-4 — `remover_acentos` escrita de novo, igual à do `jogo_da_forca`

**Decisão.** A função que tira os acentos repete, dentro do `main.py`, a do `jogo_da_forca`, com o
mesmo nome e a mesma forma NFD.

**Alternativas.** (a) importar a função do `jogo_da_forca`. (b) uma tabela à mão, de cada letra
acentuada do português para a letra base, com o `str.maketrans`.

**Porquê.** Cada mini-projeto roda sozinho, com a pasta copiada para qualquer lugar, e o NFD é o
jeito que a série já ensinou para tirar os acentos (decisão 1 do `requirements.md`). Descartar (a): ligaria as duas pastas. Descartar (b): esqueceria alguma letra
(`ü`, `ñ`, `è`), e o NFD trata todas.

**Trade-off.** Duas funções iguais em dois projetos. São três linhas, e o teste de cada projeto
confere as letras do português.

### ADR-5 — A frequência pela soma dos produtos, não pelo qui-quadrado nem pela letra mais comum

**Decisão.** `pontuar` soma, para cada letra, a contagem vezes o percentual de `FREQUENCIAS`, e a
chave mais provável é a de maior soma.

**Alternativas.** (a) supor que a letra mais comum do texto cifrado é o A. (b) o qui-quadrado, que
soma `(contagem - esperada)² / esperada` letra a letra e escolhe a menor soma.

**Porquê.** O design mediu os três métodos com trechos dos 30 primeiros capítulos de "Dom Casmurro"
(Machado de Assis, 1899, em domínio público, lido no Wikisource), de 5 a 100 letras. Numa rodada com
1.000 trechos por tamanho, cada um cifrado com uma chave sorteada, a soma dos produtos acertou a
chave em 96,5% dos trechos de 20 letras, 99,1% dos de 30 e 99,9% dos de 50, e ela sai de uma conta
que se explica numa frase: letra comum vale muito. Descartar (a): numa rodada com 200 trechos por
tamanho, cada um cifrado com as 25 chaves, acertou entre 39% (20 letras) e 59% (100 letras), porque
o A e o E estão próximos no português (decisão 6). Descartar (b): na mesma rodada, parou entre 92% e
96%, de 20 a 100 letras, e as 69 falhas com 50 letras da outra rodada tinham todas um K, um W ou um
Y no texto: o qui-quadrado divide pela frequência esperada, e essas letras valem 0,01% na tabela,
então uma só, num nome próprio, pesa mais que o resto do texto.

**Trade-off.** A soma não diz o quanto o texto se parece com português, só qual chave se parece
mais. Um texto em outra língua também recebe uma chave mais provável, que o resultado mostra sem
aviso; as três chaves e a força bruta ficam como conferência.

### ADR-6 — O aviso de texto curto abaixo de 30 letras

**Decisão.** `MINIMO_LETRAS = 30`.

**Alternativas.** (a) 20 letras. (b) 40 letras. (c) aviso sempre.

**Porquê.** Na medição do ADR-5, 30 letras é o primeiro tamanho em que a chave mais provável acerta
em mais de 99% dos trechos (98,7% com 25, 99,1% com 30). Descartar (a): com 20, a chave mais
provável erra em cerca de 1 de cada 30 trechos, e o aviso faltaria justamente onde ajuda. Descartar
(b): com 40, o aviso apareceria em textos que a contagem resolve. Descartar (c): um aviso que
aparece sempre deixa de ser lido (decisão 8).

**Trade-off.** A medição usou o português de 1899 de um só autor. O teste da frequência usa frases
de hoje, e o resultado mostra três chaves para o caso em que a primeira erra (decisão 7).

### ADR-7 — A tabela de frequência dentro do `main.py`

**Decisão.** `FREQUENCIAS` é um `dict` no `main.py`, com os 26 percentuais da tabela 1.2.1 sem
alteração e o comentário com o título, o autor, a instituição, a data e o endereço do estudo.

**Alternativas.** (a) um arquivo de texto ao lado do `main.py`, como o `senhas_comuns.txt` do
verificador. (b) calcular a frequência na hora, a partir de um texto em português guardado no
projeto. (c) a tabela da 1.1.1, com quatro casas.

**Porquê.** São 26 números, que cabem em poucas linhas e se leem junto do código que os usa, e o
programa continua sem ler arquivo (RNF-07). Descartar (a): um arquivo para 26 números, e um ponto a
mais de falha. Descartar (b): um texto grande no projeto, e a fonte deixaria de ser um estudo
citável. Descartar (c): é a evolução da contagem a cada bloco acrescentado; a 1.2.1 é a que o estudo
apresenta como o histograma do português, e as duas diferem em no máximo 0,01 ponto.

**Trade-off.** A soma dá 100,03%, e não 100%, pelo arredondamento do estudo. A pontuação compara as
chaves entre si, então a soma não precisa fechar em 100; o teste aceita de 99,9 a 100,1.

### ADR-8 — As linhas longas cortadas em 54 caracteres

**Decisão.** `cortar` limita as linhas da força bruta e as alternativas da frequência a `LARGURA`
caracteres, com as reticências no último.

**Alternativas.** (a) mostrar o texto inteiro em cada linha. (b) medir a largura de cada caractere
na tela, com o `unicodedata.east_asian_width`, para o emoji contar duas colunas.

**Porquê.** As 25 linhas inteiras de um texto longo quebrariam no terminal e virariam um bloco em
que a linha legível não se acha; o começo basta para reconhecê-la (decisão 5). Descartar (b): uma
conta a mais para um caso raro, o emoji no texto cifrado, num projeto sobre cifras.

**Trade-off.** Um emoji no texto do usuário deixa a linha cortada uma coluna mais larga, o que o
terminal absorve.

### ADR-9 — `os.system` em vez de `subprocess.run(..., shell=True)`

**Decisão.** `limpar_tela` usa `os.system(comando)` com uma string fixa (`"cls"` ou `"clear"`).

**Alternativas.** (a) `subprocess.run(comando, shell=True)`. (b) uma biblioteca de terceiros
(`colorama`, `rich`) com uma função de limpar a tela.

**Porquê.** `comando` nunca vem do usuário: é sempre um literal escolhido pelo `os.name`.
`os.system` faz o mesmo com uma linha mais simples e sem o `shell=True` que as ferramentas de
análise estática sinalizam por hábito. Descartar (b): o programa não tem dependência de execução
(RNF-01).

**Trade-off.** `os.system` não captura a saída do comando, o que não importa aqui: o efeito
desejado é só o do terminal.

### ADR-10 — `main()` como função, chamada pelo `if __name__ == "__main__"`

**Decisão.** O laço do menu vive em `main()`, e o guard `if __name__ == "__main__"` só a chama.

**Alternativas.** (a) escrever o laço direto no bloco do guard.

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes chamam
`main()` com um leitor falso (RNF-06).

**Trade-off.** Nenhum relevante.

### ADR-11 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis e o `ç` das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e o texto do usuário pode trazer qualquer caractere.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-12 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada ponto que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do programa" em qualquer ponto, no menu, no
texto ou na chave, então um lugar só basta (RNF-04). Descartar (b): o stack trace assusta o
iniciante e parece erro do programa.

**Trade-off.** Nenhum relevante: não há nada da sessão para mostrar ou guardar na saída.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/cifra_de_cesar/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`). O projeto não tem `.gitignore` próprio: o comum, da raiz,
cobre tudo, porque o programa não cria arquivo. Fora da pasta, ganha uma entrada na matriz
`projeto` do workflow de CI (`ci.yml`) e do `pip-audit.yml` da raiz, uma entrada `uv` no
`dependabot.yml` e uma linha na tabela do `mini_projetos/README.md` e do `README.en.md`. Nenhum
outro mini-projeto muda.

## Estratégia de testes

Unitária, quase toda sobre funções puras, com casos parametrizados: `remover_acentos` com cada
vogal acentuada do português, o `ç` e as maiúsculas; `deslocar_letra` na volta do `z` para o `a` e,
com a chave negativa, do `a` para o `z`; `cifrar` com a cifra conhecida (`Ola, Mundo!` com a chave
3 vira `Rod, Pxqgr!`) e com espaço, número, pontuação e emoji passando sem mudança; `decifrar`
desfazendo `cifrar` para as 25 chaves; `conferir_chave` com as válidas e as inválidas do RF-05;
`tem_letras` com o texto vazio, só com números e com uma letra acentuada; `forca_bruta` com as 25
tentativas e a da chave certa igual ao texto original; e `cortar` no limite de `LARGURA` e um
caractere acima.

Para a frequência, `contar_letras` e `pontuar` com valores conferidos à mão, e `ordenar_chaves`
com frases de 30 letras ou mais, escritas para o teste, cifradas com cada uma das 25 chaves, tendo
a chave certa em primeiro. Um teste confere que `FREQUENCIAS` tem as 26 letras de `ALFABETO`, os
três maiores percentuais do estudo (A 14,64, E 12,70 e O 10,78) e a soma entre 99,9 e 100,1
(RNF-08). Os textos de `descrever_cifra`, `descrever_decifra`, `descrever_forca_bruta` e
`descrever_frequencia` são conferidos sem `capsys`, porque são devolvidos e não impressos,
inclusive o aviso de acentos só quando o texto tinha acento e o aviso de texto curto abaixo de
`MINIMO_LETRAS` e não a partir dele.

O leitor falso (`LeitorFalso`, uma pequena classe com `__call__`, como no `validador_de_cpf`)
devolve as respostas de uma lista e guarda os pedidos recebidos; `main()` recebe um, e os testes
conferem a ordem do quadro e as mensagens com o `capsys`, as opções válidas e inválidas, o texto
sem letras nas quatro opções, a chave inválida, a saída pelo menu e o Ctrl+C e o fim da entrada,
no menu, no texto e na chave, com um leitor que lança `KeyboardInterrupt` ou `EOFError` (RNF-04).
`limpar_tela` é substituída por uma fixture `autouse` com `monkeypatch`, para os testes não
chamarem `os.system`: é o único `monkeypatch` da suíte (RF-01).

O RNF-07 tem um teste com o módulo `ast`: ele lê o `main.py`, confere que os `import` ficam em
`__future__`, `collections`, `collections.abc`, `os`, `string`, `sys` e `unicodedata`, que nenhuma
chamada a `open`, `read_text`, `write_text`, `read_bytes` ou `write_bytes` aparece e que
`sys.argv` não é lido. Três testes medem a largura das linhas dos textos do programa, dos pedidos
e do quadro inteiro com um texto curto (54 colunas, com os emojis contando duas). Ver
`tests/test_main.py` e a seção "Testes" do `requirements.md`.
