"""Jogo da Forca via terminal — projeto educacional de strings e conjuntos.

Material de estudo para prática de strings (percorrer, `in`, `join`), de
conjuntos (`set`) para as letras tentadas e da remoção de acentos com
`unicodedata`, em Python puro (sem dependências externas).

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. DADOS (PALAVRAS, ERROS_MAXIMOS, FORCA, ALFABETO): Palavras por tema e desenhos.
2. PARÂMETROS (Leitor, Sorteador): O teclado e o sorteio entram por parâmetro.
3. SORTEIO (sortear_palavra): A palavra da partida, sem repetir na sessão.
4. LETRAS (remover_acentos, mascarar_palavra, contar_erros): Strings e conjuntos.
5. ENTRADA VALIDADA (Conferencia, conferir_entrada): Uma letra só, ainda não tentada.
6. INTERFACE (limpar_tela, exibir_jogo): Limpeza de tela e desenho do quadro.
7. PARTIDA (jogar_partida): O laço `while` de tentativas até a vitória ou a derrota.
8. FIM DA PARTIDA (perguntar_jogar_de_novo, exibir_placar): s/n e placar da sessão.
9. LOOP PRINCIPAL (main): O controle das partidas e a saída com Ctrl+C.
"""

from __future__ import annotations

import os
import random
import string
import sys
import unicodedata
from collections.abc import Callable
from typing import NamedTuple

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos e os emojis abaixo com
# UnicodeEncodeError; reconfigurar para UTF-8 evita o crash em qualquer ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Dados do jogo
# ---------------------------------------------------------------------------


# Do tema para as palavras dele: cada tema aparece uma vez só. As palavras ficam
# em minúsculas e com a grafia acentuada, que é como aparecem na tela.
PALAVRAS: dict[str, list[str]] = {
    "frutas": [
        "banana",
        "maçã",
        "abacaxi",
        "morango",
        "limão",
        "melancia",
        "maracujá",
        "pêssego",
    ],
    "animais": [
        "cachorro",
        "elefante",
        "girafa",
        "tartaruga",
        "jacaré",
        "onça",
        "coruja",
        "borboleta",
    ],
    "países": [
        "brasil",
        "argentina",
        "japão",
        "canadá",
        "portugal",
        "méxico",
        "alemanha",
        "egito",
    ],
    "profissões": [
        "médico",
        "professor",
        "bombeiro",
        "músico",
        "cozinheiro",
        "engenheiro",
        "jornalista",
        "padeiro",
    ],
    "objetos da casa": [
        "cadeira",
        "travesseiro",
        "geladeira",
        "fogão",
        "sofá",
        "espelho",
        "relógio",
        "lençol",
    ],
}

# Cabeça, tronco, dois braços e duas pernas: o sexto erro completa a forca.
ERROS_MAXIMOS = 6

# Um desenho por número de erros: FORCA[0] é só o poste, FORCA[6] é a forca
# completa. O `r` antes das aspas faz a barra invertida (braço e perna) valer
# como caractere; a quebra de linha logo depois das aspas separa o desenho do
# título "Tema" na tela.
FORCA: list[str] = [
    r"""
  +---+
  |   |
      |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========""",
    r"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========""",
]

# As 26 letras sem acento ("abc...xyz"): toda entrada válida vira uma delas
# depois de perder o acento.
ALFABETO = string.ascii_lowercase


# ---------------------------------------------------------------------------
# Parâmetros injetáveis
# ---------------------------------------------------------------------------


# As funções que leem o teclado recebem `ler` (que vale `input` por padrão), e o
# sorteio recebe `sortear` (que vale `random.choice`). Quem joga não percebe
# diferença; os testes passam um teclado e um sorteio falsos, e escolhem a
# palavra e o que foi "digitado". O `type` dá um nome curto a um tipo comprido,
# para as assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]
type Sorteador = Callable[[list[tuple[str, str]]], tuple[str, str]]


# ---------------------------------------------------------------------------
# Sorteio
# ---------------------------------------------------------------------------


def sortear_palavra(
    ja_sorteadas: set[str], sortear: Sorteador = random.choice
) -> tuple[str, str]:
    """Sorteia um par (tema, palavra) entre as palavras que ainda não saíram.

    Quando todas as palavras já saíram na sessão, a lista recomeça.

    Args:
        ja_sorteadas (set[str]): Palavras que já saíram na sessão. A palavra
            sorteada é acrescentada no lugar.
        sortear (Sorteador, optional): Função que escolhe um item da lista.
            Padrão: `random.choice`.

    Returns:
        tuple[str, str]: O tema e a palavra sorteados.
    """
    # "Achata" o dicionário numa lista de pares, na ordem de PALAVRAS.
    todas = [
        (tema, palavra) for tema, palavras in PALAVRAS.items() for palavra in palavras
    ]
    opcoes = [par for par in todas if par[1] not in ja_sorteadas]
    if not opcoes:
        ja_sorteadas.clear()
        opcoes = todas

    tema, palavra = sortear(opcoes)
    ja_sorteadas.add(palavra)
    return tema, palavra


