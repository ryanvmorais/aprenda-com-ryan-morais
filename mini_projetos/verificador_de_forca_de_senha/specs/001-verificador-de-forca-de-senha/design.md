---
feature: Verificador de força de senha via terminal, com nota, entropia estimada e sugestões
status: aprovado
date: 2026-11-20
related:
  - 001-verificador-de-forca-de-senha/requirements.md
origin: concepção
---

# 001 — Verificador de Força de Senha — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade, em quatro grupos: as
regras (classificar os caracteres, achar repetições e sequências, comparar com a lista de senhas
comuns), a nota (a entropia estimada, a conta dela e a faixa), os textos (o resultado, as
sugestões e os exemplos comentados) e a tela (limpar, desenhar o quadro, ler a opção e a senha). As
regras, a nota e os textos são funções puras; só `limpar_tela`, `exibir_tela` e `main()` tocam no
terminal.

A verificação é um caminho só: `analisar` recebe a senha e a lista de senhas comuns e devolve uma
`Analise`, uma tupla nomeada com tudo o que pesou na nota (o tamanho, quantos caracteres contaram,
os tipos presentes, a entropia, se há repetição, sequência ou senha comum, e a nota). O resultado
da tela e as sugestões são montados a partir da `Analise`, que não guarda a senha: depois dela,
nenhuma função recebe o texto digitado. Os exemplos comentados passam pela mesma `analisar`, então
a nota de cada exemplo é calculada, nunca escrita à mão.

`main()` repete o laço do menu: limpa a tela, mostra o título, o resultado da ação anterior e o
menu, lê a opção e guarda o texto que a opção devolveu para a próxima volta. A lista de senhas
comuns é lida uma vez, no começo de `main()`. As duas leituras do teclado entram por parâmetro
(`ler`, que vale `input`, e `ler_senha`, que vale `getpass.getpass`), e o Ctrl+C é tratado num
lugar só.

## Layout de módulos

```text
main.py                # constantes, funções das regras, da nota, dos textos e da tela, e main()
senhas_comuns.txt      # as 150 senhas da lista portuguesa do SecLists, uma por linha, sem alteração
tests/test_main.py     # suíte pytest
```

O programa não cria nenhum arquivo, e o único que ele lê é o `senhas_comuns.txt` (RNF-07).

## Modelo de dados

A senha é uma `str` que só existe dentro de `opcao_verificar`. A lista de senhas comuns é um
`set[str]`, já em minúsculas, para a comparação sem diferença de caixa ser uma busca no conjunto
(RF-06). Um trecho previsível (repetição ou sequência) é um `tuple[int, int]` com o início e o fim,
como o `span()` de um `re.Match` (RF-05).

`Analise(NamedTuple)`, como a `Conferencia` do `validador_de_cpf`:

- `tamanho: int`: quantos caracteres a senha tem.
- `contam: int`: quantos contam na entropia, com cada trecho previsível valendo um (RF-05).
- `tipos: list[str]`: os nomes dos tipos presentes, na ordem de `TIPOS` (RF-04).
- `alfabeto: int`: a soma dos tamanhos dos tipos presentes (RF-04).
- `bits: float`: a entropia estimada (RF-07).
- `repeticao: bool`, `sequencia: bool` e `comum: bool`: o que as regras acharam (RF-05, RF-06).
- `nota: int`: de 0 a 4 (RF-07).

Constantes de módulo:

- `TIPOS: dict[str, int]`: o nome de cada tipo para o tamanho dele, tirado do módulo `string`, como
  no `gerador_de_senhas`: `"minúsculas": len(string.ascii_lowercase)` (26),
  `"maiúsculas": len(string.ascii_uppercase)` (26), `"números": len(string.digits)` (10) e
  `"símbolos": len(string.punctuation)` (32) (RF-04, decisão 5 do `requirements.md`).
