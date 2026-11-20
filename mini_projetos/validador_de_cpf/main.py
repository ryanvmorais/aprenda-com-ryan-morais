"""Validador de CPF via terminal — projeto educacional de dígitos verificadores.

Material de estudo para prática de um algoritmo de verdade: a soma ponderada com
o resto da divisão por 11, que dá os dois dígitos verificadores do CPF; a limpeza
e a conferência do texto digitado (`str.isdigit` e list comprehension); e as
funções pequenas e puras, que recebem um valor e devolvem outro sem mexer em mais
nada. A conta segue a forma publicada pela Receita Federal (Anexo II do ADE Cofis
nº 41/2017). Python puro (sem dependências externas), e nenhum CPF digitado ou
gerado sai da tela.

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. TIPOS (Conta, Conferencia, Leitor, Sorteador): A conta e os parâmetros injetáveis.
2. CONSTANTES (SEPARADORES, TAMANHO_CPF, REGIOES_FISCAIS, AVISO_GERADO, OPCOES).
3. CÁLCULO (calcular_digito, calcular_digitos): Os dois dígitos verificadores.
4. CONFERÊNCIA (limpar_cpf, eh_sequencia_repetida, conferir_cpf): O CPF digitado,
   limpo e conferido sem lançar exceção.
5. FORMATAÇÃO (formatar_cpf, descrever_regiao): O número e a região fiscal.
6. GERADOR (gerar_cpf): Um CPF válido pelo cálculo, para teste.
7. TEXTOS (descrever_resultado, descrever_conta, explicar_validacao,
   descrever_gerado): O resultado de cada opção, devolvido como texto.
8. INTERFACE (conferir_opcao, limpar_tela, exibir_tela): Menu e desenho do quadro.
9. LOOP PRINCIPAL (main): O menu em laço e a saída com Ctrl+C.
"""

from __future__ import annotations

import os
import random
import sys
from collections.abc import Callable
from typing import NamedTuple

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos, os emojis e os símbolos
# da conta (÷ e →) com UnicodeEncodeError; reconfigurar para UTF-8 evita o crash
# em qualquer ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


class Conta(NamedTuple):
    """Todos os passos da conta de um dígito verificador.

    O modo simples só olha o `digito`; o modo didático mostra cada campo na tela.
    Uma conta só, usada pelos dois, garante que a tela explica a mesma conta que
    decidiu o resultado.

    Attributes:
        algarismos (list[int]): Os 9 (1º dígito) ou 10 (2º dígito) algarismos.
        pesos (list[int]): De 1 a 9 ou de 0 a 9: o último algarismo leva sempre o
            peso 9.
        produtos (list[int]): Cada algarismo vezes o seu peso.
        soma (int): A soma dos produtos.
        resto (int): O resto da soma dividida por 11.
        digito (int): O resto, com 10 valendo 0.
    """

    algarismos: list[int]
    pesos: list[int]
    produtos: list[int]
    soma: int
    resto: int
    digito: int


class Conferencia(NamedTuple):
    """Resultado da conferência de um CPF: o CPF aceito ou o motivo da recusa.

    Só um dos dois campos vem preenchido; o outro é "".

    Attributes:
        valor (str): O CPF aceito, só com os 11 algarismos.
        recusa (str): A mensagem que explica por que o CPF foi recusado.
    """

    valor: str
    recusa: str


# `main` recebe `ler` (que vale `input`) e `sortear` (que vale
# `random.randrange`). Quem usa o programa não percebe diferença; os testes
# passam um teclado falso e um sorteio de semente fixa. O `type` dá um nome curto
# a um tipo comprido, para as assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]
type Sorteador = Callable[[int], int]


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------


# Pontos, hífen e espaços saem em qualquer posição: quem digita não precisa
# acertar a máscara. Qualquer outro caractere recusa o CPF.
SEPARADORES = ".- "

# Um CPF tem 11 algarismos: 9 da base e os 2 dígitos verificadores.
TAMANHO_CPF = 11

# O 9º algarismo indica a região fiscal do cadastro inicial (folheto "CPF" da
# Educação Fiscal da Receita Federal), não onde a pessoa mora hoje.
REGIOES_FISCAIS: dict[int, str] = {
    0: "RS",
    1: "DF, GO, MS, MT e TO",
    2: "AC, AM, AP, PA, RO e RR",
    3: "CE, MA e PI",
    4: "AL, PB, PE e RN",
    5: "BA e SE",
    6: "MG",
    7: "ES e RJ",
    8: "SP",
    9: "PR e SC",
}

