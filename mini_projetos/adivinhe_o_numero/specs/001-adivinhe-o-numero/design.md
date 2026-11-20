---
feature: Jogo Adivinhe o Número via terminal
status: concluído
date: 2026-11-20
related:
  - 001-adivinhe-o-numero/requirements.md
origin: concepção
---

# 001 — Adivinhe o Número — design

## Visão geral da abordagem

Um único módulo (`main.py`) com funções pequenas, uma por responsabilidade: escolher o nível, ler
o palpite, jogar uma partida, atualizar o recorde, perguntar se o jogador quer jogar de novo e
mostrar os recordes. Os três níveis ficam numa constante de módulo (`NIVEIS`), e os recordes da
sessão, num dicionário que a função `main()` cria e passa adiante. `main()` orquestra o laço de
partidas e é o único ponto que trata o Ctrl+C.

As funções que leem o teclado recebem a leitura por parâmetro (`ler`, que vale `input` por
padrão), e a partida recebe o sorteio da mesma forma (`sortear`, que vale `random.randint`). O
jogo roda igual para quem só executa `main.py`, e os testes passam leitores e sorteadores falsos,
sem `monkeypatch`.

Não há camadas (persistência, rede, interface gráfica), e é de propósito: o projeto abre a série
nova de mini-projetos, e o fluxo precisa caber na cabeça numa leitura de cima para baixo.

## Layout de módulos

```
main.py            # constantes, funções do jogo e main() (ponto de entrada)
tests/test_main.py # suíte pytest
```

## Modelo de dados

`Nivel` é uma `NamedTuple` com os dados de um nível:

- `nome: str`: `"fácil"`, `"médio"` ou `"difícil"`.
- `minimo: int` / `maximo: int`: os extremos da faixa, ambos incluídos no sorteio.
- `limite: int`: o número máximo de tentativas da partida.

Constante de módulo `NIVEIS: dict[str, Nivel]`, em que a chave é a tecla do menu:

| Tecla | `nome`    | `minimo` | `maximo` | `limite` |
| ----- | --------- | -------- | -------- | -------- |
| `"1"` | `fácil`   | 1        | 50       | 10       |
| `"2"` | `médio`   | 1        | 100      | 8        |
| `"3"` | `difícil` | 1        | 1000     | 10       |

Recordes da sessão: `dict[str, int]`, do nome do nível para o menor número de tentativas numa
vitória. O nível que ainda não teve vitória não aparece no dicionário.

Apelidos de tipo para os parâmetros injetáveis, com `Callable` de `collections.abc`:

- `Leitor = Callable[[str], str]`: recebe o texto do pedido e devolve o que foi digitado, como o
  `input`.
- `Sorteador = Callable[[int, int], int]`: recebe os extremos e devolve o número sorteado, como o
  `random.randint`.

## Componentes

### `limpar_tela()`

Detecta o sistema pelo `os.name` (`"nt"` é Windows) e roda `cls` ou `clear` com `os.system`. É um
efeito de terminal, sem retorno. `main()` a chama só antes do menu de níveis (RF-08).

### `escolher_nivel(ler)`

Mostra o menu com as três opções de `NIVEIS` (tecla, nome, faixa e limite) e lê a tecla. Repete o
pedido, com uma mensagem de erro, enquanto a resposta não for uma chave de `NIVEIS`. Devolve o
`Nivel` escolhido (RF-01).

### `ler_palpite(nivel, tentativa, ler)`

Pede o palpite com o número da tentativa ("Tentativa 2 de 8"). Converte a entrada com `int()`
dentro de `try`/`except ValueError` e confere a faixa. Texto, decimal, entrada vazia e número fora
da faixa geram uma mensagem e um novo pedido, com o mesmo número de tentativa, porque a entrada
inválida não conta. Devolve o palpite válido (RF-03).

### `jogar_partida(nivel, recorde, sortear, ler)`

Sorteia o número secreto com `sortear(nivel.minimo, nivel.maximo)` e informa a faixa, o limite e
o recorde do nível, se houver (RF-02, RF-06). Laço `while tentativa <= nivel.limite`: lê o
palpite, compara e sai com `return` na vitória; no erro, dá a dica "maior" ou "menor" com as
tentativas restantes (RF-04). Se o laço termina sem acerto, revela o número (RF-05). Devolve o
número de tentativas usadas na vitória, ou `None` na derrota.

### `atualizar_recorde(recordes, nome_nivel, tentativas)`

Função pura: grava `tentativas` em `recordes[nome_nivel]` quando o nível não tem recorde ou quando
`tentativas` é menor que o recorde atual. Devolve `True` se houve recorde novo (RF-06). Empate não
é recorde novo.