- `SEQUENCIAS = ("abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiop", "asdfghjkl",
  "zxcvbnm")`: o alfabeto, os números e as três fileiras do teclado, lidas para a frente; o
  contrário sai do `[::-1]` (RF-05, decisão 4).
- `REPETICAO = re.compile(r"(.)\1{2,}", re.IGNORECASE)`: um caractere seguido de pelo menos mais
  duas cópias dele (RF-05, ADR-3).
- `LIMITES = (28, 36, 60, 80)`: os bits a partir dos quais a nota sobe para 1, 2, 3 e 4 (RF-07,
  decisão 1).
- `NOMES = ("muito fraca", "fraca", "razoável", "boa", "forte")`: o nome de cada nota, pelo índice.
- `TAMANHO_MINIMO = 8` e `NOTA_MAXIMA_CURTA = 1`: abaixo do tamanho mínimo, a nota não passa de 1
  (RF-07, decisão 8).
- `ARQUIVO_SENHAS_COMUNS = Path(__file__).parent / "senhas_comuns.txt"`: a lista, ao lado do
  `main.py`, de onde quer que o programa seja chamado, como o `ARQUIVO_PALAVRAS` do gerador (ADR-6).
- `EXEMPLOS: list[tuple[str, str]]`: as senhas dos exemplos comentados, cada uma com a linha que
  explica o que pesou (RF-10, ADR-9).
- `OPCOES = ["Verificar uma senha", "Ver exemplos comentados", "Sair"]`: o menu, numerado a partir
  de 1 na exibição.

