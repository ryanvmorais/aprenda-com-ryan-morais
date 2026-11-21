"""Cifra de César via terminal — projeto educacional de cifra e de quebra.

Material de estudo para prática de três ideias: o `ord`, o `chr` e a aritmética
modular, que andam cada letra a chave de posições no alfabeto (o resto da
divisão por 26 faz o Z voltar para o A); o laço de força bruta, que testa as 25
chaves possíveis; e o `collections.Counter`, que conta as letras do texto para
compará-las com a frequência das letras no português e achar a chave mais
provável. Python puro (sem dependências externas), e o texto digitado não é
guardado nem sai do computador. A cifra de César não protege nada: o programa
mostra como uma cifra funciona e por que esta cai em segundos.

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. TIPOS (Leitor): O parâmetro injetável da leitura do teclado.
2. CONSTANTES (ALFABETO, CHAVES, FREQUENCIAS, MINIMO_LETRAS, LARGURA, OPCOES).
3. CIFRA (remover_acentos, deslocar_letra, montar_tabela, deslocar, cifrar,
   decifrar): A troca de cada letra pela letra deslocada.
4. QUEBRA (tem_letras, forca_bruta, contar_letras, pontuar, ordenar_chaves):
   As 25 tentativas e a chave mais provável pela frequência.
5. TEXTOS (cortar, aviso_acentos, descrever_cifra, descrever_decifra,
   descrever_forca_bruta, descrever_frequencia): O resultado de cada opção,
   devolvido como texto.
6. PERGUNTAS (eh_numero, conferir_opcao, conferir_chave): A escolha do menu e a
   chave, conferidas.
7. OPÇÕES (pedir_texto, opcao_cifrar, opcao_decifrar, opcao_forca_bruta,
   opcao_frequencia): Os pedidos do texto e da chave, e o resultado.
8. INTERFACE (limpar_tela, exibir_tela): A limpeza e o desenho do quadro.
9. LOOP PRINCIPAL (main): O menu em laço e a saída com Ctrl+C.
"""

from __future__ import annotations

import os
import string
import sys
import unicodedata
from collections import Counter
from collections.abc import Callable

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos e os emojis com
# UnicodeEncodeError; reconfigurar para UTF-8 evita o crash em qualquer
# ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


# `main` recebe `ler`, que vale `input`: recebe o texto do pedido e devolve o
# que foi digitado. Quem usa o programa não percebe diferença; os testes passam
# um teclado falso. O `type` dá um nome curto a um tipo comprido, para as
# assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------


# As 26 letras, de "a" a "z", na ordem em que a chave anda.
ALFABETO = string.ascii_lowercase

# As chaves válidas. A 0 e a 26 deixam o texto igual, e a 27 cifra como a 1,
# porque o deslocamento é o resto da divisão por 26: de 1 a 25, cada cifra tem
# um nome só.
CHAVES = range(1, 26)

# O percentual de cada letra no português, da tabela 1.2.1 ("Agrupamento das
# letras por similaridade das freqüências para o Português") do estudo "Análise
# de Freqüências de Línguas", de Bruno da Rocha Braga (Ravel/COPPE/UFRJ, 24 de
# março de 2003), copiado sem alteração:
# https://www.lockabit.coppe.ufrj.br/sites/lockabit.coppe.ufrj.br/files/publicacoes/lockabit/analise_freq.pdf
# O estudo contou 1,1 MB de textos de autores brasileiros, sem acentos e com o Ç
# como C, o mesmo tratamento que o programa dá aos acentos. A soma dá 100,03%,
# pelo arredondamento de cada letra a duas casas.
FREQUENCIAS: dict[str, float] = {
    "a": 14.64,
    "b": 1.16,
    "c": 3.76,
    "d": 4.97,
    "e": 12.70,
    "f": 1.02,
    "g": 1.29,
    "h": 1.42,
    "i": 5.90,
    "j": 0.32,
    "k": 0.01,
    "l": 2.95,
    "m": 4.71,
    "n": 4.85,
    "o": 10.78,
    "p": 2.58,
    "q": 1.09,
    "r": 6.88,
    "s": 7.97,
    "t": 4.26,
    "u": 4.42,
    "v": 1.68,
    "w": 0.01,
    "x": 0.23,
    "y": 0.01,
    "z": 0.42,
}

