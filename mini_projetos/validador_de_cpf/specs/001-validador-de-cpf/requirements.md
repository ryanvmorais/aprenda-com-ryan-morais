---
feature: Validador de CPF via terminal, com a conta passo a passo
status: aprovado
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Validador de CPF

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. É um validador de CPF no
terminal: o usuário digita um número, com ou sem pontuação, e o programa diz se ele é válido pelo
cálculo dos dois dígitos verificadores e o mostra no formato `000.000.000-00`. Um modo didático
mostra a conta passo a passo, e um gerador monta números válidos para testar formulários. É o
primeiro mini-projeto da série cujo centro é um algoritmo, e exercita três conceitos: a soma
ponderada com o resto da divisão por 11, a limpeza e a conferência de texto digitado (`str.isdigit`
e list comprehension) e as funções pequenas e puras, que recebem um valor e devolvem outro sem
mexer em mais nada, o que as torna fáceis de testar. O resto (menu em laço, validação da entrada)
fica no nível dos outros mini-projetos, para o código se ler de cima para baixo.

A regra do cálculo segue a publicada pela Receita Federal no Anexo II do Ato Declaratório
Executivo Cofis nº 41, de 2017 (seção 2.2.15, regra `REGRA_VALIDA_CPF`), que traz um exemplo
resolvido com a base `280012389`. A relação entre o 9º dígito e a região fiscal segue o folheto
"CPF" da Educação Fiscal da Receita Federal.

## Objetivos

- Validar um CPF digitado com ou sem pontuação e mostrá-lo no formato `000.000.000-00`.
- Explicar por que um CPF é inválido: caractere que não é algarismo, quantidade errada de
  algarismos, sequência repetida ou dígitos verificadores que não conferem.
- Mostrar, no modo didático, cada multiplicação, a soma, o resto e o dígito obtido, para os dois
  dígitos verificadores.
- Gerar um CPF válido pelo cálculo para teste, com o aviso de que ele pode coincidir com o de uma
  pessoa real.
- Não guardar nem enviar nenhum CPF: o número digitado ou gerado só existe na tela.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Consultar a situação do CPF na Receita Federal ou em qualquer serviço externo.
- CNPJ, título de eleitor ou outro documento.
- Receber o CPF como argumento de linha de comando ou ler uma lista de CPFs de um arquivo.
- Gravar histórico, log ou qualquer arquivo.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como a soma
  ponderada, o resto da divisão e as funções puras se encaixam num programa de verdade.
- **Usuário casual:** recebeu um cadastro recusado e quer conferir se digitou o CPF certo, sem
  colar o número num site.
- **Quem testa um formulário:** está escrevendo um cadastro e precisa de números que passem na
  validação, sem usar o CPF de alguém conhecido.

## Requisitos funcionais

### RF-01 — Mostrar o resultado e o menu a cada volta

- **Given** o programa está aberto
  **When** o menu vai ser mostrado
  **Then** a tela é limpa (`cls` no Windows, `clear` no Linux e no macOS) e mostra, nesta ordem, o
  título, o resultado da ação anterior, quando houver, e o menu numerado (Validar um CPF, Validar
  mostrando a conta, Gerar um CPF válido para teste e Sair).

### RF-02 — Validar a escolha do menu

- **Given** o menu está na tela
  **When** o usuário digita um número de 1 a 4
  **Then** o programa segue para a opção correspondente.
- **Given** o menu está na tela
  **When** o usuário digita outra coisa (nada, `0`, `9` ou `abc`)
  **Then** o menu volta com uma mensagem de opção inválida, sem stack trace.

### RF-03 — Ler o CPF com ou sem pontuação

- **Given** o usuário escolheu validar (com ou sem a conta)
  **When** ele digita 11 algarismos, com ou sem pontos, hífen e espaços em qualquer posição
  (`280.012.389-38`, `28001238938` ou `280 012 389 38`)
  **Then** a pontuação e os espaços são descartados e os 11 algarismos seguem para a conferência.
- **Given** o usuário escolheu validar
  **When** o texto tem outro caractere além de algarismos de 0 a 9, pontos, hífen e espaços (uma
  letra, uma barra, `²` ou um algarismo de outra escrita, como `٣`)
  **Then** o resultado diz que o CPF é inválido porque tem um caractere que não é algarismo, e
  mostra qual.
- **Given** o usuário escolheu validar
  **When** sobram menos ou mais de 11 algarismos depois da limpeza
  **Then** o resultado diz que o CPF é inválido porque tem a quantidade de algarismos encontrada, e
  não 11, sem completar com zeros à esquerda.
- **Given** o usuário escolheu validar
  **When** ele não digita nada (ou só espaços e pontuação)
  **Then** o resultado diz que nenhum CPF foi digitado.

### RF-04 — Calcular os dígitos verificadores

- **Given** os 9 primeiros algarismos do CPF (a base)
  **When** o 1º dígito verificador é calculado
  **Then** cada algarismo da base, da esquerda para a direita, é multiplicado por 1, 2, 3, ..., 9,
  os produtos são somados, e o dígito é o resto da soma dividida por 11 (resto 10 vale 0).