Apelido de tipo para os parâmetros injetáveis, com a instrução `type` (Python 3.12) e `Callable` de
`collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado. O
  `input` e o `getpass.getpass` têm essa assinatura, e os dois parâmetros de `main()` usam o mesmo
  apelido (ADR-2).

## Componentes

### `classificar(senha)`

Função pura: devolve os nomes dos tipos presentes, na ordem de `TIPOS`, com um `any()` por tipo:
`any(c.islower() for c in senha)`, `any(c.isupper() for c in senha)`,
`any(c.isdigit() for c in senha)`, e os símbolos com
`any(not (c.islower() or c.isupper() or c.isdigit()) for c in senha)`. Um caractere entra em um
tipo só: a letra acentuada passa no `islower` ou no `isupper`, e o espaço cai nos símbolos (RF-04).

### `achar_repeticoes(senha)`

Função pura: `[m.span() for m in REPETICAO.finditer(senha)]`. O `\1` é a referência ao grupo: o
mesmo caractere que o `(.)` pegou, e o `{2,}` pede pelo menos mais duas cópias. Com o
`re.IGNORECASE`, `aAa` também é repetição (RF-05, ADR-3).

### `achar_sequencias(senha)`

Função pura: percorre as janelas de 3 caracteres (`senha[i : i + 3]`) e devolve o `(i, i + 3)` de
cada janela que, em minúsculas, está dentro de uma das `SEQUENCIAS` ou do contrário dela:
`any(janela in s or janela in s[::-1] for s in SEQUENCIAS)`. Uma sequência de 4 (`abcd`) devolve
duas janelas que se sobrepõem, juntadas por `juntar_trechos` (RF-05, ADR-3).

### `juntar_trechos(trechos)`

Função pura: ordena os trechos e junta os que se sobrepõem, para cada trecho previsível valer um
caractere só, mesmo quando uma repetição encosta numa sequência (`aaabc`). Trechos vizinhos sem
sobreposição (`aaabbb`) continuam dois (RF-05, ADR-4).

### `contar_caracteres(tamanho, trechos)`

Função pura: o tamanho menos os caracteres dentro dos trechos juntados, mais um por trecho:
`tamanho - sum(fim - inicio for inicio, fim in trechos) + len(trechos)` (RF-05, ADR-4).

### `carregar_senhas_comuns(arquivo)`

Lê o arquivo com `Path.read_text(encoding="utf-8")` e devolve o conjunto das linhas em minúsculas,
com uma set comprehension sobre `splitlines()` (RF-06, ADR-6).

### `calcular_entropia(quantidade, tamanho_alfabeto)`

Função pura: `quantidade * math.log2(tamanho_alfabeto)`, a mesma do `gerador_de_senhas` (RF-07,
ADR-7).

### `descrever_entropia(quantidade, tamanho_alfabeto)`

Função pura: a linha da entropia, `Entropia estimada: 7 × log2(94) ≈ 45,9 bits`, com `=` e sem casa
decimal quando o resultado é inteiro e `≈` com uma casa e vírgula quando não é, como no gerador
(RF-08, ADR-7).

### `dar_nota(bits, tamanho, comum)`

Função pura: 0 se a senha é comum; senão, quantos `LIMITES` os bits alcançam
(`sum(bits >= limite for limite in LIMITES)`), limitado a `NOTA_MAXIMA_CURTA` quando o tamanho é
menor que `TAMANHO_MINIMO` (RF-06, RF-07, ADR-5).

### `analisar(senha, comuns)`

Função pura: liga as regras e a nota. Classifica, acha e junta os trechos, conta os caracteres,
soma o alfabeto pelos `TIPOS` presentes, calcula a entropia, confere `senha.lower() in comuns` e dá
a nota, devolvendo a `Analise`, que não guarda a senha (RF-04 a RF-07, ADR-8).

### `faltam_caracteres(analise)`

Função pura: quantos caracteres a mais, com o mesmo alfabeto, levam a entropia a `LIMITES[-1]`
(80 bits): `math.ceil((80 - bits) / math.log2(alfabeto))`, ou 0 quando já passou (RF-09).

### `sugerir(analise)`

Função pura: a lista das sugestões, nesta ordem de prioridade: se a senha é comum, só a de trocar
de senha; senão, a de tirar a repetição ou a sequência, quando há, e a dos caracteres que faltam,
com a lembrança da frase-senha, quando a nota é menor que 4. Sem nenhuma, a lista traz só a linha
de que não há nada a melhorar (RF-09).

### `descrever_analise(analise)`

Função pura: o texto do resultado (RF-08), na ordem do quadro em "Interfaces": a nota com o nome,
o tamanho e quantos contam, a linha de `descrever_entropia`, os tipos presentes e os que faltam, as
três conferências (repetição, sequência e lista) com ✅ ou ❌ e as sugestões de `sugerir`. Nenhuma
linha recebe a senha, então nenhuma pode mostrá-la (RF-08, ADR-8).

### `descrever_exemplos(comuns)`

Função pura: para cada senha de `EXEMPLOS`, chama `analisar` e monta duas linhas, a senha à vista
com a nota calculada (`🔑 Senha@123: 2 de 4, razoável`) e a explicação; no fim, as linhas do RF-10
sobre a estimativa por regras (RF-10, ADR-9).

### `eh_numero(texto)`

Função pura, igual à do gerador: confere `isascii()` e `isdecimal()`, para um algarismo de outra
escrita não virar um número (RF-02).

### `conferir_opcao(entrada)`

Função pura, igual à do gerador: tira os espaços e devolve o número da opção (de 1 a
`len(OPCOES)`), conferido com `eh_numero`, ou `None` para qualquer outra coisa (RF-02).

### `opcao_verificar(ler_senha, comuns)`

Lê a senha com `ler_senha` e o pedido do RF-03. A senha vazia devolve o aviso de que nenhuma senha
foi digitada; qualquer outra, sem `strip()`, vai para `analisar`, e a função devolve o texto de
`descrever_analise`. A senha é uma variável local e some quando a função termina (RF-03, RNF-07,
ADR-8).

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama a cada volta do menu (RF-01, ADR-10).

### `exibir_tela(resultado)`

Imprime, nesta ordem: o título, o resultado da ação anterior (se houver) e o menu numerado de
`OPCOES` (RF-01, decisão 11 do `requirements.md`).

### `main(ler, ler_senha, comuns)`

Carrega a lista de `ARQUIVO_SENHAS_COMUNS` quando `comuns` não é passada e repete: limpa a tela,
exibe o quadro, lê a opção e escolhe num `if`/`elif` qual função chamar (`opcao_verificar` ou
`descrever_exemplos`), guardando o texto devolvido; na opção inválida, guarda a mensagem de opção
inválida (RF-02); em Sair, encerra o laço com a despedida (RF-11). Os padrões são `ler=input` e
`ler_senha=getpass.getpass` (RNF-06, ADR-2). O laço inteiro fica dentro de um `try` que captura
`KeyboardInterrupt` e `EOFError` (RNF-04, ADR-13). O resultado só vive na variável do laço, até a
volta seguinte, e não contém a senha (RNF-07).

## Interfaces

### O terminal

Como a tela é limpa a cada volta do menu, o terminal mostra sempre um quadro só. O quadro
ilustrativo abaixo é o de `Senha@123` (o texto exato de cada mensagem fica no `main.py`):

```text
====== VERIFICADOR DE FORÇA DE SENHA ======

