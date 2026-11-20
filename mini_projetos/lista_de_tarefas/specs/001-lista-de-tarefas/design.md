---
feature: Lista de Tarefas via terminal com arquivo JSON
status: em andamento
date: 2026-11-20
related:
  - 001-lista-de-tarefas/requirements.md
origin: concepção
---

# 001 — Lista de Tarefas — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade, em três grupos: o
arquivo (carregar, validar, guardar a cópia do corrompido e salvar), a tela (formatar a linha da
tarefa, desenhar a lista e o menu) e as ações (adicionar, concluir ou reabrir, editar e remover).
A lista é uma `list` de dicionários, um por tarefa, com o texto, a situação e a data de criação, e
é o "banco de dados" do programa: o JSON é essa mesma lista escrita em texto. `main()` carrega a
lista uma vez, repete o laço do menu e é o único ponto que trata o Ctrl+C.

O arquivo é o centro do projeto. Ao abrir, três caminhos: o arquivo não existe (a lista começa
vazia), existe e é válido (a lista vem dele), ou existe e está corrompido (vira uma cópia com data
e hora no nome, e a lista começa vazia). Cada ação que altera a lista a grava logo em seguida, e a
gravação é atômica: o texto vai para `tarefas.json.tmp`, que substitui o `tarefas.json` de uma vez
com `Path.replace`. Uma queda no meio deixa o arquivo anterior inteiro.

As funções que leem o teclado recebem a leitura por parâmetro (`ler`, que vale `input` por
padrão), e o relógio e o caminho do arquivo entram da mesma forma (`agora`, que vale
`datetime.now`, e `arquivo`, que vale o `tarefas.json` ao lado do `main.py`). O programa roda igual
para quem só executa `main.py`, e os testes passam leitores e relógios falsos e uma pasta
temporária, sem `monkeypatch`.

## Layout de módulos

```text
main.py            # constantes, funções do arquivo, da tela e das ações, e main()
tests/test_main.py # suíte pytest
tarefas.json       # criado na primeira alteração; fora do Git (.gitignore)
```

## Modelo de dados

Uma tarefa é um `TypedDict` (ADR-2), o dicionário com as chaves e os tipos declarados para o
mypy:

```python
class Tarefa(TypedDict):
    texto: str        # de 1 a 80 caracteres, sem os espaços das pontas
    concluida: bool   # False = pendente, True = concluída
    criada_em: str    # data em ISO 8601, "AAAA-MM-DD"
```

A lista do programa é `list[Tarefa]`, na ordem de criação; o número que a tela mostra é a posição
mais 1 (decisão 5 do `requirements.md`).

Constantes de módulo:

- `ARQUIVO_PADRAO = Path(__file__).parent / "tarefas.json"`: o arquivo ao lado do `main.py`
  (ADR-4).
- `TAMANHO_MAXIMO = 80`: o limite do texto (decisão 8).
- `CAMPOS = {"texto", "concluida", "criada_em"}`: as chaves que toda tarefa do arquivo tem que ter,
  nem mais nem menos.
- `OPCOES = ["Adicionar", "Concluir", "Editar", "Remover", "Sair"]`: o menu, numerado a partir
  de 1 na exibição.

Apelidos de tipo para os parâmetros injetáveis, com a instrução `type` (Python 3.12) e `Callable`
de `collections.abc`:

