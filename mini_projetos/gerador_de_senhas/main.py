"""Gerador de senhas via terminal — projeto educacional de sorteio seguro e entropia.

Material de estudo para prática de três ideias: a diferença entre o `random`, que
a documentação do Python avisa que não serve para segurança, e o `secrets`, que
existe para isso; as constantes do módulo `string`, que montam os alfabetos da
senha; e a entropia, a medida, em bits, de quantas tentativas alguém precisa
fazer para adivinhar a senha. A frase-senha sorteia palavras da lista portuguesa
do BIP-39. Python puro (sem dependências externas), e nenhuma senha gerada sai
da tela.

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. TIPOS (Leitor, Escolhedor): Os parâmetros injetáveis.
2. CONSTANTES (TIPOS, PARECIDOS, TAMANHO_*, PALAVRAS_*, SEPARADOR,
   SEMENTE_DEMONSTRACAO, ARQUIVO_PALAVRAS, OPCOES).
3. SORTEIO (montar_grupos, tem_um_de_cada, gerar_senha, carregar_palavras,
   gerar_frase): O alfabeto, a senha e a frase-senha.
4. ENTROPIA (calcular_entropia, descrever_entropia): A conta e o texto dela.
5. PERGUNTAS (eh_numero, conferir_opcao, conferir_numero, conferir_sim_nao,
   perguntar_numero, perguntar_sim_nao): Cada resposta do teclado, conferida.
6. TEXTOS (descrever_gerada, explicar_random): O resultado de uma senha e a
   demonstração do `random`, devolvidos como texto.
7. OPÇÕES (opcao_senha_forte, opcao_senha_personalizada, opcao_frase_senha):
   O que cada opção do menu faz.
8. INTERFACE (limpar_tela, exibir_tela): A limpeza e o desenho do quadro.
9. LOOP PRINCIPAL (main): O menu em laço e a saída com Ctrl+C.
"""

from __future__ import annotations

import math
import os
import random
import secrets
import string
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos, os emojis e os símbolos
# da conta (× e ≈) com UnicodeEncodeError; reconfigurar para UTF-8 evita o crash
# em qualquer ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


# `main` recebe `ler` (que vale `input`) e `escolher` (que vale
# `secrets.choice`). Quem usa o programa não percebe diferença; os testes passam
# um teclado falso e um sorteio de semente fixa. O `type` dá um nome curto a um
# tipo comprido, para as assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]

# A assinatura do `secrets.choice` e do `choice` de um `random.Random`: recebe
# uma sequência (o alfabeto, que é um `str`, ou a lista de palavras) e devolve um
# item dela. As duas funções aceitam qualquer sequência; aqui o tipo fica só com
# a de textos, que é a que o programa usa.
type Escolhedor = Callable[[Sequence[str]], str]


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------


# Os tipos de caractere, na ordem das perguntas da senha personalizada. Juntos,
# são 94 caracteres: 26 + 26 + 10 + os 32 símbolos de `string.punctuation`.
TIPOS: dict[str, str] = {
    "Minúsculas": string.ascii_lowercase,
    "Maiúsculas": string.ascii_uppercase,
    "Números": string.digits,
    "Símbolos": string.punctuation,
}

# Caracteres que se confundem em muitas fontes: zero e o maiúsculo, o um, o L
# minúsculo, o i maiúsculo e a barra vertical.
PARECIDOS = "0O1lI|"

# Abaixo de 8 a senha fica fraca demais até com os quatro tipos; acima de 64,
# passa do limite de muitos sites.
TAMANHO_PADRAO = 16
TAMANHO_MINIMO = 8
TAMANHO_MAXIMO = 64

# Cada palavra da lista vale 11 bits (2048 = 2 elevado a 11): 7 palavras dão 77
# bits, e abaixo de 5 a frase fica mais fraca que a senha mínima de 8.
PALAVRAS_PADRAO = 7
PALAVRAS_MINIMO = 5
PALAVRAS_MAXIMO = 12