# Há cerca de 1 bilhão de combinações válidas e centenas de milhões de CPFs
# emitidos: um número sorteado pode ser de alguém, então não é "fictício".
AVISO_GERADO = (
    "⚠️ Sorteado ao acaso: passa no cálculo, mas pode\n"
    "   ser o CPF de uma pessoa real. Use só para testes."
)

# O menu, numerado a partir de 1 na tela.
OPCOES = [
    "Validar um CPF",
    "Validar mostrando a conta",
    "Gerar um CPF válido para teste",
    "Sair",
]


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------


def calcular_digito(algarismos: list[int]) -> Conta:
    """Calcula um dígito verificador, guardando cada passo da conta.

    A mesma função serve aos dois dígitos: com os 9 algarismos da base, os pesos
    vão de 1 a 9; com a base e o 1º dígito (10 algarismos), de 0 a 9. Nos dois
    casos o último algarismo leva o peso 9.

    Args:
        algarismos (list[int]): Os 9 ou 10 algarismos da conta, da esquerda para
            a direita.

    Returns:
        Conta: Os algarismos, os pesos, os produtos, a soma, o resto e o dígito.
    """
    # Na forma mais divulgada, os pesos vão de 10 a 2 (e de 11 a 2) e o dígito é
    # 11 menos o resto, com 10 e 11 valendo 0. Dá sempre o mesmo dígito: cada
    # peso de lá é 11 menos o peso daqui, então a soma de lá deixa o resto
    # "11 menos o resto daqui", e 11 menos isso volta a ser o resto daqui.
    pesos = list(range(10 - len(algarismos), 10))
    produtos = [algarismo * peso for algarismo, peso in zip(algarismos, pesos)]
    soma = sum(produtos)
    resto = soma % 11
    # O dígito é um algarismo só: o resto 10 vale 0.
    digito = 0 if resto == 10 else resto
    return Conta(algarismos, pesos, produtos, soma, resto, digito)


def calcular_digitos(base: list[int]) -> tuple[Conta, Conta]:
    """Calcula os dois dígitos verificadores de uma base de 9 algarismos.

    Args:
        base (list[int]): Os 9 primeiros algarismos do CPF.

    Returns:
        tuple[Conta, Conta]: A conta do 1º e a do 2º dígito verificador.
    """
    primeira = calcular_digito(base)
    # O 2º dígito entra o 1º na conta, como o 10º algarismo.
    segunda = calcular_digito(base + [primeira.digito])
    return primeira, segunda


# ---------------------------------------------------------------------------
# Conferência
# ---------------------------------------------------------------------------


def limpar_cpf(entrada: str) -> Conferencia:
    """Descarta a pontuação e confere se sobram só os 11 algarismos.

    As recusas seguem esta ordem: um caractere que não é algarismo, nada
    digitado e a quantidade errada de algarismos. Sem completar com zeros à
    esquerda: o CPF é texto, e 10 algarismos não viram um CPF.

    Args:
        entrada (str): O CPF digitado, com ou sem pontuação.

    Returns:
        Conferencia: Os 11 algarismos, ou a mensagem de recusa.
    """
    sobra = [caractere for caractere in entrada if caractere not in SEPARADORES]
    for caractere in sobra:
        # O `isdigit()` sozinho aceita "²", que o `int()` recusa com ValueError,
        # e algarismos de outras escritas, como o "٣" árabe, que o `int()` lê
        # como 3. O `isascii()` limita aos algarismos de 0 a 9.
        if not (caractere.isascii() and caractere.isdigit()):
            return Conferencia(
                "", f'❌ CPF inválido\n   "{caractere}" não é um algarismo.'
            )
    if not sobra:
        return Conferencia("", "⚠️ Nenhum CPF digitado.")
    if len(sobra) != TAMANHO_CPF:
        return Conferencia(
            "",
            f"❌ CPF inválido\n"
            f"   Um CPF tem {TAMANHO_CPF} algarismos, e este tem {len(sobra)}.",
        )
    return Conferencia("".join(sobra), "")


def eh_sequencia_repetida(cpf: str) -> bool:
    """Diz se os algarismos do CPF são todos iguais.

    Args:
        cpf (str): O CPF limpo, com os 11 algarismos.

    Returns:
        bool: True para "00000000000" a "99999999999".
    """
    # O conjunto guarda cada algarismo uma vez só: com todos iguais, sobra um.
    return len(set(cpf)) == 1