# Abaixo de 30 letras, o resultado da frequência ganha o aviso de texto curto:
# na medição do design, 30 é o primeiro tamanho em que a chave mais provável
# acerta em mais de 99% dos trechos (ADR-6).
MINIMO_LETRAS = 30

# As colunas de uma linha do programa, para o quadro caber num terminal
# estreito. As linhas da força bruta e as alternativas da frequência são
# cortadas nela (ADR-8).
LARGURA = 54

# O menu, numerado a partir de 1 na tela.
OPCOES = [
    "Cifrar um texto",
    "Decifrar com a chave",
    "Quebrar por força bruta",
    "Quebrar pela frequência das letras",
    "Sair",
]


# ---------------------------------------------------------------------------
# Cifra
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


def deslocar_letra(letra: str, chave: int) -> str:
    """Anda a letra `chave` posições no alfabeto, voltando ao começo depois do Z.

    A conta usa o resto da divisão por 26, e a chave negativa anda para trás.
    No Python, o resto de um número negativo por 26 fica entre 0 e 25
    (`-3 % 26 == 23`), então o "a" com a chave -3 vira o "x". Em outras
    linguagens, como C e JavaScript, o `%` de um número negativo dá um
    resultado negativo, e a mesma conta precisaria somar 26 antes.

    Args:
        letra (str): Uma letra de "a" a "z", minúscula ou maiúscula.
        chave (int): Quantas posições andar: positiva para a frente, negativa
            para trás.

    Returns:
        str: A letra deslocada, minúscula ou maiúscula como a original.
    """
    base = "a" if letra.islower() else "A"
    # A posição da letra no alfabeto, de 0 (a) a 25 (z).
    posicao = ord(letra) - ord(base)
    # O `% 26` é o resto da divisão por 26: a posição 25 (z) mais 1 dá 26, e o
    # resto de 26 por 26 é 0, o "a" de novo.
    nova = (posicao + chave) % 26
    return chr(ord(base) + nova)


def montar_tabela(chave: int) -> dict[int, int]:
    """Monta a tabela de tradução de cada letra para a letra deslocada.

    A tabela é a `deslocar_letra` feita uma vez para cada uma das 52 letras,
    minúsculas e maiúsculas. Só elas entram: no `translate`, todo o resto
    (espaço, número, pontuação, emoji, uma letra de outro alfabeto como o "ß")
    passa sem mudança, sem nenhum `if`.

    Args:
        chave (int): Quantas posições andar.

    Returns:
        dict[int, int]: O código de cada letra para o código da deslocada, no
            formato do `str.maketrans`.
    """
    letras = ALFABETO + ALFABETO.upper()
    deslocadas = "".join(deslocar_letra(letra, chave) for letra in letras)
    return str.maketrans(letras, deslocadas)


def deslocar(texto: str, chave: int) -> str:
    """Tira os acentos do texto e anda cada letra a chave de posições.

    Args:
        texto (str): O texto, com ou sem acento.
        chave (int): Quantas posições andar.

    Returns:
        str: O texto sem acentos, com as letras deslocadas.
    """
    return remover_acentos(texto).translate(montar_tabela(chave))


def cifrar(texto: str, chave: int) -> str:
    """Cifra o texto: cada letra anda a chave de posições para a frente.

    Args:
        texto (str): O texto original.
        chave (int): A chave, de 1 a 25.

    Returns:
        str: O texto cifrado, sem acentos.
    """
    return deslocar(texto, chave)


def decifrar(texto: str, chave: int) -> str:
    """Decifra o texto: cada letra anda a chave de posições para trás.

    Args:
        texto (str): O texto cifrado.
        chave (int): A chave usada para cifrá-lo, de 1 a 25.

    Returns:
        str: O texto decifrado, sem acentos.
    """
    # Decifrar é andar para trás: a chave negativa desfaz a cifra.
    return deslocar(texto, -chave)


# ---------------------------------------------------------------------------
# Quebra
# ---------------------------------------------------------------------------


