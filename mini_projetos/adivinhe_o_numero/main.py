"""Jogo Adivinhe o Número via terminal — projeto educacional de laço e validação.

Material de estudo para prática do sorteio com `random`, do laço `while` e da
conversão da entrada do teclado com `int()` dentro de `try`/`except`, em Python
puro (sem dependências externas).

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. NÍVEIS (Nivel, NIVEIS): A tabela com a faixa e o limite de cada dificuldade.
2. PARÂMETROS (Leitor, Sorteador): O teclado e o sorteio entram por parâmetro.
3. INTERFACE (limpar_tela, escolher_nivel): Limpeza de tela e menu de níveis.
4. ENTRADA VALIDADA (ler_palpite): `int()` com `try`/`except` e conferência da faixa.
5. PARTIDA (jogar_partida): O sorteio, o laço `while` e as dicas "maior" e "menor".
6. RECORDES (atualizar_recorde, exibir_recordes): O melhor resultado de cada nível.
7. JOGAR DE NOVO (perguntar_jogar_de_novo): A pergunta s/n do fim da partida.
8. LOOP PRINCIPAL (main): O controle das partidas e a saída com Ctrl+C.
"""

from __future__ import annotations

import os
import random
import sys
from collections.abc import Callable
from typing import NamedTuple

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os emojis abaixo com
# UnicodeEncodeError; reconfigurar para UTF-8 evita o crash em qualquer ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Níveis
# ---------------------------------------------------------------------------


# Uma NamedTuple é uma tupla com nome em cada posição: `nivel.maximo` se lê
# melhor que `nivel[2]`. Ela só guarda dados, como um registro; aqui, os dados
# de um nível.
class Nivel(NamedTuple):
    """Faixa do sorteio e limite de tentativas de um nível de dificuldade.

    Attributes:
        nome (str): Nome do nível, como aparece nas mensagens ("fácil").
        minimo (int): Menor número que pode ser sorteado (incluído).
        maximo (int): Maior número que pode ser sorteado (incluído).
        limite (int): Número máximo de tentativas da partida.
    """

    nome: str
    minimo: int
    maximo: int
    limite: int


# A chave é a tecla do menu: o menu e a validação leem a mesma tabela. Os
# limites seguem a busca binária (chutar sempre o meio da faixa acerta em até
# 6, 7 e 10 tentativas), com folga no fácil e quase nenhuma no difícil.
NIVEIS: dict[str, Nivel] = {
    "1": Nivel("fácil", 1, 50, 10),
    "2": Nivel("médio", 1, 100, 8),
    "3": Nivel("difícil", 1, 1000, 10),
}


# ---------------------------------------------------------------------------
# Parâmetros injetáveis
# ---------------------------------------------------------------------------


# As funções que leem o teclado recebem `ler` (que vale `input` por padrão), e a
# partida recebe `sortear` (que vale `random.randint`). Quem joga não percebe
# diferença; os testes passam um teclado e um sorteio falsos, e escolhem o
# número secreto e o que foi "digitado". O `type` dá um nome curto a um tipo
# comprido, para as assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]
type Sorteador = Callable[[int, int], int]


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def limpar_tela() -> None:
    """Limpa o terminal, detectando o sistema operacional automaticamente."""
    # 'nt' é o identificador interno para Windows. O comando é sempre um destes
    # dois textos fixos, nunca algo digitado pelo jogador.
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def escolher_nivel(ler: Leitor = input) -> Nivel:
    """Mostra o menu de níveis e lê a escolha, repetindo até ser válida.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.

    Returns:
        Nivel: O nível escolhido.
    """
    print("Escolha o nível:")
    for tecla, nivel in NIVEIS.items():
        # `:<8` alinha o nome à esquerda em 8 colunas, para as faixas
        # ficarem uma embaixo da outra.
        faixa = f"{nivel.minimo} a {nivel.maximo}, {nivel.limite} tentativas"
        print(f"  {tecla} - {nivel.nome.capitalize():<8}({faixa})")

    while True:
        resposta = ler("Digite o número do nível: ").strip()
        if resposta in NIVEIS:
            return NIVEIS[resposta]
        print("❌ Opção inválida. Escolha um dos níveis do menu.")


# ---------------------------------------------------------------------------
# Entrada validada
# ---------------------------------------------------------------------------


def ler_palpite(nivel: Nivel, tentativa: int, ler: Leitor = input) -> int:
    """Lê um palpite inteiro dentro da faixa do nível, repetindo até ser válido.

    A entrada inválida (texto, decimal, vazio ou fora da faixa) não conta como
    tentativa: o pedido se repete com o mesmo número de tentativa.

    Args:
        nivel (Nivel): Nível da partida, com a faixa aceita.
        tentativa (int): Número da tentativa atual, mostrado no pedido.
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.

    Returns:
        int: O palpite válido.
    """
    pedido = f"Tentativa {tentativa} de {nivel.limite}. Seu palpite: "
    while True:
        # `int()` lança ValueError para "abc", "3.5" e entrada vazia; o
        # `except` transforma o erro numa mensagem em vez de derrubar o jogo.
        try:
            palpite = int(ler(pedido))
        except ValueError:
            print("❌ Digite um número inteiro.")
            continue

        if nivel.minimo <= palpite <= nivel.maximo:
            return palpite
        print(f"❌ O palpite precisa estar entre {nivel.minimo} e {nivel.maximo}.")


