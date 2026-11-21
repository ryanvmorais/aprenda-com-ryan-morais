"""Testes para main.py.

Estratégia de isolamento: quase todas as funções do programa são puras, e os
testes as chamam com um valor e conferem o que elas devolvem, inclusive os
textos do resultado, que são devolvidos e não impressos. A leitura do teclado
entra por parâmetro: o `LeitorFalso` devolve as respostas na ordem e guarda cada
pedido, sem `monkeypatch` em `input`, e a saída de `main()` se confere com o
`capsys`. O único `monkeypatch` da suíte troca `limpar_tela` por uma função que
só conta as chamadas, porque ela chama `os.system`, um efeito de terminal.
"""

from __future__ import annotations

import ast
import inspect
import unicodedata
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

import main as modulo_main
from main import (
    ALFABETO,
    CHAVES,
    FREQUENCIAS,
    LARGURA,
    MINIMO_LETRAS,
    OPCOES,
    Leitor,
    aviso_acentos,
    cifrar,
    conferir_chave,
    conferir_opcao,
    contar_letras,
    cortar,
    decifrar,
    descrever_cifra,
    descrever_decifra,
    descrever_forca_bruta,
    descrever_frequencia,
    deslocar_letra,
    exibir_tela,
    forca_bruta,
    main,
    montar_tabela,
    opcao_cifrar,
    opcao_decifrar,
    opcao_forca_bruta,
    opcao_frequencia,
    ordenar_chaves,
    pontuar,
    remover_acentos,
    tem_letras,
)

# Frases do português atual, com 30 letras ou mais, para a frequência achar a
# chave certa (a medição do design usou um texto de 1899).
FRASES = [
    "A cifra de César cai em segundos com a força bruta.",
    "Quem tem a chave decifra; quem não tem, conta as letras.",
    "O computador testa as vinte e cinco chaves num piscar de olhos.",
    "Nenhuma mensagem importante deve ser protegida com esta cifra.",
]

# A largura máxima de cada linha do programa, para o quadro caber num terminal
# estreito.
LARGURA_MAXIMA = 54

# Os pedidos, iguais aos do `main.py`.
PEDIDO_OPCAO = "Escolha uma opção: "
PEDIDO_TEXTO = "Digite o texto: "
PEDIDO_CHAVE = "Digite a chave (de 1 a 25): "

# O exemplo do design: 43 letras, cifradas com a chave 7.
CIFRADO_7 = "Xblt alt h johcl kljpmyh; xblt uhv alt, jvuah hz slayhz."

# As despedidas, pelo menu e pelo Ctrl+C.
DESPEDIDA = "Até a próxima! 👋\n"
ENCERRADA = "\nCifra de César encerrada. Até a próxima! 👋\n"


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


@pytest.fixture(autouse=True)
def limpezas(monkeypatch: pytest.MonkeyPatch) -> list[None]:
    """Troca `limpar_tela` por uma função que só conta as chamadas.

    Args:
        monkeypatch (pytest.MonkeyPatch): A fixture do pytest.

    Returns:
        list[None]: Um item por limpeza de tela pedida.
    """
    chamadas: list[None] = []
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: chamadas.append(None))
    return chamadas


def colunas(linha: str) -> int:
    """Conta quantas colunas do terminal uma linha ocupa.

    Os caracteres largos (como 🔒 e 💡) ocupam duas colunas.

    Args:
        linha (str): Uma linha de texto, sem "\\n".

    Returns:
        int: A largura da linha em colunas.
    """
    return sum(
        2 if unicodedata.east_asian_width(caractere) in ("W", "F") else 1
        for caractere in linha
    )


# ---------------------------------------------------------------------------
# Cifra
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("acentuada", "base"),
    [
        ("á", "a"),
        ("à", "a"),
        ("â", "a"),
        ("ã", "a"),
        ("é", "e"),
        ("ê", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ô", "o"),
        ("õ", "o"),
        ("ú", "u"),
        ("ü", "u"),
        ("ç", "c"),
        ("Á", "A"),
        ("Ã", "A"),
        ("É", "E"),
        ("Ô", "O"),
        ("Ç", "C"),
    ],
)
def test_remover_acentos_troca_pela_letra_base(acentuada: str, base: str) -> None:
    assert remover_acentos(acentuada) == base