def tem_letras(texto: str) -> bool:
    """Diz se o texto tem alguma letra de "a" a "z", depois de tirar os acentos.

    Args:
        texto (str): O texto digitado.

    Returns:
        bool: True para "ç" ou "2026 a"; False para "", "2026!" ou "ß".
    """
    return any(caractere in ALFABETO for caractere in remover_acentos(texto).lower())


def forca_bruta(texto: str) -> list[tuple[int, str]]:
    """Decifra o texto com cada uma das 25 chaves.

    Args:
        texto (str): O texto cifrado.

    Returns:
        list[tuple[int, str]]: A chave e o texto decifrado com ela, da chave 1
            à 25.
    """
    return [(chave, decifrar(texto, chave)) for chave in CHAVES]


def contar_letras(texto: str) -> Counter[str]:
    """Conta quantas vezes cada letra aparece no texto.

    Args:
        texto (str): O texto, com ou sem acento.

    Returns:
        Counter[str]: Cada letra minúscula de "a" a "z" do texto, sem os
            acentos, e quantas vezes ela aparece.
    """
    # O `Counter` faz a contagem que um `dict` com `+= 1` faria num laço.
    letras = remover_acentos(texto).lower()
    return Counter(caractere for caractere in letras if caractere in ALFABETO)


def pontuar(texto: str) -> float:
    """Dá ao texto uma pontuação pela frequência das letras no português.

    Cada letra vale o percentual dela em `FREQUENCIAS`, vezes quantas vezes
    aparece. Um texto em português tem muitos "a", "e" e "o", que valem muito,
    e soma mais que o mesmo texto decifrado com a chave errada, cheio de letras
    raras.

    Args:
        texto (str): O texto decifrado com uma chave.

    Returns:
        float: A soma da contagem de cada letra vezes o percentual dela.
    """
    contagem = contar_letras(texto)
    return sum(
        quantidade * FREQUENCIAS[letra] for letra, quantidade in contagem.items()
    )


def ordenar_chaves(texto: str) -> list[int]:
    """Ordena as 25 chaves da mais provável para a menos provável.

    Args:
        texto (str): O texto cifrado.

    Returns:
        list[int]: As chaves, pela pontuação do texto decifrado com cada uma,
            da maior para a menor. Num empate, a chave menor vem antes.
    """
    # O `sorted` mantém a ordem original dos iguais, mesmo com `reverse=True`:
    # é ela que põe a chave menor antes, num empate.
    return sorted(
        CHAVES, key=lambda chave: pontuar(decifrar(texto, chave)), reverse=True
    )


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


def cortar(linha: str) -> str:
    """Corta a linha que não cabe em `LARGURA` caracteres, com reticências.

    Args:
        linha (str): Uma linha do resultado.

    Returns:
        str: A linha inteira, quando cabe; senão, os primeiros `LARGURA - 1`
            caracteres e o "…".
    """
    if len(linha) <= LARGURA:
        return linha
    return linha[: LARGURA - 1] + "…"


def aviso_acentos(texto: str) -> list[str]:
    """Monta o aviso de que os acentos e o ç foram tirados, se foram.

    Args:
        texto (str): O texto digitado.

    Returns:
        list[str]: A linha do aviso, quando o texto tinha acento ou ç; senão,
            a lista vazia, para o resultado juntar as listas sem `if`.
    """
    if remover_acentos(texto) != texto:
        return ["📝 Os acentos e o ç foram tirados do texto."]
    return []


def descrever_cifra(texto: str, chave: int) -> str:
    """Monta o resultado de cifrar, com o texto cifrado inteiro.

    Args:
        texto (str): O texto original.
        chave (int): A chave usada.

    Returns:
        str: A chave, o texto cifrado e o aviso de acentos, se houver.
    """
    linhas = [f"🔒 Texto cifrado com a chave {chave}:", cifrar(texto, chave)]
    return "\n".join(linhas + aviso_acentos(texto))


def descrever_decifra(texto: str, chave: int) -> str:
    """Monta o resultado de decifrar, com o texto decifrado inteiro.

    Args:
        texto (str): O texto cifrado.
        chave (int): A chave usada para cifrá-lo.

    Returns:
        str: A chave, o texto decifrado e o aviso de acentos, se houver.
    """
    linhas = [f"🔓 Texto decifrado com a chave {chave}:", decifrar(texto, chave)]
    return "\n".join(linhas + aviso_acentos(texto))


