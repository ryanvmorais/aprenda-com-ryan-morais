---
feature: Gerador de senhas e frases-senha via terminal, com a entropia de cada uma
status: concluído
date: 2026-11-20
related:
  - 001-gerador-de-senhas/requirements.md
origin: concepção
---

# 001 — Gerador de Senhas — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade, em quatro grupos: o
sorteio (montar o alfabeto, sortear a senha e a frase-senha), a entropia (a conta e o texto dela),
as perguntas (conferir e repetir cada resposta do teclado) e a tela (limpar, desenhar o quadro,
ler a opção e montar o resultado de cada opção do menu). As funções do sorteio e da entropia são
puras ou recebem o sorteio por parâmetro; só as perguntas, `limpar_tela`, `exibir_tela` e `main()`
tocam no terminal.

O sorteio é o centro do projeto, e toda função que sorteia recebe um parâmetro `escolher`, com a
mesma assinatura do `secrets.choice`: recebe uma sequência e devolve um item dela. No programa, ele
vale `secrets.choice`; na demonstração do RF-09, vale o `choice` de um `random.Random` com semente
fixa; nos testes, também. É a mesma função gerando a senha nos três casos, e só o sorteador muda,
que é exatamente o que o projeto quer mostrar.

`main()` repete o laço do menu: limpa a tela, mostra o título, o resultado da ação anterior e o
menu, lê a opção e guarda o texto que a opção devolveu para a próxima volta. A lista de palavras é
lida uma vez, no começo de `main()`. A leitura do teclado entra por parâmetro (`ler`, que vale
`input`), e o Ctrl+C é tratado num lugar só.

## Layout de módulos

```text
main.py                # constantes, funções do sorteio, da entropia, das perguntas e da tela, e main()
palavras.txt           # as 2048 palavras da lista portuguesa do BIP-39, uma por linha, sem alteração
tests/test_main.py     # suíte pytest
```

O programa não cria nenhum arquivo, e o único que ele lê é o `palavras.txt` (RNF-07).

## Modelo de dados

A senha e a frase-senha são `str`. O alfabeto de uma senha é guardado em grupos, uma `list[str]`
com um texto por tipo de caractere escolhido (`["abc…z", "0123456789"]`): a junção dos grupos é o
alfabeto do sorteio, e cada grupo, separado, é o que a regra "um de cada tipo" confere (ADR-4). A
lista de palavras é uma `list[str]`.

Constantes de módulo:

- `TIPOS: dict[str, str]`: o nome de cada tipo de caractere para os caracteres dele, nesta ordem,
  que é a das perguntas: `"Minúsculas": string.ascii_lowercase`,
  `"Maiúsculas": string.ascii_uppercase`, `"Números": string.digits` e
  `"Símbolos": string.punctuation` (RF-03, decisão 6 do `requirements.md`).
- `PARECIDOS = "0O1lI|"`: os caracteres que ficam de fora quando o usuário pede (RF-06, decisão 5).
- `TAMANHO_PADRAO = 16`, `TAMANHO_MINIMO = 8` e `TAMANHO_MAXIMO = 64` (RF-03, RF-04, decisão 4).
- `PALAVRAS_PADRAO = 7`, `PALAVRAS_MINIMO = 5` e `PALAVRAS_MAXIMO = 12` (RF-08, decisão 8).
- `SEPARADOR = "-"`: o que vai entre as palavras da frase-senha (decisão 9).
- `SEMENTE_DEMONSTRACAO = 2026`: a semente do `random` na demonstração (decisão 10).
- `ARQUIVO_PALAVRAS = Path(__file__).parent / "palavras.txt"`: a lista, ao lado do `main.py`, de
  onde quer que o programa seja chamado, como o `ARQUIVO_PADRAO` do `lista_de_tarefas` (ADR-6).
- `OPCOES = ["Gerar senha forte", "Gerar senha personalizada", "Gerar frase-senha",
  "Ver por que usar secrets e não random", "Sair"]`: o menu, numerado a partir de 1 na exibição.