# O separador é sempre o mesmo, então não entra na conta da entropia.
SEPARADOR = "-"

# Fixa, para a demonstração do `random` sair igual a cada vez.
SEMENTE_DEMONSTRACAO = 2026

# Ao lado do `main.py`, de onde quer que o programa seja chamado.
ARQUIVO_PALAVRAS = Path(__file__).parent / "palavras.txt"

# O menu, numerado a partir de 1 na tela.
OPCOES = [
    "Gerar senha forte",
    "Gerar senha personalizada",
    "Gerar frase-senha",
    "Ver por que usar secrets e não random",
    "Sair",
]


# ---------------------------------------------------------------------------
# Sorteio
# ---------------------------------------------------------------------------


def montar_grupos(tipos: list[str], evitar_parecidos: bool) -> list[str]:
    """Monta os caracteres de cada tipo escolhido, um texto por tipo.

    A junção dos grupos é o alfabeto do sorteio, e cada grupo, separado, é o que
    a regra "um de cada tipo" confere.

    Args:
        tipos (list[str]): Os nomes dos tipos escolhidos, chaves de `TIPOS`.
        evitar_parecidos (bool): True para deixar de fora os `PARECIDOS`.

    Returns:
        list[str]: Os caracteres de cada tipo, na ordem de `tipos`.
    """
    grupos = []
    for tipo in tipos:
        caracteres = TIPOS[tipo]
        if evitar_parecidos:
            caracteres = "".join(c for c in caracteres if c not in PARECIDOS)
        grupos.append(caracteres)
    return grupos


def tem_um_de_cada(senha: str, grupos: list[str]) -> bool:
    """Diz se a senha tem pelo menos um caractere de cada grupo.

    Args:
        senha (str): A senha sorteada.
        grupos (list[str]): Os caracteres de cada tipo escolhido.

    Returns:
        bool: True se nenhum tipo ficou de fora.
    """
    # Lida de dentro para fora: para cada grupo, algum caractere da senha está
    # nele.
    return all(any(c in grupo for c in senha) for grupo in grupos)


def gerar_senha(tamanho: int, grupos: list[str], escolher: Escolhedor) -> str:
    """Sorteia uma senha com pelo menos um caractere de cada grupo.

    O tamanho precisa ser pelo menos o número de grupos; o mínimo do programa,
    8, cobre os quatro tipos.

    Args:
        tamanho (int): Quantos caracteres a senha tem.
        grupos (list[str]): Os caracteres de cada tipo escolhido.
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.

    Returns:
        str: A senha sorteada.
    """
    alfabeto = "".join(grupos)
    # Faltou um tipo? A senha inteira é sorteada de novo, em vez de forçar um
    # caractere do tipo que faltou numa posição: assim, toda senha que cumpre a
    # regra tem a mesma chance de sair, e nenhuma posição fica mais previsível.
    while True:
        senha = "".join(escolher(alfabeto) for _ in range(tamanho))
        if tem_um_de_cada(senha, grupos):
            return senha


def carregar_palavras(arquivo: Path) -> list[str]:
    """Lê a lista de palavras, uma por linha.

    Args:
        arquivo (Path): O arquivo da lista, como o `ARQUIVO_PALAVRAS`.

    Returns:
        list[str]: As palavras, na ordem do arquivo.
    """
    return arquivo.read_text(encoding="utf-8").split()


def gerar_frase(quantidade: int, palavras: list[str], escolher: Escolhedor) -> str:
    """Sorteia as palavras da frase-senha, com reposição, e as junta com hífen.

    Args:
        quantidade (int): Quantas palavras a frase tem.
        palavras (list[str]): A lista de onde as palavras saem.
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.

    Returns:
        str: As palavras sorteadas, separadas pelo `SEPARADOR`.
    """
    # Com reposição: a mesma palavra pode sair duas vezes, e é por isso que cada
    # uma vale os mesmos 11 bits.
    return SEPARADOR.join(escolher(palavras) for _ in range(quantidade))