def descrever_forca_bruta(texto: str) -> str:
    """Monta o resultado da força bruta, uma linha por chave.

    Args:
        texto (str): O texto cifrado.

    Returns:
        str: As 25 tentativas, cada uma cortada em `LARGURA` caracteres, o
            aviso de acentos, se houver, e a explicação da força bruta.
    """
    linhas = ["🔨 As 25 chaves possíveis:"]
    for chave, decifrado in forca_bruta(texto):
        # O `:2` alinha a chave em duas colunas: "Chave  3" e "Chave 25".
        linhas.append(cortar(f"Chave {chave:2}: {decifrado}"))
    linhas += aviso_acentos(texto)
    linhas += [
        "💡 A chave certa é a da linha que dá para ler.",
        "   Testar todas as chaves é a força bruta.",
    ]
    return "\n".join(linhas)


def descrever_frequencia(texto: str) -> str:
    """Monta o resultado da quebra pela frequência das letras.

    Args:
        texto (str): O texto cifrado.

    Returns:
        str: As três letras mais comuns do texto, a chave mais provável com o
            texto decifrado inteiro, as duas alternativas cortadas, o aviso de
            acentos, se houver, e o aviso de texto curto abaixo de
            `MINIMO_LETRAS` letras.
    """
    contagem = contar_letras(texto)
    # `most_common(3)` devolve as três letras mais contadas, da maior para a
    # menor; um texto com menos de três letras diferentes devolve menos.
    comuns = [f"{letra.upper()} ({vezes})" for letra, vezes in contagem.most_common(3)]
    if len(comuns) > 1:
        comuns = [", ".join(comuns[:-1]) + " e " + comuns[-1]]
    primeira, segunda, terceira = ordenar_chaves(texto)[:3]
    linhas = [
        f"📊 Mais comuns no texto: {comuns[0]}",
        "   No português, as mais comuns são A, E e O.",
        f"🔓 Chave mais provável: {primeira}",
        decifrar(texto, primeira),
        "Outras chaves possíveis:",
        cortar(f"- Chave {segunda}: {decifrar(texto, segunda)}"),
        cortar(f"- Chave {terceira}: {decifrar(texto, terceira)}"),
    ]
    linhas += aviso_acentos(texto)
    # O aviso conta as letras, não os caracteres: espaço, número e pontuação
    # não entram na contagem e não ajudam a achar a chave. O `total()` as soma.
    if contagem.total() < MINIMO_LETRAS:
        linhas += [
            f"💡 Com menos de {MINIMO_LETRAS} letras, a contagem pode enganar:",
            "   confira na força bruta.",
        ]
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------


def eh_numero(texto: str) -> bool:
    """Diz se o texto é um número inteiro escrito com os algarismos de 0 a 9.

    Args:
        texto (str): O texto, já sem os espaços das pontas.

    Returns:
        bool: True para "1" ou "3"; False para "", "1.5", "-1" ou "٣".
    """
    # `isdecimal()` antes do `int()` dispensa o `try`, e o `isascii()` recusa os
    # algarismos de outras escritas, como o "٣" árabe, que o `int()` leria como 3.
    return texto.isascii() and texto.isdecimal()


def conferir_opcao(entrada: str) -> int | None:
    """Confere se a entrada é o número de uma opção do menu.

    Args:
        entrada (str): O que foi digitado no menu.

    Returns:
        int | None: O número da opção, de 1 a `len(OPCOES)`, ou None para
            qualquer outra coisa.
    """
    limpa = entrada.strip()
    if eh_numero(limpa) and 1 <= int(limpa) <= len(OPCOES):
        return int(limpa)
    return None


def conferir_chave(entrada: str) -> int | None:
    """Confere se a entrada é uma chave de 1 a 25.

    Args:
        entrada (str): O que foi digitado no pedido da chave.

    Returns:
        int | None: A chave, ou None para qualquer outra coisa. O "-3" cai no
            None pelo `eh_numero`, porque o sinal não é algarismo.
    """
    limpa = entrada.strip()
    if eh_numero(limpa) and int(limpa) in CHAVES:
        return int(limpa)
    return None


# ---------------------------------------------------------------------------
# Opções
# ---------------------------------------------------------------------------


