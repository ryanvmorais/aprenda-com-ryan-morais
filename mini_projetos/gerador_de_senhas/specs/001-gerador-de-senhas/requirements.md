---
feature: Gerador de senhas e frases-senha via terminal, com a entropia de cada uma
status: aprovado
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Gerador de Senhas

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. É um gerador de senhas
no terminal: o usuário pede uma senha forte com um Enter, monta uma senha personalizada (tamanho e
tipos de caractere) ou pede uma frase-senha com palavras em português, e o programa mostra, junto
de cada uma, a entropia em bits. É o primeiro mini-projeto do trio de segurança da série e
exercita três conceitos: a diferença entre `random` e `secrets` (a documentação do Python avisa que
o `random` não serve para segurança, e o `secrets` existe para isso), as constantes do módulo
`string` (`ascii_lowercase`, `ascii_uppercase`, `digits` e `punctuation`) e a entropia, a medida
de quantas tentativas alguém precisa fazer para adivinhar a senha. O resto (menu em laço, validação
da entrada) fica no nível dos outros mini-projetos, para o código se ler de cima para baixo.

A frase-senha sorteia palavras da lista em português do BIP-39 (2048 palavras sem acento, com a
mesma grafia no Brasil e em Portugal), publicada sob a licença MIT junto da especificação BIP-39.

## Objetivos

- Gerar, com um Enter, uma senha forte no padrão do programa: 16 caracteres com minúsculas,
  maiúsculas, números e símbolos.
- Gerar uma senha personalizada, com o tamanho e os tipos de caractere escolhidos pelo usuário,
  com pelo menos um caractere de cada tipo escolhido e a opção de evitar caracteres parecidos.
- Gerar uma frase-senha com palavras em português.
- Mostrar a entropia de cada senha e de cada frase-senha, com a conta que a produz.
- Mostrar na tela por que o `random` não serve para senha: com a mesma semente, ele repete a mesma
  "senha".
- Sortear todo caractere e toda palavra de senha com o `secrets`.
- Não guardar nem enviar nenhuma senha: o que é gerado só existe na tela.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Copiar a senha para a área de transferência (pede uma dependência externa ou um comando
  diferente em cada sistema).
- Guardar senhas, como um gerenciador de senhas.
- Avaliar a força de uma senha digitada pelo usuário.
- Receber opções ou senhas como argumento de linha de comando.
- Gravar histórico, log ou qualquer arquivo.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender por que o
  `secrets` substitui o `random`, como o módulo `string` monta os alfabetos e de onde vem o número
  de bits.
- **Usuário casual:** vai criar uma conta e quer uma senha forte sem usar um gerador num site, que
  ele não sabe se guarda o que gera.
- **Quem precisa decorar uma senha:** prefere uma frase-senha, mais fácil de lembrar e de digitar
  que uma sequência de símbolos, e quer saber quantas palavras bastam.

## Requisitos funcionais

### RF-01 — Mostrar o resultado e o menu a cada volta

- **Given** o programa está aberto
  **When** o menu vai ser mostrado
  **Then** a tela é limpa (`cls` no Windows, `clear` no Linux e no macOS) e mostra, nesta ordem, o
  título, o resultado da ação anterior, quando houver, e o menu numerado (Gerar senha forte, Gerar
  senha personalizada, Gerar frase-senha, Ver por que usar `secrets` e não `random` e Sair).

### RF-02 — Validar a escolha do menu

- **Given** o menu está na tela
  **When** o usuário digita um número de 1 a 5
  **Then** o programa segue para a opção correspondente.
- **Given** o menu está na tela
  **When** o usuário digita outra coisa (nada, `0`, `9` ou `abc`)
  **Then** o menu volta com uma mensagem de opção inválida, sem stack trace.

### RF-03 — Gerar a senha forte padrão

- **Given** o usuário escolheu Gerar senha forte
  **When** a opção é processada
  **Then** o resultado mostra uma senha de 16 caracteres sorteada entre minúsculas, maiúsculas,
  números e símbolos (os 94 caracteres de `string.ascii_lowercase`, `string.ascii_uppercase`,
  `string.digits` e `string.punctuation`), com pelo menos um de cada tipo (RF-05), e a entropia
  (RF-07), sem fazer nenhuma pergunta.

### RF-04 — Montar a senha personalizada

- **Given** o usuário escolheu Gerar senha personalizada
  **When** o programa pergunta o tamanho, mostrando o padrão `16`
  **Then** Enter aceita o padrão, e um número inteiro de 8 a 64 vira o tamanho.
- **Given** o programa perguntou o tamanho
  **When** o usuário digita outra coisa (`7`, `65`, `abc` ou `12.5`)
  **Then** uma mensagem diz que o tamanho vai de 8 a 64 e a pergunta se repete.