- **Given** a base seguida do 1º dígito verificador (10 algarismos)
  **When** o 2º dígito verificador é calculado
  **Then** cada algarismo, da esquerda para a direita, é multiplicado por 0, 1, 2, ..., 9, e o
  dígito sai da mesma forma.
- **Given** a base `280012389`, do exemplo da Receita Federal
  **When** os dois dígitos são calculados
  **Then** o resultado é `38`.

### RF-05 — Recusar as sequências repetidas

- **Given** o CPF tem os 11 algarismos iguais (`000.000.000-00` a `999.999.999-99`)
  **When** ele é conferido
  **Then** o resultado diz que o CPF é inválido por ser uma sequência repetida, embora os dígitos
  verificadores confiram.

### RF-06 — Mostrar o resultado da validação

- **Given** o CPF passou nas conferências (RF-03, RF-04 e RF-05)
  **When** o resultado é mostrado
  **Then** ele diz que o CPF é válido, mostra o número no formato `000.000.000-00` e a região
  fiscal indicada pelo 9º dígito (1: DF, GO, MS, MT e TO; 2: AC, AM, AP, PA, RO e RR; 3: CE, MA e
  PI; 4: AL, PB, PE e RN; 5: BA e SE; 6: MG; 7: ES e RJ; 8: SP; 9: PR e SC; 0: RS).
- **Given** os 11 algarismos não formam uma sequência repetida, mas os dígitos verificadores não
  conferem
  **When** o resultado é mostrado
  **Then** ele diz que o CPF é inválido porque os dígitos verificadores não conferem, mostra o
  número formatado como foi digitado e não diz quais dígitos seriam os certos.

### RF-07 — Mostrar a conta no modo didático

- **Given** o usuário escolheu Validar mostrando a conta e digitou 11 algarismos
  **When** o resultado é mostrado
  **Then** antes do resultado do RF-06 aparece, para cada dígito verificador, a linha dos
  algarismos, a linha dos pesos, os produtos, a soma, a divisão por 11 com o resto e o dígito
  obtido, ao lado do dígito digitado, com a marca de que confere ou não.
- **Given** o usuário escolheu Validar mostrando a conta e digitou uma sequência repetida
  **When** o resultado é mostrado
  **Then** a conta aparece (e confere), seguida da explicação de que a sequência é recusada mesmo
  assim (RF-05).
- **Given** o usuário escolheu Validar mostrando a conta e a entrada falhou no RF-03
  **When** o resultado é mostrado
  **Then** só o motivo aparece, sem conta.

### RF-08 — Gerar um CPF válido para teste

- **Given** o usuário escolheu Gerar um CPF válido para teste
  **When** a opção é processada
  **Then** 9 algarismos são sorteados como base (sorteando de novo se saírem todos iguais), os dois
  dígitos verificadores são calculados pelo RF-04 e o resultado mostra o número no formato
  `000.000.000-00`, a região fiscal do 9º dígito e o aviso de que o número foi sorteado, passa no
  cálculo e pode coincidir com o CPF de uma pessoa real, então serve só para testar um sistema.
- **Given** um CPF gerado
  **When** ele é conferido pela validação
  **Then** é válido.

### RF-09 — Sair pelo menu

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

Nenhuma entrada do teclado (no menu ou no CPF) lança exceção não tratada: o programa sempre
mostra o resultado ou explica o erro e volta ao menu.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o programa está esperando uma entrada do teclado
  **When** o usuário aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o programa se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive das letras acentuadas e dos emojis das mensagens, não lança
`UnicodeEncodeError`, nem quando a saída padrão não está presa a um console UTF-8 (saída
redirecionada para arquivo, pipe ou executor de CI).

### RNF-06 — Testável sem sorteio nem teclado reais

A leitura do teclado e o sorteio do gerador entram nas funções do programa por parâmetro, para a
suíte de testes ser determinística: o teste escolhe as entradas e um sorteio com semente fixa, sem
`monkeypatch` em `input` ou `random`. As funções do cálculo e da conferência são puras: recebem o
texto ou os algarismos e devolvem o resultado, sem ler o teclado nem imprimir.

### RNF-07 — O CPF não sai da tela

O programa não grava arquivo, não usa rede e não guarda o histórico dos números digitados ou
gerados entre uma volta do menu e outra. Os exemplos do projeto (código, testes e README) usam só
a base do exemplo da Receita Federal (`280.012.389-38`), números inválidos montados a partir dela e
números gerados com semente fixa dentro da suíte, nunca o CPF de uma pessoa conhecida.