def pedir_texto(ler: Leitor) -> str | None:
    """Pede o texto e confere se ele tem alguma letra.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.

    Returns:
        str | None: O texto digitado, ou None quando ele não tem nenhuma letra.
    """
    # Sem `strip()`: um espaço no começo ou no fim também é parte do texto.
    texto = ler("Digite o texto: ")
    return texto if tem_letras(texto) else None


def opcao_cifrar(ler: Leitor) -> str:
    """Pede o texto e a chave e devolve o resultado de cifrar.

    O texto só vive na variável local desta função e some quando ela termina.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.

    Returns:
        str: O resultado de `descrever_cifra`, ou a mensagem do texto sem
            letras ou da chave inválida.
    """
    texto = pedir_texto(ler)
    if texto is None:
        return "❌ Não há letras para cifrar."
    chave = conferir_chave(ler("Digite a chave (de 1 a 25): "))
    if chave is None:
        return "❌ A chave vai de 1 a 25."
    return descrever_cifra(texto, chave)


def opcao_decifrar(ler: Leitor) -> str:
    """Pede o texto cifrado e a chave e devolve o resultado de decifrar.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.

    Returns:
        str: O resultado de `descrever_decifra`, ou a mensagem do texto sem
            letras ou da chave inválida.
    """
    texto = pedir_texto(ler)
    if texto is None:
        return "❌ Não há letras para decifrar."
    chave = conferir_chave(ler("Digite a chave (de 1 a 25): "))
    if chave is None:
        return "❌ A chave vai de 1 a 25."
    return descrever_decifra(texto, chave)


def opcao_forca_bruta(ler: Leitor) -> str:
    """Pede o texto cifrado e devolve as 25 tentativas da força bruta.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.

    Returns:
        str: O resultado de `descrever_forca_bruta`, ou a mensagem do texto
            sem letras.
    """
    texto = pedir_texto(ler)
    if texto is None:
        return "❌ Não há letras para quebrar."
    return descrever_forca_bruta(texto)


def opcao_frequencia(ler: Leitor) -> str:
    """Pede o texto cifrado e devolve a quebra pela frequência das letras.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.

    Returns:
        str: O resultado de `descrever_frequencia`, ou a mensagem do texto
            sem letras.
    """
    texto = pedir_texto(ler)
    if texto is None:
        return "❌ Não há letras para quebrar."
    return descrever_frequencia(texto)


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def limpar_tela() -> None:
    """Limpa o terminal, detectando o sistema operacional automaticamente."""
    # 'nt' é o identificador interno para Windows. O comando é sempre um destes
    # dois textos fixos, nunca algo digitado pelo usuário.
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def exibir_tela(resultado: str) -> None:
    """Desenha o quadro: título, resultado da ação anterior e menu.

    Args:
        resultado (str): Resultado da ação anterior, ou "" se não houver.
    """
    print("======== CIFRA DE CÉSAR ========")
    print()
    if resultado:
        print(resultado)
        print()
    for numero, opcao in enumerate(OPCOES, start=1):
        print(f"{numero} : {opcao}")
    print()


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main(ler: Leitor = input) -> None:
    """Roda o programa: repete o menu até o usuário sair.

    O resultado de cada opção aparece acima do menu na volta seguinte e só vive
    na variável `resultado`. Ctrl+C e o fim da entrada (Ctrl+D no Linux)
    encerram o programa em qualquer ponto, no menu, no texto ou na chave, com
    uma despedida, sem stack trace.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
    """
    resultado = ""
    try:
        while True:
            limpar_tela()
            exibir_tela(resultado)
            opcao = conferir_opcao(ler("Escolha uma opção: "))
            if opcao == 1:
                resultado = opcao_cifrar(ler)
            elif opcao == 2:
                resultado = opcao_decifrar(ler)
            elif opcao == 3:
                resultado = opcao_forca_bruta(ler)
            elif opcao == 4:
                resultado = opcao_frequencia(ler)
            elif opcao == 5:
                break
            else:
                resultado = f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}."

        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída, qualquer que seja o pedido interrompido.
        print("\nCifra de César encerrada. Até a próxima! 👋")


if __name__ == "__main__":
    main()
