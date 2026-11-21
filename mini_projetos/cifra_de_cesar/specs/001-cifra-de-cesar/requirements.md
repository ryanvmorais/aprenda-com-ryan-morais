---
feature: Cifra de César via terminal, com cifrar, decifrar e quebrar por força bruta e por frequência
status: concluído
date: 2026-11-21
related: []
origin: concepção
---

# 001 — Cifra de César

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. É a cifra de César no
terminal: o usuário cifra um texto deslocando cada letra por uma chave de 1 a 25, decifra com a
chave e quebra uma mensagem sem saber a chave, de dois jeitos: por força bruta, mostrando as 25
chaves possíveis, e pela frequência das letras, sugerindo a chave mais provável. É o último
mini-projeto do trio de segurança da série, depois do `gerador_de_senhas` e do
`verificador_de_forca_de_senha`: mostra uma cifra caindo em segundos, porque 25 chaves se testam
na hora. Exercita três conceitos: `ord`, `chr` e a aritmética modular (o resto da divisão por 26
faz o Z voltar para o A), o laço de força bruta sobre todas as chaves e o `collections.Counter`,
que conta as letras do texto para compará-las com a frequência das letras no português. O resto
(menu em laço, validação da entrada) fica no nível dos outros mini-projetos, para o código se ler
de cima para baixo.

A frequência das letras no português vem do estudo "Análise de Freqüências de Línguas" (B. R.
Braga, COPPE/UFRJ, 2003), que contou 1,1 MB de textos de autores brasileiros somando as letras
acentuadas à letra base e o Ç ao C, o mesmo tratamento que o programa dá aos acentos. A cifra de
César não protege nada: o programa serve para estudar como uma cifra funciona e por que esta cai.

## Objetivos

- Cifrar um texto com uma chave de 1 a 25, mantendo maiúsculas, minúsculas, espaços, números e
  pontuação.
- Decifrar um texto com a chave usada para cifrá-lo.
- Quebrar um texto cifrado por força bruta, mostrando o resultado de cada uma das 25 chaves.
- Quebrar um texto cifrado pela frequência das letras, sugerindo a chave mais provável e mostrando
  as letras mais comuns do texto.
- Tirar os acentos e a cedilha antes de cifrar, avisando quando isso acontece.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Outras cifras, como a de Vigenère ou a de substituição com alfabeto embaralhado.
- Cifrar números ou pontuação: eles passam sem mudança.
- Proteger mensagens de verdade: a cifra de César se quebra em segundos.
- Ler ou gravar arquivos com o texto, ou receber o texto ou a chave como argumento de linha de
  comando.
- Usar a rede.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como `ord`,
  `chr` e o resto da divisão deslocam uma letra e como o `Counter` acha a chave.
- **Curioso por criptografia:** quer cifrar uma mensagem, entregá-la a alguém e ver o programa
  descobrir a chave sem que ninguém a conte.
- **Quem estudou o trio de segurança:** viu a entropia no gerador e no verificador e quer ver o
  que acontece quando há só 25 chaves possíveis.

## Requisitos funcionais

### RF-01 — Mostrar o resultado e o menu a cada volta

- **Given** o programa está aberto
  **When** o menu vai ser mostrado
  **Then** a tela é limpa (`cls` no Windows, `clear` no Linux e no macOS) e mostra, nesta ordem, o
  título, o resultado da ação anterior, quando houver, e o menu numerado (Cifrar um texto,
  Decifrar com a chave, Quebrar por força bruta, Quebrar pela frequência das letras e Sair).

### RF-02 — Validar a escolha do menu

- **Given** o menu está na tela
  **When** o usuário digita um número de 1 a 5
  **Then** o programa segue para a opção correspondente.
- **Given** o menu está na tela
  **When** o usuário digita outra coisa (nada, `0`, `9` ou `abc`)
  **Then** o menu volta com uma mensagem de opção inválida, sem stack trace.