### RNF-08 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o `README.en.md`, com as
mesmas seções e abertos por uma animação de uma sessão no terminal, que fica parada na última tela
para quem pede movimento reduzido; o `CLAUDE.md`, com os comandos e a arquitetura; o
`docs/stack.md`, com o mapa da stack; e o `LICENSE`, o `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md`
e o `SECURITY.md`. O portão de qualidade (ruff, black, mypy strict e pytest) roda no CI, e o
Dependabot propõe as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **O gerador fica no menu, com aviso:** ele reaproveita as mesmas funções do cálculo, o que
   mostra na prática o valor de uma função pura, e serve a quem testa um formulário. O aviso não
   chama o número de fictício: há cerca de 1 bilhão de combinações válidas e centenas de milhões de
   CPFs emitidos, então um número sorteado pode ser de alguém.
2. **A conta segue a forma publicada pela Receita Federal:** pesos 1 a 9 (e 0 a 9 no 2º dígito), e
   o dígito é o próprio resto, com 10 valendo 0. A forma mais divulgada (pesos 10 a 2 e 11 a 2, e o
   dígito é 11 menos o resto, com 10 e 11 valendo 0) dá sempre o mesmo resultado, porque cada peso
   de uma forma é 11 menos o peso da outra.
3. **O CPF é texto, não número:** guardado como inteiro, ele perderia o zero à esquerda. Por isso
   10 algarismos não viram um CPF com zero na frente: o resultado pede os 11.
4. **Pontos, hífen e espaços são aceitos em qualquer posição** e descartados antes da conferência:
   quem digita não precisa acertar a máscara. Qualquer outro caractere recusa o CPF.
5. **Só algarismos de 0 a 9:** o `str.isdigit` sozinho também aceita `²` e algarismos de outras
   escritas, então a conferência exige, além dele, que o caractere seja ASCII.
6. **As sequências repetidas são recusadas** mesmo passando na conta: é a convenção dos
   validadores de cadastro, porque são os números que se digitam para pular o campo. O modo
   didático mostra a conta conferindo e explica a recusa.
7. **O CPF inválido pelos dígitos não ganha os dígitos certos:** "corrigir" um número digitado
   errado é trabalho para quem tem o documento em mãos, e o gerador já mostra um número válido.
8. **O resultado aparece acima do menu, depois de limpar a tela,** sem pausa de "aperte Enter":
   cada volta pede uma entrada só, e o resultado (inclusive a conta) fica à vista enquanto o
   usuário escolhe a próxima opção.
9. **A região fiscal vem do 9º dígito,** pela tabela do folheto da Receita Federal. Ela indica o
   endereço do cadastro inicial, não onde a pessoa mora hoje.
10. **O CPF nunca entra pela linha de comando:** um argumento fica gravado no histórico do shell.
11. **O gerador usa `random`, não `secrets`:** o número não é segredo, e o sorteio com semente fixa
    deixa o teste reproduzível.

## Testes

### RF-03, RNF-03 — Leitura e limpeza

`tests/test_main.py` cobre o CPF com e sem pontuação, com espaços, com letra, com barra, com `²`,
com algarismo de outra escrita, com 10 e com 12 algarismos, vazio e só com pontuação, conferindo o
motivo de cada recusa.

### RF-04, RF-05, RF-06 — Cálculo e resultado

A suíte confere o exemplo da Receita Federal (base `280012389`, dígitos `38`), os restos 0, 1 e 10
(o 10 vale 0), as dez sequências repetidas, um CPF com cada dígito verificador errado, a formatação
`000.000.000-00` e a região fiscal de cada um dos 10 valores do 9º dígito. Um teste compara a forma
da Receita com a forma mais divulgada em milhares de bases sorteadas com semente fixa.

### RF-07 — Modo didático

A suíte confere as linhas da conta no exemplo da Receita Federal (pesos, produtos, soma, resto e
dígito), a marca de dígito que confere e que não confere, a sequência repetida com a conta e a
recusa, e a entrada recusada pelo RF-03 sem conta.

### RF-08 — Gerador

Com um sorteio de semente fixa, a suíte confere que todo CPF gerado passa na validação, que uma
base sorteada com os 9 algarismos iguais é sorteada de novo e que o aviso aparece no resultado.

### RF-01, RF-02, RF-09 — Menu

A suíte cobre a escolha válida e as inválidas do menu, a ordem da tela (título, resultado e menu)
e a saída pelo menu. As entradas são simuladas por uma sequência passada por parâmetro (RNF-06).

### RNF-04, RNF-05 — Saída do programa

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o
programa sem stack trace. A codificação da saída é conferida rodando o programa com a saída
redirecionada.

### RNF-07 — O CPF não sai da tela

Um teste lê o `main.py` e confere que ele só importa os módulos previstos no design, nenhum de
rede, e que não chama `open`.

### RF-01 — Limpeza de tela

A limpeza em si não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de
terminal, e não devolve nada. Fica coberta pela verificação manual ao rodar o programa e é
substituída nos testes dos outros requisitos.

### RNF-08 — Projeto conferido

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links), e `tests/test_impessoalidade.py`, que os arquivos
versionados não citam o mantenedor nem apontam para ferramentas que quem clona não tem. A animação
e os arquivos da comunidade são conferidos à mão, antes de cada pull request.