# ---------------------------------------------------------------------------
# Partida
# ---------------------------------------------------------------------------


def jogar_partida(
    nivel: Nivel,
    recorde: int | None,
    sortear: Sorteador = random.randint,
    ler: Leitor = input,
) -> int | None:
    """Joga uma partida: sorteia o número e lê palpites até o acerto ou o limite.

    Args:
        nivel (Nivel): Nível da partida, com a faixa e o limite de tentativas.
        recorde (int | None): Recorde do nível na sessão, ou None se ainda não
            houve vitória nele.
        sortear (Sorteador, optional): Função que sorteia o número entre dois
            extremos incluídos. Padrão: `random.randint`.
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.

    Returns:
        int | None: As tentativas usadas na vitória, ou None na derrota.
    """
    numero_sorteado = sortear(nivel.minimo, nivel.maximo)
    print(
        f"\nPensei num número de {nivel.minimo} a {nivel.maximo}. "
        f"Você tem {nivel.limite} tentativas."
    )
    if recorde is not None:
        print(f"🏆 Seu recorde neste nível: acerto na tentativa {recorde}.")
    print()

    tentativa = 1
    # O laço para sozinho quando a última tentativa é usada; o acerto sai antes,
    # com `return`.
    while tentativa <= nivel.limite:
        palpite = ler_palpite(nivel, tentativa, ler)
        if palpite == numero_sorteado:
            print(
                f"🎉 Acertou na tentativa {tentativa}! O número era {numero_sorteado}."
            )
            return tentativa

        restantes = nivel.limite - tentativa
        if palpite < numero_sorteado:
            print(
                f"⬆️  O número é maior que {palpite}. Tentativas restantes: {restantes}."
            )
        else:
            print(
                f"⬇️  O número é menor que {palpite}. Tentativas restantes: {restantes}."
            )
        tentativa += 1

    print(f"😢 Suas tentativas acabaram. O número era {numero_sorteado}.")
    return None


# ---------------------------------------------------------------------------
# Recordes
# ---------------------------------------------------------------------------


def atualizar_recorde(
    recordes: dict[str, int], nome_nivel: str, tentativas: int
) -> bool:
    """Grava o resultado como recorde do nível, se for o melhor da sessão.

    Recorde é o menor número de tentativas numa vitória. O nível que ainda não
    teve vitória não aparece no dicionário. Empatar com o recorde não conta.

    Args:
        recordes (dict[str, int]): Recordes da sessão, do nome do nível para o
            número de tentativas. É atualizado no lugar.
        nome_nivel (str): Nome do nível da partida vencida.
        tentativas (int): Tentativas usadas na vitória.

    Returns:
        bool: True se o resultado virou o novo recorde do nível.
    """
    if nome_nivel not in recordes or tentativas < recordes[nome_nivel]:
        recordes[nome_nivel] = tentativas
        return True
    return False


def exibir_recordes(recordes: dict[str, int]) -> None:
    """Mostra o recorde de cada nível, na ordem do menu, ou um traço sem vitória.

    Args:
        recordes (dict[str, int]): Recordes da sessão, do nome do nível para o
            número de tentativas.
    """
    print("\nRecordes da sessão (menor número de tentativas):")
    # Percorre NIVEIS, e não `recordes`, para mostrar também os níveis sem vitória.
    for nivel in NIVEIS.values():
        valor = str(recordes[nivel.nome]) if nivel.nome in recordes else "—"
        rotulo = f"{nivel.nome.capitalize()}:"
        print(f"  {rotulo:<9}{valor}")


# ---------------------------------------------------------------------------
# Jogar de novo
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


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main(sortear: Sorteador = random.randint, ler: Leitor = input) -> None:
    """Roda a sessão: partidas em sequência, recordes por nível e resumo final.

    Ctrl+C e o fim da entrada (Ctrl+D no Linux) encerram o jogo em qualquer
    ponto com uma despedida, sem stack trace.

    Args:
        sortear (Sorteador, optional): Função que sorteia o número secreto.
            Padrão: `random.randint`.
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
    """
    recordes: dict[str, int] = {}
    try:
        jogar_de_novo = True
        while jogar_de_novo:
            limpar_tela()
            nivel = escolher_nivel(ler)
            tentativas = jogar_partida(nivel, recordes.get(nivel.nome), sortear, ler)
            if tentativas is not None and atualizar_recorde(
                recordes, nivel.nome, tentativas
            ):
                print(f"🏆 Novo recorde no nível {nivel.nome}!")
            jogar_de_novo = perguntar_jogar_de_novo(ler)

        exibir_recordes(recordes)
        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída: as funções de leitura ficam só validando.
        print("\nJogo encerrado. Até a próxima! 👋")


if __name__ == "__main__":
    main()
