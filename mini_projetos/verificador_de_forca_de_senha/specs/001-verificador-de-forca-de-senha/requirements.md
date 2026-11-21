---
feature: Verificador de força de senha via terminal, com nota, entropia estimada e sugestões
status: em andamento
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Verificador de Força de Senha

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. É um verificador de
força de senha no terminal: o usuário digita uma senha, que não aparece na tela, e o programa dá
uma nota de 0 a 4, mostra o que pesou na nota e diz o que melhorar, sem que a senha saia do
computador. É o segundo mini-projeto do trio de segurança da série, par do `gerador_de_senhas`:
usa a mesma fórmula de entropia (tamanho vezes o log2 do tamanho do alfabeto), agora para avaliar
uma senha em vez de gerá-la. Exercita três conceitos: regras escritas com `any()` e os métodos de
string (`islower`, `isupper` e `isdigit`), o módulo `re` para achar repetições e sequências
(`aaa`, `abc`, `123`) e o `getpass`, que lê a senha sem mostrá-la. O resto (menu em laço,
validação da entrada) fica no nível dos outros mini-projetos, para o código se ler de cima para
baixo.

A comparação com senhas comuns usa a lista em português do SecLists (150 senhas mais usadas por
falantes de português, extraídas pelo projeto Pwdb-Public de credenciais vazadas), publicada sob a
licença MIT. A nota é uma estimativa didática feita por regras, não uma auditoria: ferramentas
como o zxcvbn reconhecem palavras de dicionário, datas e trocas de letra por número, que estas
regras não reconhecem.

## Objetivos

- Ler a senha sem mostrá-la na tela, com o `getpass`.
- Dar uma nota de 0 a 4 (muito fraca, fraca, razoável, boa e forte) a partir da entropia estimada,
  com a conta que a produz.
- Mostrar o que pesou na nota: o tamanho, os tipos de caractere presentes, as sequências e
  repetições e a presença na lista de senhas comuns.
- Dizer o que mudar para a senha melhorar, inclusive quantos caracteres faltam para a nota 4.
- Mostrar, com exemplos fixos, por que ter os quatro tipos de caractere não basta para uma senha
  ser forte.
- Não guardar, não mostrar e não enviar a senha digitada: ela só existe na memória do programa
  durante a verificação.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Consultar vazamentos de senhas na internet (como o Have I Been Pwned): o programa não usa rede.
- Reconhecer palavras de dicionário, nomes, datas ou trocas de letra por número (`s3nh4`), como
  fazem estimadores como o zxcvbn.
- Gerar senhas (é o que o `gerador_de_senhas` faz).
- Guardar senhas, como um gerenciador de senhas.
- Receber a senha como argumento de linha de comando.
- Gravar histórico, log ou qualquer arquivo.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como uma regra
  vira `any()`, como uma expressão regular acha `aaa` e de onde vem a nota.
- **Usuário casual:** quer saber se a senha que usa é fraca, sem digitá-la num site que ele não
  sabe se guarda o que recebe.
- **Quem estudou o gerador:** quer ver a mesma conta de entropia do outro lado, avaliando uma senha
  feita à mão, e entender por que `Senha@123` não é tão forte quanto parece.

## Requisitos funcionais

### RF-01 — Mostrar o resultado e o menu a cada volta

- **Given** o programa está aberto
  **When** o menu vai ser mostrado
  **Then** a tela é limpa (`cls` no Windows, `clear` no Linux e no macOS) e mostra, nesta ordem, o
  título, o resultado da ação anterior, quando houver, e o menu numerado (Verificar uma senha, Ver
  exemplos comentados e Sair).

### RF-02 — Validar a escolha do menu

- **Given** o menu está na tela
  **When** o usuário digita um número de 1 a 3
  **Then** o programa segue para a opção correspondente.
- **Given** o menu está na tela
  **When** o usuário digita outra coisa (nada, `0`, `9` ou `abc`)
  **Then** o menu volta com uma mensagem de opção inválida, sem stack trace.

### RF-03 — Ler a senha sem mostrá-la

- **Given** o usuário escolheu Verificar uma senha
  **When** o programa pede a senha
  **Then** a leitura é feita com o `getpass`, e o pedido avisa que o que for digitado não aparece
  na tela.
- **Given** o programa pediu a senha
  **When** o usuário aperta Enter sem digitar nada
  **Then** o menu volta com uma mensagem de que nenhuma senha foi digitada, sem nota.
- **Given** a senha foi digitada com espaços no começo ou no fim
  **When** ela é verificada
  **Then** os espaços contam como parte da senha.

### RF-04 — Classificar os caracteres