@pytest.mark.parametrize("texto", [" ", "2026", "!?.,;:", "🔒", "Sem acento"])
def test_remover_acentos_deixa_o_resto_sem_mudanca(texto: str) -> None:
    assert remover_acentos(texto) == texto


@pytest.mark.parametrize(
    ("letra", "chave", "deslocada"),
    [
        ("a", 3, "d"),
        ("A", 3, "D"),
        ("z", 1, "a"),
        ("Z", 3, "C"),
        ("a", -1, "z"),
        ("a", -3, "x"),
        ("C", -3, "Z"),
    ],
)
def test_deslocar_letra_volta_ao_comeco_e_ao_fim(
    letra: str, chave: int, deslocada: str
) -> None:
    assert deslocar_letra(letra, chave) == deslocada


def test_montar_tabela_tem_so_as_52_letras() -> None:
    tabela = montar_tabela(3)
    assert len(tabela) == 52
    assert tabela[ord("a")] == ord("d")
    assert tabela[ord("Z")] == ord("C")


def test_cifrar_a_cifra_conhecida() -> None:
    assert cifrar("Ola, Mundo!", 3) == "Rod, Pxqgr!"


def test_cifrar_mantem_maiusculas_e_minusculas() -> None:
    assert cifrar("ABC xyz", 3) == "DEF abc"


def test_cifrar_tira_os_acentos() -> None:
    assert cifrar("A ação começou às três.", 3) == "D dfdr frphfrx dv wuhv."


@pytest.mark.parametrize("texto", ["2026", " !?.,;: ", "🔒💡", "ß"])
def test_cifrar_deixa_o_que_nao_e_letra_sem_mudanca(texto: str) -> None:
    assert cifrar(texto, 7) == texto


@pytest.mark.parametrize("chave", CHAVES)
def test_decifrar_desfaz_cifrar(chave: int) -> None:
    for frase in FRASES:
        assert decifrar(cifrar(frase, chave), chave) == remover_acentos(frase)


# ---------------------------------------------------------------------------
# Quebra
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [("", False), ("2026!", False), ("ß", False), ("ç", True), ("2026 a", True)],
)
def test_tem_letras(texto: str, esperado: bool) -> None:
    assert tem_letras(texto) is esperado


def test_forca_bruta_tem_as_25_chaves_em_ordem() -> None:
    tentativas = forca_bruta("Rod, Pxqgr!")
    assert [chave for chave, _ in tentativas] == list(CHAVES)


@pytest.mark.parametrize("chave", CHAVES)
def test_forca_bruta_acha_o_texto_original_na_chave_certa(chave: int) -> None:
    tentativas = dict(forca_bruta(cifrar("Ola, Mundo!", chave)))
    assert tentativas[chave] == "Ola, Mundo!"


def test_contar_letras_sem_acentos_e_em_minusculas() -> None:
    assert contar_letras("Ação, AÇÃO! 2026") == Counter({"a": 4, "c": 2, "o": 2})


def test_contar_letras_sem_letras_e_vazia() -> None:
    assert contar_letras("2026!") == Counter()


@pytest.mark.parametrize(
    ("texto", "pontuacao"),
    [
        # 14,64 do "a" mais 1,16 do "b".
        ("ab", 15.80),
        # Dois "a" (2 × 14,64) e um "e" (12,70).
        ("Aa é", 41.98),
        ("2026!", 0.0),
    ],
)
def test_pontuar_soma_contagem_vezes_percentual(texto: str, pontuacao: float) -> None:
    assert pontuar(texto) == pytest.approx(pontuacao)


@pytest.mark.parametrize("chave", CHAVES)
def test_ordenar_chaves_poe_a_chave_certa_em_primeiro(chave: int) -> None:
    for frase in FRASES:
        assert ordenar_chaves(cifrar(frase, chave))[0] == chave


def test_ordenar_chaves_devolve_as_25_chaves() -> None:
    assert sorted(ordenar_chaves(cifrar(FRASES[0], 5))) == list(CHAVES)