Apelidos de tipo para os parâmetros injetáveis, com a instrução `type` (Python 3.12) e `Callable` e
`Sequence` de `collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado,
  como o `input`.
- `type Escolhedor = Callable[[Sequence[str]], str]`: recebe uma sequência (o alfabeto, que é um
  `str`, ou a lista de palavras) e devolve um item dela, como o `secrets.choice` e o `choice` de
  um `random.Random` (ADR-2).

## Componentes

### `montar_grupos(tipos, evitar_parecidos)`

Função pura: recebe os nomes dos tipos escolhidos e devolve, para cada um, os caracteres de
`TIPOS`, sem os de `PARECIDOS` quando `evitar_parecidos` é verdadeiro, com uma comprehension sobre
o texto do tipo. Com os quatro tipos, os grupos somam 94 caracteres; sem os parecidos, 88 (25
minúsculas, 24 maiúsculas, 8 números e 31 símbolos) (RF-03, RF-04, RF-06, ADR-4).

### `tem_um_de_cada(senha, grupos)`

Função pura: `all(any(c in grupo for c in senha) for grupo in grupos)`. Lida de dentro para fora:
para cada grupo, algum caractere da senha está nele (RF-05).

### `gerar_senha(tamanho, grupos, escolher)`

Junta os grupos no alfabeto e repete: sorteia `tamanho` caracteres, cada um com
`escolher(alfabeto)`, e devolve a senha se `tem_um_de_cada` aprovar; senão, sorteia a senha inteira
de novo (RF-05, ADR-3).

### `carregar_palavras(arquivo)`

Lê o arquivo com `Path.read_text(encoding="utf-8")` e devolve `texto.split()`, a lista das palavras
(RF-08, ADR-6).

### `gerar_frase(quantidade, palavras, escolher)`

Sorteia `quantidade` palavras, cada uma com `escolher(palavras)`, com reposição, e as junta com o
`SEPARADOR` (RF-08).

### `calcular_entropia(quantidade, tamanho_alfabeto)`

Função pura: `quantidade * math.log2(tamanho_alfabeto)`. Serve à senha (a quantidade é o número de
caracteres, e o alfabeto, a soma dos grupos) e à frase-senha (o número de palavras e o tamanho da
lista) (RF-07, decisão 3).

### `descrever_entropia(quantidade, tamanho_alfabeto)`

Função pura: as duas linhas da entropia. A primeira traz a conta, com `=` e sem casa decimal quando
o resultado é inteiro (`7 × log2(2048) = 77 bits`), e com `≈` e uma casa decimal, com vírgula,
quando não é (`16 × log2(94) ≈ 104,9 bits`). A segunda explica que cada bit a mais dobra as
tentativas (RF-07, ADR-5).

### `descrever_gerada(titulo, gerada, quantidade, tamanho_alfabeto)`

Função pura: o texto do resultado de uma senha ou de uma frase-senha, com a linha do título
(`🔐 Senha forte:`), a senha ou a frase sozinha na linha seguinte e as linhas de
`descrever_entropia` (RF-03, RF-04, RF-07, RF-08).

### `explicar_random(escolher)`

O texto da demonstração: gera duas senhas fortes com `gerar_senha`, cada uma com o `choice` de um
`random.Random(SEMENTE_DEMONSTRACAO)` novo, e duas com `escolher`, e devolve as quatro, com um
título antes de cada par e a explicação do RF-09 no fim (RF-09, ADR-7).

### `conferir_opcao(entrada)`

Função pura: tira os espaços e devolve o número da opção (de 1 a `len(OPCOES)`) ou `None` para
qualquer outra coisa. Confere `isascii()` e `isdecimal()` antes do `int()`, como o `isdigit` do
`validador_de_cpf`, para um algarismo de outra escrita não virar um número (RF-02).

### `conferir_numero(entrada, padrao, minimo, maximo)`

Função pura: tira os espaços; o texto vazio devolve o `padrao`; um número de `minimo` a `maximo`,
conferido como em `conferir_opcao`, devolve o `int`; qualquer outra coisa (inclusive `12.5`)
devolve `None`. Serve ao tamanho da senha e à quantidade de palavras (RF-04, RF-08).

### `conferir_sim_nao(entrada, padrao)`

Função pura: tira os espaços e passa para minúsculas; o texto vazio devolve o `padrao`; `s` e
`sim` devolvem `True`; `n`, `não` e `nao` devolvem `False`; qualquer outra coisa, `None` (RF-04).

### `perguntar_numero(ler, pedido, padrao, minimo, maximo)` e `perguntar_sim_nao(ler, pedido, padrao)`

Repetem, num `while`, a pergunta com `ler` até a função `conferir_*` correspondente aceitar a
resposta, e devolvem o valor. A cada resposta recusada imprimem a mensagem do erro (`O tamanho vai
de 8 a 64.` ou `Responda s ou n.`) e perguntam de novo, sem limpar a tela, para as respostas
anteriores continuarem à vista (RF-04, RF-08, RNF-03, ADR-8).

### `opcao_senha_forte(escolher)`

Monta os grupos dos quatro tipos, gera a senha de `TAMANHO_PADRAO` e devolve o texto de
`descrever_gerada`, sem perguntar nada (RF-03).

### `opcao_senha_personalizada(ler, escolher)`

Pergunta o tamanho com `perguntar_numero`, cada tipo de `TIPOS` com `perguntar_sim_nao` (padrão
sim) e os caracteres parecidos (padrão não). Se nenhum tipo foi escolhido, devolve a recusa do
RF-04; senão, gera a senha com os grupos escolhidos e devolve o texto de `descrever_gerada` (RF-04,
RF-05, RF-06).

### `opcao_frase_senha(ler, escolher, palavras)`

Pergunta a quantidade de palavras com `perguntar_numero`, gera a frase com `gerar_frase` e devolve o
texto de `descrever_gerada`, com o tamanho da lista como alfabeto (RF-08).

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama a cada volta do menu (RF-01, ADR-9).

### `exibir_tela(resultado)`

Imprime, nesta ordem: o título, o resultado da ação anterior (se houver) e o menu numerado de
`OPCOES` (RF-01, decisão 11).

### `main(ler, escolher, palavras)`

Carrega a lista de `ARQUIVO_PALAVRAS` quando `palavras` não é passada e repete: limpa a tela, exibe
o quadro, lê a opção e escolhe num `if`/`elif` qual `opcao_*` chamar (a 4 chama `explicar_random`),
guardando o texto devolvido; na opção inválida, guarda a mensagem de opção inválida (RF-02); em
Sair, encerra o laço com a despedida (RF-10). Os padrões são `ler=input` e
`escolher=secrets.choice` (RNF-06). O laço inteiro fica dentro de um `try` que captura
`KeyboardInterrupt` e `EOFError` (RNF-04, ADR-12). O resultado só vive na variável do laço, até a
volta seguinte (RNF-07).

## Interfaces

### O terminal

Como a tela é limpa a cada volta do menu, o terminal mostra sempre um quadro só. O quadro
ilustrativo abaixo é o da senha forte (o texto exato de cada mensagem fica no `main.py`; a senha é
a do sorteio com `random.Random(2026)`):

```text
======== GERADOR DE SENHAS ========