### RF-03 — Ler o texto

- **Given** o usuário escolheu uma das opções de 1 a 4
  **When** o programa pede o texto
  **Then** o texto é lido numa linha, e os espaços do começo e do fim contam como parte dele.
- **Given** o programa pediu o texto
  **When** o usuário aperta Enter sem digitar nada, ou digita um texto sem nenhuma letra
  (`2026!`)
  **Then** o menu volta com uma mensagem de que não há letras para cifrar, decifrar ou quebrar.

### RF-04 — Tirar os acentos e a cedilha

- **Given** o texto tem letras acentuadas ou o Ç (`ação`, `Às`)
  **When** ele vai ser cifrado, decifrado ou quebrado
  **Then** cada uma vira a letra sem acento, mantendo maiúscula ou minúscula (`acao`, `As`), e o
  resultado avisa, numa linha, que os acentos foram tirados.
- **Given** o texto tem um caractere que não é letra, nem depois de tirar o acento (espaço, número,
  pontuação, emoji)
  **When** ele é cifrado ou decifrado
  **Then** o caractere passa sem mudança.

### RF-05 — Ler a chave

- **Given** o usuário escolheu Cifrar ou Decifrar e digitou um texto com letras
  **When** o programa pede a chave
  **Then** ele aceita um número inteiro de 1 a 25.
- **Given** o programa pediu a chave
  **When** o usuário digita outra coisa (nada, `0`, `26`, `-3` ou `três`)
  **Then** o menu volta com uma mensagem de que a chave vai de 1 a 25, sem cifrar nem decifrar.

### RF-06 — Cifrar

- **Given** um texto com letras e uma chave válida
  **When** o texto é cifrado
  **Then** cada letra anda a chave de posições para a frente no alfabeto de 26 letras, voltando ao
  começo depois do Z (com chave 3, `A` vira `D` e `Z` vira `C`), e continua maiúscula ou
  minúscula.
- **Given** o texto foi cifrado
  **When** o resultado é mostrado
  **Then** ele traz a chave usada e o texto cifrado inteiro.

### RF-07 — Decifrar com a chave

- **Given** um texto cifrado e a chave usada para cifrá-lo
  **When** o texto é decifrado
  **Then** cada letra anda a chave de posições para trás, voltando ao fim depois do A, e o
  resultado é o texto original sem os acentos (RF-04).
- **Given** o texto foi decifrado
  **When** o resultado é mostrado
  **Then** ele traz a chave usada e o texto decifrado inteiro.

### RF-08 — Quebrar por força bruta

- **Given** um texto cifrado com letras
  **When** o usuário escolhe Quebrar por força bruta
  **Then** o resultado mostra 25 linhas, da chave 1 à 25, cada uma com a chave e o texto decifrado
  com ela, cortado com reticências quando não cabe numa linha do terminal.
- **Given** as 25 linhas estão na tela
  **When** o usuário as lê
  **Then** uma linha no fim diz que a chave certa é a da linha que dá para ler e que testar todas
  as chaves é a força bruta.

### RF-09 — Quebrar pela frequência das letras

- **Given** um texto cifrado com letras
  **When** o usuário escolhe Quebrar pela frequência das letras
  **Then** o programa conta as letras do texto, compara a contagem decifrada com cada chave de 1 a
  25 com a frequência das letras no português e ordena as chaves da mais provável para a menos
  provável.
- **Given** as chaves foram ordenadas
  **When** o resultado é mostrado
  **Then** ele traz as três letras mais comuns do texto com quantas vezes aparecem, a chave mais
  provável com o texto decifrado inteiro e as duas chaves seguintes como alternativas, cada uma
  com o começo do texto decifrado.
- **Given** o texto tem menos letras do que o mínimo fixado no design
  **When** o resultado é mostrado
  **Then** uma linha avisa que, com tão poucas letras, a contagem pode enganar e que a força bruta
  resolve.

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