def test_ordenar_chaves_no_empate_a_chave_menor_vem_antes() -> None:
    # Sem letras, todas as chaves pontuam 0.
    assert ordenar_chaves("2026!") == list(CHAVES)


def test_frases_dos_testes_tem_pelo_menos_30_letras() -> None:
    for frase in FRASES:
        assert sum(contar_letras(frase).values()) >= 30, frase


def test_frequencias_tem_as_26_letras_do_alfabeto() -> None:
    assert list(FREQUENCIAS) == list(ALFABETO)


def test_frequencias_tem_os_percentuais_do_estudo() -> None:
    assert FREQUENCIAS["a"] == 14.64
    assert FREQUENCIAS["e"] == 12.70
    assert FREQUENCIAS["o"] == 10.78


def test_frequencias_somam_perto_de_100() -> None:
    assert 99.9 <= sum(FREQUENCIAS.values()) <= 100.1


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


def test_cortar_deixa_a_linha_que_cabe() -> None:
    linha = "x" * LARGURA
    assert cortar(linha) == linha


def test_cortar_corta_a_linha_um_caractere_acima() -> None:
    linha = "x" * (LARGURA + 1)
    assert cortar(linha) == "x" * (LARGURA - 1) + "…"
    assert len(cortar(linha)) == LARGURA


def test_aviso_acentos_com_acento() -> None:
    assert aviso_acentos("ação") == ["📝 Os acentos e o ç foram tirados do texto."]


def test_aviso_acentos_sem_acento() -> None:
    assert aviso_acentos("acao 2026!") == []


def test_descrever_cifra_com_a_chave_e_o_texto_inteiro() -> None:
    assert descrever_cifra("Ola, Mundo!", 3) == (
        "🔒 Texto cifrado com a chave 3:\nRod, Pxqgr!"
    )


def test_descrever_cifra_avisa_dos_acentos() -> None:
    assert descrever_cifra("A ação começou às três.", 3) == (
        "🔒 Texto cifrado com a chave 3:\n"
        "D dfdr frphfrx dv wuhv.\n"
        "📝 Os acentos e o ç foram tirados do texto."
    )


def test_descrever_cifra_mostra_o_texto_longo_inteiro() -> None:
    texto = "abc " * 30
    assert cifrar(texto, 1) in descrever_cifra(texto, 1)


def test_descrever_decifra_com_a_chave_e_o_texto_inteiro() -> None:
    assert descrever_decifra("Rod, Pxqgr!", 3) == (
        "🔓 Texto decifrado com a chave 3:\nOla, Mundo!"
    )


def test_descrever_decifra_avisa_dos_acentos() -> None:
    assert descrever_decifra("Rõd", 3).endswith(
        "\n📝 Os acentos e o ç foram tirados do texto."
    )


def test_descrever_forca_bruta_tem_as_25_linhas_e_a_explicacao() -> None:
    linhas = descrever_forca_bruta("D fliud gh Fhvdu fdl hp vhjxqgrv.").splitlines()
    assert linhas[0] == "🔨 As 25 chaves possíveis:"
    assert linhas[1] == "Chave  1: C ekhtc fg Eguct eck go ugiwpfqu."
    assert linhas[3] == "Chave  3: A cifra de Cesar cai em segundos."
    assert linhas[25] == "Chave 25: E gmjve hi Giwev gem iq wikyrhsw."
    assert linhas[26:] == [
        "💡 A chave certa é a da linha que dá para ler.",
        "   Testar todas as chaves é a força bruta.",
    ]


def test_descrever_forca_bruta_corta_as_linhas_longas() -> None:
    linhas = descrever_forca_bruta(cifrar(FRASES[2], 9)).splitlines()[1:26]
    for linha in linhas:
        assert len(linha) == LARGURA
        assert linha.endswith("…")


def test_descrever_forca_bruta_avisa_dos_acentos() -> None:
    assert "📝 Os acentos" in descrever_forca_bruta("Rõd")
    assert "📝 Os acentos" not in descrever_forca_bruta("Rod")