- `type Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado,
  como o `input`.
- `type Relogio = Callable[[], datetime]`: devolve a data e a hora do momento, como o
  `datetime.now`.

O resultado de uma validação é uma `NamedTuple` `Conferencia(valor, recusa)`, como no
`jogo_da_forca`: só um dos dois campos vem preenchido, e o outro é `""`.

## Componentes

### `validar_tarefas(dados)`

Recebe o que o `json.loads` devolveu (`object`) e confere a forma: é uma `list`, e cada item é um
`dict` com exatamente as chaves de `CAMPOS`, `texto` é `str` não vazio depois do `strip()`,
`concluida` é `bool` e `criada_em` é uma `str` que `date.fromisoformat` aceita. Devolve a lista
tipada como `list[Tarefa]`, ou lança `ValueError` com o motivo (RF-02, ADR-6). O tamanho do texto
não é conferido aqui: um texto longo editado à mão no arquivo não justifica tratar a lista inteira
como corrompida.

### `guardar_corrompido(arquivo, agora)`

Monta o nome da cópia, `tarefas.corrompido-AAAAMMDD-HHMMSS.json`, com a data e a hora de `agora`,
na mesma pasta. Se esse nome já existir (dois arquivos corrompidos no mesmo segundo), acrescenta
`-2`, `-3`, até achar um livre. Renomeia o arquivo com `Path.rename` e devolve o caminho da cópia
(RF-02, ADR-6).

### `carregar_tarefas(arquivo, agora)`

Se o arquivo não existe, devolve a lista vazia e nenhum aviso (RF-01). Se existe, lê com
`read_text(encoding="utf-8")`, passa pelo `json.loads` e pelo `validar_tarefas`. Um único
`except ValueError` pega os três problemas possíveis: o JSON inválido (`json.JSONDecodeError`), o
arquivo que não é UTF-8 (`UnicodeDecodeError`) e a forma errada (o `ValueError` do
`validar_tarefas`), porque os dois primeiros são subclasses de `ValueError`. Nesse caso, chama
`guardar_corrompido` e devolve a lista vazia e o aviso com o nome da cópia (RF-02). O retorno é
`tuple[list[Tarefa], str]`.

### `salvar_tarefas(tarefas, arquivo)`

Gera o texto com `json.dumps(tarefas, ensure_ascii=False, indent=2)` e uma quebra de linha no fim,
grava em `tarefas.json.tmp` (na mesma pasta) com `write_text(..., encoding="utf-8")` e troca o
temporário pelo arquivo com `Path.replace` (RF-03, ADR-3, ADR-5).

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama a cada volta do menu (RF-04).

### `formatar_data(criada_em)`

Função pura: converte `"2026-11-20"` em `"20/11/2026"` com `date.fromisoformat(...).strftime(...)`
(RF-04, decisão 10).

### `formatar_tarefa(numero, tarefa)`

Função pura: devolve a linha da tarefa, com o número alinhado à direita em 2 posições, a marca
(`[ ]` ou `[x]`), a data e o texto, nesta ordem: `1. [ ] 20/11/2026  Estudar pathlib`, com um
espaço antes do `1`. A data vem antes do texto porque tem tamanho fixo, e assim as colunas ficam
alinhadas sem completar o texto com espaços (RF-04).

### `exibir_tela(tarefas, mensagem)`

Imprime, nesta ordem: o título, a linha de cada tarefa (ou a linha da lista vazia), a contagem
"Pendentes: N | Concluídas: N", o menu numerado de `OPCOES` e, por último, a mensagem da ação
anterior, se houver (RF-04).

### `conferir_opcao(entrada)`

Função pura: tira os espaços e devolve o número da opção (de 1 a `len(OPCOES)`) ou `None` para
qualquer outra coisa. Confere `isdecimal()` antes do `int()`, para não precisar de `try`; o
`isdigit()` não serve, porque aceita caracteres como `"²"`, que o `int()` recusa com `ValueError`
(RF-05). `conferir_numero` usa a mesma conferência.

### `conferir_texto(entrada)`

Função pura: tira os espaços das pontas e devolve `Conferencia(texto, "")`, ou
`Conferencia("", recusa)` quando o texto fica vazio ou passa de `TAMANHO_MAXIMO` (RF-06, RF-09).

### `conferir_numero(entrada, total)`

Função pura: devolve `Conferencia(entrada_limpa, "")` quando a entrada é um número de 1 a
`total`, ou a recusa "digite um número de 1 a N" (RF-07). O chamador converte o valor para `int`.

### `ler_texto(ler, pedido)`, `ler_numero(ler, total)` e `confirmar(ler, pergunta)`

Laços `while True` que leem, conferem e, na recusa, imprimem a mensagem e pedem de novo, sem limpar
a tela, para a lista continuar à vista. `ler_numero` devolve o índice na lista (o número menos 1).
`confirmar` aceita `s`/`n` em maiúscula e minúscula e devolve `bool` (RF-06, RF-07, RF-09, RF-10,
RNF-03).

### O que as quatro ações têm em comum

Cada ação recebe a lista, o arquivo e o leitor, altera a lista no lugar, chama `salvar_tarefas`
logo em seguida e devolve a mensagem que a próxima tela mostra (ADR-7). Concluir, editar e remover
começam conferindo se a lista está vazia: se estiver, devolvem a mensagem "não há tarefas" sem
pedir número e sem gravar (RF-07).

### `adicionar(tarefas, arquivo, ler, hoje)`

Lê o texto com `ler_texto`, acrescenta a tarefa pendente com `hoje.isoformat()` em `criada_em` e
grava (RF-06).

### `alternar_conclusao(tarefas, arquivo, ler)`

Lê o número, inverte `concluida` com `not` e grava. A mensagem diz se a tarefa foi concluída ou
reaberta (RF-08, decisão 6).

### `editar(tarefas, arquivo, ler)`

Lê o número e o texto novo e troca só o `texto` (RF-09).

### `remover(tarefas, arquivo, ler)`

Lê o número e pergunta, com `confirmar` e o texto da tarefa, `Remover "Gravar o vídeo"? (s/n)`.
No `s`, tira a tarefa com `pop(indice)` e grava. No `n`, não grava, e a mensagem diz que nada
foi removido (RF-10).

### `main(ler, agora, arquivo)`

Carrega a lista com `carregar_tarefas`, e o aviso de arquivo corrompido, se houver, vira a
primeira mensagem. Repete: limpa a tela, exibe a lista, o menu e a mensagem, lê a opção e chama a
ação correspondente num `if`/`elif`, guardando a mensagem que ela devolve. A opção inválida vira a
mensagem de opção inválida (RF-05), e Sair encerra o laço com a despedida (RF-11). O laço inteiro
fica dentro de um `try` que captura `KeyboardInterrupt` e `EOFError` (RNF-04, ADR-12). A data de
hoje passada a `adicionar` sai de `agora().date()`.

## Interfaces

### O arquivo `tarefas.json`

Uma lista JSON no topo, um objeto por tarefa, com as três chaves do `Tarefa`, em UTF-8, com os
acentos escritos como letras (não como `ã`) e indentação de 2 espaços, para o arquivo se ler
num editor (ADR-3):

```json
[
  {
    "texto": "Estudar pathlib",
    "concluida": false,
    "criada_em": "2026-11-20"
  },
  {
    "texto": "Comprar pão",
    "concluida": true,
    "criada_em": "2026-11-19"
  }
]
```

### O terminal

Como a tela é limpa a cada volta do menu, o terminal mostra sempre um quadro só. O quadro
ilustrativo abaixo é o de uma lista com três tarefas, logo depois de concluir a segunda (o texto
exato de cada mensagem fica no `main.py`):

```text
======== LISTA DE TAREFAS ========

 1. [ ] 20/11/2026  Estudar pathlib
 2. [x] 19/11/2026  Comprar pão
 3. [ ] 20/11/2026  Gravar o vídeo