- **Given** o tamanho foi aceito
  **When** o programa pergunta, um de cada vez, se usa minúsculas, maiúsculas, números e símbolos,
  com o padrão sim (`[S/n]`), e se evita os caracteres parecidos, com o padrão não (`[s/N]`)
  **Then** Enter aceita o padrão, `s` ou `sim` respondem sim e `n` ou `não` (ou `nao`) respondem
  não, em maiúsculas ou minúsculas.
- **Given** o programa fez uma das perguntas de sim ou não
  **When** o usuário digita outra resposta
  **Then** uma mensagem pede `s` ou `n` e a mesma pergunta se repete, sem perder as respostas
  anteriores.
- **Given** as perguntas foram respondidas
  **When** o usuário recusou os quatro tipos de caractere
  **Then** o resultado diz que a senha precisa de pelo menos um tipo de caractere, e nenhuma senha
  é gerada.
- **Given** as perguntas foram respondidas com pelo menos um tipo
  **When** a senha é gerada
  **Then** o resultado mostra a senha, do tamanho pedido, sorteada só entre os tipos escolhidos,
  com pelo menos um de cada (RF-05), e a entropia (RF-07).

### RF-05 — Sortear sem enviesar a regra "um de cada tipo"

- **Given** o alfabeto é a junção dos tipos escolhidos
  **When** a senha é sorteada
  **Then** cada caractere é sorteado com o `secrets` entre todos os caracteres do alfabeto, e, se a
  senha sorteada não tiver pelo menos um caractere de cada tipo escolhido, ela é descartada e
  sorteada de novo, inteira, até ter.
- **Given** uma senha gerada
  **When** ela é conferida
  **Then** nenhuma posição é reservada a um tipo de caractere: o primeiro caractere, por exemplo,
  pode ser de qualquer tipo escolhido.

### RF-06 — Evitar os caracteres parecidos

- **Given** o usuário pediu para evitar os caracteres parecidos
  **When** o alfabeto é montado
  **Then** ficam de fora `0` e `O`, `1`, `l` e `I`, e `|`, que se confundem em muitas fontes, e a
  senha não tem nenhum deles.
- **Given** a pergunta mostra o padrão não
  **When** o usuário aceita o padrão
  **Then** o alfabeto fica completo.

### RF-07 — Mostrar a entropia com a conta

- **Given** uma senha foi gerada
  **When** o resultado é mostrado
  **Then** abaixo da senha aparece a entropia com a conta, o tamanho vezes o log2 do tamanho do
  alfabeto, arredondada para uma casa decimal, com vírgula (`16 × log2(94) ≈ 104,9 bits`), e uma
  linha explicando que cada bit a mais dobra o número de tentativas de quem tenta adivinhar.
- **Given** uma frase-senha foi gerada
  **When** o resultado é mostrado
  **Then** a conta usa o número de palavras e o tamanho da lista (`7 × log2(2048) = 77 bits`).

### RF-08 — Gerar a frase-senha

- **Given** o usuário escolheu Gerar frase-senha
  **When** o programa pergunta quantas palavras, mostrando o padrão `7`
  **Then** Enter aceita o padrão, e um número inteiro de 5 a 12 vira a quantidade.
- **Given** o programa perguntou quantas palavras
  **When** o usuário digita outra coisa (`4`, `13` ou `abc`)
  **Then** uma mensagem diz que a quantidade vai de 5 a 12 e a pergunta se repete.
- **Given** a quantidade foi aceita
  **When** a frase-senha é gerada
  **Then** cada palavra é sorteada com o `secrets` entre as 2048 palavras da lista, com reposição
  (a mesma palavra pode sair duas vezes), e o resultado mostra as palavras em minúsculas,
  separadas por hífen, seguidas da entropia (RF-07).

### RF-09 — Mostrar por que o `random` não serve para senha

- **Given** o usuário escolheu Ver por que usar `secrets` e não `random`
  **When** a opção é processada
  **Then** o resultado mostra duas senhas de 16 caracteres geradas pelo `random` com a mesma
  semente, que saem iguais, e duas geradas pelo `secrets`, que saem diferentes.
- **Given** a demonstração está na tela
  **When** o usuário a lê
  **Then** ela explica, em poucas linhas, que o `random` segue uma conta a partir da semente, então
  quem descobre a semente (ou vê números suficientes da sequência) prevê os próximos, e que o
  `secrets` usa a fonte aleatória do sistema operacional, feita para segurança.

### RF-10 — Sair pelo menu

- **Given** o menu está na tela
  **When** o usuário escolhe Sair
  **Then** o programa se despede com uma linha e termina.

## Requisitos não funcionais

### RNF-01 — Sem dependências externas

