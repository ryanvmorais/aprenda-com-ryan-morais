"""Testes para main.py.

Estratégia de isolamento: nenhum teste abre um terminal real — a
`_FakeJanela` abaixo simula os métodos de uma `curses.window`
(`getmaxyx`, `addch`, `addstr`, `clear`, `border`, `timeout`, `getch`,
`refresh`) só registrando as chamadas. `input()` é mockado via
`monkeypatch.setattr("builtins.input", ...)` para simular a digitação do
usuário. `time.sleep` é mockado em `finalizar_jogo` para a suíte não
esperar os 3 segundos reais. `ciclo_do_jogo` roda inteiro contra a
`_FakeJanela`, com `curses.curs_set` (que exige um terminal real) trocado
por um registro e as frutas fixadas por `random.randint`; o
`curses.wrapper`, que só prepara e restaura o terminal, fica de fora.
"""

from __future__ import annotations

import curses
import random
import time
from collections.abc import Iterator

import pytest

import main

# A partida mais longa dos testes dura 24 quadros; 200 leituras de tecla é
# folga de sobra, e passar disso quer dizer que a cobra nunca bateu em nada.
LEITURAS_MAXIMAS = 200

# ---------------------------------------------------------------------------
# Fake de curses.window
# ---------------------------------------------------------------------------


class _FakeJanela:
    """Finge ser uma `curses.window`: tamanho fixo, chamadas registradas."""

    def __init__(
        self, altura: int = 20, largura: int = 40, teclas: tuple[int, ...] = ()
    ) -> None:
        """Cria uma janela falsa com o tamanho e a fila de teclas dados.

        Args:
            altura (int, optional): Altura simulada da janela. Padrão: 20.
            largura (int, optional): Largura simulada da janela. Padrão: 40.
            teclas (tuple[int, ...], optional): Sequência de teclas que
                `getch` devolve, uma por chamada. Padrão: vazia.
        """
        self.altura = altura
        self.largura = largura
        self._teclas = iter(teclas)
        self.chamadas_addch: list[tuple[int, int, str]] = []
        self.chamadas_addstr: list[tuple[int, int, str, int]] = []
        self.limpezas = 0
        self.bordas = 0
        self.timeout_chamado: int | None = None
        self.refrescada = False
        self.leituras = 0

    def getmaxyx(self) -> tuple[int, int]:
        """Returns:
        tuple[int, int]: A altura e a largura simuladas da janela.
        """
        return (self.altura, self.largura)

    def clear(self) -> None:
        self.limpezas += 1

    def border(self) -> None:
        self.bordas += 1

    def addch(self, y: int, x: int, ch: str) -> None:
        self.chamadas_addch.append((y, x, ch))

    def addstr(self, y: int, x: int, texto: str, attr: int = 0) -> None:
        self.chamadas_addstr.append((y, x, texto, attr))

    def timeout(self, ms: int) -> None:
        self.timeout_chamado = ms

    def getch(self) -> int:
        """Devolve a próxima tecla da fila, ou -1 (nenhuma) quando ela acaba.

        Returns:
            int: O código da tecla, como o `getch` do curses.

        Raises:
            AssertionError: Depois de `LEITURAS_MAXIMAS` leituras: uma partida
                que nunca termina (a colisão quebrada) falha o teste em vez de
                travar a suíte.
        """
        self.leituras += 1
        if self.leituras > LEITURAS_MAXIMAS:
            raise AssertionError(f"a partida passou de {LEITURAS_MAXIMAS} quadros")
        return next(self._teclas, -1)

    def refresh(self) -> None:
        self.refrescada = True


def _digitar(monkeypatch: pytest.MonkeyPatch, *respostas: str) -> Iterator[str]:
    """Simula uma sequência de respostas do usuário no `input()`.

    Args:
        monkeypatch (pytest.MonkeyPatch): Fixture de monkeypatch do teste.
        *respostas (str): Respostas a devolver, uma por chamada de `input()`.

    Returns:
        Iterator[str]: O iterador usado internamente (raramente precisa ser
            inspecionado pelo teste).
    """
    valores = iter(respostas)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(valores))
    return valores