# ---------------------------------------------------------------------------
# Entropia
# ---------------------------------------------------------------------------


def calcular_entropia(quantidade: int, tamanho_alfabeto: int) -> float:
    """Calcula a entropia, em bits, de um sorteio.

    Serve à senha (os caracteres sorteados entre os do alfabeto) e à frase-senha
    (as palavras sorteadas entre as da lista).

    Args:
        quantidade (int): Quantos itens são sorteados.
        tamanho_alfabeto (int): Entre quantos itens cada um é sorteado.

    Returns:
        float: A quantidade vezes o log2 do tamanho do alfabeto.
    """
    # O log2 diz quantos bits cada item vale: 2048 palavras são 2 elevado a 11,
    # então cada palavra vale 11 bits.
    return quantidade * math.log2(tamanho_alfabeto)


def descrever_entropia(quantidade: int, tamanho_alfabeto: int) -> str:
    """Monta as duas linhas da entropia: a conta e o que ela quer dizer.

    Args:
        quantidade (int): Quantos itens são sorteados.
        tamanho_alfabeto (int): Entre quantos itens cada um é sorteado.

    Returns:
        str: A conta, como "Entropia: 16 × log2(94) ≈ 104,9 bits", e a linha
            que explica o bit.
    """
    bits = calcular_entropia(quantidade, tamanho_alfabeto)
    if bits.is_integer():
        resultado = f"= {int(bits)}"
    else:
        # `:.1f` arredonda para uma casa decimal com ponto; o `replace` troca
        # pela vírgula, sem depender do `locale` do sistema.
        resultado = "≈ " + f"{bits:.1f}".replace(".", ",")
    return (
        f"Entropia: {quantidade} × log2({tamanho_alfabeto}) {resultado} bits\n"
        "Cada bit a mais dobra as tentativas de adivinhar."
    )


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------


