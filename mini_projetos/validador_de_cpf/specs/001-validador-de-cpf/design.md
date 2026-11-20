---
feature: Validador de CPF via terminal, com a conta passo a passo
status: concluído
date: 2026-11-20
related:
  - 001-validador-de-cpf/requirements.md
origin: concepção
---

# 001 — Validador de CPF — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade, em quatro grupos: o
cálculo (os dígitos verificadores), a conferência (limpar o texto digitado e decidir se o CPF é
válido), os textos (o resultado, a conta do modo didático e o CPF gerado) e a tela (limpar, desenhar
o quadro e ler a opção). Quase todas são puras: recebem um texto ou uma lista de algarismos e
devolvem outro valor, sem ler o teclado nem imprimir. Só `limpar_tela`, `exibir_tela` e `main()`
tocam no terminal.

O cálculo é o centro do projeto, e uma função só faz a conta dos dois dígitos: recebe os algarismos
(9 para o 1º dígito, 10 para o 2º), multiplica cada um pelo seu peso, soma, tira o resto da divisão
por 11 e devolve todos esses passos, não só o dígito. O modo simples usa o dígito; o modo didático
usa os passos para montar a conta na tela; o gerador usa a mesma função para completar uma base
sorteada. O CPF circula como texto de 11 algarismos e vira lista de `int` só dentro da conta.

`main()` repete o laço do menu: limpa a tela, mostra o título, o resultado da ação anterior e o
menu, lê a opção e guarda o texto que a opção devolveu para a próxima volta. A leitura do teclado e
o sorteio entram por parâmetro (`ler`, que vale `input`, e `sortear`, que vale `random.randrange`),
e o Ctrl+C é tratado num lugar só.

## Layout de módulos

```text
main.py            # constantes, funções do cálculo, da conferência, dos textos e da tela, e main()
tests/test_main.py # suíte pytest
```

O programa não cria nenhum arquivo (RNF-07).

## Modelo de dados

O CPF é um `str` (ADR-2): o texto digitado, a versão limpa, com os 11 algarismos e nada mais
(`"28001238938"`), e a versão formatada (`"280.012.389-38"`). Dentro da conta, os algarismos são
uma `list[int]`, montada com a list comprehension `[int(c) for c in cpf]`.

A conta de um dígito é uma `NamedTuple` (ADR-4):

```python
class Conta(NamedTuple):
    algarismos: list[int]  # os 9 (1º dígito) ou 10 (2º dígito) algarismos da conta
    pesos: list[int]       # de 1 a 9 ou de 0 a 9: o último algarismo leva sempre o peso 9
    produtos: list[int]    # cada algarismo vezes o seu peso
    soma: int              # a soma dos produtos
    resto: int             # soma % 11
    digito: int            # o resto, com 10 valendo 0
```

O resultado de uma conferência é a `NamedTuple` `Conferencia(valor, recusa)`, como no
`jogo_da_forca` e no `lista_de_tarefas`: só um dos dois campos vem preenchido, e o outro é `""`. O
`valor` é o CPF limpo, com 11 algarismos.

Constantes de módulo:

- `SEPARADORES = ".- "`: os caracteres descartados antes da conferência (decisão 4 do
  `requirements.md`).
- `TAMANHO_CPF = 11`.
- `REGIOES_FISCAIS: dict[int, str]`: o 9º dígito para os estados da região fiscal, de `0: "RS"` a
  `9: "PR e SC"`, pela tabela do RF-06.
- `AVISO_GERADO`: o aviso do RF-08, um texto só para o programa e os testes.
- `OPCOES = ["Validar um CPF", "Validar mostrando a conta", "Gerar um CPF válido para teste",
  "Sair"]`: o menu, numerado a partir de 1 na exibição.

