"""Testes para main.py.

Estratégia de isolamento: o teclado e o sorteio entram nas funções do jogo por
parâmetro, então cada teste passa um `LeitorFalso` (devolve as respostas na
ordem e guarda cada pedido) e um `SorteadorFalso` (devolve o par escolhido pelo
teste e guarda as opções recebidas), sem `monkeypatch` em `input` ou `random`. A
saída se confere com o `capsys`. O único `monkeypatch` da suíte troca
`limpar_tela` por um no-op, porque ela chama `os.system`, um efeito de terminal.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import main as modulo_main
from main import (
    ALFABETO,
    ERROS_MAXIMOS,
    FORCA,
    PALAVRAS,
    Conferencia,
    conferir_entrada,
    contar_erros,
    exibir_jogo,
    exibir_placar,
    jogar_partida,
    mascarar_palavra,
    perguntar_jogar_de_novo,
    remover_acentos,
    sortear_palavra,
)

# Todas as palavras da lista, na ordem de PALAVRAS.
TODAS = [palavra for palavras in PALAVRAS.values() for palavra in palavras]


@pytest.fixture(autouse=True)
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte.

    `limpar_tela` chama `os.system`, que limparia o terminal de quem roda os testes.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


class SorteadorFalso:
    """Simula o sorteio: escolhe sempre a mesma posição e guarda as opções.

    Attributes:
        opcoes (list[list[tuple[str, str]]]): Lista recebida em cada sorteio.
    """

    def __init__(self, posicao: int = 0) -> None:
        """Guarda a posição a escolher.

        Args:
            posicao (int, optional): Índice do par escolhido em cada sorteio.
                Padrão: 0, o primeiro par.
        """
        self._posicao = posicao
        self.opcoes: list[list[tuple[str, str]]] = []

    def __call__(self, opcoes: list[tuple[str, str]]) -> tuple[str, str]:
        """Registra as opções e devolve o par da posição guardada.

        Args:
            opcoes (list[tuple[str, str]]): Pares (tema, palavra) que poderiam
                ser sorteados.

        Returns:
            tuple[str, str]: O par da posição guardada.
        """
        self.opcoes.append(list(opcoes))
        return opcoes[self._posicao]


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
            pedido (str): Texto que o jogo mostraria antes de ler o teclado.

        Returns:
            str: A próxima resposta da sequência.
        """
        self.pedidos.append(pedido)
        return next(self._respostas)


class LeitorQueInterrompe:
    """Simula o jogador saindo: lança a exceção na primeira leitura.

    Attributes:
        excecao (type[BaseException]): Exceção lançada ao ler o teclado.
    """

    def __init__(self, excecao: type[BaseException]) -> None:
        """Guarda a exceção a lançar.

        Args:
            excecao (type[BaseException]): `KeyboardInterrupt` ou `EOFError`.
        """
        self.excecao = excecao

    def __call__(self, pedido: str) -> str:
        """Lança a exceção guardada, como o Ctrl+C ou o fim da entrada.

        Args:
            pedido (str): Texto do pedido (ignorado).

        Raises:
            BaseException: A exceção guardada.
        """
        raise self.excecao


# ---------------------------------------------------------------------------
# PALAVRAS e FORCA
# ---------------------------------------------------------------------------


def test_palavras_tem_cinco_temas_de_oito_palavras() -> None:
    assert list(PALAVRAS) == [
        "frutas",
        "animais",
        "países",
        "profissões",
        "objetos da casa",
    ]
    assert all(len(palavras) == 8 for palavras in PALAVRAS.values())


def test_palavras_sao_so_letras_minusculas_depois_de_tirar_o_acento() -> None:
    for palavra in TODAS:
        assert remover_acentos(palavra) != ""
        assert set(remover_acentos(palavra)) <= set(ALFABETO), palavra


def test_palavras_nao_se_repetem() -> None:
    assert len(set(TODAS)) == len(TODAS)


def test_palavras_tem_acento_e_cedilha() -> None:
    assert any(remover_acentos(palavra) != palavra for palavra in TODAS)
    assert any("ç" in palavra for palavra in TODAS)


def test_forca_tem_um_desenho_por_numero_de_erros() -> None:
    assert len(FORCA) == ERROS_MAXIMOS + 1


def test_forca_completa_tem_cabeca_bracos_e_pernas() -> None:
    assert FORCA[ERROS_MAXIMOS].splitlines()[3:6] == [
        "  O   |",
        r" /|\  |",
        r" / \  |",
    ]


# ---------------------------------------------------------------------------
# sortear_palavra
# ---------------------------------------------------------------------------


def test_sortear_palavra_devolve_o_par_e_guarda_a_palavra() -> None:
    ja_sorteadas: set[str] = set()
    assert sortear_palavra(ja_sorteadas, SorteadorFalso()) == ("frutas", "banana")
    assert ja_sorteadas == {"banana"}