- **Given** uma senha digitada
  **When** os caracteres são classificados
  **Then** cada um entra em um de quatro tipos: minúsculas (`islower`), maiúsculas (`isupper`),
  números (`isdigit`) e símbolos (todo o resto, inclusive o espaço), e uma letra acentuada conta
  como minúscula ou maiúscula.
- **Given** os tipos presentes na senha
  **When** o tamanho do alfabeto é calculado
  **Then** ele é a soma do tamanho de cada tipo presente, com os tamanhos do módulo `string` usados
  no `gerador_de_senhas`: 26 minúsculas, 26 maiúsculas, 10 números e 32 símbolos.

### RF-05 — Descontar repetições e sequências

- **Given** a senha tem 3 ou mais caracteres iguais seguidos (`aaa`, `111`)
  **When** a entropia é estimada
  **Then** o trecho repetido conta como um caractere só.
- **Given** a senha tem 3 ou mais caracteres seguidos em sequência, para a frente ou para trás, no
  alfabeto (`abc`, `cba`), nos números (`123`, `987`) ou numa fileira do teclado (`qwe`, `asd`,
  `zxc`)
  **When** a entropia é estimada
  **Then** o trecho em sequência conta como um caractere só, sem diferença entre maiúsculas e
  minúsculas (`ABC` e `Abc` também são sequências).
- **Given** a senha tem 2 caracteres iguais ou em sequência (`aa`, `ab`)
  **When** a entropia é estimada
  **Then** nada é descontado.

### RF-06 — Comparar com a lista de senhas comuns

- **Given** a senha digitada, sem diferença entre maiúsculas e minúsculas, é igual a uma das
  senhas da lista
  **When** a nota é calculada
  **Then** a nota é 0, qualquer que seja a entropia, e o resultado diz que a senha está entre as
  mais usadas.
- **Given** a senha só contém uma senha da lista como parte dela (`flamengo2026x`)
  **When** a nota é calculada
  **Then** a lista não pesa na nota: a comparação é com a senha inteira.

### RF-07 — Dar a nota pela entropia estimada

- **Given** uma senha fora da lista de senhas comuns
  **When** a nota é calculada
  **Then** ela sai da entropia estimada, o tamanho que conta (RF-05) vezes o log2 do tamanho do
  alfabeto (RF-04): 0, muito fraca, abaixo de 28 bits; 1, fraca, de 28 a menos de 36; 2,
  razoável, de 36 a menos de 60; 3, boa, de 60 a menos de 80; e 4, forte, de 80 bits em diante.
- **Given** uma senha com menos de 8 caracteres
  **When** a nota é calculada
  **Then** ela fica em no máximo 1, qualquer que seja a entropia.

### RF-08 — Mostrar o resultado da verificação

- **Given** uma senha foi verificada
  **When** o resultado é mostrado
  **Then** ele traz, sem mostrar a senha nem nenhum trecho dela: a nota com o nome (`3 de 4,
  boa`); o tamanho e quantos caracteres contaram na entropia; a entropia estimada com a conta,
  arredondada para uma casa decimal, com vírgula (`10 × log2(62) ≈ 59,5 bits`); os tipos de
  caractere presentes e ausentes; e se a senha tem repetição, tem sequência e está na lista de
  senhas comuns.

### RF-09 — Sugerir o que melhorar

- **Given** a senha está na lista de senhas comuns
  **When** as sugestões são mostradas
  **Then** a única sugestão é trocar de senha, porque ela é das primeiras que alguém testa.
- **Given** a senha tem repetição ou sequência
  **When** as sugestões são mostradas
  **Then** uma sugestão diz para tirar a repetição ou a sequência, que quase não acrescentam força.
- **Given** a nota é menor que 4 e a senha não está na lista
  **When** as sugestões são mostradas
  **Then** uma sugestão diz quantos caracteres a mais, dos tipos que a senha já tem, levam a
  entropia a 80 bits, e lembra que uma frase-senha de palavras sorteadas é longa e fácil de
  decorar.
- **Given** a nota é 4, sem repetição nem sequência
  **When** o resultado é mostrado
  **Then** ele diz que não há nada a melhorar nas regras do programa.

### RF-10 — Mostrar exemplos comentados

- **Given** o usuário escolheu Ver exemplos comentados
  **When** a opção é processada
  **Then** o resultado mostra uma lista fixa de senhas de exemplo, à vista, cada uma com a nota e
  uma linha explicando o que pesou, cobrindo as notas de 0 a 4, com pelo menos uma senha da lista
  de senhas comuns, uma com sequência e uma com os quatro tipos de caractere que não chega à nota
  4.
- **Given** os exemplos estão na tela
  **When** o usuário os lê
  **Then** uma linha explica que a nota é uma estimativa por regras e que uma palavra conhecida
  com um número e um símbolo no fim continua fácil de adivinhar, mesmo com os quatro tipos.