### `perguntar_jogar_de_novo(ler)`

Lê a resposta, tira os espaços e converte para minúscula. Devolve `True` para `s` e `False` para
`n`; outra resposta gera uma mensagem de erro e a pergunta se repete (RF-07).

### `exibir_recordes(recordes)`

Imprime uma linha por nível, na ordem de `NIVEIS`, com o recorde ou com um traço quando o nível
não teve vitória (RF-07).

### `main(sortear, ler)`

Cria o dicionário de recordes vazio e repete: limpa a tela, escolhe o nível, joga a partida,
atualiza o recorde (avisando "novo recorde" quando for o caso) e pergunta se o jogador quer jogar
de novo. Na saída, mostra os recordes e se despede. O laço inteiro fica dentro de um `try` que
captura `KeyboardInterrupt` e `EOFError`, e a despedida sai em uma linha, sem stack trace (RNF-04).

## Interfaces

Nenhuma: é um programa de terminal, sem rede, arquivo ou API. A única "interface" é a entrada e a
saída pelo terminal, descrita nos requisitos funcionais. Uma sessão ilustrativa, com a vitória no
nível médio (o texto exato de cada mensagem fica no `main.py`):

```
Escolha o nível:
  1 - Fácil   (1 a 50, 10 tentativas)
  2 - Médio   (1 a 100, 8 tentativas)
  3 - Difícil (1 a 1000, 10 tentativas)
Digite o número do nível: 2

Pensei num número de 1 a 100. Você tem 8 tentativas.

Tentativa 1 de 8. Seu palpite: 50
⬆️  O número é maior que 50. Restam 7 tentativas.
Tentativa 2 de 8. Seu palpite: abc
❌ Digite um número inteiro.
Tentativa 2 de 8. Seu palpite: 75
⬇️  O número é menor que 75. Restam 6 tentativas.
Tentativa 3 de 8. Seu palpite: 63
🎉 Acertou! O número era 63, e você usou 3 tentativas.
🏆 Novo recorde no nível médio!

Jogar de novo? (s/n): n

Recordes da sessão:
  Fácil:   —
  Médio:   3 tentativas
  Difícil: —
Até a próxima! 👋
```

Na derrota, a última linha da partida revela o número: "😢 Suas tentativas acabaram. O número era
63."

## ADRs

### ADR-1 — Funções soltas em vez de uma classe

**Decisão.** O jogo é um conjunto de funções no nível do módulo, e o único estado que atravessa
partidas (os recordes) é um dicionário passado por parâmetro.

**Alternativas.** (a) uma classe `AdivinheONumero` com os recordes em `self`, como o
`pedra_papel_tesoura` e o `jogo_da_velha`.

**Porquê.** O centro deste projeto é o `while`, o `random` e o `try`/`except`, e não a
Orientação a Objetos. Funções com entrada e saída explícitas se leem de cima para baixo e se
testam sem montar um objeto. A série já tem os dois estilos: a calculadora e a cobrinha também são
funções.

**Trade-off.** Os recordes precisam ser passados de função em função, em vez de morar em `self`.
Com um dicionário só, o custo é pequeno.

### ADR-2 — `NIVEIS` como constante de módulo, com `NamedTuple`

**Decisão.** Os três níveis ficam em `NIVEIS: dict[str, Nivel]`, em que `Nivel` é uma
`NamedTuple`, e a chave é a tecla do menu.

**Alternativas.** (a) um dicionário de tuplas simples (`"1": ("fácil", 1, 50, 10)`), desempacotado
a cada uso. (b) um dicionário de dicionários (`"1": {"nome": "fácil", ...}`). (c) `if`/`elif` com
os números escritos dentro de `escolher_nivel`.

**Porquê.** A constante com a tecla como chave segue o padrão do `NIVEIS_DIFICULDADE` da cobrinha:
o menu e a validação leem a mesma tabela. A `NamedTuple` deixa o uso legível (`nivel.maximo` em
vez de `nivel[2]`) e satisfaz o mypy strict, o que o dicionário de dicionários (b) não faz sem um
`TypedDict`. Descartar (c): espalha os números pelo código e duplica o menu.

**Trade-off.** A `NamedTuple` é um conceito a mais para o iniciante. Fica explicada num comentário
de três linhas, e o uso dela se limita ao acesso por nome.

### ADR-3 — Leitura do teclado e sorteio por parâmetro, com padrões reais

**Decisão.** As funções que leem o teclado recebem `ler: Leitor = input`, e `jogar_partida`
recebe `sortear: Sorteador = random.randint`. `main()` repassa os dois.