🔎 Nota: 2 de 4, razoável
Tamanho: 9 caracteres, 7 contam na entropia
Entropia estimada: 7 × log2(94) ≈ 45,9 bits
Tem: minúsculas, maiúsculas, números e símbolos
✅ Sem repetição (como aaa ou 111)
❌ Tem sequência (como abc, 123 ou qwe)
✅ Fora da lista de senhas comuns

💡 O que melhorar:
- Tire a sequência: ela quase não soma força.
- Com mais 6 caracteres, a senha passa de 80 bits.
  Uma frase-senha é longa e fácil de decorar.

1 : Verificar uma senha
2 : Ver exemplos comentados
3 : Sair

Escolha uma opção:
```

O pedido da senha aparece abaixo do menu, e o que se digita não aparece:

```text
Escolha uma opção: 1
Digite a senha (ela não aparece na tela):
```

Quando falta um tipo, a linha `Tem:` ganha a vizinha `Falta:` (`Falta: símbolos`). A senha comum
troca as sugestões por uma só:

```text
💡 O que melhorar:
- Troque de senha: ela está entre as mais usadas,
  e é das primeiras que alguém testa.
```

Os exemplos comentados ocupam o mesmo lugar, entre o título e o menu; as notas abaixo são as
calculadas pelo protótipo das regras:

```text
🔑 123mudar: 0 de 4, muito fraca
   Está na lista das senhas mais usadas.
🔑 Gato@7: 1 de 4, fraca
   Tem os quatro tipos, mas só 6 caracteres.
🔑 Senha@123: 2 de 4, razoável
   Os quatro tipos, mas o 123 é uma sequência.
🔑 girassol-azul: 3 de 4, boa
   Só minúsculas e o hífen: o tamanho faz a força.
🔑 sotaque-haver-abreviar-briga: 4 de 4, forte
   Quatro palavras sorteadas: longa e fácil.
