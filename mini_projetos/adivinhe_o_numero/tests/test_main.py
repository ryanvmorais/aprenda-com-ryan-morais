"""Testes para main.py.

Estratégia de isolamento: o teclado e o sorteio entram nas funções do jogo por
parâmetro, então cada teste passa um `LeitorFalso` (devolve as respostas na
ordem e guarda cada pedido) e um `SorteadorFalso` (devolve um número fixo e
guarda os extremos recebidos), sem `monkeypatch` em `input` ou `random`. A saída
se confere com o `capsys`. O único `monkeypatch` da suíte troca `limpar_tela`
por um no-op, porque ela chama `os.system`, um efeito de terminal.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import main as modulo_main
from main import (
    NIVEIS,
    atualizar_recorde,
    escolher_nivel,
    exibir_recordes,
    jogar_partida,
    ler_palpite,
    perguntar_jogar_de_novo,
)

# Atalhos para os níveis mais usados nos testes (faixas 1-50 e 1-100).
FACIL = NIVEIS["1"]
MEDIO = NIVEIS["2"]


@pytest.fixture(autouse=True)
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte.

    `limpar_tela` chama `os.system`, que limparia o terminal de quem roda os testes.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


class SorteadorFalso:
    """Simula o sorteio: devolve sempre o mesmo número e guarda os extremos.

    Attributes:
        extremos (list[tuple[int, int]]): Faixa recebida em cada sorteio.
    """

    def __init__(self, numero: int) -> None:
        """Guarda o número a devolver.

        Args:
            numero (int): Número "sorteado" em toda chamada.
        """
        self._numero = numero
        self.extremos: list[tuple[int, int]] = []

    def __call__(self, minimo: int, maximo: int) -> int:
        """Registra a faixa e devolve o número fixo.

        Args:
            minimo (int): Menor número que poderia ser sorteado.
            maximo (int): Maior número que poderia ser sorteado.

        Returns:
            int: O número fixo.
        """
        self.extremos.append((minimo, maximo))
        return self._numero


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


# ---------------------------------------------------------------------------
# escolher_nivel
# ---------------------------------------------------------------------------


def test_escolher_nivel_mostra_as_tres_opcoes_com_faixa_e_limite(
    capsys: pytest.CaptureFixture[str],
) -> None:
    escolher_nivel(LeitorFalso("1"))
    saida = capsys.readouterr().out
    assert "1 - Fácil   (1 a 50, 10 tentativas)" in saida
    assert "2 - Médio   (1 a 100, 8 tentativas)" in saida
    assert "3 - Difícil (1 a 1000, 10 tentativas)" in saida


@pytest.mark.parametrize(
    ("tecla", "nome"), [("1", "fácil"), ("2", "médio"), ("3", "difícil")]
)
def test_escolher_nivel_devolve_o_nivel_da_tecla(tecla: str, nome: str) -> None:
    assert escolher_nivel(LeitorFalso(tecla)).nome == nome


@pytest.mark.parametrize("invalida", ["4", "0", "abc", ""])
def test_escolher_nivel_repete_o_pedido_na_opcao_invalida(
    invalida: str, capsys: pytest.CaptureFixture[str]
) -> None:
    leitor = LeitorFalso(invalida, "2")
    assert escolher_nivel(leitor) == NIVEIS["2"]
    assert "Opção inválida" in capsys.readouterr().out
    assert len(leitor.pedidos) == 2


# ---------------------------------------------------------------------------
# ler_palpite
# ---------------------------------------------------------------------------


def test_ler_palpite_aceita_inteiro_na_faixa() -> None:
    leitor = LeitorFalso("25")
    assert ler_palpite(FACIL, 1, leitor) == 25
    assert leitor.pedidos == ["Tentativa 1 de 10. Seu palpite: "]


@pytest.mark.parametrize("extremo", ["1", "50"])
def test_ler_palpite_aceita_os_extremos_da_faixa(extremo: str) -> None:
    assert ler_palpite(FACIL, 1, LeitorFalso(extremo)) == int(extremo)


@pytest.mark.parametrize("invalida", ["abc", "3.5", ""])
def test_ler_palpite_rejeita_o_que_nao_e_inteiro_sem_gastar_tentativa(
    invalida: str, capsys: pytest.CaptureFixture[str]
) -> None:
    leitor = LeitorFalso(invalida, "7")
    assert ler_palpite(FACIL, 3, leitor) == 7
    assert "Digite um número inteiro" in capsys.readouterr().out
    # O pedido repetido mostra o mesmo número de tentativa: a inválida não contou.
    assert leitor.pedidos == ["Tentativa 3 de 10. Seu palpite: "] * 2


@pytest.mark.parametrize("fora", ["0", "51", "-5"])
def test_ler_palpite_rejeita_fora_da_faixa_sem_gastar_tentativa(
    fora: str, capsys: pytest.CaptureFixture[str]
) -> None:
    leitor = LeitorFalso(fora, "50")
    assert ler_palpite(FACIL, 1, leitor) == 50
    assert "entre 1 e 50" in capsys.readouterr().out
    assert leitor.pedidos == ["Tentativa 1 de 10. Seu palpite: "] * 2


# ---------------------------------------------------------------------------
# atualizar_recorde
# ---------------------------------------------------------------------------


def test_atualizar_recorde_grava_o_primeiro_resultado_do_nivel() -> None:
    recordes: dict[str, int] = {}
    assert atualizar_recorde(recordes, "fácil", 5) is True
    assert recordes == {"fácil": 5}


def test_atualizar_recorde_troca_quando_usa_menos_tentativas() -> None:
    recordes = {"fácil": 5}
    assert atualizar_recorde(recordes, "fácil", 3) is True
    assert recordes == {"fácil": 3}


@pytest.mark.parametrize("tentativas", [5, 8])
def test_atualizar_recorde_mantem_no_empate_e_no_pior_resultado(
    tentativas: int,
) -> None:
    recordes = {"fácil": 5}
    assert atualizar_recorde(recordes, "fácil", tentativas) is False
    assert recordes == {"fácil": 5}


def test_atualizar_recorde_nao_mexe_nos_outros_niveis() -> None:
    recordes = {"fácil": 5}
    assert atualizar_recorde(recordes, "difícil", 9) is True
    assert recordes == {"fácil": 5, "difícil": 9}


# ---------------------------------------------------------------------------
# exibir_recordes
# ---------------------------------------------------------------------------


def test_exibir_recordes_sem_vitoria_mostra_traco_nos_tres_niveis(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_recordes({})
    saida = capsys.readouterr().out
    assert "  Fácil:   —" in saida
    assert "  Médio:   —" in saida
    assert "  Difícil: —" in saida


def test_exibir_recordes_mostra_o_recorde_na_ordem_do_menu(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_recordes({"difícil": 9, "médio": 3})
    linhas = capsys.readouterr().out.splitlines()[-3:]
    assert linhas == ["  Fácil:   —", "  Médio:   3", "  Difícil: 9"]


# ---------------------------------------------------------------------------
# perguntar_jogar_de_novo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("resposta", "esperado"),
    [("s", True), ("S", True), (" s ", True), ("n", False), ("N", False)],
)
def test_perguntar_jogar_de_novo_aceita_s_e_n_sem_diferenciar_caixa(
    resposta: str, esperado: bool
) -> None:
    assert perguntar_jogar_de_novo(LeitorFalso(resposta)) is esperado


def test_perguntar_jogar_de_novo_repete_na_resposta_invalida(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("talvez", "", "n")
    assert perguntar_jogar_de_novo(leitor) is False
    assert capsys.readouterr().out.count("Responda s (sim) ou n (não)") == 2
    assert len(leitor.pedidos) == 3


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
# jogar_partida
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tecla", ["1", "2", "3"])
def test_jogar_partida_sorteia_nos_extremos_da_faixa_do_nivel(tecla: str) -> None:
    nivel = NIVEIS[tecla]
    sorteador = SorteadorFalso(1)
    jogar_partida(nivel, None, sorteador, LeitorFalso("1"))
    assert sorteador.extremos == [(nivel.minimo, nivel.maximo)]


def test_jogar_partida_informa_a_faixa_e_o_limite(
    capsys: pytest.CaptureFixture[str],
) -> None:
    jogar_partida(MEDIO, None, SorteadorFalso(63), LeitorFalso("63"))
    saida = capsys.readouterr().out
    assert "Pensei num número de 1 a 100. Você tem 8 tentativas." in saida
    assert "recorde" not in saida


def test_jogar_partida_mostra_o_recorde_do_nivel_no_inicio(
    capsys: pytest.CaptureFixture[str],
) -> None:
    jogar_partida(MEDIO, 3, SorteadorFalso(63), LeitorFalso("63"))
    assert "Seu recorde neste nível: acerto na tentativa 3." in capsys.readouterr().out


def test_jogar_partida_da_as_dicas_com_as_tentativas_restantes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    jogar_partida(MEDIO, None, SorteadorFalso(63), LeitorFalso("50", "75", "63"))
    saida = capsys.readouterr().out
    assert "O número é maior que 50. Tentativas restantes: 7." in saida
    assert "O número é menor que 75. Tentativas restantes: 6." in saida


def test_jogar_partida_vence_na_primeira_tentativa(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert jogar_partida(MEDIO, None, SorteadorFalso(63), LeitorFalso("63")) == 1
    assert "Acertou na tentativa 1! O número era 63." in capsys.readouterr().out


def test_jogar_partida_vence_na_ultima_tentativa() -> None:
    palpites = ["1"] * 7 + ["63"]
    resultado = jogar_partida(MEDIO, None, SorteadorFalso(63), LeitorFalso(*palpites))
    assert resultado == MEDIO.limite


def test_jogar_partida_perde_e_revela_o_numero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso(*["1"] * MEDIO.limite)
    assert jogar_partida(MEDIO, None, SorteadorFalso(63), leitor) is None
    assert "Suas tentativas acabaram. O número era 63." in capsys.readouterr().out
    # Sem leitura a mais depois da última tentativa.
    assert len(leitor.pedidos) == MEDIO.limite


def test_jogar_partida_nao_conta_a_entrada_invalida_como_tentativa() -> None:
    palpites = ["abc", "0"] + ["1"] * 7 + ["63"]
    resultado = jogar_partida(MEDIO, None, SorteadorFalso(63), LeitorFalso(*palpites))
    assert resultado == MEDIO.limite


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_sessao_de_duas_partidas_guarda_o_recorde(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Partida 1: médio em 3 tentativas. Partida 2: médio em 2 (recorde batido).
    leitor = LeitorFalso("2", "50", "75", "63", "s", "2", "70", "63", "n")
    modulo_main.main(SorteadorFalso(63), leitor)
    saida = capsys.readouterr().out
    assert saida.count("Novo recorde no nível médio!") == 2
    assert "Seu recorde neste nível: acerto na tentativa 3." in saida
    assert saida.splitlines()[-4:] == [
        "  Fácil:   —",
        "  Médio:   2",
        "  Difícil: —",
        "Até a próxima! 👋",
    ]


def test_main_sem_recorde_novo_na_derrota_nem_no_empate(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Vitória em 1, empate em 1 e derrota no fácil: só a primeira é recorde.
    derrota = ["2"] * FACIL.limite
    leitor = LeitorFalso("1", "1", "s", "1", "1", "s", "1", *derrota, "n")
    modulo_main.main(SorteadorFalso(1), leitor)
    saida = capsys.readouterr().out
    assert saida.count("Novo recorde no nível fácil!") == 1
    assert "  Fácil:   1" in saida


def test_main_limpa_a_tela_antes_de_cada_partida(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chamadas: list[None] = []
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: chamadas.append(None))
    leitor = LeitorFalso("1", "1", "s", "1", "1", "n")
    modulo_main.main(SorteadorFalso(1), leitor)
    assert len(chamadas) == 2


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
def test_main_sai_com_despedida_sem_stack_trace(
    excecao: type[BaseException], capsys: pytest.CaptureFixture[str]
) -> None:
    modulo_main.main(SorteadorFalso(1), LeitorQueInterrompe(excecao))
    saida = capsys.readouterr()
    assert "Jogo encerrado. Até a próxima! 👋" in saida.out
    assert "Traceback" not in saida.out + saida.err