### RF-11 — Sair pelo menu

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

Nenhuma entrada do teclado (no menu ou na senha, de qualquer tamanho e com qualquer caractere)
lança exceção não tratada: o programa sempre mostra o resultado ou explica o erro e volta ao menu.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o programa está esperando uma entrada do teclado, no menu ou na senha
  **When** o usuário aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o programa se despede com uma linha e termina, sem stack trace.

### RNF-05 — Saída não crasha por codificação

A impressão no terminal, inclusive das letras acentuadas, dos símbolos da conta (`×` e `≈`) e dos
emojis das mensagens, não lança `UnicodeEncodeError`, nem quando a saída padrão não está presa a um
console UTF-8 (saída redirecionada para arquivo, pipe ou executor de CI).

### RNF-06 — Testável sem teclado real

A leitura do menu e a leitura da senha entram nas funções do programa por parâmetro, para a suíte
de testes ser determinística: o teste escolhe as entradas, sem `monkeypatch` em `input` ou
`getpass`. O programa, fora dos testes, lê a senha sempre com o `getpass`. As funções que
classificam os caracteres, descontam repetições e sequências, comparam com a lista, calculam a
entropia e dão a nota são puras: recebem os valores e devolvem o resultado, sem ler o teclado nem
imprimir.

### RNF-07 — A senha não sai do computador

O programa não grava arquivo, não usa rede, não recebe nada pela linha de comando, não mostra a
senha digitada nem trecho dela e não a guarda entre uma volta do menu e outra: o único arquivo que
ele lê é a lista de senhas comuns. Os exemplos do projeto (código, testes e README) são senhas
inventadas ou da lista de senhas comuns, nunca uma senha em uso.

### RNF-08 — Lista de senhas comuns conferida e com atribuição

A lista fica num arquivo de texto dentro do projeto, uma senha por linha, com as 150 senhas do
arquivo `Portugese_Pwdb_common-password-list-top-150.txt` do SecLists, sem alteração. A origem
(SecLists e Pwdb-Public), a licença MIT e os avisos de copyright dos dois projetos ficam
registrados no `LICENSE` e no README.

### RNF-09 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o `README.en.md`, com as
mesmas seções e abertos por uma animação de uma sessão no terminal, que fica parada na última tela
para quem pede movimento reduzido, e com o aviso de que a nota é uma estimativa didática, não uma
auditoria; o `CLAUDE.md`, com os comandos e a arquitetura; o `docs/stack.md`, com o mapa da stack;
e o `LICENSE`. O `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md` e o `SECURITY.md` são os da raiz do
repositório, que valem para todos os mini-projetos, e as regras de contribuição próprias deste
projeto ficam na seção de dúvidas e sugestões do README. O portão de qualidade (ruff, black, mypy
strict e pytest) roda no CI, junto da conferência de impessoalidade da raiz, e o Dependabot propõe
as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **Nota de 0 a 4:** é a escala do zxcvbn, o estimador mais usado em páginas de cadastro, e cabe
   numa linha (`3 de 4, boa`). As faixas em bits são deste projeto, escolhidas para conversar com
   o `gerador_de_senhas`: a senha mínima dele (8 caracteres com os quatro tipos, 52,4 bits) é
   razoável, 12 caracteres (78,7 bits) dão boa, e a senha forte padrão (16 caracteres, 104,9 bits)
   dá forte.
2. **A entropia é a mesma fórmula do gerador,** com o tamanho do alfabeto montado pelos tipos
   presentes. Ela supõe que cada caractere foi sorteado, o que uma senha feita à mão não é: por
   isso a conta se chama entropia estimada, e as repetições, as sequências e a lista de senhas
   comuns corrigem os casos mais previsíveis.
3. **Repetição e sequência contam como um caractere só, a partir de 3:** `aaaa` e `abcd` se
   adivinham quase tão rápido quanto um caractere. Com 2, o desconto pegaria pares que aparecem
   por acaso em qualquer senha sorteada.
4. **As fileiras do teclado são as do padrão QWERTY** (`qwertyuiop`, `asdfghjkl` e `zxcvbnm`),
   o mesmo nos teclados ABNT2 e americano para essas letras.
5. **Os tipos saem dos métodos de string, e os tamanhos, do módulo `string`:** `islower`,
   `isupper` e `isdigit` são o que o projeto ensina com `any()`. Contar uma letra acentuada como
   uma letra comum e o espaço como símbolo deixa a estimativa para baixo, nunca para cima.
6. **A lista é comparada com a senha inteira, sem diferença entre maiúsculas e minúsculas:** a
   NIST SP 800-63B (revisão 4) pede a comparação com uma lista de senhas comuns ou vazadas, com a
   senha inteira, não com partes dela. `Brasil` e `BRASIL` estão na lista como duas linhas, e a
   comparação sem diferença de caixa as trata como uma.