Pendentes: 2 | Concluídas: 1

1 : Adicionar
2 : Concluir
3 : Editar
4 : Remover
5 : Sair

✅ Tarefa concluída: Comprar pão
Escolha uma opção: 4
Número da tarefa (1 a 3): 3
Remover "Gravar o vídeo"? (s/n):
```

O menu segue o formato do `calculadora_simples` (`1 : Adicionar`). As mensagens evitam concordar
com o número ("Pendentes: 2"), para nenhuma frase precisar de plural. Com a lista vazia, a lista
dá lugar a "Nenhuma tarefa por aqui. Escolha 1 para adicionar a primeira.". Na primeira tela depois
de um arquivo corrompido, a mensagem é "⚠️ O arquivo tarefas.json estava corrompido. A cópia ficou
em tarefas.corrompido-20261120-153000.json, e a lista começou vazia.".

## ADRs

### ADR-1 — Funções soltas em vez de uma classe

**Decisão.** O programa é um conjunto de funções no nível do módulo, e a lista de tarefas é
passada por parâmetro.

**Alternativas.** (a) uma classe `ListaDeTarefas` com a lista e o caminho do arquivo em `self`,
como o `pedra_papel_tesoura` e o `jogo_da_velha`.

**Porquê.** O centro deste projeto é o arquivo (`json`, `pathlib` e a gravação atômica), e não a
Orientação a Objetos. Funções com entrada e saída explícitas se leem de cima para baixo e se
testam sem montar um objeto. Segue os dois projetos anteriores da série, o `adivinhe_o_numero` e o
`jogo_da_forca`.

**Trade-off.** A lista e o arquivo passam de função em função. São dois parâmetros, então o custo
é pequeno.

### ADR-2 — A tarefa é um dicionário tipado com `TypedDict`

**Decisão.** Cada tarefa é um `dict` com as chaves `texto`, `concluida` e `criada_em`, declarado
como `class Tarefa(TypedDict)`.

**Alternativas.** (a) `dict[str, str | bool]`, sem declarar as chaves. (b) uma `@dataclass
Tarefa`, convertida com `asdict` ao gravar e montada de volta ao carregar.

**Porquê.** A lista de dicionários é o conceito do projeto, e o JSON é essa mesma lista escrita em
texto: `json.dumps` grava a lista como está, e `json.loads` a devolve igual. O `TypedDict`
continua sendo um `dict` comum na execução, mas diz ao mypy quais chaves existem e o tipo de cada
uma. Descartar (a): o mypy strict não sabe que `tarefa["concluida"]` é `bool`, e cada uso pediria
uma conversão. Descartar (b): a conversão nos dois sentidos é um passo a mais entre a lista e o
arquivo, justamente o que o projeto quer mostrar como direto.

**Trade-off.** O `TypedDict` não confere nada na execução: um arquivo editado à mão pode trazer
qualquer coisa, e é por isso que o `validar_tarefas` existe.

### ADR-3 — JSON com a lista no topo, acentos legíveis e indentação

**Decisão.** O arquivo é a lista de tarefas, sem objeto em volta, gravado com
`ensure_ascii=False` e `indent=2`.

**Alternativas.** (a) um objeto `{"versao": 1, "tarefas": [...]}`, para uma mudança futura do
formato saber de qual versão o arquivo veio. (b) o padrão do `json.dumps`, numa linha só e com os
acentos escapados (`"pão"`). (c) CSV ou `pickle`.

**Porquê.** O arquivo igual à lista do programa se explica em uma frase, e com
acentos e quebras de linha ele se lê e se confere num editor qualquer. Descartar (a): o projeto
tem um formato só, e a versão seria um campo sem uso. Descartar (c): o CSV não guarda o `bool`
como `bool`, e o `pickle` não se lê num editor e executa código ao carregar um arquivo adulterado.

**Trade-off.** Sem campo de versão, uma spec futura que mude os campos precisa reconhecer o
formato antigo pela forma (a armadilha registrada no `specs/README.md`).

### ADR-4 — O arquivo fica ao lado do `main.py`, pelo `Path(__file__)`

**Decisão.** `ARQUIVO_PADRAO = Path(__file__).parent / "tarefas.json"`.

**Alternativas.** (a) `Path("tarefas.json")`, relativo à pasta de onde o programa foi chamado.
(b) `Path.home() / ".lista_de_tarefas.json"`, na pasta do usuário.

**Porquê.** O caminho relativo (a) depende da pasta atual do terminal: rodar `python
mini_projetos/lista_de_tarefas/main.py` a partir de outra pasta criaria uma segunda lista, vazia,
em outro lugar. O `Path(__file__)` aponta sempre para a pasta do programa, de onde quer que ele
seja chamado, e o operador `/` do `pathlib` monta o caminho com o separador de cada sistema
(RNF-02). Descartar (b): decisão 1 do `requirements.md`.

**Trade-off.** Num programa instalado, a pasta do programa pode não aceitar escrita; para um
mini-projeto clonado, ela sempre aceita. Um comentário ao lado da constante cita a pasta do
usuário como o lugar certo para um programa instalado.

### ADR-5 — Gravação atômica com arquivo temporário e `Path.replace`, sem `fsync`

**Decisão.** `salvar_tarefas` grava em `tarefas.json.tmp`, na mesma pasta, e troca o temporário
pelo arquivo com `Path.replace`.

**Alternativas.** (a) `arquivo.write_text(...)` direto. (b) o `tempfile.NamedTemporaryFile`.
(c) chamar `os.fsync` antes da troca.

**Porquê.** O `write_text` direto (a) primeiro esvazia o arquivo e depois escreve: uma queda nesse
meio deixa um arquivo pela metade, que a próxima abertura trata como corrompido. O `Path.replace`
(o `os.replace` por baixo) troca um arquivo pelo outro numa operação só, no Windows, no Linux e no
macOS, desde que os dois estejam no mesmo disco, e por isso o temporário fica na mesma pasta.
Descartar (b): o nome sorteado e o `delete=False` somam explicação sem mudar o princípio.
Descartar (c): o `fsync` protege contra a queda de energia logo depois da gravação, um caso que
pede explicar o cache do sistema operacional, além do que um mini-projeto precisa.

**Trade-off.** Sem `fsync`, uma queda de energia no instante seguinte à gravação ainda pode perder
a última alteração em alguns sistemas de arquivos. Se a gravação falhar no meio, sobra um
`tarefas.json.tmp`, que a próxima gravação sobrescreve e que o `.gitignore` deixa fora do Git.

### ADR-6 — Validar a forma ao carregar e guardar o corrompido com `rename`

**Decisão.** Depois do `json.loads`, `validar_tarefas` confere a lista e cada tarefa, e um único
`except ValueError` trata o JSON inválido, o arquivo que não é UTF-8 e a forma errada.
`guardar_corrompido` renomeia o arquivo com `Path.rename`, nunca com `Path.replace`.

**Alternativas.** (a) confiar no `json.loads` e deixar o erro aparecer só quando o programa usar
uma chave que falta. (b) três `except` separados, um por exceção. (c) apagar o arquivo corrompido.

**Porquê.** Um JSON válido pode não ser uma lista de tarefas (`{}`, `[1, 2]`, uma tarefa sem
`texto`); sem a validação (a), o programa quebraria mais tarde, longe da causa. O `except
ValueError` único funciona porque `json.JSONDecodeError` e `UnicodeDecodeError` são subclasses de
`ValueError`, um bom exemplo de hierarquia de exceções; um comentário mostra isso. O `rename`, e
não o `replace`, porque o `replace` sobrescreveria em silêncio uma cópia com o mesmo nome, e a
data e a hora no nome mais o contador garantem que o nome está livre. Descartar (c): decisão 2 do
`requirements.md`.

**Trade-off.** Uma chave a mais escrita à mão no arquivo (por exemplo, `"prazo"`) também conta
como forma errada, e a lista vai para a cópia. É o preço de nunca perder um campo em silêncio ao
gravar de novo.

### ADR-7 — Cada ação grava logo depois de alterar

**Decisão.** `adicionar`, `alternar_conclusao`, `editar` e `remover` chamam `salvar_tarefas`
dentro da própria função, logo depois de alterar a lista.

**Alternativas.** (a) gravar só ao escolher Sair. (b) as ações devolverem se alteraram a lista, e
`main()` gravar.

**Porquê.** Atende a decisão 9 do `requirements.md` e o RNF-04: um Ctrl+C ou o terminal fechado
não perdem nada, porque nada fica só na memória. Gravar dentro da ação deixa "altera e grava" lado
a lado, na ordem em que se lê. Descartar (b): o retorno duplo (mensagem e "alterou?") é um conceito
a mais para o mesmo efeito.

**Trade-off.** A lista inteira é regravada a cada alteração. Para uma lista pessoal, de dezenas de
tarefas, o custo não aparece.

### ADR-8 — Teclado, relógio e caminho do arquivo por parâmetro, com padrões reais

**Decisão.** As funções que leem o teclado recebem `ler: Leitor = input`; `main()` recebe também
`agora: Relogio = datetime.now` e `arquivo: Path = ARQUIVO_PADRAO`, e repassa os três.

**Alternativas.** (a) chamar `input` e `datetime.now` direto e substituí-los nos testes com
`monkeypatch`, como fazem os mini-projetos mais antigos.

**Porquê.** Atende o RNF-06: o teste diz qual é a sequência de entradas, a data e a pasta na
própria chamada, e nunca toca no `tarefas.json` de quem usa o programa. Quem só roda o programa não
percebe diferença, porque os padrões são as funções reais. É o mesmo desenho do
`adivinhe_o_numero` e do `jogo_da_forca`.

**Trade-off.** As assinaturas ganham parâmetros e os apelidos `Leitor` e `Relogio`. Um comentário
no topo do arquivo explica o motivo.

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
chamam `main()` com um leitor, um relógio e um arquivo falsos.

**Trade-off.** Nenhum relevante.

### ADR-11 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos, e os acentos do texto das tarefas não teriam como sair.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8. A configuração vale só para a tela; o arquivo
tem o `encoding="utf-8"` próprio em cada leitura e gravação.

### ADR-12 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada função que lê o teclado. (b) não tratar,
como os mini-projetos mais antigos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do programa" em qualquer ponto, então um
lugar só basta, e as funções de leitura ficam focadas em validar (RNF-04). Como cada alteração já
foi gravada (ADR-7), sair no meio de uma ação não perde nada: a ação interrompida simplesmente não
acontece. Descartar (b): o stack trace assusta o iniciante e parece erro do programa.

**Trade-off.** Nenhum relevante: diferente do placar dos jogos, não há nada da sessão para mostrar
na saída.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/lista_de_tarefas/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`). O `.gitignore` do projeto ganha, além das linhas de sempre,
`tarefas.json`, `tarefas.corrompido-*.json` e `tarefas.json.tmp` (RNF-07). Fora da pasta, ganha
uma entrada na matriz `projeto` do workflow de CI (`ci.yml`) e do `pip-audit.yml` da raiz, e uma
linha na tabela do `mini_projetos/README.md` e do `README.en.md`. Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, com o disco de verdade numa pasta temporária: a fixture `tmp_path` do pytest dá a cada
teste uma pasta vazia, e o teste passa `tmp_path / "tarefas.json"` como `arquivo`. O leitor falso
(`LeitorFalso`, uma pequena classe com `__call__`, como no `jogo_da_forca`) devolve as respostas de
uma lista e guarda os pedidos recebidos; o relógio falso é uma função que devolve sempre o mesmo
`datetime`, o que fixa a data de criação e o nome da cópia do corrompido. As funções puras
(`validar_tarefas`, `formatar_data`, `formatar_tarefa`, `conferir_opcao`, `conferir_texto`,
`conferir_numero`) são testadas direto, com casos parametrizados; os arquivos inválidos do RF-02
são escritos pelo próprio teste com `write_text` ou `write_bytes` (o que não é UTF-8). A falha no
meio da gravação (RF-03) é simulada sem `monkeypatch`: o teste cria uma pasta chamada
`tarefas.json.tmp`, a gravação do temporário falha, e o teste confere que o `tarefas.json`
anterior continua igual. A saída se confere com o `capsys`. `limpar_tela` é substituída por uma
fixture `autouse` com `monkeypatch`, para os testes não chamarem `os.system`: é o único
`monkeypatch` da suíte (RF-04). Os testes de `main()` também cobrem o Ctrl+C e o fim da entrada,
com um leitor que lança `KeyboardInterrupt` ou `EOFError`, e conferem que o arquivo não mudou
(RNF-04). Ver `tests/test_main.py` e a seção "Testes" do `requirements.md`.