def test_descrever_frequencia_com_as_letras_e_as_tres_chaves() -> None:
    assert descrever_frequencia(CIFRADO_7) == (
        "📊 Mais comuns no texto: L (7), H (7) e T (4)\n"
        "   No português, as mais comuns são A, E e O.\n"
        "🔓 Chave mais provável: 7\n"
        "Quem tem a chave decifra; quem nao tem, conta as letras.\n"
        "Outras chaves possíveis:\n"
        "- Chave 19: Eisa hsa o qvojs rsqwtfo; eisa boc hsa, q…\n"
        "- Chave 11: Mqai pai w ydwra zayebnw; mqai jwk pai, y…"
    )


@pytest.mark.parametrize(
    ("texto", "comuns"),
    [("aaa", "A (3)"), ("aab", "A (2) e B (1)")],
)
def test_descrever_frequencia_com_menos_de_tres_letras_diferentes(
    texto: str, comuns: str
) -> None:
    assert descrever_frequencia(texto).startswith(
        f"📊 Mais comuns no texto: {comuns}\n"
    )


def test_descrever_frequencia_avisa_do_texto_curto() -> None:
    texto = "b" * (MINIMO_LETRAS - 1)
    assert descrever_frequencia(texto).endswith(
        "\n💡 Com menos de 30 letras, a contagem pode enganar:\n"
        "   confira na força bruta."
    )


def test_descrever_frequencia_sem_aviso_a_partir_do_minimo() -> None:
    assert "💡" not in descrever_frequencia("b" * MINIMO_LETRAS)


def test_descrever_frequencia_avisa_dos_acentos() -> None:
    assert "📝 Os acentos" in descrever_frequencia("Rõd")
    assert "📝 Os acentos" not in descrever_frequencia("Rod")


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("numero", range(1, len(OPCOES) + 1))
def test_conferir_opcao_aceita_as_opcoes_do_menu(numero: int) -> None:
    assert conferir_opcao(str(numero)) == numero


def test_conferir_opcao_tira_os_espacos() -> None:
    assert conferir_opcao(" 2 ") == 2


@pytest.mark.parametrize("entrada", ["", "0", "6", "9", "abc", "1.5", "-1", "٣"])
def test_conferir_opcao_recusa_o_resto(entrada: str) -> None:
    assert conferir_opcao(entrada) is None


@pytest.mark.parametrize("chave", CHAVES)
def test_conferir_chave_aceita_de_1_a_25(chave: int) -> None:
    assert conferir_chave(str(chave)) == chave


def test_conferir_chave_tira_os_espacos() -> None:
    assert conferir_chave(" 3 ") == 3


@pytest.mark.parametrize("entrada", ["", "0", "26", "-3", "três", "3.0", "٣"])
def test_conferir_chave_recusa_o_resto(entrada: str) -> None:
    assert conferir_chave(entrada) is None


# ---------------------------------------------------------------------------
# Opções
# ---------------------------------------------------------------------------


def test_opcao_cifrar_pede_o_texto_e_a_chave() -> None:
    ler = LeitorFalso("Ola, Mundo!", "3")
    assert opcao_cifrar(ler) == descrever_cifra("Ola, Mundo!", 3)
    assert ler.pedidos == [PEDIDO_TEXTO, PEDIDO_CHAVE]


def test_opcao_decifrar_pede_o_texto_e_a_chave() -> None:
    ler = LeitorFalso("Rod, Pxqgr!", "3")
    assert opcao_decifrar(ler) == descrever_decifra("Rod, Pxqgr!", 3)
    assert ler.pedidos == [PEDIDO_TEXTO, PEDIDO_CHAVE]


def test_opcao_forca_bruta_pede_so_o_texto() -> None:
    ler = LeitorFalso("Rod, Pxqgr!")
    assert opcao_forca_bruta(ler) == descrever_forca_bruta("Rod, Pxqgr!")
    assert ler.pedidos == [PEDIDO_TEXTO]


def test_opcao_frequencia_pede_so_o_texto() -> None:
    ler = LeitorFalso(CIFRADO_7)
    assert opcao_frequencia(ler) == descrever_frequencia(CIFRADO_7)
    assert ler.pedidos == [PEDIDO_TEXTO]