A nota é uma estimativa por regras. Uma palavra
conhecida com um número e um símbolo no fim
continua fácil de adivinhar, mesmo com os quatro
tipos de caractere.
```

O menu segue o formato do `calculadora_simples` (`1 : Verificar uma senha`). Nenhuma linha do
programa passa de 54 colunas, com os emojis contando duas, para o quadro caber num terminal
estreito.

### O arquivo `senhas_comuns.txt`

Cópia, byte a byte, do `Passwords/Common-Credentials/Language-Specific/Portugese_Pwdb_common-password-list-top-150.txt`
do repositório `danielmiessler/SecLists` (o "Portugese" é a grafia do nome original), no commit
`fef30127d19485fb91f390a3c8c535aefbd50047` (de 2025-03-22, que deu ao arquivo o nome atual): 150
linhas em LF, uma senha ASCII por linha, com o SHA-256
`e827d8607d9812e0140be005fcff49d1a0a151cfa853e392127ae79d61fdaf38`. O `.gitattributes` da raiz
mantém o LF no checkout, então o hash vale em qualquer sistema. O `LICENSE` do projeto ganha, abaixo
da licença do projeto, uma seção com a origem da lista e as duas licenças MIT: a do SecLists
(Copyright (c) 2018 Daniel Miessler) e a do Pwdb-Public, de onde a lista veio (Copyright (c) 2020
Ata Hakçıl) (RNF-08).

## ADRs

### ADR-1 — Funções soltas e uma `NamedTuple`, em vez de uma classe

**Decisão.** O programa é um conjunto de funções no nível do módulo, e o resultado da verificação é
a `Analise`, uma `NamedTuple`.

**Alternativas.** (a) uma classe `Verificador` com a lista de senhas comuns guardada e um método
`verificar`. (b) um `dict` com as chaves da análise.

**Porquê.** Cada verificação é independente: entram a senha e a lista, e sai a análise. Funções
soltas se leem de cima para baixo e se testam chamando-as com um valor, como nos projetos
anteriores da série, e a `NamedTuple` dá nome a cada campo, como a `Conferencia` do
`validador_de_cpf`. Descartar (a): a lista é o único estado, e ela já entra por parâmetro.
Descartar (b): o mypy não confere as chaves de um `dict` comum, e um campo escrito errado só
apareceria ao rodar.

**Trade-off.** A `Analise` tem nove campos, mais que as tuplas nomeadas dos outros projetos. Cada um
é um item do resultado (RF-08), e o teste confere um de cada vez.

### ADR-2 — A senha entra por `ler_senha`, com o `getpass.getpass` como padrão

**Decisão.** `main()` recebe `ler_senha: Leitor = getpass.getpass`, e o teste passa um leitor falso.

**Alternativas.** (a) chamar o `getpass.getpass` direto e trocá-lo nos testes com `monkeypatch`.
(b) o parâmetro `echo_char` do `getpass`, que mostra um `*` por caractere digitado. (c) ler a senha
com o mesmo `ler` do menu.

**Porquê.** O `getpass.getpass` recebe o pedido e devolve o texto, como o `input`, então um
parâmetro separado, com o mesmo tipo, deixa a troca à vista e o teste sem `monkeypatch` (RNF-06).
Descartar (a): o RNF-06 pede a leitura por parâmetro. Descartar (b): o `echo_char` só existe a
partir do Python 3.14, e o piso do projeto é o 3.12. Descartar (c): o menu tem de mostrar o que se
digita, e a senha não.

**Trade-off.** Num terminal em que o `getpass` não consegue esconder o que se digita (como o IDLE),
o Python avisa com um `GetPassWarning` e mostra a senha. O README diz para rodar o programa num
terminal.

### ADR-3 — Repetição com expressão regular, sequência com janelas de 3

**Decisão.** `achar_repeticoes` usa a expressão `(.)\1{2,}`, e `achar_sequencias` confere cada
janela de 3 caracteres com o operador `in` contra as `SEQUENCIAS` e o contrário delas.

**Alternativas.** (a) uma expressão regular também para as sequências, com todas as janelas
possíveis numa alternância (`abc|bcd|…|cba|…`). (b) a diferença dos códigos dos caracteres
(`ord(b) - ord(a) == 1`). (c) um laço também para as repetições.

**Porquê.** A repetição é o exemplo clássico da referência a um grupo (`\1`), o recurso do `re` que
um laço não mostra. A sequência é "este trecho está dentro daquela string", e o `in` diz isso em
português. Descartar (a): uma alternância com mais de cem janelas, montada por código, esconde a
ideia. Descartar (b): pega sequências que ninguém digita (`:;<`) e não pega as fileiras do
teclado. Descartar (c): perderia a lição do `re`.

**Trade-off.** As duas regras usam formas diferentes de procurar. O docstring de cada uma diz por
quê, e as duas devolvem trechos no mesmo formato (`span()`), que `juntar_trechos` trata igual.

### ADR-4 — Cada trecho previsível vale um caractere

**Decisão.** Os trechos que se sobrepõem se juntam, e cada trecho juntado conta como um caractere
na entropia.

**Alternativas.** (a) tirar o trecho inteiro da conta (`aaa` valeria zero). (b) tirar um número fixo
de bits por trecho. (c) baixar a nota em um ponto por trecho.

**Porquê.** Quem testa `aaaa` ou `1234` escolheu um caractere e uma regra: a força está no
primeiro, e o resto quase não acrescenta (decisão 3 do `requirements.md`). Contar um mantém a mesma
fórmula do gerador, só com um tamanho menor, e a conta mostrada (`7 × log2(94)`) explica o
desconto. Descartar (a): uma senha só de sequência (`abcd`) daria zero bits, e a conta mostraria
`0 × log2(26)`. Descartar (b) e (c): o desconto viraria um número sem origem na fórmula.

**Trade-off.** O desconto ignora quanto a regra é conhecida: `abc` e `qwe` valem o mesmo. Para uma
estimativa didática, a diferença não muda a nota.

### ADR-5 — A nota por faixas de bits, com a lista e o tamanho mínimo como travas

**Decisão.** `dar_nota` conta quantos `LIMITES` a entropia estimada alcança, dá 0 à senha comum e
limita a 1 a senha com menos de 8 caracteres.

**Alternativas.** (a) um ponto por regra cumprida (tamanho, cada tipo, sem sequência). (b) as faixas
do zxcvbn, em número de tentativas (de 10³ a 10¹⁰, de 10 a 33 bits).

**Porquê.** A nota sai da mesma conta que aparece na tela, então quem lê a entropia entende a nota
(decisão 1). Descartar (a): daria a nota máxima a `Senha@123`, o caso que a NIST aponta contra as
regras de composição (decisão 9). Descartar (b): as faixas do zxcvbn medem tentativas estimadas com
dicionários e padrões; com a fórmula de caracteres sorteados, que conta bem mais tentativas que as
de quem adivinha de verdade, quase toda senha de 8 caracteres passaria de 33 bits e tiraria 4.

**Trade-off.** As faixas são deste projeto, sem uma norma por trás. Os testes fixam as fronteiras, e
a decisão 1 diz de onde vem cada uma.

### ADR-6 — A lista num arquivo ao lado do `main.py`, copiado sem alteração

**Decisão.** As 150 senhas ficam no `senhas_comuns.txt`, lido por `carregar_senhas_comuns` a partir
de `Path(__file__).parent`, e o arquivo é a cópia exata da lista do SecLists.

**Alternativas.** (a) a lista dentro do `main.py`, como uma constante. (b) baixar a lista da
internet na primeira execução. (c) adaptar a lista (tirar duplicadas de caixa, tirar o palavrão).

**Porquê.** Um arquivo de texto, uma senha por linha, é o formato de origem, e o `main.py` continua
do tamanho dos outros mini-projetos, como o `palavras.txt` do gerador. Descartar (a): 150 linhas de
dados esconderiam o código. Descartar (b): o programa não usa rede (RNF-07). Descartar (c): a cópia
exata mantém a licença simples e o hash conferível (decisão 7), e a comparação em minúsculas já
trata `Brasil` e `BRASIL` como uma.

**Trade-off.** Se o arquivo sumir, o programa para com o `FileNotFoundError` ao abrir. Ele é parte
do projeto, como o `main.py`, e um teste confere que está lá.

### ADR-7 — A entropia e a conta escritas de novo, iguais às do gerador

**Decisão.** `calcular_entropia` e `descrever_entropia` repetem a conta e a formatação do
`gerador_de_senhas` (`math.log2`, a vírgula trocada à mão com `replace`), dentro do `main.py`.

**Alternativas.** (a) importar as funções do `gerador_de_senhas`. (b) o módulo `locale` para a
vírgula.

**Porquê.** Cada mini-projeto roda sozinho, com a pasta copiada para qualquer lugar, e a mesma
conta nos dois mostra que o verificador avalia com a régua do gerador. Descartar (a): ligaria as
duas pastas, e o verificador pararia sem a outra. Descartar (b): o `locale` depende da configuração
do sistema, e o mesmo programa mostraria ponto num terminal e vírgula em outro (RNF-02).

**Trade-off.** Duas funções iguais em dois projetos. São quatro linhas, e o teste de cada projeto
confere os mesmos valores (`16 × log2(94) ≈ 104,9 bits`).

### ADR-8 — Nada depois de `analisar` recebe a senha

**Decisão.** A senha só passa por `opcao_verificar` e `analisar`; a `Analise` guarda números,
nomes de tipos e verdadeiro ou falso, e os textos são montados a partir dela.

**Alternativas.** (a) guardar a senha na `Analise`, para os textos usarem. (b) mostrar os trechos
achados (`abc`), para o usuário saber o que tirar.

**Porquê.** Se nenhuma função de texto recebe a senha, nenhuma pode mostrá-la, e o teste confere
isso pelo formato, não por cada mensagem (RF-08, decisão 10). Descartar (a): um campo a mais que um
texto futuro poderia imprimir. Descartar (b): o trecho é parte da senha que o `getpass` escondeu.

**Trade-off.** A sugestão de tirar a sequência não diz qual é. A senha é de quem digitou, que sabe
onde pôs o `123`. O Python também não apaga a `str` da memória ao fim da função: ela fica até o
coletor de lixo reaproveitar o espaço, o que nenhum programa em Python consegue evitar.

### ADR-9 — Os exemplos com a nota calculada

**Decisão.** `EXEMPLOS` guarda só a senha e a explicação; a nota de cada uma sai de `analisar` na
hora de mostrar.

**Alternativas.** (a) escrever a nota junto da explicação, na constante.

**Porquê.** Uma nota escrita à mão desencontraria da regra na primeira mudança das faixas, e os
exemplos mostrariam uma coisa e a verificação outra. O teste confere que as notas calculadas cobrem
de 0 a 4 (RF-10).

**Trade-off.** A explicação de cada exemplo continua escrita à mão e fala do que pesou na nota. O
teste confere a cobertura das notas, e a leitura confere as explicações.

### ADR-10 — `os.system` em vez de `subprocess.run(..., shell=True)`

**Decisão.** `limpar_tela` usa `os.system(comando)` com uma string fixa (`"cls"` ou `"clear"`).

**Alternativas.** (a) `subprocess.run(comando, shell=True)`. (b) uma biblioteca de terceiros
(`colorama`, `rich`) com uma função de limpar a tela.

**Porquê.** `comando` nunca vem do usuário: é sempre um literal escolhido pelo `os.name`.
`os.system` faz o mesmo com uma linha mais simples e sem o `shell=True` que as ferramentas de
análise estática sinalizam por hábito. Descartar (b): o programa não tem dependência de execução
(RNF-01).

**Trade-off.** `os.system` não captura a saída do comando, o que não importa aqui: o efeito
desejado é só o do terminal.

### ADR-11 — `main()` como função, chamada pelo `if __name__ == "__main__"`

**Decisão.** O laço do menu vive em `main()`, e o guard `if __name__ == "__main__"` só a chama.

**Alternativas.** (a) escrever o laço direto no bloco do guard.

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes
chamam `main()` com dois leitores falsos e uma lista de senhas comuns curta (RNF-06).

**Trade-off.** Nenhum relevante.

### ADR-12 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis e os símbolos (`×`, `≈`) das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e o `×` e o `≈` deixam a conta da entropia legível.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-13 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada ponto que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do programa" em qualquer ponto, inclusive no
pedido da senha, então um lugar só basta (RNF-04). O `getpass` devolve o terminal ao normal antes
de repassar o Ctrl+C. Descartar (b): o stack trace assusta o iniciante e parece erro do programa.

**Trade-off.** Nenhum relevante: não há nada da sessão para mostrar ou guardar na saída.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/verificador_de_forca_de_senha/`, com o mesmo kit
dos outros mini-projetos (listado no `tasks.md`), mais o `senhas_comuns.txt`. O projeto não tem
`.gitignore` próprio: o comum, da raiz, cobre tudo, porque o programa não cria arquivo. Fora da
pasta, ganha uma entrada na matriz `projeto` do workflow de CI (`ci.yml`) e do `pip-audit.yml` da
raiz, uma entrada `uv` no `dependabot.yml` e uma linha na tabela do `mini_projetos/README.md` e do
`README.en.md`. Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, quase toda sobre funções puras, com casos parametrizados: `classificar` com cada tipo,
com letra acentuada e com espaço; `achar_repeticoes`, `achar_sequencias`, `juntar_trechos` e
`contar_caracteres` com os casos do RF-05 (`aaa`, `1111`, `abc`, `cba`, `123`, `987`, `qwe`,
`asd`, `ABC`, `aa`, `ab`, `aaabc` e `aaabbb`); `calcular_entropia` e `descrever_entropia` com os
valores do gerador e do quadro; `dar_nota` nas fronteiras de cada faixa, com a senha comum e com 7
caracteres; `faltam_caracteres` e `sugerir` em cada caso do RF-09; e os textos de
`descrever_analise` e `descrever_exemplos`, conferidos sem `capsys`, porque são devolvidos e não
impressos.