# ---------------------------------------------------------------------------
# Letras: strings e conjuntos
# ---------------------------------------------------------------------------


def remover_acentos(texto: str) -> str:
    """Tira os acentos e a cedilha do texto: "maçã" vira "maca".

    Args:
        texto (str): Texto com ou sem acento.

    Returns:
        str: O mesmo texto, só com as letras base.
    """
    # A forma NFD separa cada letra acentuada na letra base mais a marca do
    # acento: "ã" vira "a" + "~", e "ç" vira "c" + cedilha. As marcas são os
    # caracteres em que `combining` é diferente de zero; o `join` junta o resto.
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(
        caractere for caractere in decomposto if not unicodedata.combining(caractere)
    )


def mascarar_palavra(palavra: str, tentadas: set[str]) -> str:
    """Mostra a palavra em maiúsculas, com `_` em cada letra ainda escondida.

    A letra descoberta aparece com a grafia original: "maçã" com {"a"} vira
    "_ A _ Ã".

    Args:
        palavra (str): Palavra da partida, com acento.
        tentadas (set[str]): Letras já tentadas, sem acento.

    Returns:
        str: A palavra mascarada, com um espaço entre as posições.
    """
    posicoes = [
        letra.upper() if remover_acentos(letra) in tentadas else "_"
        for letra in palavra
    ]
    return " ".join(posicoes)


def contar_erros(letras_da_palavra: set[str], tentadas: set[str]) -> int:
    """Conta as letras tentadas que a palavra não tem.

    Args:
        letras_da_palavra (set[str]): Letras da palavra, sem acento.
        tentadas (set[str]): Letras já tentadas, sem acento.

    Returns:
        int: O número de erros da partida.
    """
    # A diferença `a - b` guarda o que está em `a` e não está em `b`.
    return len(tentadas - letras_da_palavra)


# ---------------------------------------------------------------------------
# Entrada validada
# ---------------------------------------------------------------------------


class Conferencia(NamedTuple):
    """Resultado da conferência de uma entrada: a letra aceita ou o motivo da recusa.

    Só um dos dois campos vem preenchido; o outro é "".

    Attributes:
        letra (str): A letra aceita, minúscula e sem acento.
        recusa (str): A mensagem que explica por que a entrada foi recusada.
    """

    letra: str
    recusa: str


def conferir_entrada(entrada: str, tentadas: set[str]) -> Conferencia:
    """Confere se a entrada é uma letra só, de A a Z, que ainda não foi tentada.

    A entrada perde os espaços, o acento e a maiúscula antes da conferência:
    "Á" e "ç" valem como "a" e "c".

    Args:
        entrada (str): O que o jogador digitou.
        tentadas (set[str]): Letras já tentadas, sem acento.

    Returns:
        Conferencia: A letra aceita, ou a mensagem de recusa.
    """
    letra = remover_acentos(entrada.strip().lower())
    # O tamanho vem antes do `in`: com strings, `in` procura um trecho, e não um
    # caractere, então `"" in ALFABETO` e `"ab" in ALFABETO` dão True.
    if len(letra) != 1 or letra not in ALFABETO:
        return Conferencia("", "❌ Digite uma letra só, de A a Z.")
    if letra in tentadas:
        return Conferencia(
            "", f"🔁 A letra {letra.upper()} já foi tentada. Tente outra."
        )
    return Conferencia(letra, "")


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def limpar_tela() -> None:
    """Limpa o terminal, detectando o sistema operacional automaticamente."""
    # 'nt' é o identificador interno para Windows. O comando é sempre um destes
    # dois textos fixos, nunca algo digitado pelo jogador.
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def exibir_jogo(tema: str, palavra: str, tentadas: set[str], mensagem: str) -> None:
    """Desenha o quadro da partida: tema, forca, palavra, letras e erros restantes.

    Args:
        tema (str): Tema da palavra, mostrado como dica.
        palavra (str): Palavra da partida, com acento.
        tentadas (set[str]): Letras já tentadas, sem acento.
        mensagem (str): Resultado da tentativa anterior, ou "" se não houver.
    """
    erros = contar_erros(set(remover_acentos(palavra)), tentadas)
    # O conjunto não tem ordem: `sorted` devolve as letras em ordem alfabética.
    letras = ", ".join(sorted(tentadas)).upper() or "—"

    print(f"Tema: {tema}")
    print(FORCA[erros])
    print()
    print(f"Palavra: {mascarar_palavra(palavra, tentadas)}")
    print(f"Letras tentadas: {letras}")
    print(f"Erros restantes: {ERROS_MAXIMOS - erros}")
    print()
    if mensagem:
        print(mensagem)