O programa roda com Python puro (só a biblioteca padrão), sem instalar nenhum pacote para usar.
As ferramentas de desenvolvimento (ruff, black, mypy, pytest) ficam no grupo `dev` do
`pyproject.toml`, gerenciado pelo `uv`.

### RNF-02 — Portabilidade

O mesmo `main.py` funciona, sem alteração, nos terminais do Windows, do Linux e do macOS. Os
atalhos `.bat` e `.sh` cobrem só a conveniência de abrir o programa.

### RNF-03 — Feedback nunca deixa o usuário travado

Nenhuma entrada do teclado (no menu, no tamanho, nas perguntas de sim ou não ou na quantidade de
palavras) lança exceção não tratada: o programa sempre mostra o resultado ou explica o erro e
volta à pergunta ou ao menu.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o programa está esperando uma entrada do teclado
  **When** o usuário aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o programa se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive das letras acentuadas, dos símbolos da conta (`×` e `≈`) e dos
emojis das mensagens, não lança `UnicodeEncodeError`, nem quando a saída padrão não está presa a um
console UTF-8 (saída redirecionada para arquivo, pipe ou executor de CI).

### RNF-06 — Testável sem sorteio nem teclado reais

A leitura do teclado e o sorteio entram nas funções do programa por parâmetro, para a suíte de
testes ser determinística: o teste escolhe as entradas e um sorteio com semente fixa, sem
`monkeypatch` em `input`, `random` ou `secrets`. O programa, fora dos testes e da demonstração do
RF-09, sorteia sempre com o `secrets`. As funções que montam o alfabeto, conferem a regra "um de
cada tipo" e calculam a entropia são puras: recebem os valores e devolvem o resultado, sem ler o
teclado nem imprimir.

### RNF-07 — A senha não sai da tela

O programa não grava arquivo, não usa rede, não recebe nada pela linha de comando e não guarda as
senhas geradas entre uma volta do menu e outra: o único arquivo que ele lê é a lista de palavras.
Os exemplos do projeto (código, testes e README) são senhas geradas com semente fixa, nunca uma
senha em uso.

### RNF-08 — Lista de palavras conferida e com atribuição

A lista de palavras fica num arquivo de texto dentro do projeto, uma palavra por linha, com as
2048 palavras da lista portuguesa do BIP-39, sem alteração. A origem, a licença MIT e o aviso de
copyright ficam registrados no `LICENSE` e no README.

### RNF-09 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o `README.en.md`, com as
mesmas seções e abertos por uma animação de uma sessão no terminal, que fica parada na última tela
para quem pede movimento reduzido; o `CLAUDE.md`, com os comandos e a arquitetura; o
`docs/stack.md`, com o mapa da stack; e o `LICENSE`. O `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md`
e o `SECURITY.md` são os da raiz do repositório, que valem para todos os mini-projetos, e as
regras de contribuição próprias deste projeto ficam na seção de dúvidas e sugestões do README. O
portão de qualidade (ruff, black, mypy strict e pytest) roda no CI, junto da conferência de
impessoalidade da raiz, e o Dependabot propõe as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **Senha forte com um Enter, e personalizada à parte:** quem só quer uma senha boa não responde
   pergunta nenhuma; quem precisa atender às regras de um site (sem símbolos, por exemplo) usa a
   personalizada, em que Enter aceita o padrão de cada pergunta.
2. **A regra "um de cada tipo" sorteia de novo, nunca força a posição:** colocar um caractere de
   cada tipo em posições fixas, ou trocar um caractere sorteado por outro do tipo que faltou,
   deixa a senha mais previsível. Sortear a senha inteira de novo mantém todas as senhas que
   cumprem a regra com a mesma chance.
3. **A entropia mostrada é a da fórmula** (tamanho vezes o log2 do alfabeto). A regra "um de cada
   tipo" descarta algumas senhas e tira um pouco da entropia real: no máximo 1,3 bit com 8
   caracteres e 0,4 bit com 16. A diferença é pequena e a fórmula é a que se lê e se confere de
   cabeça.
4. **Tamanho de 8 a 64 caracteres:** abaixo de 8 a senha fica fraca demais até com os quatro
   tipos, e acima de 64 passa do limite de muitos sites.
5. **Caracteres parecidos:** `0`, `O`, `1`, `l`, `I` e `|`. Evitá-los ajuda quem vai ler a senha
   num papel ou digitá-la em outro aparelho; o padrão é não evitar, porque cada caractere a menos
   tira um pouco da entropia.
6. **Os símbolos são os 32 de `string.punctuation`:** o módulo `string` é parte do que o projeto
   ensina, e um site que recuse algum símbolo pede a senha personalizada sem símbolos.
