---
feature: Lista de Tarefas via terminal com arquivo JSON
status: concluído
date: 2026-11-20
related: []
origin: concepção
---

# 001 — Lista de Tarefas

## Contexto e problema

Este mini-projeto é material de estudo para quem está começando em Python. É uma lista de tarefas
no terminal: o usuário adiciona, conclui, edita e remove tarefas, e tudo fica guardado num arquivo
JSON, para a lista continuar de onde parou na próxima vez que o programa abrir. É o primeiro
mini-projeto da série que guarda dado entre execuções, e exercita três conceitos: ler e gravar
arquivo com `json` e `pathlib` (sempre em UTF-8), a lista de dicionários como um "banco de dados"
simples, e o tratamento do que pode dar errado com um arquivo: ele ainda não existir, estar
corrompido ou o programa cair no meio da gravação. O resto (funções, menu em laço, validação da
entrada) fica no nível dos outros mini-projetos, para o código se ler de cima para baixo.

## Objetivos

- Adicionar, concluir, editar e remover tarefas num menu no terminal, com a lista sempre à vista.
- Guardar cada tarefa com o texto, a situação (pendente ou concluída) e a data de criação.
- Gravar a lista num arquivo JSON a cada alteração e recarregá-la ao abrir o programa.
- Tratar a primeira execução (arquivo ausente) e o arquivo corrompido sem perder dado e sem
  travar o usuário.
- Gravar de forma atômica, para uma queda no meio da gravação não corromper a lista.
- Validar toda entrada do teclado sem que o programa quebre.
- Funcionar em Windows, Linux e macOS sem alteração de código.

## Não objetivos

- Prioridade, prazo, lembrete e categoria.
- Sincronização entre computadores ou com serviço externo.
- Mais de uma lista, ou escolher o arquivo pela linha de comando.
- Banco de dados (SQLite ou outro) no lugar do arquivo JSON.
- Reordenar as tarefas, buscar ou filtrar.
- Interface gráfica ou web.

## Personas

- **Aprendiz de Python:** acabou de ver o vídeo e quer ler o código para entender como `json`,
  `pathlib` e a gravação atômica se encaixam num programa de verdade.
- **Usuário casual:** quer abrir o programa (com duplo clique ou um comando), anotar o que tem
  para fazer e encontrar a lista no mesmo lugar no dia seguinte.

## Requisitos funcionais

### RF-01 — Carregar a lista ao abrir

- **Given** o arquivo `tarefas.json` não existe na pasta do projeto (primeira execução)
  **When** o programa abre
  **Then** a lista começa vazia, sem mensagem de erro, e o arquivo só é criado na primeira
  alteração.
- **Given** o arquivo `tarefas.json` existe e é válido
  **When** o programa abre
  **Then** as tarefas aparecem na tela, na mesma ordem e com a mesma situação e data de criação
  com que foram gravadas.

### RF-02 — Guardar o arquivo corrompido e começar vazio

- **Given** o arquivo `tarefas.json` existe, mas não é JSON válido ou não tem a forma de uma lista
  de tarefas (cada uma com texto, situação e data de criação válidos)
  **When** o programa abre
  **Then** o arquivo é renomeado para `tarefas.corrompido-AAAAMMDD-HHMMSS.json`, na mesma pasta e
  com a data e a hora do momento, a lista começa vazia e a tela avisa que o arquivo estava
  corrompido e onde está a cópia.
- **Given** uma cópia de arquivo corrompido já existe na pasta
  **When** outro arquivo corrompido é guardado
  **Then** a cópia anterior continua intacta.

### RF-03 — Gravar a cada alteração, de forma atômica

- **Given** o usuário adicionou, concluiu, reabriu, editou ou removeu uma tarefa
  **When** a alteração é feita
  **Then** a lista inteira é gravada em `tarefas.json`, em UTF-8 e com os acentos legíveis no
  arquivo, antes de o menu voltar.