@pytest.mark.parametrize("texto", ["", "2026!", "   "])
@pytest.mark.parametrize(
    ("opcao", "mensagem"),
    [
        (opcao_cifrar, "❌ Não há letras para cifrar."),
        (opcao_decifrar, "❌ Não há letras para decifrar."),
        (opcao_forca_bruta, "❌ Não há letras para quebrar."),
        (opcao_frequencia, "❌ Não há letras para quebrar."),
    ],
)
def test_opcoes_recusam_o_texto_sem_letras(
    opcao: Callable[[Leitor], str], mensagem: str, texto: str
) -> None:
    ler = LeitorFalso(texto)
    assert opcao(ler) == mensagem
    # Sem letras, a chave nem é pedida.
    assert ler.pedidos == [PEDIDO_TEXTO]


@pytest.mark.parametrize("opcao", [opcao_cifrar, opcao_decifrar])
@pytest.mark.parametrize("chave", ["", "0", "26", "-3", "três"])
def test_opcoes_recusam_a_chave_invalida(
    opcao: Callable[[Leitor], str], chave: str
) -> None:
    assert opcao(LeitorFalso("Ola", chave)) == "❌ A chave vai de 1 a 25."


def test_opcao_cifrar_mantem_os_espacos_do_comeco_e_do_fim() -> None:
    resultado = opcao_cifrar(LeitorFalso("  Ola  ", "3"))
    assert resultado.endswith("\n  Rod  ")


def test_opcao_frequencia_mantem_os_espacos_do_comeco_e_do_fim() -> None:
    resultado = opcao_frequencia(LeitorFalso("  " + CIFRADO_7 + "  "))
    assert (
        "\n  Quem tem a chave decifra; quem nao tem, conta as letras.  \n" in resultado
    )


# ---------------------------------------------------------------------------
# Largura das linhas
# ---------------------------------------------------------------------------


def textos_do_programa() -> list[str]:
    """Monta um resultado de cada tipo, com textos curtos e com acento.

    Returns:
        list[str]: Os resultados das quatro opções, com todos os avisos, e as
            mensagens de erro.
    """
    return [
        descrever_cifra("Ação às três", 25),
        descrever_decifra("Ação às três", 25),
        descrever_forca_bruta(cifrar(FRASES[2], 9)),
        descrever_forca_bruta("Ação às três"),
        descrever_frequencia("Ação às três"),
        opcao_cifrar(LeitorFalso("")),
        opcao_decifrar(LeitorFalso("")),
        opcao_forca_bruta(LeitorFalso("")),
        opcao_cifrar(LeitorFalso("Ola", "0")),
        f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}.",
    ]


def test_nenhuma_linha_dos_textos_passa_da_largura_maxima() -> None:
    for texto in textos_do_programa():
        for linha in texto.splitlines():
            assert colunas(linha) <= LARGURA_MAXIMA, linha


def test_nenhum_pedido_passa_da_largura_maxima() -> None:
    for pedido in [PEDIDO_OPCAO, PEDIDO_TEXTO, PEDIDO_CHAVE]:
        assert colunas(pedido) <= LARGURA_MAXIMA, pedido