def conferir_cpf(entrada: str) -> Conferencia:
    """Confere o CPF digitado: a limpeza, a sequência repetida e os dígitos.

    Args:
        entrada (str): O CPF digitado, com ou sem pontuação.

    Returns:
        Conferencia: Os 11 algarismos do CPF válido, ou a mensagem de recusa.
            A recusa pelos dígitos mostra o número digitado, não os certos.
    """
    limpo = limpar_cpf(entrada)
    if limpo.recusa:
        return limpo
    cpf = limpo.valor

    # As sequências repetidas passam na conta, mas são os números que se
    # digitam para pular o campo de um cadastro.
    if eh_sequencia_repetida(cpf):
        return Conferencia(
            "",
            f"❌ CPF inválido: {formatar_cpf(cpf)}\n"
            "   Sequência repetida: passa na conta, mas é recusada.",
        )

    base = [int(algarismo) for algarismo in cpf[:9]]
    primeira, segunda = calcular_digitos(base)
    if cpf[9:] != f"{primeira.digito}{segunda.digito}":
        return Conferencia(
            "",
            f"❌ CPF inválido: {formatar_cpf(cpf)}\n"
            "   Os dígitos verificadores não conferem.",
        )
    return Conferencia(cpf, "")


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------


def formatar_cpf(cpf: str) -> str:
    """Formata o CPF limpo como 000.000.000-00.

    Args:
        cpf (str): O CPF limpo, com os 11 algarismos.

    Returns:
        str: O CPF com os pontos e o hífen.
    """
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def descrever_regiao(cpf: str) -> str:
    """Descreve a região fiscal indicada pelo 9º algarismo do CPF.

    Args:
        cpf (str): O CPF limpo, com os 11 algarismos.

    Returns:
        str: A linha da região, como "Região fiscal 9: PR e SC".
    """
    # O 9º algarismo fica no índice 8: a contagem dos índices começa no 0.
    regiao = int(cpf[8])
    return f"Região fiscal {regiao}: {REGIOES_FISCAIS[regiao]}"


# ---------------------------------------------------------------------------
# Gerador
# ---------------------------------------------------------------------------


def gerar_cpf(sortear: Sorteador) -> str:
    """Sorteia uma base de 9 algarismos e a completa com os dois dígitos.

    Args:
        sortear (Sorteador): Função que recebe `n` e devolve um inteiro de 0 a
            `n - 1`, como o `random.randrange`.

    Returns:
        str: O CPF gerado, só com os 11 algarismos.
    """
    base = [sortear(10) for _ in range(9)]
    # Uma base com os 9 algarismos iguais daria uma sequência repetida, que a
    # validação recusa; sorteia a base inteira de novo (a chance é de 10 em
    # 1 bilhão).
    while len(set(base)) == 1:
        base = [sortear(10) for _ in range(9)]
    primeira, segunda = calcular_digitos(base)
    return "".join(str(algarismo) for algarismo in base) + (
        f"{primeira.digito}{segunda.digito}"
    )


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


def descrever_resultado(entrada: str) -> str:
    """Monta o resultado do modo simples.

    Args:
        entrada (str): O CPF digitado, com ou sem pontuação.

    Returns:
        str: O CPF válido formatado e a região fiscal, ou o motivo da recusa.
    """
    conferencia = conferir_cpf(entrada)
    if conferencia.recusa:
        return conferencia.recusa
    cpf = conferencia.valor
    return f"✅ CPF válido: {formatar_cpf(cpf)}\n{descrever_regiao(cpf)}"