Para o RF-08, um teste verifica uma lista de senhas e confere que nenhuma delas, nem nenhum trecho
de 3 caracteres dela, aparece no texto do resultado. Para o RF-10, o teste confere que as notas dos
exemplos, calculadas por `analisar`, cobrem de 0 a 4.

O leitor falso (`LeitorFalso`, uma pequena classe com `__call__`, como no `validador_de_cpf`)
devolve as respostas de uma lista e guarda os pedidos recebidos; `main()` recebe um para o menu e
outro para a senha, e os testes conferem a ordem do quadro e as mensagens com o `capsys`, as opções
válidas e inválidas, a senha vazia, a saída pelo menu e o Ctrl+C e o fim da entrada, no menu e no
pedido da senha, com um leitor que lança `KeyboardInterrupt` ou `EOFError` (RNF-04). Um teste
confere, com o `inspect.signature`, que o padrão do `ler_senha` de `main()` é o `getpass.getpass`
(RNF-06). Os testes de `main()` recebem uma lista de senhas comuns curta, e um teste à parte chama
`carregar_senhas_comuns(ARQUIVO_SENHAS_COMUNS)` e confere as 150 linhas do arquivo e o SHA-256 dele
(RNF-08). `limpar_tela` é substituída por uma fixture `autouse` com `monkeypatch`, para os testes
não chamarem `os.system`: é o único `monkeypatch` da suíte (RF-01).

O RNF-07 tem um teste com o módulo `ast`: ele lê o `main.py`, confere que os `import` ficam em
`__future__`, `collections.abc`, `getpass`, `math`, `os`, `pathlib`, `re`, `string`, `sys` e
`typing`, que nenhuma chamada a `open`, `write_text` ou `write_bytes` aparece e que `sys.argv` não
é lido. Três testes medem a largura das linhas dos textos e do quadro inteiro (54 colunas, com os
emojis contando duas). Ver `tests/test_main.py` e a seção "Testes" do `requirements.md`.