- **Given** a lista vai ser gravada
  **When** a gravação acontece
  **Then** o conteúdo vai primeiro para um arquivo temporário na mesma pasta, que depois substitui
  `tarefas.json` de uma vez, e uma interrupção no meio deixa a versão anterior inteira.

### RF-04 — Mostrar a lista e o menu a cada volta

- **Given** o programa está aberto
  **When** o menu vai ser mostrado
  **Then** a tela é limpa (`cls` no Windows, `clear` no Linux e no macOS) e mostra, nesta ordem, a
  lista de tarefas, o menu numerado (Adicionar, Concluir, Editar, Remover e Sair) e a mensagem da
  ação anterior, quando houver.
- **Given** a lista tem tarefas
  **When** ela é mostrada
  **Then** cada tarefa aparece numa linha com o número (a partir de 1, na ordem de criação), a
  marca `[ ]` para pendente ou `[x]` para concluída, o texto e a data de criação em `DD/MM/AAAA`,
  e abaixo vem a contagem de pendentes e de concluídas.
- **Given** a lista está vazia
  **When** ela é mostrada
  **Then** aparece uma linha dizendo que não há tarefas, no lugar da lista.

### RF-05 — Validar a escolha do menu

- **Given** o menu está na tela
  **When** o usuário digita um número de 1 a 5
  **Then** o programa segue para a opção correspondente.
- **Given** o menu está na tela
  **When** o usuário digita outra coisa (nada, `0`, `9` ou `abc`)
  **Then** o menu volta com uma mensagem de opção inválida, sem stack trace.

### RF-06 — Adicionar tarefa

- **Given** o usuário escolheu Adicionar
  **When** ele digita um texto de 1 a 80 caracteres, depois de tirar os espaços das pontas
  **Then** a tarefa entra no fim da lista como pendente, com a data de hoje como data de criação,
  e a mensagem confirma o texto adicionado.
- **Given** o usuário escolheu Adicionar
  **When** ele digita um texto vazio (ou só espaços) ou com mais de 80 caracteres
  **Then** uma mensagem explica o limite e o texto é pedido de novo.

### RF-07 — Escolher a tarefa pelo número

- **Given** o usuário escolheu Concluir, Editar ou Remover e a lista tem tarefas
  **When** ele digita o número de uma tarefa da lista
  **Then** a ação segue com aquela tarefa.
- **Given** o usuário escolheu Concluir, Editar ou Remover e a lista tem tarefas
  **When** ele digita um número fora da lista ou algo que não é número
  **Then** uma mensagem explica o intervalo válido e o número é pedido de novo.
- **Given** o usuário escolheu Concluir, Editar ou Remover e a lista está vazia
  **When** a opção é processada
  **Then** o menu volta com uma mensagem de que não há tarefas, sem pedir número.

### RF-08 — Concluir ou reabrir a tarefa

- **Given** o usuário escolheu Concluir e uma tarefa pendente
  **When** a ação é feita
  **Then** a tarefa passa a concluída, e a mensagem confirma.
- **Given** o usuário escolheu Concluir e uma tarefa já concluída
  **When** a ação é feita
  **Then** a tarefa volta a pendente, e a mensagem diz que ela foi reaberta.

### RF-09 — Editar o texto da tarefa

- **Given** o usuário escolheu Editar e uma tarefa
  **When** ele digita o texto novo, com a mesma validação do RF-06
  **Then** só o texto muda: a situação e a data de criação continuam as mesmas, e a mensagem
  confirma.

### RF-10 — Remover a tarefa com confirmação

- **Given** o usuário escolheu Remover e uma tarefa
  **When** ele responde `s` (ou `S`) à pergunta que mostra o texto da tarefa
  **Then** a tarefa sai da lista, as seguintes passam a usar o número de baixo, e a mensagem
  confirma.
- **Given** o usuário escolheu Remover e uma tarefa
  **When** ele responde `n` (ou `N`)
  **Then** a lista não muda, e a mensagem diz que nada foi removido.