Apelidos de tipo para os parâmetros injetáveis, com a instrução `type` (Python 3.12) e `Callable`
de `collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado,
  como o `input`.
- `type Sorteador = Callable[[int], int]`: recebe `n` e devolve um inteiro de 0 a `n - 1`, como o
  `random.randrange`.

## Componentes

### `calcular_digito(algarismos)`

Função pura: monta os pesos com `list(range(10 - len(algarismos), 10))`, que dá de 1 a 9 para os 9
algarismos da base e de 0 a 9 para os 10 algarismos do 2º dígito, calcula os produtos com uma list
comprehension sobre o `zip` dos algarismos e dos pesos, soma com `sum`, tira o resto com `% 11` e
troca o 10 por 0. Devolve a `Conta` inteira (RF-04, ADR-3, ADR-4).

### `calcular_digitos(base)`

Função pura: recebe a base (`list[int]` com 9 algarismos), chama `calcular_digito(base)` e depois
`calcular_digito(base + [primeira.digito])`, e devolve as duas contas numa `tuple[Conta, Conta]`
(RF-04).

### `limpar_cpf(entrada)`

Função pura: descarta os `SEPARADORES` com uma list comprehension e confere o que sobrou, nesta
ordem: o primeiro caractere que não é um algarismo de 0 a 9 (ADR-5) recusa com a menção a ele;
nada sobrou, recusa com "nenhum CPF digitado"; sobraram menos ou mais de 11, recusa com a
quantidade encontrada. Senão, devolve `Conferencia(cpf_limpo, "")` (RF-03, decisões 3, 4 e 5).

### `eh_sequencia_repetida(cpf)`

Função pura: `len(set(cpf)) == 1`. O conjunto de um texto com os 11 algarismos iguais tem um
elemento só (RF-05).

### `conferir_cpf(entrada)`

Função pura: passa a entrada por `limpar_cpf` e, se ela foi aceita, recusa a sequência repetida
(RF-05) e, depois, compara os dois últimos algarismos com os calculados por `calcular_digitos` sobre
os 9 primeiros (RF-04). Devolve `Conferencia(cpf_limpo, "")` para o CPF válido ou a recusa com o
motivo, que para os dígitos que não conferem traz o número formatado e não traz os dígitos certos
(RF-06, decisão 7).

### `formatar_cpf(cpf)`

Função pura: monta `000.000.000-00` com fatias do CPF limpo (`cpf[:3]`, `cpf[3:6]`, `cpf[6:9]` e
`cpf[9:]`) (RF-06).

### `descrever_regiao(cpf)`

Função pura: lê o 9º algarismo, `int(cpf[8])`, e devolve a linha "Região fiscal 9: PR e SC", com
os estados de `REGIOES_FISCAIS` (RF-06, decisão 9).

### `descrever_resultado(entrada)`

Função pura: o texto do modo simples. Para o CPF válido, a linha com o número formatado e a linha
da região; para o inválido, a linha com o motivo da recusa (RF-06).

### `descrever_conta(conta, digitado, ordem)`

Função pura: o bloco de um dígito no modo didático, com o título ("1º dígito verificador"), as
linhas dos algarismos, dos pesos e dos produtos, alinhadas em colunas de largura fixa, a linha da
soma, da divisão com o resto e do dígito, e a linha do dígito digitado, com a marca de que confere
ou não (RF-07).

### `explicar_validacao(entrada)`

Função pura: o texto do modo didático. Passa a entrada por `limpar_cpf`; se ela foi recusada,
devolve só o resultado (sem conta). Senão, calcula as duas contas, junta os dois blocos de
`descrever_conta` com os dígitos digitados e acaba com o `descrever_resultado` (RF-07). A sequência
repetida mostra a conta conferindo e, no resultado, a recusa (RF-05).

### `gerar_cpf(sortear)`

Sorteia 9 algarismos com `[sortear(10) for _ in range(9)]`, sorteando a base inteira de novo
enquanto `len(set(base)) == 1`, completa com os dígitos de `calcular_digitos` e devolve o CPF limpo,
com 11 algarismos (RF-08, ADR-6).

### `descrever_gerado(cpf)`

Função pura: o texto do gerador, com o número formatado, a linha da região e o `AVISO_GERADO`
(RF-08).

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama a cada volta do menu (RF-01, ADR-7).

### `exibir_tela(resultado)`

Imprime, nesta ordem: o título, o resultado da ação anterior (se houver) e o menu numerado de
`OPCOES` (RF-01, decisão 8).

### `conferir_opcao(entrada)`

Função pura: tira os espaços e devolve o número da opção (de 1 a `len(OPCOES)`) ou `None` para
qualquer outra coisa. Confere `isdecimal()` antes do `int()`, como no `lista_de_tarefas` (RF-02).

### `main(ler, sortear)`

Repete: limpa a tela, exibe o quadro, lê a opção e escolhe num `if`/`elif`: nas opções 1 e 2, pede
o CPF com `ler` e guarda `descrever_resultado` ou `explicar_validacao`; na 3, guarda
`descrever_gerado(gerar_cpf(sortear))`; na opção inválida, guarda a mensagem de opção inválida
(RF-02); em Sair, encerra o laço com a despedida (RF-09). O laço inteiro fica dentro de um `try`
que captura `KeyboardInterrupt` e `EOFError` (RNF-04, ADR-10). O resultado só vive na variável do
laço, até a volta seguinte (RNF-07).

## Interfaces

### O terminal

Como a tela é limpa a cada volta do menu, o terminal mostra sempre um quadro só. O quadro
ilustrativo abaixo é o do modo didático, logo depois de validar o exemplo da Receita Federal (o
texto exato de cada mensagem fica no `main.py`):

```text
======== VALIDADOR DE CPF ========