**Alternativas.** (a) chamar `input` e `random.randint` direto e substituí-los nos testes com
`monkeypatch`, como fazem os outros mini-projetos.

**Porquê.** Atende o RNF-06: o teste diz qual é o número secreto e qual é a sequência de entradas
na própria chamada, sem trocar funções da biblioteca padrão por baixo. Quem só roda o jogo não
percebe diferença, porque os padrões são as funções reais.

**Trade-off.** As assinaturas ganham um ou dois parâmetros e os apelidos de tipo `Leitor` e
`Sorteador`. Para o iniciante, o parâmetro com função como valor padrão é uma ideia nova; um
comentário no topo do arquivo explica o motivo.

### ADR-4 — `os.system` em vez de `subprocess.run(..., shell=True)`

**Decisão.** `limpar_tela` usa `os.system(comando)` com uma string fixa (`"cls"` ou `"clear"`).

**Alternativas.** (a) `subprocess.run(comando, shell=True)`. (b) uma biblioteca de terceiros
(`colorama`, `rich`) com uma função de limpar a tela.

**Porquê.** `comando` nunca vem do usuário: é sempre um literal escolhido pelo `os.name`.
`os.system` faz o mesmo com uma linha mais simples e sem o `shell=True` que as ferramentas de
análise estática sinalizam por hábito. Descartar (b): o jogo não tem dependência de execução
(RNF-01).

**Trade-off.** `os.system` não captura a saída do comando, o que não importa aqui: o efeito
desejado é só o do terminal.

### ADR-5 — `main()` como função, chamada pelo `if __name__ == "__main__"`

**Decisão.** O laço de partidas vive em `main()`, e o guard `if __name__ == "__main__"` só a
chama.

**Alternativas.** (a) escrever o laço direto no bloco do guard.

**Porquê.** Uma função nomeada é importável, documentável (docstring) e testável: os testes
chamam `main()` com um leitor e um sorteador falsos.

**Trade-off.** Nenhum relevante.

### ADR-6 — Reconfigurar `sys.stdout` para UTF-8 no import