- **Given** a pergunta de confirmação está na tela
  **When** o usuário responde outra coisa
  **Then** uma mensagem de erro é exibida e a pergunta se repete.

### RF-11 — Sair pelo menu

- **Given** o menu está na tela
  **When** o usuário escolhe Sair
  **Then** o programa se despede com uma linha e termina; não há gravação a fazer, porque cada
  alteração já foi gravada (RF-03).

## Requisitos não funcionais

### RNF-01 — Sem dependências externas

O programa roda com Python puro (só a biblioteca padrão), sem instalar nenhum pacote para usar.
As ferramentas de desenvolvimento (ruff, black, mypy, pytest) ficam no grupo `dev` do
`pyproject.toml`, gerenciado pelo `uv`.

### RNF-02 — Portabilidade

O mesmo `main.py` funciona, sem alteração, nos terminais do Windows, do Linux e do macOS, e o
caminho do arquivo é montado com `pathlib`, nunca com barra escrita à mão. Os atalhos `.bat` e
`.sh` cobrem só a conveniência de abrir o programa.

### RNF-03 — Feedback nunca deixa o usuário travado

Nenhuma entrada do teclado (no menu, no texto, no número da tarefa ou na confirmação) lança
exceção não tratada: o programa sempre explica o erro e pede a entrada de novo.

### RNF-04 — Sair com Ctrl+C sem stack trace

- **Given** o programa está esperando uma entrada do teclado
  **When** o usuário aperta Ctrl+C (ou o terminal fecha a entrada, como no Ctrl+D do Linux)
  **Then** o programa se despede com uma linha e termina, sem stack trace, e a lista fica como
  estava na última alteração gravada.

### RNF-05 — Codificação na tela e no arquivo

A impressão no terminal, inclusive das letras acentuadas e dos emojis das mensagens, não lança
`UnicodeEncodeError`, nem quando a saída padrão não está presa a um console UTF-8 (saída
redirecionada para arquivo, pipe ou executor de CI). O arquivo JSON é lido e gravado sempre com
`encoding="utf-8"`, para a mesma lista abrir igual em qualquer sistema.

### RNF-06 — Testável sem teclado, relógio nem pasta reais

A leitura do teclado, a data e a hora do momento e o caminho do arquivo entram nas funções do
programa por parâmetro, para a suíte de testes ser determinística: o teste escolhe as entradas, a
data e uma pasta temporária, sem `monkeypatch` em `input` ou `datetime` e sem tocar no
`tarefas.json` de quem usa o programa.

### RNF-07 — A lista de quem usa fica fora do Git

O `tarefas.json` e as cópias de arquivo corrompido estão no `.gitignore` do projeto: a lista de
quem clona e usa o programa nunca entra num commit.

### RNF-08 — Projeto pronto para estudo

Quem abre o projeto o encontra documentado e conferido: o `README.md` e o `README.en.md`, com as
mesmas seções e abertos por uma animação de uma sessão no terminal, que fica parada na última tela
para quem pede movimento reduzido; o `CLAUDE.md`, com os comandos e a arquitetura; o
`docs/stack.md`, com o mapa da stack; e o `LICENSE`, o `CONTRIBUTING.md`, o `CODE_OF_CONDUCT.md`
e o `SECURITY.md`. O portão de qualidade (ruff, black, mypy strict e pytest) roda no CI, e o
Dependabot propõe as atualizações das ferramentas de desenvolvimento.

## Perguntas em aberto / decisões resolvidas

Nenhuma pergunta em aberto. Decisões tomadas na revisão dos requisitos:

1. **O arquivo fica na pasta do projeto,** ao lado do `main.py`: quem estuda o código abre o
   arquivo na mesma pasta e vê a lista mudar a cada ação, e o caminho entra por parâmetro
   (RNF-06), então o teste usa uma pasta temporária.
2. **Arquivo corrompido vira cópia com data e hora, e a lista começa vazia:** nada se perde, quem
   não sabe editar JSON não fica sem o programa, e a data e a hora no nome evitam sobrescrever uma
   cópia anterior.