1º dígito verificador
Algarismos   2   8   0   0   1   2   3   8   9
Pesos        1   2   3   4   5   6   7   8   9
Produtos     2  16   0   0   5  12  21  64  81
Soma 201 ÷ 11 = 18, resto 3 → dígito 3
Digitado: 3 ✅

2º dígito verificador
Algarismos   2   8   0   0   1   2   3   8   9   3
Pesos        0   1   2   3   4   5   6   7   8   9
Produtos     0   8   0   0   4  10  18  56  72  27
Soma 195 ÷ 11 = 17, resto 8 → dígito 8
Digitado: 8 ✅

✅ CPF válido: 280.012.389-38
Região fiscal 9: PR e SC

1 : Validar um CPF
2 : Validar mostrando a conta
3 : Gerar um CPF válido para teste
4 : Sair

Escolha uma opção:
```

O menu segue o formato do `calculadora_simples` (`1 : Validar um CPF`). Os outros resultados
ocupam o mesmo lugar, entre o título e o menu. O CPF inválido usa duas linhas, a do resultado e a
do motivo, e nenhuma linha do programa passa de 54 colunas, para o quadro caber num terminal
estreito. As frases evitam concordar com o número ("e este tem 10"), para nenhuma precisar de
plural:

```text
❌ CPF inválido: 280.012.389-39
   Os dígitos verificadores não conferem.

❌ CPF inválido: 111.111.111-11
   Sequência repetida: passa na conta, mas é recusada.

❌ CPF inválido
   Um CPF tem 11 algarismos, e este tem 10.

❌ CPF inválido
   "a" não é um algarismo.

⚠️ Nenhum CPF digitado.

🎲 CPF gerado: 280.012.389-38
Região fiscal 9: PR e SC
⚠️ Sorteado ao acaso: passa no cálculo, mas pode
   ser o CPF de uma pessoa real. Use só para testes.