def test_sortear_palavra_tira_a_ja_sorteada_das_opcoes() -> None:
    sorteador = SorteadorFalso()
    ja_sorteadas: set[str] = set()
    sortear_palavra(ja_sorteadas, sorteador)
    assert sortear_palavra(ja_sorteadas, sorteador) == ("frutas", "maçã")
    assert len(sorteador.opcoes[0]) == len(TODAS)
    assert ("frutas", "banana") not in sorteador.opcoes[1]
    assert len(sorteador.opcoes[1]) == len(TODAS) - 1


def test_sortear_palavra_recomeca_quando_a_lista_acaba() -> None:
    sorteador = SorteadorFalso()
    ja_sorteadas = set(TODAS)
    assert sortear_palavra(ja_sorteadas, sorteador) == ("frutas", "banana")
    assert len(sorteador.opcoes[0]) == len(TODAS)
    assert ja_sorteadas == {"banana"}


# ---------------------------------------------------------------------------
# remover_acentos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("áàâã", "aaaa"),
        ("éêí", "eei"),
        ("óôõú", "ooou"),
        ("ç", "c"),
        ("maçã", "maca"),
        ("pêssego", "pessego"),
        ("banana", "banana"),
    ],
)
def test_remover_acentos(texto: str, esperado: str) -> None:
    assert remover_acentos(texto) == esperado


# ---------------------------------------------------------------------------
# mascarar_palavra e contar_erros
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tentadas", "esperado"),
    [
        (set(), "_ _ _ _"),
        ({"a"}, "_ A _ Ã"),
        ({"m", "a", "c"}, "M A Ç Ã"),
        ({"x", "a"}, "_ A _ Ã"),
    ],
)
def test_mascarar_palavra(tentadas: set[str], esperado: str) -> None:
    assert mascarar_palavra("maçã", tentadas) == esperado


@pytest.mark.parametrize(
    ("tentadas", "esperado"),
    [(set(), 0), ({"m", "a"}, 0), ({"a", "x"}, 1), ({"x", "y", "z", "c"}, 3)],
)
def test_contar_erros(tentadas: set[str], esperado: int) -> None:
    assert contar_erros({"m", "a", "c"}, tentadas) == esperado


# ---------------------------------------------------------------------------
# conferir_entrada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "letra"),
    [("a", "a"), ("A", "a"), ("á", "a"), ("Ã", "a"), ("ç", "c"), ("  e  ", "e")],
)
def test_conferir_entrada_aceita_uma_letra(entrada: str, letra: str) -> None:
    assert conferir_entrada(entrada, set()) == Conferencia(letra, "")


@pytest.mark.parametrize("entrada", ["", "   ", "ab", "3", "?", "ß"])
def test_conferir_entrada_recusa_o_que_nao_e_uma_letra_so(entrada: str) -> None:
    assert conferir_entrada(entrada, set()) == Conferencia(
        "", "❌ Digite uma letra só, de A a Z."
    )


@pytest.mark.parametrize("entrada", ["a", "A", "á"])
def test_conferir_entrada_recusa_a_letra_repetida(entrada: str) -> None:
    # "á" depois de "a" também é repetida: a comparação é sem acento.
    assert conferir_entrada(entrada, {"a"}) == Conferencia(
        "", "🔁 A letra A já foi tentada. Tente outra."
    )


# ---------------------------------------------------------------------------
# perguntar_jogar_de_novo e exibir_placar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("resposta", "esperado"), [("s", True), ("S", True), ("n", False), ("N", False)]
)
def test_perguntar_jogar_de_novo(resposta: str, esperado: bool) -> None:
    assert perguntar_jogar_de_novo(LeitorFalso(resposta)) is esperado