def descrever_conta(conta: Conta, digitado: int, ordem: int) -> str:
    """Monta o bloco de um dígito verificador no modo didático.

    Os algarismos, os pesos e os produtos ficam em colunas de largura fixa, um
    embaixo do outro, para cada multiplicação se ler de cima para baixo.

    Args:
        conta (Conta): A conta do dígito, com todos os passos.
        digitado (int): O dígito que veio no CPF digitado, nessa posição.
        ordem (int): 1 para o 1º dígito verificador e 2 para o 2º.

    Returns:
        str: O título, as três linhas da conta, a soma com o resto e o dígito, e
            o dígito digitado com a marca de que confere ou não.
    """

    def linha(rotulo: str, numeros: list[int]) -> str:
        # `:<10` completa o rótulo com espaços até 10 caracteres, e `:>4` alinha
        # cada número à direita numa coluna de 4: até 81 (9 x 9) cabe com folga.
        return f"{rotulo:<10}" + "".join(f"{numero:>4}" for numero in numeros)

    conta_da_divisao = (
        f"Soma {conta.soma} ÷ 11 = {conta.soma // 11}, resto {conta.resto}"
        f" → dígito {conta.digito}"
    )
    if conta.resto == 10:
        conta_da_divisao += " (10 vale 0)"
    marca = "✅ confere" if digitado == conta.digito else "❌ não confere"
    return "\n".join(
        [
            f"{ordem}º dígito verificador",
            linha("Algarismos", conta.algarismos),
            linha("Pesos", conta.pesos),
            linha("Produtos", conta.produtos),
            conta_da_divisao,
            f"Digitado: {digitado} {marca}",
        ]
    )


def explicar_validacao(entrada: str) -> str:
    """Monta o resultado do modo didático: a conta dos dois dígitos e o resultado.

    A entrada recusada na limpeza (letra, quantidade errada, nada digitado) não
    tem conta para mostrar: vem só o motivo. A sequência repetida mostra a conta
    conferindo e, no resultado, a recusa.

    Args:
        entrada (str): O CPF digitado, com ou sem pontuação.

    Returns:
        str: Os dois blocos da conta e o resultado, ou só o motivo da recusa.
    """
    limpo = limpar_cpf(entrada)
    if limpo.recusa:
        return limpo.recusa
    cpf = limpo.valor

    base = [int(algarismo) for algarismo in cpf[:9]]
    primeira, segunda = calcular_digitos(base)
    blocos = [
        descrever_conta(primeira, int(cpf[9]), 1),
        descrever_conta(segunda, int(cpf[10]), 2),
        descrever_resultado(cpf),
    ]
    return "\n\n".join(blocos)


def descrever_gerado(cpf: str) -> str:
    """Monta o resultado do gerador: o número, a região fiscal e o aviso.

    Args:
        cpf (str): O CPF gerado, só com os 11 algarismos.

    Returns:
        str: O CPF formatado, a linha da região e o `AVISO_GERADO`.
    """
    return (
        f"🎲 CPF gerado: {formatar_cpf(cpf)}\n{descrever_regiao(cpf)}\n{AVISO_GERADO}"
    )


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def conferir_opcao(entrada: str) -> int | None:
    """Confere se a entrada é o número de uma opção do menu.

    Args:
        entrada (str): O que foi digitado no menu.

    Returns:
        int | None: O número da opção, de 1 a `len(OPCOES)`, ou None para
            qualquer outra coisa.
    """
    limpa = entrada.strip()
    # `isdecimal()` antes do `int()` dispensa o `try`. O `isdigit()` não serve:
    # ele aceita caracteres como "²", que o `int()` recusa com ValueError.
    if limpa.isdecimal() and 1 <= int(limpa) <= len(OPCOES):
        return int(limpa)
    return None


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
    print("======== VALIDADOR DE CPF ========")
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


def main(ler: Leitor = input, sortear: Sorteador = random.randrange) -> None:
    """Roda o programa: repete o menu até o usuário sair.

    O resultado de cada opção aparece acima do menu na volta seguinte e só vive
    na variável `resultado`: nenhum CPF fica guardado depois que a tela muda.
    Ctrl+C e o fim da entrada (Ctrl+D no Linux) encerram o programa em qualquer
    ponto com uma despedida, sem stack trace.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
        sortear (Sorteador, optional): Função que sorteia um inteiro de 0 a
            `n - 1`. Padrão: `random.randrange`.
    """
    resultado = ""
    try:
        while True:
            limpar_tela()
            exibir_tela(resultado)
            opcao = conferir_opcao(ler("Escolha uma opção: "))
            if opcao == 1:
                resultado = descrever_resultado(ler("Digite o CPF: "))
            elif opcao == 2:
                resultado = explicar_validacao(ler("Digite o CPF: "))
            elif opcao == 3:
                resultado = descrever_gerado(gerar_cpf(sortear))
            elif opcao == 4:
                break
            else:
                resultado = f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}."

        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída: as outras funções ficam só conferindo.
        print("\nValidador encerrado. Até a próxima! 👋")


if __name__ == "__main__":
    main()