🔐 Senha forte:
pO#$?nC/<*1,)~!.
Entropia: 16 × log2(94) ≈ 104,9 bits
Cada bit a mais dobra as tentativas de adivinhar.

1 : Gerar senha forte
2 : Gerar senha personalizada
3 : Gerar frase-senha
4 : Ver por que usar secrets e não random
5 : Sair

Escolha uma opção:
```

O menu segue o formato do `calculadora_simples` (`1 : Gerar senha forte`). A senha e a frase-senha
ficam sozinhas numa linha, sem emoji nem rótulo, para serem selecionadas e copiadas inteiras. As
outras linhas do programa não passam de 54 colunas, para o quadro caber num terminal estreito; a
senha de até 64 caracteres e a frase de até 12 palavras podem passar disso, e o terminal quebra a
linha sozinho, sem mudar o que se copia.

As perguntas da senha personalizada aparecem abaixo do menu, uma por linha, com o padrão entre
colchetes:

```text
Tamanho, de 8 a 64 [16]: 7
⚠️ O tamanho vai de 8 a 64.
Tamanho, de 8 a 64 [16]: 20
Minúsculas? [S/n]:
Maiúsculas? [S/n]:
Números? [S/n]:
Símbolos? [S/n]: talvez
⚠️ Responda s ou n.
Símbolos? [S/n]: n
Evitar 0 O 1 l I |? [s/N]: s
```

Os outros resultados ocupam o mesmo lugar, entre o título e o menu:

```text
🔐 Frase-senha:
sotaque-haver-abreviar-briga-cimento-locutor-carvalho
Entropia: 7 × log2(2048) = 77 bits
Cada bit a mais dobra as tentativas de adivinhar.