7. **A lista de palavras é a portuguesa do BIP-39:** 2048 palavras sem acento (cada palavra vale
   11 bits), escolhidas para ter a mesma grafia no Brasil e em Portugal, sem palavras ofensivas e
   sem homófonos, e publicada sob a licença MIT, compatível com a do projeto. As listas diceware
   em português de 7776 palavras não têm licença clara.
8. **Frase-senha de 7 palavras por padrão, de 5 a 12:** 7 palavras dão 77 bits, a força das 6
   palavras de uma lista de 7776 que a Electronic Frontier Foundation recomenda. Abaixo de 5
   (55 bits), a frase fica mais fraca que a senha mínima de 8 caracteres.
9. **Hífen entre as palavras, todas em minúsculas:** a frase se lê e se digita sem ambiguidade, e
   o separador não entra na conta da entropia, porque é sempre o mesmo.
10. **A demonstração usa o `random` de propósito:** é o único lugar do programa em que ele gera
    algo parecido com uma senha, e só para mostrar que ele se repete. A semente é fixa, para a
    demonstração sair igual a cada vez.
11. **O resultado aparece acima do menu, depois de limpar a tela,** sem pausa de "aperte Enter":
    a senha fica à vista enquanto o usuário escolhe a próxima opção e some da tela na volta
    seguinte.
12. **Nenhuma senha entra ou sai pela linha de comando:** um argumento fica gravado no histórico do
    shell.
13. **Os testes sorteiam com semente fixa, e o programa, com o `secrets`:** é a mesma lição da
    demonstração, ao contrário. No teste, a repetição é o que se quer.

## Testes

### RF-03, RF-04, RNF-03 — Senha forte e personalizada

`tests/test_main.py` cobre a senha forte (tamanho 16, os quatro tipos presentes) e a
personalizada: o tamanho padrão, os limites 8 e 64, as recusas de `7`, `65`, `abc` e `12.5`, cada
resposta aceita nas perguntas de sim ou não (Enter, `s`, `sim`, `n`, `não`, `nao`, em maiúsculas e
minúsculas), a resposta inválida repetindo a pergunta e a recusa dos quatro tipos.

### RF-05, RF-06 — Alfabeto e regra "um de cada tipo"

Com um sorteio de semente fixa, a suíte confere que cada senha gerada só tem caracteres dos tipos
escolhidos e tem pelo menos um de cada, que uma senha sorteada sem um dos tipos é descartada e
sorteada de novo, e que, em milhares de senhas, cada tipo aparece na primeira posição. Com os
caracteres parecidos evitados, nenhum deles aparece, e o alfabeto completo tem 94 caracteres.

### RF-07 — Entropia

A suíte confere a conta da senha forte (`16 × log2(94) ≈ 104,9 bits`), a de um alfabeto só de
números, a de cada alfabeto sem os caracteres parecidos e a da frase-senha padrão
(`7 × log2(2048) = 77 bits`), com a vírgula decimal.

### RF-08, RNF-08 — Frase-senha e lista de palavras

A suíte confere o padrão de 7 palavras, os limites 5 e 12, as recusas de `4`, `13` e `abc`, o
hífen entre as palavras e que toda palavra sorteada é da lista. Um teste confere que o arquivo da
lista tem 2048 palavras distintas, todas em letras minúsculas sem acento.

### RF-09 — Demonstração

A suíte confere que as duas senhas do `random` com a mesma semente saem iguais, que as do sorteio
passado por parâmetro no lugar do `secrets` saem diferentes e que a explicação aparece no resultado.

### RF-01, RF-02, RF-10 — Menu

A suíte cobre a escolha válida e as inválidas do menu, a ordem da tela (título, resultado e menu)
e a saída pelo menu. As entradas são simuladas por uma sequência passada por parâmetro (RNF-06).

### RNF-04, RNF-05 — Saída do programa

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o
programa sem stack trace, inclusive no meio das perguntas da senha personalizada. A codificação da
saída é conferida rodando o programa com a saída redirecionada.

### RNF-06, RNF-07 — Sorteio e a senha não sai da tela

Um teste lê o `main.py` e confere que ele só importa os módulos previstos no design, nenhum de
rede, que não grava arquivo (o único acesso a arquivo é a leitura da lista de palavras) e que não
lê `sys.argv`. Outro confere que, sem o parâmetro do sorteio, as funções usam o `secrets`.

### RF-01 — Limpeza de tela

A limpeza em si não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de
terminal, e não devolve nada. Fica coberta pela verificação manual ao rodar o programa e é
substituída nos testes dos outros requisitos.

### RNF-09 — Projeto conferido

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links). A conferência de impessoalidade é a da raiz
(`.github/scripts/conferir_impessoalidade.py`), que o CI roda a cada pull request. A animação é
conferida à mão, antes de cada pull request.