7. **A lista é a portuguesa do SecLists:** 150 senhas reais de falantes de português (`123mudar`,
   `flamengo`, `102030`), que nenhuma lista em inglês traz, sob a licença MIT, compatível com a do
   projeto. A lista do NCSC britânico não tem licença declarada. A cópia é sem alteração, como a
   lista de palavras do gerador, para um teste conferir a integridade; ela contém um palavrão, que
   o programa nunca mostra (os exemplos do RF-10 são escolhidos à parte).
8. **Menos de 8 caracteres limita a nota a 1:** 8 é o mínimo do gerador e o mínimo que a NIST
   aceita quando há um segundo fator de autenticação. Sem o limite, 7 caracteres com os quatro
   tipos (45,9 bits) dariam razoável.
9. **Os tipos de caractere não são exigidos, só contados:** a NIST deixou de recomendar regras de
   composição, porque elas levam a senhas previsíveis como `Senha@123`. Cada tipo a mais aumenta o
   alfabeto e, com ele, a entropia, mas a sugestão principal é o tamanho.
10. **O resultado não mostra a senha nem trecho dela:** o `getpass` esconde a senha ao digitar, e
    mostrar a sequência achada (`abc`) devolveria parte dela à tela. O tamanho aparece, porque
    explica a conta.
11. **O resultado aparece acima do menu, depois de limpar a tela,** sem pausa de "aperte Enter",
    como no gerador: a nota fica à vista enquanto o usuário escolhe a próxima opção.
12. **Nenhuma senha entra pela linha de comando:** um argumento fica gravado no histórico do shell.
13. **Os exemplos comentados mostram a senha à vista** porque são inventados ou da lista de senhas
    comuns: é a única tela em que uma senha aparece.

## Testes

### RF-04, RF-07 — Tipos, entropia e nota

`tests/test_main.py` confere a classificação de cada tipo (inclusive letra acentuada e espaço), o
tamanho do alfabeto para cada combinação de tipos, a conta da entropia com a vírgula decimal e as
fronteiras de cada nota (27,9 e 28, 35,9 e 36, 59,9 e 60, 79,9 e 80 bits), além do limite de nota
1 para senhas de 7 caracteres e da senha forte padrão do gerador dando 4.

### RF-05 — Repetições e sequências

A suíte confere o desconto de `aaa`, `1111`, `abc`, `cba`, `123`, `987`, `qwe`, `asd` e `ABC`,
que `aa` e `ab` não são descontados e que a contagem dos caracteres que contam bate com a conta
mostrada.

### RF-06, RNF-08 — Lista de senhas comuns

A suíte confere que uma senha da lista dá nota 0 em maiúsculas e em minúsculas, que uma senha que
só contém uma da lista não é afetada e que o arquivo da lista tem as 150 linhas do original, com o
SHA-256 conferido.

### RF-03, RF-08, RF-09 — Verificação, resultado e sugestões

A suíte confere a senha vazia voltando ao menu, os espaços contando como parte da senha, cada item
do resultado, que nenhum trecho da senha aparece no resultado, cada sugestão no caso que a pede e
a conta de quantos caracteres faltam para a nota 4.

### RF-10 — Exemplos comentados

A suíte confere que os exemplos cobrem as notas de 0 a 4, que cada nota mostrada é a calculada
pelas funções do programa e que a explicação aparece no resultado.

### RF-01, RF-02, RF-11 — Menu

A suíte cobre a escolha válida e as inválidas do menu, a ordem da tela (título, resultado e menu)
e a saída pelo menu. As entradas são simuladas por sequências passadas por parâmetro (RNF-06).

### RNF-04, RNF-05 — Saída do programa

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o
programa sem stack trace, no menu e na leitura da senha. A codificação da saída é conferida
rodando o programa com a saída redirecionada.

### RNF-06, RNF-07 — Leitura e a senha não sai do computador

Um teste lê o `main.py` e confere que ele só importa os módulos previstos no design, nenhum de
rede, que não grava arquivo (o único acesso a arquivo é a leitura da lista de senhas comuns) e que
não lê `sys.argv`. Outro confere que, sem o parâmetro de leitura, a senha é lida com o `getpass`.

### RF-01 — Limpeza de tela

A limpeza em si não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de
terminal, e não devolve nada. Fica coberta pela verificação manual ao rodar o programa e é
substituída nos testes dos outros requisitos.

### RNF-09 — Projeto conferido

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links). A conferência de impessoalidade é a da raiz
(`.github/scripts/conferir_impessoalidade.py`), que o CI roda a cada pull request. A animação é
conferida à mão, antes de cada pull request.