```

O número do gerador acima é ilustrativo: na tela, cada geração sorteia outro.

## ADRs

### ADR-1 — Funções soltas em vez de uma classe

**Decisão.** O programa é um conjunto de funções no nível do módulo.

**Alternativas.** (a) uma classe `CPF` que guarda o número e tem os métodos `validar`, `formatar`
e `regiao`.

**Porquê.** O conceito do projeto é a função pura: entra um valor, sai outro, e nada mais muda. Um
objeto com estado esconde justamente isso. Funções soltas se leem de cima para baixo e se testam
chamando-as com um valor. Segue os projetos anteriores da série, o `adivinhe_o_numero`, o
`jogo_da_forca` e o `lista_de_tarefas`.

**Trade-off.** O CPF limpo passa de função em função. É um parâmetro só.

### ADR-2 — O CPF é texto; a lista de `int` existe só dentro da conta

**Decisão.** Todas as funções, menos as do cálculo, recebem e devolvem o CPF como `str`. A conta
recebe `list[int]`, montada com `[int(c) for c in cpf]`.

**Alternativas.** (a) guardar o CPF como `int`. (b) converter para `list[int]` logo depois da
leitura e usar a lista em todo o programa.

**Porquê.** Descartar (a): `int("01234567890")` vira `1234567890`, e o zero à esquerda some
(decisão 3 do `requirements.md`). Descartar (b): a formatação usa fatias de texto, e a sequência
repetida e a conferência dos dígitos comparam texto com texto; a lista só ajuda onde há conta. A
list comprehension da conversão fica num ponto só, onde é o assunto.

**Trade-off.** A base vira lista em `conferir_cpf` e em `explicar_validacao`. São duas list
comprehensions iguais e curtas.

### ADR-3 — Uma função para os dois dígitos, com os pesos da Receita Federal

**Decisão.** `calcular_digito` serve aos dois dígitos: os pesos são
`range(10 - len(algarismos), 10)`, e o dígito é o resto da divisão por 11, com 10 valendo 0.

**Alternativas.** (a) a forma mais divulgada: pesos de 10 a 2 (1º dígito) e de 11 a 2 (2º
dígito), e o dígito é 11 menos o resto, com 10 e 11 valendo 0. (b) duas funções, uma por dígito.

**Porquê.** É a forma publicada pela Receita Federal no Anexo II do ADE Cofis nº 41/2017, e a conta
tem um passo a menos: o dígito é o próprio resto. Escrita a partir do último algarismo, que leva
sempre o peso 9, a regra é a mesma para os dois dígitos, e uma função basta. Descartar (a): dá o
mesmo resultado (decisão 2 do `requirements.md`), e um teste compara as duas formas, mas a
subtração e os dois casos que valem 0 são dois passos a mais para explicar. Descartar (b): as duas
funções repetiriam a mesma conta.

**Trade-off.** Quem conhece a forma mais divulgada estranha o peso 0 do 2º dígito. Um comentário ao
lado dos pesos mostra a equivalência, e o README também.

### ADR-4 — A conta devolve todos os passos numa `NamedTuple`

**Decisão.** `calcular_digito` devolve a `Conta`, com os algarismos, os pesos, os produtos, a soma,
o resto e o dígito; as funções `descrever_*` montam o texto a partir dela.

**Alternativas.** (a) `calcular_digito` devolve só o `int`, e o modo didático refaz a conta para
mostrar os passos. (b) a conta imprime os passos enquanto calcula, quando recebe `mostrar=True`.

**Porquê.** Uma conta só, usada pelos três modos: o simples olha o `digito`, o didático mostra
tudo, e o gerador completa a base. Descartar (a): duas cópias da conta podem divergir, e a tela
explicaria uma conta diferente da que decidiu. Descartar (b): a função deixaria de ser pura, e o
teste teria de ler a saída do terminal para conferir um número.

**Trade-off.** O modo simples recebe passos que não usa. São seis campos pequenos por dígito.

### ADR-5 — Algarismo válido é `isascii()` e `isdigit()`

**Decisão.** `limpar_cpf` aceita um caractere quando `c.isascii() and c.isdigit()`.

**Alternativas.** (a) só `isdigit()`. (b) só `isdecimal()`. (c) `c in "0123456789"` ou uma
expressão regular.

**Porquê.** O `isdigit()` sozinho (a) aceita `²`, que o `int()` recusa com `ValueError`, e o
`isdecimal()` (b) aceita algarismos de outras escritas, como `٣`, que o `int()` converte em 3: um
CPF com eles passaria pela conta. O `isascii()` limita aos algarismos de 0 a 9, e as duas
conferências lado a lado mostram a pegadinha (decisão 5 do `requirements.md`). Descartar (c): a
lista literal dá o mesmo resultado, mas esconde o comportamento de `isdigit` que vale a pena
conhecer; a expressão regular é o conceito de outro mini-projeto da série.

**Trade-off.** Duas chamadas no lugar de uma. Um comentário dá os dois exemplos.

### ADR-6 — Sorteio por `randrange`, injetado, com a base sorteada de novo se repetir

**Decisão.** `gerar_cpf` recebe `sortear: Sorteador`, que vale `random.randrange` em `main()`, e
sorteia a base inteira de novo quando os 9 algarismos saem iguais.

**Alternativas.** (a) `random.randint(0, 999_999_999)` formatado com zeros à esquerda. (b) o
módulo `secrets`. (c) trocar só o último algarismo da base repetida.

**Porquê.** Um algarismo por vez, numa list comprehension, é o mesmo formato que a conta usa, e o
teste pode passar um sorteador que devolve uma sequência escolhida. Descartar (a): exige o zero à
esquerda de volta (`f"{n:09d}"`), o assunto que a ADR-2 evita. Descartar (b): o número não é
segredo (decisão 11 do `requirements.md`). Descartar (c): sortear de novo é a regra mais simples
de explicar, e a chance de repetir é de 10 em 1 bilhão.

**Trade-off.** Nenhum relevante: o laço de novo sorteio quase nunca roda, e um teste o exercita
com um sorteador falso.

### ADR-7 — `os.system` em vez de `subprocess.run(..., shell=True)`

**Decisão.** `limpar_tela` usa `os.system(comando)` com uma string fixa (`"cls"` ou `"clear"`).

**Alternativas.** (a) `subprocess.run(comando, shell=True)`. (b) uma biblioteca de terceiros
(`colorama`, `rich`) com uma função de limpar a tela.

**Porquê.** `comando` nunca vem do usuário: é sempre um literal escolhido pelo `os.name`.
`os.system` faz o mesmo com uma linha mais simples e sem o `shell=True` que as ferramentas de
análise estática sinalizam por hábito. Descartar (b): o programa não tem dependência de execução
(RNF-01).

**Trade-off.** `os.system` não captura a saída do comando, o que não importa aqui: o efeito
desejado é só o do terminal.

### ADR-8 — `main()` como função, chamada pelo `if __name__ == "__main__"`

**Decisão.** O laço do menu vive em `main()`, e o guard `if __name__ == "__main__"` só a chama.

**Alternativas.** (a) escrever o laço direto no bloco do guard.

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes
chamam `main()` com um leitor e um sorteador falsos (RNF-06).

**Trade-off.** Nenhum relevante.

### ADR-9 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis e os símbolos (`÷`, `→`) das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e o `÷` e o `→` deixam a conta legível.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-10 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada ponto que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do programa" em qualquer ponto, então um
lugar só basta (RNF-04). Descartar (b): o stack trace assusta o iniciante e parece erro do
programa.

**Trade-off.** Nenhum relevante: não há nada da sessão para mostrar ou guardar na saída.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/validador_de_cpf/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`). O `.gitignore` do projeto fica com as linhas de sempre, sem
nenhuma a mais, porque o programa não cria arquivo. Fora da pasta, ganha uma entrada na matriz
`projeto` do workflow de CI (`ci.yml`) e do `pip-audit.yml` da raiz, e uma linha na tabela do
`mini_projetos/README.md` e do `README.en.md`. Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, quase toda sobre funções puras, com casos parametrizados: `limpar_cpf` com cada entrada
do RF-03, `calcular_digito` e `calcular_digitos` com o exemplo da Receita Federal e com bases
escolhidas para dar resto 0, 1 e 10, `conferir_cpf` com as dez sequências repetidas e com cada
dígito errado, `formatar_cpf`, `descrever_regiao` com os 10 valores do 9º dígito, e os textos de
`descrever_resultado`, `descrever_conta`, `explicar_validacao` e `descrever_gerado`, conferidos sem
`capsys`, porque são devolvidos e não impressos.