Nenhuma entrada do teclado (no menu, no texto ou na chave, de qualquer tamanho e com qualquer
caractere) lança exceção não tratada: o programa sempre mostra o resultado ou explica o erro e
volta ao menu.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o programa está esperando uma entrada do teclado, no menu, no texto ou na chave
  **When** o usuário aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o programa se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive das letras acentuadas e dos emojis das mensagens e dos
caracteres que o usuário digitou, não lança `UnicodeEncodeError`, nem quando a saída padrão não
está presa a um console UTF-8 (saída redirecionada para arquivo, pipe ou executor de CI).

### RNF-06 — Testável sem teclado real

A leitura do teclado entra nas funções do programa por parâmetro, para a suíte de testes ser
determinística: o teste escolhe as entradas, sem `monkeypatch` em `input`. As funções que tiram os
acentos, cifram, decifram, montam as 25 tentativas da força bruta, contam as letras e ordenam as
chaves pela frequência são puras: recebem os valores e devolvem o resultado, sem ler o teclado nem
imprimir.

### RNF-07 — Nada sai do computador

O programa não grava nem lê arquivo, não usa rede, não recebe nada pela linha de comando e não
guarda o texto entre uma volta do menu e outra.

### RNF-08 — Frequência das letras com a fonte citada

A frequência de cada uma das 26 letras fica no `main.py`, com os percentuais da tabela 1.2.1 do
estudo "Análise de Freqüências de Línguas" (B. R. Braga, COPPE/UFRJ, 2003), sem alteração, e um
comentário com o título, o autor, a instituição, o ano e o endereço do estudo. O README cita a
mesma fonte.

### RNF-09 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o `README.en.md`, com as
mesmas seções e abertos por uma animação de uma sessão no terminal, que fica parada na última tela
para quem pede movimento reduzido, e com o aviso de que a cifra de César não protege nada; o
`CLAUDE.md`, com os comandos e a arquitetura; o `docs/stack.md`, com o mapa da stack; e o
`LICENSE`. O `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md` e o `SECURITY.md` são os da raiz do
repositório, que valem para todos os mini-projetos, e as regras de contribuição próprias deste
projeto ficam na seção de dúvidas e sugestões do README. O portão de qualidade (ruff, black, mypy
strict e pytest) roda no CI, junto da conferência de impessoalidade da raiz, e o Dependabot propõe
as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **Os acentos e a cedilha saem antes de cifrar,** com o `unicodedata`, como no `jogo_da_forca`:
   a cifra trabalha com as 26 letras do alfabeto latino, e uma letra acentuada que passasse sem
   mudança daria uma pista do texto original (`ç` e `ã` à vista). O preço é que o texto decifrado
   volta sem acentos, e o resultado avisa quando isso acontece.
2. **A chave vai de 1 a 25:** 0 e 26 deixam o texto igual, e 27 cifra como 1, porque o
   deslocamento é o resto da divisão por 26. Aceitar só de 1 a 25 dá a cada cifra um nome só.
3. **Números e pontuação passam sem mudança:** a cifra de César desloca letras; deslocar os
   dígitos seria outra cifra.
4. **A força bruta mostra as 25 chaves, e não só a certa:** o programa não sabe qual linha é
   português; quem lê acha a linha legível num olhar. Ver as 25 juntas mostra por que a cifra
   cai: uma chave de 128 bits teria 2¹²⁸ linhas.
5. **As linhas da força bruta são cortadas para caber no terminal:** a linha legível se reconhece
   pelo começo, e o texto inteiro sai pela opção de decifrar com a chave achada.
6. **A frequência compara a contagem inteira, não só a letra mais comum:** no português o A
   (14,64%) e o E (12,70%) estão próximos, e supor que a letra mais comum do texto cifrado é o A
   erra com frequência em textos curtos. Comparar as 26 letras de uma vez acerta mais; o método da
   comparação fica no design. As três letras mais comuns aparecem no resultado porque mostram a
   ideia do jeito mais simples.