⚠️ Escolha pelo menos um tipo de caractere.

🎲 random, duas vezes com a semente 2026:
pO#$?nC/<*1,)~!.
pO#$?nC/<*1,)~!.
🔐 secrets, duas vezes:
<uma senha>
<outra senha>
O random segue uma conta a partir da semente:
quem descobre a semente, ou vê números seguidos
dele, prevê os próximos. O secrets usa a fonte
aleatória do sistema operacional, feita para
segurança.
```

Na tela, as duas senhas do `secrets` são sorteadas a cada vez; as do `random` saem sempre as
mesmas.

### O arquivo `palavras.txt`

Cópia, byte a byte, do `bip-0039/portuguese.txt` do repositório `bitcoin/bips`, no commit
`d353c54154bac64a88eb18cf2d47d15ead083de4` (o único que criou o arquivo, de 2020-09-01): 2048
linhas em LF, uma palavra de 4 a 8 letras minúsculas sem acento por linha, com o SHA-256
`2685e9c194c82ae67e10ba59d9ea5345a23dc093e92276fc5361f6667d79cd3f`. O `.gitattributes` da raiz
mantém o LF no checkout, então o hash vale em qualquer sistema. O `LICENSE` do projeto ganha, abaixo
da licença do projeto, uma seção com a origem da lista, a licença MIT da BIP-39 e os autores (os da
BIP-39 e os da lista portuguesa, pelos nomes de usuário do GitHub registrados no commit) (RNF-08).

## ADRs

### ADR-1 — Funções soltas em vez de uma classe

**Decisão.** O programa é um conjunto de funções no nível do módulo.

**Alternativas.** (a) uma classe `Gerador` que guarda a configuração (tamanho, tipos, parecidos) e
tem os métodos `senha` e `frase`.

**Porquê.** Cada geração é independente: entram o tamanho, os grupos e o sorteador, e sai a senha.
Uma configuração guardada num objeto seria estado que sobrevive entre uma volta do menu e outra, e
a senha personalizada pergunta tudo a cada vez. Funções soltas se leem de cima para baixo e se
testam chamando-as com um valor. Segue os projetos anteriores da série.

**Trade-off.** Os grupos e o sorteador passam de função em função. São dois parâmetros.

### ADR-2 — O sorteio entra como `escolher`, com a assinatura do `secrets.choice`

**Decisão.** Toda função que sorteia recebe `escolher: Escolhedor`, que vale `secrets.choice` em
`main()`, e o teste e a demonstração passam o `choice` de um `random.Random(semente)`.

**Alternativas.** (a) chamar `secrets.choice` direto e trocá-lo nos testes com `monkeypatch`. (b)
receber um objeto `random.Random`, que nos testes seria um `random.Random(semente)` e no programa um
`secrets.SystemRandom()`. (c) sortear índices com `secrets.randbelow`, como o `randrange` do
`validador_de_cpf`.

**Porquê.** O `secrets.choice` e o `random.Random(semente).choice` têm a mesma assinatura, então a
mesma função gera a senha de verdade, a da demonstração e a do teste, e o leitor vê que a diferença
está só no sorteador (RNF-06). Descartar (a): o RNF-06 pede o sorteio por parâmetro, sem
`monkeypatch`. Descartar (b): o `SystemRandom` é o que o `secrets` usa por dentro, mas o projeto
ensina o `secrets`, que é o módulo que a documentação recomenda para senhas. Descartar (c): o índice
seria um passo a mais (`alfabeto[randbelow(len(alfabeto))]`) para o mesmo resultado.

**Trade-off.** O tipo `Escolhedor` recebe `Sequence[str]`, e o `secrets.choice` é genérico; o mypy
aceita a troca, mas o apelido de tipo precisa de um comentário dizendo de onde vem a assinatura.

### ADR-3 — "Um de cada tipo" sorteia a senha inteira de novo

**Decisão.** `gerar_senha` sorteia cada caractere entre todos os do alfabeto e, se faltar um tipo,
descarta a senha e sorteia outra, inteira, até `tem_um_de_cada` aprovar.

**Alternativas.** (a) sortear um caractere de cada tipo, completar o resto com o alfabeto inteiro e
embaralhar. (b) sortear tudo e, se faltar um tipo, trocar um caractere sorteado por um daquele
tipo. (c) não garantir os tipos.

**Porquê.** Sortear de novo deixa todas as senhas que cumprem a regra com a mesma chance (decisão 2
do `requirements.md`). Descartar (a): as senhas com exatamente um caractere de um tipo raro, como
os números, saem mais vezes do que deviam, e o embaralhamento pede o `SystemRandom().shuffle`, mais
um conceito. Descartar (b): o caractere trocado e a posição dele ficam mais previsíveis. Descartar
(c): muitos sites recusam a senha sem um dos tipos, e a senha personalizada sem símbolos é o caso
de uso da persona casual.

**Trade-off.** O laço pode sortear mais de uma vez: com 8 caracteres e os quatro tipos, cerca de
metade das senhas sorteadas cumpre a regra, então são cerca de duas tentativas em média, e com 16
caracteres, cerca de 4 em cada 5, ou 1,2 tentativa em média. A entropia mostrada é a da fórmula,
um pouco acima da real (decisão 3).

### ADR-4 — O alfabeto em grupos, um por tipo de caractere

**Decisão.** `montar_grupos` devolve uma lista de textos, um por tipo escolhido, e o alfabeto é
`"".join(grupos)`.

**Alternativas.** (a) devolver só o alfabeto e descobrir o tipo de cada caractere com
`str.islower`, `str.isupper`, `str.isdigit` e "o resto é símbolo". (b) um `dict` do nome do tipo
para os caracteres.

**Porquê.** Os grupos servem às duas coisas que o programa faz com o alfabeto: a junção é o que se
sorteia, e cada grupo separado é o que a regra confere, sem uma segunda forma de classificar o
caractere. Descartar (a): a classificação ficaria em dois lugares (as constantes de `string` e os
métodos `is*`), que precisam concordar. Descartar (b): os nomes só servem às perguntas, que leem
`TIPOS` direto.

**Trade-off.** O tamanho do alfabeto é a soma dos tamanhos dos grupos, calculada onde a entropia é
mostrada. É uma linha (`sum(len(g) for g in grupos)`, ou `len` da junção).

### ADR-5 — A entropia com `math.log2`, e a vírgula decimal trocada à mão

**Decisão.** `calcular_entropia` usa `math.log2`, e `descrever_entropia` formata com `f"{bits:.1f}"`
e troca o ponto pela vírgula com `replace`; o resultado inteiro aparece sem casa decimal e com `=`.

**Alternativas.** (a) o módulo `locale`, com `locale.format_string`. (b) a entropia exata, contando
as senhas que cumprem a regra "um de cada tipo" (inclusão e exclusão). (c) o ponto decimal.

**Porquê.** A fórmula é a que se lê e se confere de cabeça (decisão 3). Descartar (a): o `locale`
depende de como o sistema está configurado, e o mesmo programa mostraria ponto num terminal e
vírgula em outro (RNF-02). Descartar (b): a conta exata pede uma soma alternada sobre os
subconjuntos de tipos, que não é o assunto do projeto, para mudar menos de 1,3 bit. Descartar (c):
o resultado é para quem lê em português.

**Trade-off.** O `replace` só serve a números com uma casa decimal e sem separador de milhar, que é
o caso: a maior entropia possível, 64 caracteres entre 94, dá 419,5 bits.

### ADR-6 — A lista de palavras num arquivo ao lado do `main.py`, copiado sem alteração

**Decisão.** As 2048 palavras ficam no `palavras.txt`, lido por `carregar_palavras` a partir de
`Path(__file__).parent`, e o arquivo é a cópia exata da lista portuguesa do BIP-39.

**Alternativas.** (a) a lista dentro do `main.py`, como uma constante. (b) baixar a lista da
internet na primeira execução. (c) adaptar a lista (tirar palavras, acrescentar acentos).

**Porquê.** Um arquivo de texto, uma palavra por linha, é o formato de origem, e o `main.py`
continua do tamanho dos outros mini-projetos. O `Path(__file__).parent` faz o programa achar a
lista de qualquer pasta, a lição do `lista_de_tarefas`. Descartar (a): 2048 linhas de dados
esconderiam o código. Descartar (b): o programa não usa rede (RNF-07). Descartar (c): a cópia exata
mantém a licença simples e o hash conferível, e as regras com que a lista foi feita (sem homófonos,
sem grafia dupla, sem acentos) são as que a frase-senha quer.

**Trade-off.** Se o arquivo sumir, o programa para com o `FileNotFoundError` ao abrir. Ele é parte
do projeto, como o `main.py`, e um teste confere que está lá.

### ADR-7 — A demonstração usa `random.Random(semente)`, não `random.seed`

**Decisão.** `explicar_random` cria um `random.Random(SEMENTE_DEMONSTRACAO)` novo para cada uma das
duas senhas e passa o `choice` dele a `gerar_senha`.

**Alternativas.** (a) `random.seed(SEMENTE_DEMONSTRACAO)` seguido de `random.choice`, duas vezes.
(b) mostrar só o texto da explicação, sem gerar nada.

**Porquê.** Um gerador com a semente própria não mexe no `random` do módulo, então a demonstração
não muda o sorteio de mais nada, e as duas instâncias com a mesma semente mostram a repetição lado a
lado. Usar `gerar_senha`, a mesma função das senhas de verdade, mostra que o problema não está no
código que monta a senha, e sim no sorteador. Descartar (a): mudar o estado global é o efeito
colateral que as funções do projeto evitam. Descartar (b): ver as duas senhas iguais convence mais
que ler que elas seriam.

**Trade-off.** O `random.seed` é a forma que o iniciante vê nos tutoriais. A explicação na tela diz
"semente", e um comentário no código mostra a forma com `random.seed`.

### ADR-8 — A resposta inválida repete a pergunta, sem voltar ao menu

**Decisão.** `perguntar_numero` e `perguntar_sim_nao` repetem a mesma pergunta até a resposta ser
aceita, imprimindo o motivo da recusa.

**Alternativas.** (a) voltar ao menu com a mensagem de erro, como o `validador_de_cpf`, que pede uma
entrada só por volta. (b) aceitar qualquer resposta que não seja `n` como sim.

**Porquê.** A senha personalizada faz seis perguntas: voltar ao menu por um erro na quinta perderia
as quatro anteriores (RF-04). Descartar (b): uma resposta digitada errado viraria uma escolha que o
usuário não fez.

**Trade-off.** As perguntas imprimem, então não são puras; a conferência de cada resposta fica nas
funções `conferir_*`, que são, e o teste das perguntas usa o leitor falso e o `capsys`.

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

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes
chamam `main()` com um leitor, um sorteador e uma lista de palavras falsos (RNF-06).

**Trade-off.** Nenhum relevante.

### ADR-11 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis e os símbolos (`×`, `≈`) das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e o `×` e o `≈` deixam a conta da entropia legível.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-12 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada ponto que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do programa" em qualquer ponto, inclusive no
meio das perguntas da senha personalizada, então um lugar só basta (RNF-04). Descartar (b): o stack
trace assusta o iniciante e parece erro do programa.

**Trade-off.** Nenhum relevante: não há nada da sessão para mostrar ou guardar na saída.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/gerador_de_senhas/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`), mais o `palavras.txt`. O projeto não tem `.gitignore`
próprio: o comum, da raiz, cobre tudo, porque o programa não cria arquivo. Fora da pasta, ganha uma
entrada na matriz `projeto` do workflow de CI (`ci.yml`) e do `pip-audit.yml` da raiz, e uma linha
na tabela do `mini_projetos/README.md` e do `README.en.md`. Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, quase toda sobre funções puras, com casos parametrizados: `montar_grupos` com cada tipo,
com os quatro e sem os parecidos (94 e 88 caracteres), `tem_um_de_cada` com senhas montadas à mão,
`calcular_entropia` e `descrever_entropia` com os valores do RF-07, `conferir_opcao`,
`conferir_numero` e `conferir_sim_nao` com cada entrada do RF-02, do RF-04 e do RF-08, e os textos
de `descrever_gerada` e `explicar_random`, conferidos sem `capsys`, porque são devolvidos e não
impressos.