def test_nenhuma_linha_do_quadro_passa_da_largura_maxima(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_tela("")
    exibir_tela(descrever_frequencia("Ação às três"))
    exibir_tela(descrever_forca_bruta("Ação às três"))
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
    return saida[saida.rindex("======== CIFRA DE CÉSAR") :]


def test_main_primeira_tela_sem_resultado(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("5"))
    assert capsys.readouterr().out.startswith(
        "======== CIFRA DE CÉSAR ========\n\n"
        "1 : Cifrar um texto\n"
        "2 : Decifrar com a chave\n"
        "3 : Quebrar por força bruta\n"
        "4 : Quebrar pela frequência das letras\n"
        "5 : Sair\n\n"
    )


def test_main_mostra_titulo_resultado_e_menu_nessa_ordem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ler = LeitorFalso("1", "Ola, Mundo!", "3", "5")
    main(ler)
    tela = ultima_tela(capsys.readouterr().out)
    assert tela.startswith(
        "======== CIFRA DE CÉSAR ========\n\n"
        "🔒 Texto cifrado com a chave 3:\nRod, Pxqgr!\n\n"
        "1 : Cifrar um texto\n"
    )
    assert ler.pedidos == [PEDIDO_OPCAO, PEDIDO_TEXTO, PEDIDO_CHAVE, PEDIDO_OPCAO]


@pytest.mark.parametrize(
    ("respostas", "resultado"),
    [
        (("1", "Ola, Mundo!", "3"), descrever_cifra("Ola, Mundo!", 3)),
        (("2", "Rod, Pxqgr!", "3"), descrever_decifra("Rod, Pxqgr!", 3)),
        (("3", "Rod, Pxqgr!"), descrever_forca_bruta("Rod, Pxqgr!")),
        (("4", CIFRADO_7), descrever_frequencia(CIFRADO_7)),
        (("1", "2026!"), "❌ Não há letras para cifrar."),
        (("2", "Ola", "26"), "❌ A chave vai de 1 a 25."),
    ],
)
def test_main_mostra_o_resultado_de_cada_opcao(
    capsys: pytest.CaptureFixture[str], respostas: tuple[str, ...], resultado: str
) -> None:
    main(LeitorFalso(*respostas, "5"))
    tela = ultima_tela(capsys.readouterr().out)
    assert f"\n\n{resultado}\n\n1 : Cifrar um texto" in tela


@pytest.mark.parametrize("entrada", ["", "0", "6", "9", "abc", "٣"])
def test_main_recusa_a_opcao_invalida(
    capsys: pytest.CaptureFixture[str], entrada: str
) -> None:
    main(LeitorFalso(entrada, "5"))
    tela = ultima_tela(capsys.readouterr().out)
    assert "❌ Opção inválida. Digite um número de 1 a 5." in tela


def test_main_limpa_a_tela_a_cada_volta(
    capsys: pytest.CaptureFixture[str], limpezas: list[None]
) -> None:
    main(LeitorFalso("x", "3", "Rod", "4", "", "5"))
    assert len(limpezas) == 4
    assert capsys.readouterr().out.count("======== CIFRA DE CÉSAR") == 4


def test_main_o_resultado_some_na_volta_seguinte(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main(LeitorFalso("1", "Ola", "3", "x", "5"))
    tela = ultima_tela(capsys.readouterr().out)
    assert "Rod" not in tela


def test_main_sai_pelo_menu_com_despedida(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("5"))
    assert capsys.readouterr().out.endswith("5 : Sair\n\n" + DESPEDIDA)


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
@pytest.mark.parametrize(
    ("respostas", "pedido"),
    [
        ((), PEDIDO_OPCAO),
        (("x",), PEDIDO_OPCAO),
        (("1",), PEDIDO_TEXTO),
        (("3",), PEDIDO_TEXTO),
        (("4",), PEDIDO_TEXTO),
        (("1", "Ola"), PEDIDO_CHAVE),
        (("2", "Rod"), PEDIDO_CHAVE),
    ],
)
def test_main_sai_sem_stack_trace_em_qualquer_pedido(
    capsys: pytest.CaptureFixture[str],
    excecao: type[BaseException],
    respostas: tuple[str, ...],
    pedido: str,
) -> None:
    ler = LeitorQueInterrompe(excecao, *respostas)
    main(ler)
    assert ler.pedidos[-1] == pedido
    assert capsys.readouterr().out.endswith(ENCERRADA)


def test_main_le_o_teclado_com_o_input_por_padrao() -> None:
    assert inspect.signature(main).parameters["ler"].default is input


# ---------------------------------------------------------------------------
# Nada sai do computador
# ---------------------------------------------------------------------------


def test_main_py_so_importa_os_modulos_previstos_e_nao_le_nem_grava_arquivo() -> None:
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
        if isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name):
            atributos.add((no.value.id, no.attr))

    previstos = {
        "__future__",
        "collections",
        "collections.abc",
        "os",
        "string",
        "sys",
        "unicodedata",
    }
    assert modulos <= previstos
    proibidas = {"open", "read_text", "write_text", "read_bytes", "write_bytes"}
    assert not chamadas & proibidas
    assert ("sys", "argv") not in atributos