# ---------------------------------------------------------------------------
# Partida
# ---------------------------------------------------------------------------


def jogar_partida(tema: str, palavra: str, ler: Leitor = input) -> bool:
    """Joga uma partida: lê letras até descobrir a palavra ou completar a forca.

    A entrada recusada (inválida ou repetida) não conta como erro: ela só vira a
    mensagem do próximo quadro.

    Args:
        tema (str): Tema da palavra, mostrado como dica.
        palavra (str): Palavra da partida, com acento.
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.

    Returns:
        bool: True na vitória e False na derrota.
    """
    # Os dois conjuntos guardam letras sem acento: "maçã" vira {"m", "a", "c"}.
    letras_da_palavra = set(remover_acentos(palavra))
    tentadas: set[str] = set()
    mensagem = ""

    # `issubset` responde se toda letra da palavra já está entre as tentadas.
    while contar_erros(
        letras_da_palavra, tentadas
    ) < ERROS_MAXIMOS and not letras_da_palavra.issubset(tentadas):
        limpar_tela()
        exibir_jogo(tema, palavra, tentadas, mensagem)
        conferencia = conferir_entrada(ler("Digite uma letra: "), tentadas)
        if conferencia.recusa:
            mensagem = conferencia.recusa
            continue

        tentadas.add(conferencia.letra)
        letra = conferencia.letra.upper()
        if conferencia.letra in letras_da_palavra:
            mensagem = f"✅ A palavra tem a letra {letra}."
        else:
            mensagem = f"❌ A palavra não tem a letra {letra}."

    venceu = letras_da_palavra.issubset(tentadas)
    erros = contar_erros(letras_da_palavra, tentadas)
    if venceu:
        mensagem = (
            f"🎉 Você descobriu a palavra: {palavra.upper()}! "
            f"Erros cometidos: {erros}."
        )
    else:
        mensagem = f"💀 A forca completou. A palavra era {palavra.upper()}."
    limpar_tela()
    exibir_jogo(tema, palavra, tentadas, mensagem)
    return venceu


# ---------------------------------------------------------------------------
# Fim da partida
# ---------------------------------------------------------------------------


def perguntar_jogar_de_novo(ler: Leitor = input) -> bool:
    """Pergunta se o jogador quer outra partida, repetindo até ouvir s ou n.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.

    Returns:
        bool: True para `s` e False para `n`, em maiúscula ou minúscula.
    """
    while True:
        resposta = ler("\nJogar de novo? (s/n): ").strip().lower()
        if resposta == "s":
            return True
        if resposta == "n":
            return False
        print("❌ Responda s (sim) ou n (não).")


def exibir_placar(placar: dict[str, int]) -> None:
    """Mostra as vitórias e as derrotas da sessão.

    Args:
        placar (dict[str, int]): Placar da sessão, com as chaves "vitórias" e
            "derrotas".
    """
    print("\nPlacar da sessão:")
    print(f"  Vitórias: {placar['vitórias']}")
    print(f"  Derrotas: {placar['derrotas']}")


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main(sortear: Sorteador = random.choice, ler: Leitor = input) -> None:
    """Roda a sessão: partidas em sequência, sem repetir palavra, e placar final.

    Ctrl+C e o fim da entrada (Ctrl+D no Linux) encerram o jogo em qualquer
    ponto com uma despedida, sem stack trace.

    Args:
        sortear (Sorteador, optional): Função que escolhe o par (tema, palavra).
            Padrão: `random.choice`.
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
    """
    ja_sorteadas: set[str] = set()
    placar = {"vitórias": 0, "derrotas": 0}
    try:
        jogar_de_novo = True
        while jogar_de_novo:
            tema, palavra = sortear_palavra(ja_sorteadas, sortear)
            if jogar_partida(tema, palavra, ler):
                placar["vitórias"] += 1
            else:
                placar["derrotas"] += 1
            jogar_de_novo = perguntar_jogar_de_novo(ler)

        exibir_placar(placar)
        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída: as funções de leitura ficam só validando.
        print("\nJogo encerrado. Até a próxima! 👋")


if __name__ == "__main__":
    main()