# ---------------------------------------------------------------------------
# selecionar_nivel_dificuldade
# ---------------------------------------------------------------------------


# A tabela escrita aqui, e não lida do `main.py`: do nível 1 (fácil, a cobra
# lenta) ao 5 (difícil), a espera entre quadros só diminui.
@pytest.mark.parametrize(
    ("nivel", "espera"), [("1", 1000), ("2", 500), ("3", 150), ("4", 90), ("5", 35)]
)
def test_selecionar_nivel_dificuldade_aceita_entrada_valida(
    monkeypatch: pytest.MonkeyPatch, nivel: str, espera: int
) -> None:
    _digitar(monkeypatch, nivel)
    assert main.selecionar_nivel_dificuldade() == espera


def test_selecionar_nivel_dificuldade_repete_apos_entrada_fora_do_intervalo(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Número fora de 1-5 não deve travar: o loop pede de novo até validar."""
    _digitar(monkeypatch, "9", "1")

    resultado = main.selecionar_nivel_dificuldade()

    assert resultado == 1000
    assert "Por favor, escolha" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# desenhar_tela / desenhar_ator / desenhar_cobra
# ---------------------------------------------------------------------------


def test_desenhar_tela_limpa_e_desenha_borda() -> None:
    janela = _FakeJanela()
    main.desenhar_tela(janela)  # type: ignore[arg-type]
    assert janela.limpezas == 1
    assert janela.bordas == 1


def test_desenhar_ator_escreve_caractere_na_coordenada() -> None:
    janela = _FakeJanela()
    main.desenhar_ator([5, 7], janela, "*")  # type: ignore[arg-type]
    assert janela.chamadas_addch == [(5, 7, "*")]


def test_desenhar_cobra_marca_cabeca_diferente_do_corpo() -> None:
    janela = _FakeJanela()
    cobra = [[10, 15], [9, 15], [8, 15]]

    main.desenhar_cobra(cobra, janela)  # type: ignore[arg-type]

    assert janela.chamadas_addch[0] == (10, 15, "@")
    assert janela.chamadas_addch[1:] == [(9, 15, "#"), (8, 15, "#")]


# ---------------------------------------------------------------------------
# gerar_nova_fruta
# ---------------------------------------------------------------------------


def test_gerar_nova_fruta_fica_dentro_das_bordas(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    janela = _FakeJanela(altura=20, largura=40)
    chamadas: list[tuple[int, int]] = []

    def _randint_fake(a: int, b: int) -> int:
        chamadas.append((a, b))
        return a

    monkeypatch.setattr(random, "randint", _randint_fake)

    fruta = main.gerar_nova_fruta(janela)  # type: ignore[arg-type]

    assert fruta == [1, 1]
    assert chamadas == [(1, 18), (1, 38)]  # altura-2, largura-2


# ---------------------------------------------------------------------------
# obter_nova_direcao
# ---------------------------------------------------------------------------


def test_obter_nova_direcao_configura_o_timeout() -> None:
    janela = _FakeJanela(teclas=(curses.KEY_UP,))
    main.obter_nova_direcao(janela, 150)  # type: ignore[arg-type]
    assert janela.timeout_chamado == 150


@pytest.mark.parametrize(
    "tecla", [curses.KEY_UP, curses.KEY_LEFT, curses.KEY_DOWN, curses.KEY_RIGHT]
)
def test_obter_nova_direcao_aceita_cada_tecla_de_seta(tecla: int) -> None:
    janela = _FakeJanela(teclas=(tecla,))
    assert main.obter_nova_direcao(janela, 150) == tecla  # type: ignore[arg-type]


def test_obter_nova_direcao_ignora_tecla_nao_direcional() -> None:
    """Uma tecla que não é seta (ex.: espaço) não deve virar direção."""
    janela = _FakeJanela(teclas=(ord(" "),))
    assert main.obter_nova_direcao(janela, 150) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# direcao_e_oposta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("direcao", "direcao_atual"),
    [
        (curses.KEY_UP, curses.KEY_DOWN),
        (curses.KEY_DOWN, curses.KEY_UP),
        (curses.KEY_LEFT, curses.KEY_RIGHT),
        (curses.KEY_RIGHT, curses.KEY_LEFT),
    ],
)
def test_direcao_e_oposta_detecta_meia_volta(direcao: int, direcao_atual: int) -> None:
    assert main.direcao_e_oposta(direcao, direcao_atual) is True


def test_direcao_e_oposta_permite_curva_lateral() -> None:
    assert main.direcao_e_oposta(curses.KEY_UP, curses.KEY_RIGHT) is False


# ---------------------------------------------------------------------------
# mover_cobra
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("direcao", "cabeca_esperada"),
    [
        (curses.KEY_UP, [9, 15]),
        (curses.KEY_DOWN, [11, 15]),
        (curses.KEY_LEFT, [10, 14]),
        (curses.KEY_RIGHT, [10, 16]),
    ],
)
def test_mover_cobra_desloca_a_cabeca_na_direcao(
    direcao: int, cabeca_esperada: list[int]
) -> None:
    cobra = [[10, 15], [9, 15], [8, 15]]
    main.mover_cobra(cobra, direcao, cobra_comeu_fruta=False)
    assert cobra[0] == cabeca_esperada


def test_mover_cobra_remove_a_cauda_quando_nao_comeu() -> None:
    cobra = [[10, 15], [9, 15], [8, 15]]
    main.mover_cobra(cobra, curses.KEY_DOWN, cobra_comeu_fruta=False)
    # Sai o último gomo; o resto anda junto, sem buraco no corpo.
    assert cobra == [[11, 15], [10, 15], [9, 15]]


def test_mover_cobra_mantem_a_cauda_quando_comeu() -> None:
    """Comer a fruta faz a cobra crescer: a cauda não é removida na jogada."""
    cobra = [[10, 15], [9, 15], [8, 15]]
    main.mover_cobra(cobra, curses.KEY_DOWN, cobra_comeu_fruta=True)
    assert len(cobra) == 4
    assert cobra[-1] == [8, 15]  # cauda antiga preservada


# ---------------------------------------------------------------------------
# verificar_colisoes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cabeca",
    [
        [0, 10],  # topo
        [19, 10],  # base (altura-1 == 19)
        [10, 0],  # esquerda
        [10, 39],  # direita (largura-1 == 39)
    ],
)
def test_verificar_colisoes_detecta_borda(cabeca: list[int]) -> None:
    janela = _FakeJanela(altura=20, largura=40)
    cobra = [cabeca, [10, 15]]
    assert main.verificar_colisoes(cobra, janela) is True  # type: ignore[arg-type]


# O par da borda: um passo para dentro de cada lado ainda é campo livre.
@pytest.mark.parametrize(
    "cabeca",
    [
        [1, 10],  # logo abaixo do topo
        [18, 10],  # logo acima da base
        [10, 1],  # logo à direita da borda esquerda
        [10, 38],  # logo à esquerda da borda direita
    ],
)
def test_verificar_colisoes_aceita_a_casa_ao_lado_da_borda(cabeca: list[int]) -> None:
    janela = _FakeJanela(altura=20, largura=40)
    cobra = [cabeca, [10, 15]]
    assert main.verificar_colisoes(cobra, janela) is False  # type: ignore[arg-type]


def test_verificar_colisoes_detecta_cabeca_no_proprio_corpo() -> None:
    janela = _FakeJanela(altura=20, largura=40)
    cobra = [[10, 15], [9, 15], [10, 15]]  # cabeça coincide com o 3º gomo
    assert main.verificar_colisoes(cobra, janela) is True  # type: ignore[arg-type]


def test_verificar_colisoes_sem_colisao() -> None:
    janela = _FakeJanela(altura=20, largura=40)
    cobra = [[10, 15], [9, 15], [8, 15]]
    assert main.verificar_colisoes(cobra, janela) is False  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# finalizar_jogo
# ---------------------------------------------------------------------------


def test_finalizar_jogo_centraliza_a_mensagem_e_atualiza_a_tela(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # não espera os 3s reais
    monkeypatch.setattr(time, "sleep", lambda _segundos: None)
    janela = _FakeJanela(altura=20, largura=40)

    main.finalizar_jogo(7, janela)  # type: ignore[arg-type]

    assert len(janela.chamadas_addstr) == 1
    y, x, texto, attr = janela.chamadas_addstr[0]
    assert "Frutas coletadas: 7" in texto
    assert y == 10  # altura // 2
    assert x == (40 - len(texto)) // 2
    assert attr == curses.A_REVERSE
    assert janela.refrescada is True


# ---------------------------------------------------------------------------
# ciclo_do_jogo
# ---------------------------------------------------------------------------


@pytest.fixture
def cursor(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Troca `curses.curs_set`, que exige um terminal real, por um registro.

    Também zera a espera de 3 segundos da tela final.

    Args:
        monkeypatch (pytest.MonkeyPatch): Fixture de monkeypatch do teste.

    Returns:
        list[int]: O valor de cada chamada a `curses.curs_set`.
    """
    chamadas: list[int] = []
    monkeypatch.setattr(curses, "curs_set", chamadas.append)
    monkeypatch.setattr(time, "sleep", lambda _segundos: None)
    return chamadas


def _sortear_frutas(monkeypatch: pytest.MonkeyPatch, *valores: int) -> None:
    """Fixa as coordenadas das frutas: cada fruta consome dois valores (y, x).

    Args:
        monkeypatch (pytest.MonkeyPatch): Fixture de monkeypatch do teste.
        *valores (int): Os valores devolvidos por `random.randint`, na ordem.
    """
    fila = iter(valores)
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(fila))