A equivalência da decisão 2 é um teste de propriedade: uma função do próprio teste implementa a
forma mais divulgada, e o teste compara as duas em 10.000 bases sorteadas com
`random.Random(2026)`. O gerador recebe `random.Random(2026).randrange`, e o teste confere que cada
CPF gerado passa em `conferir_cpf`; um sorteador falso, que devolve uma sequência escolhida (nove
`7` e depois outra base), exercita o novo sorteio da base repetida.

O leitor falso (`LeitorFalso`, uma pequena classe com `__call__`, como no `jogo_da_forca`) devolve
as respostas de uma lista e guarda os pedidos recebidos; os testes de `main()` conferem a ordem do
quadro com o `capsys`, as opções válidas e inválidas, a saída pelo menu, e o Ctrl+C e o fim da
entrada, com um leitor que lança `KeyboardInterrupt` ou `EOFError` (RNF-04). `limpar_tela` é
substituída por uma fixture `autouse` com `monkeypatch`, para os testes não chamarem `os.system`: é
o único `monkeypatch` da suíte (RF-01).

O RNF-07 tem um teste com o módulo `ast`: ele lê o `main.py`, confere que os `import` ficam em
`__future__`, `collections.abc`, `os`, `random`, `sys` e `typing`, e que nenhuma chamada a `open`
aparece. Ver `tests/test_main.py` e a seção "Testes" do `requirements.md`.