7. **A frequência mostra três chaves:** quando a mais provável erra, a certa costuma estar entre
   as seguintes, e o começo do texto de cada uma basta para conferir.
8. **O mínimo de letras do aviso de texto curto sai de uma medição no design,** com textos de
   tamanhos diferentes cifrados com todas as chaves: é o tamanho abaixo do qual a chave mais
   provável deixa de ser a certa com frequência.
9. **A tabela de frequência é a da COPPE/UFRJ:** é um estudo acadêmico que descreve o que contou
   (1,1 MB de textos de autores brasileiros) e já soma as letras acentuadas à letra base e o Ç ao
   C, como o programa faz. As tabelas da Wikipédia não dizem como trataram os acentos, e as duas
   versões, em português e em inglês, divergem entre si em até um ponto percentual (no S, 7,81% e
   6,81%).
10. **O resultado aparece acima do menu, depois de limpar a tela,** sem pausa de "aperte Enter",
    como nos outros mini-projetos: o texto cifrado fica à vista enquanto o usuário escolhe a
    próxima opção.
11. **Nenhum texto entra pela linha de comando,** como no resto do trio de segurança: um argumento
    fica gravado no histórico do shell.

## Testes

### RF-04 — Acentos e cedilha

`tests/test_main.py` confere que cada vogal acentuada do português e o Ç viram a letra sem acento,
mantendo maiúscula e minúscula, que o aviso aparece só quando o texto tinha acento e que espaço,
número, pontuação e emoji passam sem mudança.

### RF-05, RF-06, RF-07 — Chave, cifrar e decifrar

A suíte confere as chaves válidas e as inválidas (nada, `0`, `26`, `-3`, `três`), a volta do Z
para o A e do A para o Z, a cifra conhecida com chave 3 (`Ola, Mundo!` vira `Rod, Pxqgr!`) e que
decifrar com a mesma chave devolve o texto sem acentos, para todas as chaves de 1 a 25.

### RF-08 — Força bruta

A suíte confere que a força bruta devolve 25 tentativas, da chave 1 à 25, que a tentativa com a
chave usada é o texto original e que as linhas longas são cortadas com reticências.

### RF-09, RNF-08 — Frequência

A suíte confere a contagem das letras, que um texto em português de tamanho acima do mínimo,
cifrado com cada chave de 1 a 25, tem a chave certa como a mais provável, que o resultado traz as
três letras mais comuns e as três chaves, que o aviso de texto curto aparece abaixo do mínimo e
que a tabela tem as 26 letras com os percentuais do estudo, somando perto de 100%.

### RF-03 — Texto

A suíte confere que o texto vazio e o texto sem letras voltam ao menu com a mensagem, nas quatro
opções, e que os espaços do começo e do fim são mantidos.

### RF-01, RF-02, RF-10 — Menu

A suíte cobre a escolha válida e as inválidas do menu, a ordem da tela (título, resultado e menu)
e a saída pelo menu. As entradas são simuladas por sequências passadas por parâmetro (RNF-06).

### RNF-04, RNF-05 — Saída do programa

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o
programa sem stack trace, no menu, no texto e na chave. A codificação da saída é conferida rodando
o programa com a saída redirecionada.

### RNF-07 — Nada sai do computador

Um teste lê o `main.py` e confere que ele só importa os módulos previstos no design, nenhum de
rede, que não abre arquivo e que não lê `sys.argv`.

### RF-01 — Limpeza de tela

A limpeza em si não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de
terminal, e não devolve nada. Fica coberta pela verificação manual ao rodar o programa e é
substituída nos testes dos outros requisitos.

### RNF-09 — Projeto conferido

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links). A conferência de impessoalidade é a da raiz
(`.github/scripts/conferir_impessoalidade.py`), que o CI roda a cada pull request. A animação é
conferida à mão, antes de cada pull request.