3. **A gravação é atômica desde já** (arquivo temporário e `replace`): é o "porquê" que liga a
   gravação ao arquivo corrompido, e custa poucas linhas.
4. **A lista fica sempre no topo da tela:** como a tela é limpa a cada volta, uma opção "Listar"
   apagaria a listagem logo depois de mostrada. Com a lista à vista, ninguém digita o número de
   uma tarefa sem vê-la.
5. **O número da tarefa é a posição na lista,** a partir de 1: depois de uma remoção, as seguintes
   passam a usar o número de baixo, e a tela mostrada a seguir já traz a numeração nova.
6. **Concluir alterna:** escolher uma tarefa concluída a reabre, para um clique errado ter volta
   sem uma opção a mais no menu.
7. **Remover pede confirmação** (`s`/`n`, sem diferenciar maiúscula e minúscula): é a única ação
   que apaga dado gravado.
8. **Texto de 1 a 80 caracteres,** sem os espaços das pontas: cabe numa linha da tela com o número,
   a marca e a data. Textos repetidos são aceitos.
9. **Grava a cada alteração, não só ao sair:** um Ctrl+C ou o terminal fechado não perde nada.
10. **A data de criação é só o dia,** gravada em ISO 8601 (`AAAA-MM-DD`) no JSON e mostrada como
    `DD/MM/AAAA` na tela.

## Testes

### RF-01, RF-02 — Carregar e tratar o arquivo corrompido

`tests/test_main.py` cobre, numa pasta temporária, o arquivo ausente, o arquivo válido com
acentos, o JSON inválido e o JSON válido com forma errada (não é lista, tarefa sem texto,
situação que não é verdadeiro ou falso, data inválida), conferindo que a cópia ganha o nome com a
data e a hora passadas por parâmetro e que uma cópia anterior não é sobrescrita.

### RF-03, RNF-05 — Gravação

A suíte confere que gravar e carregar de novo devolve a mesma lista, que o arquivo sai em UTF-8 com
os acentos legíveis, que nenhum arquivo temporário sobra depois da gravação e que, se a gravação
falhar no meio, o `tarefas.json` anterior continua inteiro.

### RF-04, RF-05 — Tela e menu

A suíte cobre a linha de cada tarefa (número, marca, texto e data), a contagem de pendentes e
concluídas, a lista vazia, a escolha válida e as inválidas do menu.

### RF-06 a RF-11, RNF-03 — Ações

A suíte cobre o texto válido, vazio, só com espaços e longo demais; o número válido, fora da lista
e não numérico; a ação com a lista vazia; concluir e reabrir; editar sem mudar a situação nem a
data; remover com `s` e com `n`, em maiúscula e minúscula, e a resposta inválida; e sair pelo
menu. As entradas são simuladas por uma sequência passada por parâmetro (RNF-06).

### RNF-04 — Saída do programa

Um teste confere que Ctrl+C (`KeyboardInterrupt`) e o fim da entrada (`EOFError`) encerram o
programa sem stack trace e sem alterar o arquivo gravado. A codificação da saída é conferida
rodando o programa com a saída redirecionada.

### RF-04 — Limpeza de tela

A limpeza em si não tem teste automatizado direto: `limpar_tela()` chama `os.system`, um efeito de
terminal, e não devolve nada. Fica coberta pela verificação manual ao rodar o programa e é
substituída nos testes dos outros requisitos.

### RNF-07, RNF-08 — Projeto conferido

`tests/test_readme_en.py` confere que o `README.en.md` acompanha a estrutura do `README.md`
(títulos, tabelas, blocos de código e links), e `tests/test_impessoalidade.py`, que os arquivos
versionados não citam o mantenedor nem apontam para ferramentas que quem clona não tem. O
`.gitignore`, a animação e os arquivos da comunidade são conferidos à mão, antes de cada pull
request.