**Decisão.** `main.py` chama `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no nível
do módulo, se o atributo existir.

**Alternativas.** (a) não fazer nada. (b) tirar os emojis das mensagens.

**Porquê.** No Windows, quando a saída não está presa a um console UTF-8 (redirecionada para
arquivo, pipe ou executor de CI), o Python cai para a codepage do sistema (`cp1252`), e todo
`print()` com emoji lança `UnicodeEncodeError` (RNF-05). Descartar (b): os emojis fazem parte da
voz dos mini-projetos.

**Trade-off.** `errors="replace"` troca um caractere sem suporte por `?` em vez de quebrar, o que
só afeta um terminal que também não suporta UTF-8.

### ADR-7 — Ctrl+C tratado só em `main()`

**Decisão.** Um único `try`/`except (KeyboardInterrupt, EOFError)` envolve o laço de `main()` e
imprime a despedida.

**Alternativas.** (a) capturar as duas exceções em cada função que lê o teclado. (b) não tratar,
como os outros mini-projetos.

**Porquê.** Ctrl+C e fim da entrada significam "sair do jogo" em qualquer ponto, então um lugar só
basta, e as funções de leitura ficam focadas em validar (RNF-04). Descartar (b): o stack trace
assusta o iniciante e parece erro do programa.

**Trade-off.** Uma partida interrompida não aparece no resumo como derrota, e os recordes não são
mostrados na saída por Ctrl+C. Para um jogo de sessão curta, a despedida basta.

### ADR-8 — Nível sem vitória fica fora do dicionário de recordes

**Decisão.** `recordes` só tem a chave do nível depois da primeira vitória nele, e
`exibir_recordes` mostra um traço para os níveis ausentes.

**Alternativas.** (a) iniciar os três níveis com `None`. (b) iniciar com `0`.

**Porquê.** "Não tem a chave" se confere com `in`, um conceito que o iniciante já viu com
dicionários, e evita o tipo `int | None` nos valores. Descartar (b): `0` seria um recorde
impossível de bater.

**Trade-off.** `exibir_recordes` precisa percorrer `NIVEIS`, e não `recordes`, para mostrar os
três níveis na ordem do menu.

## Impacto no código existente

O projeto é novo: nasce na pasta `mini_projetos/adivinhe_o_numero/`, com o mesmo kit dos outros
mini-projetos (listado no `tasks.md`). Fora da pasta, ganha uma entrada na matriz `projeto` do
workflow de CI da raiz e uma linha na tabela do `mini_projetos/README.md` e do `README.en.md`.
Nenhum outro mini-projeto muda.

## Estratégia de testes

Unitária, sem integração (não há rede nem arquivo). O leitor falso é um iterador de respostas
embrulhado numa função (`lambda _texto: next(respostas)`), e o sorteador falso devolve um número
fixo e guarda os extremos recebidos, para o teste do RF-02 conferir a faixa. A saída se confere
com o `capsys`. `limpar_tela` é substituída por uma fixture `autouse` com `monkeypatch`, para os
testes de `main()` não chamarem `os.system`: é o único `monkeypatch` da suíte (RF-08). Os testes
de `main()` também cobrem o Ctrl+C e o fim da entrada, com um leitor que lança `KeyboardInterrupt`
ou `EOFError` (RNF-04). Ver `tests/test_main.py` e a seção "Testes" do `requirements.md`.

## Desvios

1. **Texto das mensagens (RF-04, RF-05, RF-06, RF-07).** A sessão ilustrativa de "Interfaces"
   usa "Restam 7 tentativas" e "você usou 3 tentativas". No `main.py`, a dica diz "Tentativas
   restantes: 7.", a vitória diz "Acertou na tentativa 3! O número era 63.", o recorde no início
   da partida diz "acerto na tentativa 3", e o resumo final mostra só o número, com "(menor número
   de tentativas)" no título. Assim nenhuma frase precisa concordar com o número ("1 tentativas",
   "Restam 1"), sem uma função de plural a mais. O comportamento de cada RF não muda.
2. **Leitor e sorteador falsos (RNF-06).** A estratégia de testes previa um `lambda` sobre um
   iterador. Os testes usam pequenas classes com `__call__` (`LeitorFalso`, `SorteadorFalso` e
   `LeitorQueInterrompe`), porque elas também guardam os pedidos e os extremos recebidos, e o
   teste confere que a entrada inválida repete o mesmo número de tentativa e que o sorteio usou a
   faixa do nível. Continua sem `monkeypatch` em `input` ou `random`.
3. **Pisos do grupo `dev` (RNF-01).** Os mini-projetos não tinham os mesmos pisos (dois em
   `ruff>=0.17.1`, `mypy>=2.4.0` e `pytest>=9.1.1`, dois em `ruff>=0.17.4`, `mypy>=2.4.1` e
   `pytest>=9.2.0`). Este projeto nasce com os mais novos.
4. **Apelidos de tipo (ADR-3).** O "Modelo de dados" mostra `Leitor = Callable[[str], str]`;
   no `main.py`, os dois apelidos usam a instrução `type` (PEP 695, Python 3.12), a forma
   explícita de declarar um apelido de tipo. O uso nas assinaturas não muda.
5. **Largura da animação do README.** O `tasks.md` previa a largura de 52 colunas das outras
   animações. A dica "⬇️  O número é menor que 50. Tentativas restantes: 7." tem 53 e quebraria,
   deixando o ponto final sozinho na linha de baixo; esta animação usa 54 colunas, e a letra fica
   cerca de 4% menor que nas outras.

## Notas de implementação

- **Testes:** 45 casos em `tests/test_main.py` (30 na etapa 1, 15 na etapa 2); ruff, black e
  mypy strict verdes.
- **Matriz do CI:** com cinco projetos, a lista em linha de `projeto` passava de 100 colunas, e
  virou lista em bloco no `ci.yml` e no `pip-audit.yml`.
- **Conferido à mão:** uma partida por nível com o sorteio real, a limpeza de tela antes de cada
  menu (o `cls` devolve 0 no Windows e, com a saída redirecionada, deixa o caractere de limpar a
  tela no arquivo) e o `uv run main.py` com a entrada por pipe e a saída redirecionada para
  arquivo: os emojis saem sem `UnicodeEncodeError`, e o fim da entrada encerra com a despedida.
- **Animação do README:** gravada rodando o `main()` de verdade, com o sorteio fixo em 37 e o
  roteiro de entradas do nível médio: 50 e 25 (as duas dicas), "abc" (recusado pelo `try`/`except`,
  sem gastar tentativa), 37 (acerto na 3ª, novo recorde) e "n", até o resumo de recordes.
- **README:** além das seções do `pedra_papel_tesoura`, o Guia de Implementação fecha com uma dica
  de estratégia (a busca binária, que deu os limites de cada nível, ver as decisões do
  `requirements.md`), e a nota de Como rodar lembra o Ctrl+C.
- **Testes:** com o `test_impessoalidade.py` e o `test_readme_en.py`, a suíte tem 53 casos.
