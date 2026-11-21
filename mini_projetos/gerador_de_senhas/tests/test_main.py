"""Testes para main.py.

Estratégia de isolamento: quase todas as funções do programa são puras, e os
testes as chamam com um valor e conferem o que elas devolvem. O sorteio entra
por parâmetro: os testes passam `random.Random(semente).choice`, de semente fixa,
ou um sorteador falso que devolve uma sequência escolhida, sem `monkeypatch` em
`random` nem em `secrets`. O teclado é um `LeitorFalso` (devolve as respostas na
ordem e guarda cada pedido), sem `monkeypatch` em `input`, e a saída se confere
com o `capsys`. O único `monkeypatch` da suíte troca `limpar_tela` por um no-op,
porque ela chama `os.system`, um efeito de terminal.

As senhas dos testes saem todas de um sorteio com semente fixa, nunca de uma
senha em uso.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import random
import secrets
import string
import unicodedata
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

import main as modulo_main
from main import (
    ARQUIVO_PALAVRAS,
    OPCOES,
    PARECIDOS,
    SEMENTE_DEMONSTRACAO,
    TIPOS,
    calcular_entropia,
    carregar_palavras,
    conferir_numero,
    conferir_opcao,
    conferir_sim_nao,
    descrever_entropia,
    descrever_gerada,
    exibir_tela,
    explicar_random,
    gerar_frase,
    gerar_senha,
    main,
    montar_grupos,
    opcao_frase_senha,
    opcao_senha_forte,
    opcao_senha_personalizada,
    perguntar_numero,
    perguntar_sim_nao,
    tem_um_de_cada,
)

# A largura máxima de cada linha do programa, para o quadro caber num terminal
# estreito. Só a senha e a frase-senha podem passar dela.
LARGURA_MAXIMA = 54

# O SHA-256 do `bip-0039/portuguese.txt` do repositório `bitcoin/bips`, no commit
# d353c54154bac64a88eb18cf2d47d15ead083de4.
SHA256_PALAVRAS = "2685e9c194c82ae67e10ba59d9ea5345a23dc093e92276fc5361f6667d79cd3f"

# Uma lista curta para os testes de `main()` e da frase-senha.
PALAVRAS_TESTE = ["abacate", "baleia", "caderno", "dedo", "escada", "fogo"]

# Os nomes dos quatro tipos, na ordem das perguntas.
TODOS_OS_TIPOS = list(TIPOS)


class SorteadorFalso:
    """Simula o sorteio: devolve os itens na ordem e guarda cada sequência recebida.

    Attributes:
        pedidos (list[Sequence[str]]): A sequência de cada sorteio pedido, na
            ordem.
    """

    def __init__(self, *itens: str) -> None:
        """Guarda os itens a devolver.

        Args:
            *itens (str): Itens a devolver, um por chamada.
        """
        self._itens: Iterator[str] = iter(itens)
        self.pedidos: list[Sequence[str]] = []

    def __call__(self, sequencia: Sequence[str]) -> str:
        """Registra o pedido e devolve o próximo item.

        Args:
            sequencia (Sequence[str]): De onde o item seria sorteado.

        Returns:
            str: O próximo item da sequência guardada.
        """
        self.pedidos.append(sequencia)
        return next(self._itens)


class LeitorFalso:
    """Simula o teclado: devolve as respostas na ordem e guarda cada pedido.

    Attributes:
        pedidos (list[str]): Texto de cada pedido recebido, na ordem.
    """

    def __init__(self, *respostas: str) -> None:
        """Guarda as respostas a devolver.

        Args:
            *respostas (str): Respostas a devolver, uma por chamada.
        """
        self._respostas: Iterator[str] = iter(respostas)
        self.pedidos: list[str] = []

    def __call__(self, pedido: str) -> str:
        """Registra o pedido e devolve a próxima resposta.

        Args:
            pedido (str): Texto que o programa mostraria antes de ler o teclado.

        Returns:
            str: A próxima resposta da sequência.
        """
        self.pedidos.append(pedido)
        return next(self._respostas)


class LeitorQueInterrompe(LeitorFalso):
    """Simula o teclado e, acabadas as respostas, uma interrupção.

    Attributes:
        pedidos (list[str]): Texto de cada pedido recebido, na ordem.
    """

    def __init__(self, excecao: type[BaseException], *respostas: str) -> None:
        """Guarda a exceção e as respostas a devolver antes dela.

        Args:
            excecao (type[BaseException]): `KeyboardInterrupt` (Ctrl+C) ou
                `EOFError` (fim da entrada).
            *respostas (str): Respostas a devolver antes da interrupção.
        """
        super().__init__(*respostas)
        self._excecao = excecao

    def __call__(self, pedido: str) -> str:
        """Devolve a próxima resposta ou, sem nenhuma, lança a exceção.

        Args:
            pedido (str): Texto que o programa mostraria antes de ler o teclado.

        Returns:
            str: A próxima resposta da sequência.

        Raises:
            BaseException: A exceção guardada, quando as respostas acabam.
        """
        try:
            return super().__call__(pedido)
        except StopIteration:
            raise self._excecao from None


def colunas(linha: str) -> int:
    """Conta quantas colunas do terminal uma linha ocupa.

    Os caracteres largos (como 🔐 e 🎲) ocupam duas colunas, e o seletor de
    emoji (U+FE0F, o que faz o ⚠ virar ⚠️) alarga o caractere anterior para duas.

    Args:
        linha (str): Uma linha de texto, sem "\\n".

    Returns:
        int: A largura da linha em colunas.
    """
    total = 0
    for caractere in linha:
        if caractere == "️":
            total += 1
        elif unicodedata.east_asian_width(caractere) in ("W", "F"):
            total += 2
        elif not unicodedata.combining(caractere):
            total += 1
    return total


def gerada_do_resultado(resultado: str) -> str:
    """Recorta a senha ou a frase-senha do texto de `descrever_gerada`.

    Args:
        resultado (str): O texto de uma das opções que geram.

    Returns:
        str: A linha logo abaixo do título.
    """
    return resultado.splitlines()[1]


@pytest.fixture(autouse=True)
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte.

    `limpar_tela` chama `os.system`, que limparia o terminal de quem roda os testes.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


# ---------------------------------------------------------------------------
# montar_grupos e tem_um_de_cada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tipo", "caracteres"),
    [
        ("Minúsculas", string.ascii_lowercase),
        ("Maiúsculas", string.ascii_uppercase),
        ("Números", string.digits),
        ("Símbolos", string.punctuation),
    ],
)
def test_montar_grupos_de_cada_tipo(tipo: str, caracteres: str) -> None:
    assert montar_grupos([tipo], evitar_parecidos=False) == [caracteres]


def test_montar_grupos_com_os_quatro_tipos_soma_94() -> None:
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    assert len("".join(grupos)) == 94
    assert len(set("".join(grupos))) == 94


def test_montar_grupos_sem_os_parecidos_soma_88() -> None:
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=True)
    assert [len(grupo) for grupo in grupos] == [25, 24, 8, 31]
    assert not set("".join(grupos)) & set(PARECIDOS)


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("aB3#", True),
        ("#3Ba", True),
        ("abcD5678", False),
        ("ABC#123!", False),
        ("abcdefgh", False),
    ],
)
def test_tem_um_de_cada_com_os_quatro_tipos(senha: str, esperado: bool) -> None:
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    assert tem_um_de_cada(senha, grupos) is esperado


def test_tem_um_de_cada_so_confere_os_tipos_escolhidos() -> None:
    grupos = montar_grupos(["Números"], evitar_parecidos=False)
    assert tem_um_de_cada("12345678", grupos)


# ---------------------------------------------------------------------------
# gerar_senha
# ---------------------------------------------------------------------------


def test_gerar_senha_cumpre_a_regra_sem_reservar_posicao() -> None:
    # Com o tamanho mínimo, a regra descarta muitas senhas: é o caso que mais
    # exercita o laço. O primeiro caractere de cada tipo mostra que nenhuma
    # posição é reservada.
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    alfabeto = set("".join(grupos))
    escolher = random.Random(2026).choice
    primeiros: set[int] = set()
    for _ in range(2000):
        senha = gerar_senha(8, grupos, escolher)
        assert len(senha) == 8
        assert set(senha) <= alfabeto
        assert tem_um_de_cada(senha, grupos)
        primeiros.update(i for i, grupo in enumerate(grupos) if senha[0] in grupo)
    assert primeiros == {0, 1, 2, 3}


def test_gerar_senha_sorteia_de_novo_a_senha_sem_um_tipo() -> None:
    grupos = montar_grupos(["Minúsculas", "Números"], evitar_parecidos=False)
    # A primeira senha sai só de letras; a segunda tem um número.
    sorteador = SorteadorFalso(*"abcdefgh", *"abcdefg1")
    assert gerar_senha(8, grupos, sorteador) == "abcdefg1"
    assert len(sorteador.pedidos) == 16
    assert all(pedido == "".join(grupos) for pedido in sorteador.pedidos)


def test_gerar_senha_sem_os_parecidos_nao_usa_nenhum() -> None:
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=True)
    escolher = random.Random(2026).choice
    for _ in range(500):
        assert not set(gerar_senha(16, grupos, escolher)) & set(PARECIDOS)


# ---------------------------------------------------------------------------
# carregar_palavras e gerar_frase
# ---------------------------------------------------------------------------


def test_carregar_palavras_le_a_lista_do_bip39() -> None:
    palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    assert len(palavras) == 2048
    assert len(set(palavras)) == 2048
    assert all(palavra.isascii() and palavra.isalpha() for palavra in palavras)
    assert all(palavra == palavra.lower() for palavra in palavras)


def test_palavras_txt_e_a_copia_exata_da_lista() -> None:
    conteudo = ARQUIVO_PALAVRAS.read_bytes()
    assert hashlib.sha256(conteudo).hexdigest() == SHA256_PALAVRAS


@pytest.mark.parametrize("quantidade", [5, 7, 12])
def test_gerar_frase_com_a_quantidade_e_o_hifen(quantidade: int) -> None:
    frase = gerar_frase(quantidade, PALAVRAS_TESTE, random.Random(2026).choice)
    palavras = frase.split("-")
    assert len(palavras) == quantidade
    assert all(palavra in PALAVRAS_TESTE for palavra in palavras)


def test_gerar_frase_sorteia_da_lista_com_reposicao() -> None:
    sorteador = SorteadorFalso("dedo", "fogo", "dedo", "baleia", "dedo")
    assert gerar_frase(5, PALAVRAS_TESTE, sorteador) == "dedo-fogo-dedo-baleia-dedo"
    assert all(pedido is PALAVRAS_TESTE for pedido in sorteador.pedidos)


# ---------------------------------------------------------------------------
# calcular_entropia e descrever_entropia
# ---------------------------------------------------------------------------


def test_calcular_entropia_da_frase_padrao_da_77() -> None:
    assert calcular_entropia(7, 2048) == 77


@pytest.mark.parametrize(
    ("quantidade", "alfabeto", "conta"),
    [
        (16, 94, "16 × log2(94) ≈ 104,9 bits"),
        (16, 10, "16 × log2(10) ≈ 53,2 bits"),
        (16, 88, "16 × log2(88) ≈ 103,4 bits"),
        (16, 25, "16 × log2(25) ≈ 74,3 bits"),
        (16, 24, "16 × log2(24) ≈ 73,4 bits"),
        (16, 8, "16 × log2(8) = 48 bits"),
        (16, 31, "16 × log2(31) ≈ 79,3 bits"),
        (7, 2048, "7 × log2(2048) = 77 bits"),
        (64, 94, "64 × log2(94) ≈ 419,5 bits"),
    ],
)
def test_descrever_entropia_com_a_conta(
    quantidade: int, alfabeto: int, conta: str
) -> None:
    assert descrever_entropia(quantidade, alfabeto) == (
        f"Entropia: {conta}\nCada bit a mais dobra as tentativas de adivinhar."
    )


# ---------------------------------------------------------------------------
# conferir_opcao, conferir_numero e conferir_sim_nao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("opcao", range(1, len(OPCOES) + 1))
def test_conferir_opcao_aceita_cada_opcao(opcao: int) -> None:
    assert conferir_opcao(f" {opcao} ") == opcao


@pytest.mark.parametrize("entrada", ["", "  ", "0", "6", "9", "abc", "٣", "²", "1.0"])
def test_conferir_opcao_recusa_o_resto(entrada: str) -> None:
    assert conferir_opcao(entrada) is None


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("", 16), ("  ", 16), ("8", 8), (" 20 ", 20), ("64", 64)],
)
def test_conferir_numero_aceita_o_padrao_e_os_limites_do_tamanho(
    entrada: str, esperado: int
) -> None:
    assert conferir_numero(entrada, 16, 8, 64) == esperado


@pytest.mark.parametrize("entrada", ["7", "65", "abc", "12.5", "-8", "٣٣"])
def test_conferir_numero_recusa_fora_do_tamanho(entrada: str) -> None:
    assert conferir_numero(entrada, 16, 8, 64) is None


@pytest.mark.parametrize(("entrada", "esperado"), [("", 7), ("5", 5), ("12", 12)])
def test_conferir_numero_aceita_o_padrao_e_os_limites_das_palavras(
    entrada: str, esperado: int
) -> None:
    assert conferir_numero(entrada, 7, 5, 12) == esperado


@pytest.mark.parametrize("entrada", ["4", "13", "abc"])
def test_conferir_numero_recusa_fora_das_palavras(entrada: str) -> None:
    assert conferir_numero(entrada, 7, 5, 12) is None


@pytest.mark.parametrize("padrao", [True, False])
def test_conferir_sim_nao_enter_aceita_o_padrao(padrao: bool) -> None:
    assert conferir_sim_nao("", padrao) is padrao
    assert conferir_sim_nao("  ", padrao) is padrao


@pytest.mark.parametrize("entrada", ["s", "S", "sim", "Sim", "SIM", " s "])
def test_conferir_sim_nao_aceita_sim(entrada: str) -> None:
    assert conferir_sim_nao(entrada, padrao=False) is True


@pytest.mark.parametrize("entrada", ["n", "N", "não", "NÃO", "nao", "Nao", " n "])
def test_conferir_sim_nao_aceita_nao(entrada: str) -> None:
    assert conferir_sim_nao(entrada, padrao=True) is False


@pytest.mark.parametrize("entrada", ["talvez", "y", "1", "si", "nã"])
def test_conferir_sim_nao_recusa_o_resto(entrada: str) -> None:
    assert conferir_sim_nao(entrada, padrao=True) is None


# ---------------------------------------------------------------------------
# perguntar_numero e perguntar_sim_nao
# ---------------------------------------------------------------------------


def test_perguntar_numero_repete_a_pergunta_ate_aceitar(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("7", "12.5", "20")
    assert perguntar_numero(leitor, "o tamanho", 16, 8, 64) == 20
    assert leitor.pedidos == ["Digite o tamanho, de 8 a 64 [16]: "] * 3
    assert capsys.readouterr().out == "⚠️ O tamanho vai de 8 a 64.\n" * 2


def test_perguntar_numero_da_quantidade_de_palavras(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("13", "")
    assert perguntar_numero(leitor, "a quantidade de palavras", 7, 5, 12) == 7
    assert leitor.pedidos[0] == "Digite a quantidade de palavras, de 5 a 12 [7]: "
    assert capsys.readouterr().out == "⚠️ A quantidade de palavras vai de 5 a 12.\n"


@pytest.mark.parametrize(("padrao", "opcoes"), [(True, "[S/n]"), (False, "[s/N]")])
def test_perguntar_sim_nao_mostra_o_padrao(padrao: bool, opcoes: str) -> None:
    leitor = LeitorFalso("")
    assert perguntar_sim_nao(leitor, "Símbolos", padrao) is padrao
    assert leitor.pedidos == [f"Símbolos? {opcoes}: "]


def test_perguntar_sim_nao_repete_a_pergunta_ate_aceitar(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("talvez", "n")
    assert perguntar_sim_nao(leitor, "Símbolos", padrao=True) is False
    assert leitor.pedidos == ["Símbolos? [S/n]: "] * 2
    assert capsys.readouterr().out == "⚠️ Responda s ou n.\n"


# ---------------------------------------------------------------------------
# descrever_gerada e explicar_random
# ---------------------------------------------------------------------------


def test_descrever_gerada_com_a_senha_sozinha_na_linha() -> None:
    assert descrever_gerada("Senha forte", "aB3#aB3#aB3#aB3#", 16, 94) == (
        "🔐 Senha forte:\n"
        "aB3#aB3#aB3#aB3#\n"
        "Entropia: 16 × log2(94) ≈ 104,9 bits\n"
        "Cada bit a mais dobra as tentativas de adivinhar."
    )


def test_explicar_random_repete_o_random_e_nao_o_escolher() -> None:
    linhas = explicar_random(random.Random(1).choice).splitlines()
    assert linhas[0] == f"🎲 random, duas vezes com a semente {SEMENTE_DEMONSTRACAO}:"
    assert linhas[1] == linhas[2]
    assert linhas[3] == "🔐 secrets, duas vezes:"
    assert linhas[4] != linhas[5]
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    for senha in linhas[1:3] + linhas[4:6]:
        assert len(senha) == 16
        assert tem_um_de_cada(senha, grupos)


def test_explicar_random_usa_a_semente_fixa() -> None:
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    esperada = gerar_senha(16, grupos, random.Random(SEMENTE_DEMONSTRACAO).choice)
    assert explicar_random(random.Random(1).choice).splitlines()[1] == esperada


def test_explicar_random_traz_a_explicacao() -> None:
    texto = explicar_random(random.Random(1).choice)
    assert "O random segue uma conta a partir da semente:" in texto
    assert "prevê os próximos" in texto
    assert texto.endswith("aleatória do sistema operacional, feita para\nsegurança.")


# ---------------------------------------------------------------------------
# Opções
# ---------------------------------------------------------------------------


def test_opcao_senha_forte_com_16_caracteres_e_os_quatro_tipos() -> None:
    resultado = opcao_senha_forte(random.Random(2026).choice)
    senha = gerada_do_resultado(resultado)
    grupos = montar_grupos(TODOS_OS_TIPOS, evitar_parecidos=False)
    assert resultado.startswith("🔐 Senha forte:\n")
    assert len(senha) == 16
    assert tem_um_de_cada(senha, grupos)
    assert "Entropia: 16 × log2(94) ≈ 104,9 bits" in resultado


def test_opcao_senha_personalizada_com_os_tipos_escolhidos() -> None:
    # Tamanho 20, minúsculas (Enter), sem maiúsculas, com números, sem símbolos
    # e evitando os parecidos.
    leitor = LeitorFalso("20", "", "n", "s", "n", "s")
    resultado = opcao_senha_personalizada(leitor, random.Random(2026).choice)
    senha = gerada_do_resultado(resultado)
    grupos = montar_grupos(["Minúsculas", "Números"], evitar_parecidos=True)
    assert resultado.startswith("🔐 Senha personalizada:\n")
    assert len(senha) == 20
    assert set(senha) <= set("".join(grupos))
    assert tem_um_de_cada(senha, grupos)
    assert "Entropia: 20 × log2(33) ≈ 100,9 bits" in resultado
    assert leitor.pedidos == [
        "Digite o tamanho, de 8 a 64 [16]: ",
        "Minúsculas? [S/n]: ",
        "Maiúsculas? [S/n]: ",
        "Números? [S/n]: ",
        "Símbolos? [S/n]: ",
        "Evitar 0 O 1 l I |? [s/N]: ",
    ]


def test_opcao_senha_personalizada_com_os_padroes_e_a_senha_forte() -> None:
    leitor = LeitorFalso("", "", "", "", "", "")
    resultado = opcao_senha_personalizada(leitor, random.Random(2026).choice)
    assert len(gerada_do_resultado(resultado)) == 16
    assert "Entropia: 16 × log2(94) ≈ 104,9 bits" in resultado


def test_opcao_senha_personalizada_recusa_sem_nenhum_tipo() -> None:
    sorteador = SorteadorFalso()
    leitor = LeitorFalso("", "n", "n", "n", "n", "")
    resultado = opcao_senha_personalizada(leitor, sorteador)
    assert resultado == "⚠️ Escolha pelo menos um tipo de caractere."
    assert sorteador.pedidos == []


def test_opcao_senha_personalizada_nao_perde_as_respostas_anteriores(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Só números, com uma resposta inválida na última pergunta de tipo.
    leitor = LeitorFalso("65", "10", "n", "n", "s", "talvez", "n", "")
    resultado = opcao_senha_personalizada(leitor, random.Random(2026).choice)
    senha = gerada_do_resultado(resultado)
    assert len(senha) == 10
    assert senha.isdecimal()
    assert capsys.readouterr().out == (
        "⚠️ O tamanho vai de 8 a 64.\n⚠️ Responda s ou n.\n"
    )


def test_opcao_frase_senha_com_a_quantidade_pedida() -> None:
    leitor = LeitorFalso("5")
    resultado = opcao_frase_senha(leitor, random.Random(2026).choice, PALAVRAS_TESTE)
    palavras = gerada_do_resultado(resultado).split("-")
    assert resultado.startswith("🔐 Frase-senha:\n")
    assert len(palavras) == 5
    assert all(palavra in PALAVRAS_TESTE for palavra in palavras)
    assert "Entropia: 5 × log2(6) ≈ 12,9 bits" in resultado


def test_opcao_frase_senha_padrao_com_a_lista_inteira() -> None:
    palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    resultado = opcao_frase_senha(LeitorFalso(""), random.Random(2026).choice, palavras)
    assert len(gerada_do_resultado(resultado).split("-")) == 7
    assert "Entropia: 7 × log2(2048) = 77 bits" in resultado


# ---------------------------------------------------------------------------
# Largura das linhas
# ---------------------------------------------------------------------------


def linhas_sem_as_geradas(textos: list[str], geradas: set[str]) -> list[str]:
    """Junta as linhas dos textos, menos as das senhas e frases-senha.

    Args:
        textos (list[str]): Os textos que o programa mostra.
        geradas (set[str]): As senhas e frases-senha, que podem passar da
            largura.

    Returns:
        list[str]: As outras linhas, que precisam caber na largura.
    """
    return [
        linha
        for texto in textos
        for linha in texto.splitlines()
        if linha not in geradas
    ]


def test_nenhuma_linha_dos_textos_passa_da_largura_maxima(
    capsys: pytest.CaptureFixture[str],
) -> None:
    escolher = random.Random(2026).choice
    palavras = carregar_palavras(ARQUIVO_PALAVRAS)
    textos = [
        opcao_senha_forte(escolher),
        opcao_senha_personalizada(
            LeitorFalso("7", "64", "x", "", "", "", "x", "s", ""), escolher
        ),
        opcao_senha_personalizada(LeitorFalso("", "n", "n", "n", "n", ""), escolher),
        opcao_frase_senha(LeitorFalso("13", "12"), escolher, palavras),
        explicar_random(escolher),
    ]
    # As senhas e as frases ficam na 2ª linha; as da demonstração, nas linhas
    # abaixo de cada título.
    geradas = {texto.splitlines()[1] for texto in textos[:4] if "\n" in texto}
    demonstracao = textos[4].splitlines()
    geradas.update(demonstracao[1:3] + demonstracao[4:6])
    # As mensagens de recusa das perguntas também aparecem na tela.
    textos.append(capsys.readouterr().out)
    for linha in linhas_sem_as_geradas(textos, geradas):
        assert colunas(linha) <= LARGURA_MAXIMA, linha


def test_nenhum_pedido_das_perguntas_passa_da_largura_maxima() -> None:
    escolher = random.Random(2026).choice
    leitor = LeitorFalso("", "", "", "", "", "", "")
    opcao_senha_personalizada(leitor, escolher)
    opcao_frase_senha(leitor, escolher, PALAVRAS_TESTE)
    for pedido in leitor.pedidos + ["Escolha uma opção: "]:
        assert colunas(pedido) <= LARGURA_MAXIMA, pedido


def test_nenhuma_linha_do_quadro_passa_da_largura_maxima(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_tela(f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}.")
    for linha in capsys.readouterr().out.splitlines():
        assert colunas(linha) <= LARGURA_MAXIMA, linha


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def ultima_tela(saida: str) -> str:
    """Recorta a saída a partir do último título, como o terminal limpo mostraria.

    Args:
        saida (str): Tudo o que `main()` imprimiu.

    Returns:
        str: O último quadro e o que veio depois dele.
    """
    return saida[saida.rindex("GERADOR DE SENHAS") :]


def test_main_mostra_titulo_resultado_e_menu_nessa_ordem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("1", "5")
    main(leitor, random.Random(2026).choice, PALAVRAS_TESTE)

    tela = ultima_tela(capsys.readouterr().out)
    assert tela.startswith("GERADOR DE SENHAS ========\n\n🔐 Senha forte:\n")
    assert tela.index("Cada bit a mais") < tela.index("1 : Gerar senha forte")
    assert tela.index("1 : Gerar senha forte") < tela.index("5 : Sair")
    assert leitor.pedidos == ["Escolha uma opção: "] * 2


def test_main_primeira_tela_sem_resultado(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("5"), random.Random(2026).choice, PALAVRAS_TESTE)
    saida = capsys.readouterr().out
    assert saida.startswith(
        "======== GERADOR DE SENHAS ========\n\n"
        "1 : Gerar senha forte\n"
        "2 : Gerar senha personalizada\n"
        "3 : Gerar frase-senha\n"
        "4 : Ver por que usar secrets e não random\n"
        "5 : Sair\n\n"
    )


def test_main_gera_a_senha_forte(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("1", "5"), random.Random(2026).choice, PALAVRAS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert opcao_senha_forte(random.Random(2026).choice) in tela


def test_main_gera_a_senha_personalizada(capsys: pytest.CaptureFixture[str]) -> None:
    respostas = ("12", "n", "n", "s", "n", "")
    main(LeitorFalso("2", *respostas, "5"), random.Random(2026).choice)
    tela = ultima_tela(capsys.readouterr().out)
    esperado = opcao_senha_personalizada(
        LeitorFalso(*respostas), random.Random(2026).choice
    )
    assert esperado in tela


def test_main_gera_a_frase_senha_com_a_lista_do_arquivo(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Sem a lista por parâmetro, `main` lê o `palavras.txt`.
    main(LeitorFalso("3", "5", "5"), random.Random(2026).choice)
    tela = ultima_tela(capsys.readouterr().out)
    frase = tela.splitlines()[3]
    lista = carregar_palavras(ARQUIVO_PALAVRAS)
    assert all(palavra in lista for palavra in frase.split("-"))
    assert "Entropia: 5 × log2(2048) = 55 bits" in tela


def test_main_mostra_a_demonstracao(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("4", "5"), random.Random(1).choice, PALAVRAS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert explicar_random(random.Random(1).choice) in tela


@pytest.mark.parametrize("entrada", ["", "0", "6", "9", "abc", "٣"])
def test_main_recusa_a_opcao_invalida(
    capsys: pytest.CaptureFixture[str], entrada: str
) -> None:
    main(LeitorFalso(entrada, "5"), random.Random(2026).choice, PALAVRAS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert "❌ Opção inválida. Digite um número de 1 a 5." in tela


def test_main_sai_pelo_menu_com_despedida(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("5"), random.Random(2026).choice, PALAVRAS_TESTE)
    assert capsys.readouterr().out.endswith("Até a próxima! 👋\n")


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
@pytest.mark.parametrize(
    "respostas", [(), ("1",), ("2",), ("2", "20", "s"), ("3",), ("3", "abc")]
)
def test_main_sai_sem_stack_trace(
    capsys: pytest.CaptureFixture[str],
    excecao: type[BaseException],
    respostas: tuple[str, ...],
) -> None:
    # Interrompe no menu ou no meio das perguntas: `main` volta sem deixar a
    # exceção escapar.
    leitor = LeitorQueInterrompe(excecao, *respostas)
    main(leitor, random.Random(2026).choice, PALAVRAS_TESTE)
    saida = capsys.readouterr().out
    assert saida.endswith("\nGerador encerrado. Até a próxima! 👋\n")


def test_main_sorteia_com_o_secrets_por_padrao() -> None:
    parametros = inspect.signature(main).parameters
    assert parametros["escolher"].default is secrets.choice
    assert parametros["ler"].default is input


# ---------------------------------------------------------------------------
# A senha não sai da tela
# ---------------------------------------------------------------------------


def test_main_py_so_importa_os_modulos_previstos_e_nao_grava_arquivo() -> None:
    arvore = ast.parse(Path(modulo_main.__file__).read_text(encoding="utf-8"))
    modulos: set[str] = set()
    chamadas: set[str] = set()
    atributos: set[tuple[str, str]] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            modulos.update(apelido.name for apelido in no.names)
        elif isinstance(no, ast.ImportFrom):
            modulos.add(no.module or "")
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            chamadas.add(no.func.id)
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute):
            chamadas.add(no.func.attr)
        elif isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name):
            atributos.add((no.value.id, no.attr))

    previstos = {
        "__future__",
        "collections.abc",
        "math",
        "os",
        "pathlib",
        "random",
        "secrets",
        "string",
        "sys",
    }
    assert modulos <= previstos
    assert not chamadas & {"open", "write_text", "write_bytes"}
    assert ("sys", "argv") not in atributos