def test_ciclo_do_jogo_ignora_a_meia_volta_e_conta_a_fruta(
    monkeypatch: pytest.MonkeyPatch, cursor: list[int]
) -> None:
    """A cobra desce, come a fruta em [11, 15] e bate na base no 9º quadro.

    A seta para cima no 2º quadro é a meia-volta: aceita, a cabeça voltaria para
    o pescoço e a partida acabaria ali, com 2 quadros.
    """
    _sortear_frutas(monkeypatch, 11, 15, 1, 1)
    janela = _FakeJanela(altura=20, largura=40, teclas=(-1, curses.KEY_UP))

    main.ciclo_do_jogo(janela, 150)  # type: ignore[arg-type]

    assert cursor == [0]
    assert janela.timeout_chamado == 150
    assert janela.limpezas == 9  # um quadro por passo, da linha 10 até a 19
    _, _, texto, _ = janela.chamadas_addstr[0]
    assert texto == " Fim de Jogo! Frutas coletadas: 1 "


def test_ciclo_do_jogo_aceita_a_curva_lateral(
    monkeypatch: pytest.MonkeyPatch, cursor: list[int]
) -> None:
    """Com a seta para a direita, a cobra anda da coluna 15 até a borda, na 39."""
    _sortear_frutas(monkeypatch, 1, 1)
    janela = _FakeJanela(altura=20, largura=40, teclas=(curses.KEY_RIGHT,))

    main.ciclo_do_jogo(janela, 35)  # type: ignore[arg-type]

    assert janela.limpezas == 24
    _, _, texto, _ = janela.chamadas_addstr[0]
    assert texto == " Fim de Jogo! Frutas coletadas: 0 "