## Desvios

1. **ADR-8:** só `main()` tem os padrões reais (`ler = input`, `agora = datetime.now`,
   `arquivo = ARQUIVO_PADRAO`), e também `carregar_tarefas` e `guardar_corrompido`
   (`agora = datetime.now`). Nas outras funções que leem o teclado, o `ler` vem antes de um
   parâmetro obrigatório (`ler_texto(ler, pedido)`, `adicionar(tarefas, arquivo, ler, hoje)`), na
   ordem das assinaturas deste design, e por isso não tem padrão: `main()` repassa o leitor
   recebido. Quem usa o programa não percebe diferença.
2. **Ações:** a mensagem da lista vazia, que concluir, editar e remover devolvem (RF-07), é a
   constante `SEM_TAREFAS`, para o texto ser um só nas três ações e nos testes.

## Notas de implementação

- **Testes:** 89 casos em `tests/test_main.py` (59 na etapa 1, 30 na etapa 2). Ruff, black e
  mypy strict verdes.
- **Conferido à mão:** uma sessão com a entrada roteirizada por stdin e a saída redirecionada
  para arquivo, não num terminal interativo, adicionando três tarefas, concluindo duas,
  reabrindo uma, editando uma e removendo uma depois de um `n`. O `tarefas.json` ficou com as
  duas tarefas esperadas e os acentos legíveis, e a saída não teve `UnicodeEncodeError`. A
  limpeza de tela aparece no arquivo como o caractere que o `cls` emite (`^L`), uma vez por
  volta do menu. Chamado da raiz do repositório
  (`python mini_projetos/lista_de_tarefas/main.py`), o programa abriu a mesma lista, sem criar
  um `tarefas.json` na raiz. Um `tarefas.json` estragado à mão virou
  `tarefas.corrompido-AAAAMMDD-HHMMSS.json`, com o aviso na primeira tela e a lista vazia; o
  `git check-ignore` confirma que o arquivo, a cópia e o `tarefas.json.tmp` ficam fora do Git.
  Os dois atalhos abrem o programa pelo `uv`.