O sorteio usa `random.Random(2026).choice` no lugar do `secrets.choice` (ADR-2): o teste confere
que milhares de senhas geradas só têm caracteres dos grupos, têm pelo menos um de cada e que, entre
elas, cada um dos quatro tipos aparece na primeira posição (RF-05). Um
sorteador falso, que devolve os caracteres de uma lista escolhida (uma senha só de letras e depois
uma com número), exercita o novo sorteio. Na demonstração, o teste passa o `choice` de um
`random.Random(1)` como `escolher` e confere que as duas senhas do `random` com a semente 2026 saem
iguais e as duas do `escolher`, diferentes. Um teste confere, com o `inspect.signature`, que o
padrão do `escolher` de `main()` é o `secrets.choice` (RNF-06).

O leitor falso (`LeitorFalso`, uma pequena classe com `__call__`, como no `validador_de_cpf`)
devolve as respostas de uma lista e guarda os pedidos recebidos; os testes de `main()` e das
perguntas conferem a ordem do quadro e as mensagens de recusa com o `capsys`, as opções válidas e
inválidas, a saída pelo menu e o Ctrl+C e o fim da entrada, no menu e no meio das perguntas, com um
leitor que lança `KeyboardInterrupt` ou `EOFError` (RNF-04). Os testes de `main()` recebem uma
lista de palavras curta, e um teste à parte chama `carregar_palavras(ARQUIVO_PALAVRAS)` e confere as
2048 palavras distintas, todas de `[a-z]`, e o SHA-256 do arquivo (RNF-08). `limpar_tela` é
substituída por uma fixture `autouse` com `monkeypatch`, para os testes não chamarem `os.system`: é
o único `monkeypatch` da suíte (RF-01).