def eh_numero(texto: str) -> bool:
    """Diz se o texto é um número inteiro escrito com os algarismos de 0 a 9.

    Args:
        texto (str): O texto, já sem os espaços das pontas.

    Returns:
        bool: True para "8" ou "64"; False para "", "12.5", "-1" ou "٣".
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


def conferir_numero(entrada: str, padrao: int, minimo: int, maximo: int) -> int | None:
    """Confere a resposta de uma pergunta de número, como o tamanho da senha.

    Args:
        entrada (str): O que foi digitado.
        padrao (int): O valor de quando nada é digitado (só Enter).
        minimo (int): O menor número aceito.
        maximo (int): O maior número aceito.

    Returns:
        int | None: O padrão, o número digitado, ou None para qualquer outra
            coisa.
    """
    limpa = entrada.strip()
    if not limpa:
        return padrao
    if eh_numero(limpa) and minimo <= int(limpa) <= maximo:
        return int(limpa)
    return None


def conferir_sim_nao(entrada: str, padrao: bool) -> bool | None:
    """Confere a resposta de uma pergunta de sim ou não.

    Args:
        entrada (str): O que foi digitado.
        padrao (bool): O valor de quando nada é digitado (só Enter).

    Returns:
        bool | None: True para "s" ou "sim", False para "n", "não" ou "nao",
            o padrão para nada digitado e None para qualquer outra coisa.
    """
    limpa = entrada.strip().lower()
    if not limpa:
        return padrao
    if limpa in ("s", "sim"):
        return True
    if limpa in ("n", "não", "nao"):
        return False
    return None


def perguntar_numero(
    ler: Leitor, pedido: str, padrao: int, minimo: int, maximo: int
) -> int:
    """Pergunta um número e repete a pergunta até a resposta ser aceita.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.
        pedido (str): O que se pergunta, com o artigo, como "o tamanho".
        padrao (int): O valor de quando nada é digitado (só Enter).
        minimo (int): O menor número aceito.
        maximo (int): O maior número aceito.

    Returns:
        int: O número aceito.
    """
    while True:
        entrada = ler(f"Digite {pedido}, de {minimo} a {maximo} [{padrao}]: ")
        numero = conferir_numero(entrada, padrao, minimo, maximo)
        if numero is not None:
            return numero
        # Sem limpar a tela: as respostas anteriores continuam à vista.
        print(f"⚠️ {pedido.capitalize()} vai de {minimo} a {maximo}.")


def perguntar_sim_nao(ler: Leitor, pedido: str, padrao: bool) -> bool:
    """Pergunta sim ou não e repete a pergunta até a resposta ser aceita.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.
        pedido (str): O que se pergunta, sem o ponto de interrogação.
        padrao (bool): O valor de quando nada é digitado (só Enter).

    Returns:
        bool: A resposta aceita.
    """
    # A letra maiúscula mostra o padrão, como nos instaladores de terminal.
    opcoes = "[S/n]" if padrao else "[s/N]"
    while True:
        resposta = conferir_sim_nao(ler(f"{pedido}? {opcoes}: "), padrao)
        if resposta is not None:
            return resposta
        print("⚠️ Responda s ou n.")


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


def descrever_gerada(
    titulo: str, gerada: str, quantidade: int, tamanho_alfabeto: int
) -> str:
    """Monta o resultado de uma senha ou de uma frase-senha.

    A senha fica sozinha na linha, sem emoji nem rótulo, para ser selecionada e
    copiada inteira.

    Args:
        titulo (str): O nome do que foi gerado, como "Senha forte".
        gerada (str): A senha ou a frase-senha.
        quantidade (int): Quantos caracteres ou palavras foram sorteados.
        tamanho_alfabeto (int): Entre quantos itens cada um foi sorteado.

    Returns:
        str: O título, a senha e as duas linhas da entropia.
    """
    return f"🔐 {titulo}:\n{gerada}\n{descrever_entropia(quantidade, tamanho_alfabeto)}"


def explicar_random(escolher: Escolhedor) -> str:
    """Monta a demonstração de por que o `random` não serve para senha.

    Gera duas senhas fortes com o `random`, cada uma com um gerador novo e a
    mesma semente, que saem iguais, e duas com `escolher`, que saem diferentes.
    É a mesma `gerar_senha` nos dois casos: só o sorteador muda.

    Args:
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.

    Returns:
        str: As quatro senhas, com um título antes de cada par, e a explicação.
    """
    grupos = montar_grupos(list(TIPOS), evitar_parecidos=False)
    # A forma dos tutoriais faz o mesmo com o gerador do próprio módulo:
    #     random.seed(SEMENTE_DEMONSTRACAO)
    #     random.choice(alfabeto)
    # Mas ela muda o sorteio de tudo o que usa o `random`; um `random.Random`
    # com a semente própria não mexe em mais nada.
    com_random = [
        gerar_senha(TAMANHO_PADRAO, grupos, random.Random(SEMENTE_DEMONSTRACAO).choice)
        for _ in range(2)
    ]
    com_escolher = [gerar_senha(TAMANHO_PADRAO, grupos, escolher) for _ in range(2)]
    return "\n".join(
        [
            f"🎲 random, duas vezes com a semente {SEMENTE_DEMONSTRACAO}:",
            *com_random,
            "🔐 secrets, duas vezes:",
            *com_escolher,
            "O random segue uma conta a partir da semente:",
            "quem descobre a semente, ou vê números seguidos",
            "dele, prevê os próximos. O secrets usa a fonte",
            "aleatória do sistema operacional, feita para",
            "segurança.",
        ]
    )


# ---------------------------------------------------------------------------
# Opções
# ---------------------------------------------------------------------------


def opcao_senha_forte(escolher: Escolhedor) -> str:
    """Gera a senha forte padrão, sem perguntar nada.

    Args:
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.

    Returns:
        str: O resultado, com a senha de `TAMANHO_PADRAO` e a entropia.
    """
    grupos = montar_grupos(list(TIPOS), evitar_parecidos=False)
    senha = gerar_senha(TAMANHO_PADRAO, grupos, escolher)
    return descrever_gerada("Senha forte", senha, TAMANHO_PADRAO, len("".join(grupos)))


def opcao_senha_personalizada(ler: Leitor, escolher: Escolhedor) -> str:
    """Pergunta o tamanho, os tipos e os parecidos, e gera a senha.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.

    Returns:
        str: O resultado, com a senha e a entropia, ou a recusa quando nenhum
            tipo de caractere foi escolhido.
    """
    tamanho = perguntar_numero(
        ler, "o tamanho", TAMANHO_PADRAO, TAMANHO_MINIMO, TAMANHO_MAXIMO
    )
    tipos = []
    for tipo in TIPOS:
        if perguntar_sim_nao(ler, tipo, padrao=True):
            tipos.append(tipo)
    # Cada caractere a menos tira um pouco da entropia: o padrão é não evitar.
    evitar = perguntar_sim_nao(ler, "Evitar " + " ".join(PARECIDOS), padrao=False)
    if not tipos:
        return "⚠️ Escolha pelo menos um tipo de caractere."
    grupos = montar_grupos(tipos, evitar)
    senha = gerar_senha(tamanho, grupos, escolher)
    return descrever_gerada("Senha personalizada", senha, tamanho, len("".join(grupos)))


def opcao_frase_senha(ler: Leitor, escolher: Escolhedor, palavras: list[str]) -> str:
    """Pergunta quantas palavras e gera a frase-senha.

    Args:
        ler (Leitor): Função que lê o teclado, como o `input`.
        escolher (Escolhedor): Função que devolve um item de uma sequência,
            como o `secrets.choice`.
        palavras (list[str]): A lista de onde as palavras saem.

    Returns:
        str: O resultado, com a frase-senha e a entropia.
    """
    quantidade = perguntar_numero(
        ler,
        "a quantidade de palavras",
        PALAVRAS_PADRAO,
        PALAVRAS_MINIMO,
        PALAVRAS_MAXIMO,
    )
    frase = gerar_frase(quantidade, palavras, escolher)
    return descrever_gerada("Frase-senha", frase, quantidade, len(palavras))


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
    print("======== GERADOR DE SENHAS ========")
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


def main(
    ler: Leitor = input,
    escolher: Escolhedor = secrets.choice,
    palavras: list[str] | None = None,
) -> None:
    """Roda o programa: repete o menu até o usuário sair.

    O resultado de cada opção aparece acima do menu na volta seguinte e só vive
    na variável `resultado`: nenhuma senha fica guardada depois que a tela muda.
    Ctrl+C e o fim da entrada (Ctrl+D no Linux) encerram o programa em qualquer
    ponto com uma despedida, sem stack trace.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
        escolher (Escolhedor, optional): Função que devolve um item de uma
            sequência. Padrão: `secrets.choice`.
        palavras (list[str] | None, optional): A lista da frase-senha. Padrão:
            a de `ARQUIVO_PALAVRAS`.
    """
    if palavras is None:
        palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    resultado = ""
    try:
        while True:
            limpar_tela()
            exibir_tela(resultado)
            opcao = conferir_opcao(ler("Escolha uma opção: "))
            if opcao == 1:
                resultado = opcao_senha_forte(escolher)
            elif opcao == 2:
                resultado = opcao_senha_personalizada(ler, escolher)
            elif opcao == 3:
                resultado = opcao_frase_senha(ler, escolher, palavras)
            elif opcao == 4:
                resultado = explicar_random(escolher)
            elif opcao == 5:
                break
            else:
                resultado = f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}."

        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída: as outras funções ficam só conferindo.
        print("\nGerador encerrado. Até a próxima! 👋")


if __name__ == "__main__":
    main()