def test_perguntar_jogar_de_novo_repete_na_resposta_invalida(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("talvez", "", "n")
    assert perguntar_jogar_de_novo(leitor) is False
    assert len(leitor.pedidos) == 3
    assert capsys.readouterr().out.count("Responda s (sim) ou n (não).") == 2


def test_exibir_placar(capsys: pytest.CaptureFixture[str]) -> None:
    exibir_placar({"vitórias": 2, "derrotas": 1})
    assert capsys.readouterr().out.splitlines() == [
        "",
        "Placar da sessão:",
        "  Vitórias: 2",
        "  Derrotas: 1",
    ]


# ---------------------------------------------------------------------------
# exibir_jogo
# ---------------------------------------------------------------------------


def test_exibir_jogo_sem_tentativa(capsys: pytest.CaptureFixture[str]) -> None:
    exibir_jogo("frutas", "maçã", set(), "")
    assert capsys.readouterr().out.splitlines() == [
        "Tema: frutas",
        *FORCA[0].splitlines(),
        "",
        "Palavra: _ _ _ _",
        "Letras tentadas: —",
        "Erros restantes: 6",
        "",
    ]


def test_exibir_jogo_mostra_as_letras_em_ordem_e_a_forca_dos_erros(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_jogo("frutas", "maçã", {"r", "a", "e"}, "")
    saida = capsys.readouterr().out
    assert FORCA[2] in saida
    assert "Palavra: _ A _ Ã" in saida
    assert "Letras tentadas: A, E, R" in saida
    assert "Erros restantes: 4" in saida


def test_exibir_jogo_termina_com_a_mensagem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_jogo("frutas", "maçã", {"r"}, "❌ A palavra não tem a letra R.")
    assert capsys.readouterr().out.splitlines()[-1] == "❌ A palavra não tem a letra R."


# ---------------------------------------------------------------------------
# jogar_partida
# ---------------------------------------------------------------------------


def test_jogar_partida_vence_sem_erro(capsys: pytest.CaptureFixture[str]) -> None:
    leitor = LeitorFalso("m", "a", "c")
    assert jogar_partida("frutas", "maçã", leitor) is True
    saida = capsys.readouterr().out
    assert "🎉 Você descobriu a palavra: MAÇÃ! Erros cometidos: 0." in saida
    # Sem leitura a mais depois da última letra.
    assert len(leitor.pedidos) == 3


def test_jogar_partida_vence_com_erros(capsys: pytest.CaptureFixture[str]) -> None:
    leitor = LeitorFalso("x", "m", "y", "a", "c")
    assert jogar_partida("frutas", "maçã", leitor) is True
    saida = capsys.readouterr().out
    assert "❌ A palavra não tem a letra X." in saida
    assert "✅ A palavra tem a letra M." in saida
    assert "Erros cometidos: 2." in saida


def test_jogar_partida_perde_no_sexto_erro_e_revela_a_palavra(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("b", "d", "e", "f", "g", "h")
    assert jogar_partida("frutas", "maçã", leitor) is False
    saida = capsys.readouterr().out
    assert saida.splitlines()[-1] == "💀 A forca completou. A palavra era MAÇÃ."
    assert FORCA[ERROS_MAXIMOS] in saida
    assert len(leitor.pedidos) == ERROS_MAXIMOS


def test_jogar_partida_nao_conta_repetida_nem_invalida_como_erro(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("a", "a", "á", "ab", "3", "", "m", "c")
    assert jogar_partida("frutas", "maçã", leitor) is True
    saida = capsys.readouterr().out
    assert saida.count("🔁 A letra A já foi tentada. Tente outra.") == 2
    assert saida.count("❌ Digite uma letra só, de A a Z.") == 3
    assert "Erros cometidos: 0." in saida


def test_jogar_partida_letra_sem_acento_revela_a_acentuada(
    capsys: pytest.CaptureFixture[str],
) -> None:
    jogar_partida("frutas", "maçã", LeitorFalso("a", "m", "c"))
    assert "Palavra: _ A _ Ã" in capsys.readouterr().out


def test_jogar_partida_c_revela_o_c_cedilha(
    capsys: pytest.CaptureFixture[str],
) -> None:
    jogar_partida("frutas", "maçã", LeitorFalso("c", "m", "a"))
    assert "Palavra: _ _ Ç _" in capsys.readouterr().out


def test_jogar_partida_limpa_a_tela_antes_de_cada_quadro(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas: list[None] = []
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: chamadas.append(None))
    jogar_partida("frutas", "maçã", LeitorFalso("x", "m", "a", "c"))
    # Um quadro por leitura, mais o quadro final.
    assert len(chamadas) == 5


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_sessao_de_duas_partidas_sem_repetir_palavra(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Partida 1: "banana", vitória. Partida 2: "maçã", derrota.
    sorteador = SorteadorFalso()
    leitor = LeitorFalso("b", "a", "n", "s", "b", "d", "e", "f", "g", "h", "n")
    modulo_main.main(sorteador, leitor)
    assert ("frutas", "banana") not in sorteador.opcoes[1]
    saida = capsys.readouterr().out
    assert "Você descobriu a palavra: BANANA!" in saida
    assert "A palavra era MAÇÃ." in saida
    assert saida.splitlines()[-4:] == [
        "Placar da sessão:",
        "  Vitórias: 1",
        "  Derrotas: 1",
        "Até a próxima! 👋",
    ]


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
def test_main_sai_com_despedida_sem_stack_trace(
    excecao: type[BaseException], capsys: pytest.CaptureFixture[str]
) -> None:
    modulo_main.main(SorteadorFalso(), LeitorQueInterrompe(excecao))
    saida = capsys.readouterr()
    assert "Jogo encerrado. Até a próxima! 👋" in saida.out
    assert "Traceback" not in saida.out + saida.err