O RNF-07 tem um teste com o módulo `ast`: ele lê o `main.py`, confere que os `import` ficam em
`__future__`, `collections.abc`, `math`, `os`, `pathlib`, `random`, `secrets`, `string` e `sys`, que
nenhuma chamada a `open`, `write_text` ou `write_bytes` aparece e que `sys.argv` não é lido. Ver
`tests/test_main.py` e a seção "Testes" do `requirements.md`.

## Desvios

1. **RF-04, RF-08:** as perguntas de número começam por "Digite" (`Digite o tamanho, de 8 a 64
   [16]:` e `Digite a quantidade de palavras, de 5 a 12 [7]:`), e não só pelo nome, como no quadro
   ilustrativo. O `pedido` de `perguntar_numero` leva o artigo (`"o tamanho"`), e a recusa sai do
   mesmo texto com `capitalize()` (`⚠️ O tamanho vai de 8 a 64.`), sem um parâmetro a mais para a
   mensagem.
2. **RNF-09:** a animação do README fica nas 52 colunas de sempre, e não em 54 ou numa largura
   acima de 52, como pedia o `tasks.md`: a linha mais longa da sessão, o pedido da quantidade de
   palavras com a resposta (`Digite a quantidade de palavras, de 5 a 12 [7]: 5`), tem 49 colunas,
   que cabem sem quebrar.