## Desvios

1. **RF-07:** a linha do dígito digitado leva a marca e a palavra (`Digitado: 3 ✅ confere` e
   `Digitado: 4 ❌ não confere`), e não só o emoji do quadro ilustrativo, para o resultado não
   depender da cor nem do desenho do emoji. Quando o resto é 10, a linha da soma acaba em
   `(10 vale 0)`, que explica por que o dígito não é o resto.
2. **RNF-08:** a animação do README fica nas 52 colunas de sempre, e não numa largura acima de 52,
   como pedia a tarefa: a sessão não passa por uma sequência repetida (RNF-07), e a linha mais
   longa dela, a 2ª do aviso do gerador, tem 52 colunas, que cabem sem quebrar.

## Notas de implementação

- **Testes:** 125 casos: 117 em `tests/test_main.py` (67 na etapa 1, 50 na etapa 2), 6 em
  `tests/test_readme_en.py` e 2 em `tests/test_impessoalidade.py` (etapa 3). Ruff, black e mypy
  strict verdes.
- **Animação do README:** a sessão valida o exemplo da Receita com pontuação, recusa o mesmo
  número sem pontuação e com o último dígito trocado, gera um CPF com o sorteio de semente fixa,
  mostra a conta do exemplo no modo didático e sai. A última tela, a que fica parada para quem
  pede movimento reduzido, é a da conta. O modo didático ocupa 25 linhas, então o quadro fica
  mais alto que o das outras animações (viewBox de 682 × 733), num ciclo de 18 s.
- **Largura:** a linha mais longa do programa é a da sequência repetida, com 54 colunas. O teste
  mede a largura com os emojis contando duas colunas.
- **Modo didático com o 1º dígito errado:** a conta do 2º dígito usa o 1º dígito calculado, e não
  o digitado, como a conferência do modo simples; a linha dos algarismos da 2ª conta mostra o
  dígito certo, e a marca do 1º dígito mostra que o digitado não confere.
- **Conferido à mão:** uma sessão com a entrada roteirizada por stdin e a saída redirecionada
  para arquivo, chamada da raiz do repositório
  (`python mini_projetos/validador_de_cpf/main.py`), num console na codepage 1252: validou o
  exemplo da Receita com e sem pontuação, um dígito errado, uma sequência repetida no modo
  didático e uma entrada com letra, gerou dois CPFs e saiu, sem `UnicodeEncodeError`. Depois, uma
  sessão interativa aberta pelo `iniciar_validador.bat` (pelo `uv`): a tela limpa a cada volta do
  menu, e o Ctrl+C no pedido do CPF sai com a despedida, sem stack trace. O `git status` não
  mostrou nenhum arquivo criado pelo programa.