## Notas de implementação

- **Testes:** 128 casos em `tests/test_main.py` (etapas 1 e 2, implementadas juntas). Ruff, black
  e mypy strict verdes.
- **`eh_numero`:** a conferência `isascii()` e `isdecimal()` ficou numa função pequena, usada por
  `conferir_opcao` e por `conferir_numero`, para a regra não se repetir.
- **Senha da demonstração:** com a semente 2026, o `random` gera `pO#$?nC/<*1,)~!.`, a mesma do
  quadro ilustrativo.
- **Testes:** 134 casos: 128 em `tests/test_main.py` (etapas 1 e 2) e 6 em
  `tests/test_readme_en.py` (etapa 3).
- **ADR-3, a média de tentativas:** a conta exata, por inclusão e exclusão, dá 46% das senhas
  de 8 caracteres e 82% das de 16 cumprindo a regra com os quatro tipos; o trade-off do ADR-3
  dizia "quase sempre uma" para 16 caracteres e foi corrigido para "cerca de 4 em cada 5". A
  perda de entropia da decisão 3 do `requirements.md` confere: no pior caso, 1,26 bit com 8
  caracteres e 0,37 bit com 16.
- **Animação do README:** a sessão gera a senha forte, recusa o tamanho 7 na personalizada e
  gera uma de 12 caracteres sem símbolos e sem os parecidos, uma frase-senha de 5 palavras, a
  demonstração do `random` e sai. A última tela, a que fica parada para quem pede movimento
  reduzido, é a da demonstração. O sorteio da sessão usa a semente 11, e não a
  `SEMENTE_DEMONSTRACAO`, porque com a mesma semente a senha forte sairia igual às duas do
  `random`. viewBox de 682 × 635, num ciclo de 19 s.
