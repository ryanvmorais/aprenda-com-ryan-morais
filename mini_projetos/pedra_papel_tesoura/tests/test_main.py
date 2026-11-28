"""Testes para main.py.

Estratégia de isolamento: `limpar_tela` é sempre mockada (chama `os.system`,
efeito de terminal irrelevante para a lógica testada). `input()` é mockado via
`monkeypatch.setattr("builtins.input", ...)` para simular a digitação do
usuário sem bloquear a suíte. `random.choice` é mockado quando o teste precisa
de uma jogada determinística do computador.
"""

from __future__ import annotations

import random
from collections.abc import Iterator

import pytest

from main import PedraPapelTesoura, main

pytestmark = pytest.mark.usefixtures("_sem_tela")


@pytest.fixture
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte."""
    monkeypatch.setattr(PedraPapelTesoura, "limpar_tela", lambda self: None)


@pytest.fixture
def jogo() -> PedraPapelTesoura:
    """Retorna:
    PedraPapelTesoura: Instância nova, com placar zerado.
    """
    return PedraPapelTesoura()


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
# __init__
# ---------------------------------------------------------------------------


def test_init_comeca_com_placar_zerado(jogo: PedraPapelTesoura) -> None:
    assert jogo.pontos_usuario == 0
    assert jogo.pontos_computador == 0
    assert jogo.opcoes == ["pedra", "papel", "tesoura"]


# ---------------------------------------------------------------------------
# realizar_jogada_usuario
# ---------------------------------------------------------------------------


def test_realizar_jogada_usuario_aceita_entrada_valida(
    jogo: PedraPapelTesoura, monkeypatch: pytest.MonkeyPatch
) -> None:
    _digitar(monkeypatch, "1")
    jogo.realizar_jogada_usuario()
    assert jogo.jogada_usuario == "papel"


# O "-1" e o "3" ficam um passo fora de cada ponta de 0-2 (o "-1" viraria o
# índice da última opção, "tesoura").
@pytest.mark.parametrize("fora", ["-1", "3", "5"])
def test_realizar_jogada_usuario_repete_apos_numero_fora_do_intervalo(
    jogo: PedraPapelTesoura,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fora: str,
) -> None:
    """Entrada fora de 0-2 não deve travar: o loop pede de novo até validar."""
    _digitar(monkeypatch, fora, "0")
    jogo.realizar_jogada_usuario()
    assert jogo.jogada_usuario == "pedra"
    assert capsys.readouterr().out.count("Opção inválida!") == 1


def test_realizar_jogada_usuario_repete_apos_entrada_nao_numerica(
    jogo: PedraPapelTesoura, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Letra digitada no lugar do número não deve travar (ValueError tratado)."""
    _digitar(monkeypatch, "abc", "2")
    jogo.realizar_jogada_usuario()
    assert jogo.jogada_usuario == "tesoura"


# ---------------------------------------------------------------------------
# realizar_jogada_computador
# ---------------------------------------------------------------------------


def test_realizar_jogada_computador_sorteia_entre_as_opcoes(
    jogo: PedraPapelTesoura, monkeypatch: pytest.MonkeyPatch
) -> None:
    recebidas: list[list[str]] = []

    def _choice_falso(opcoes: list[str]) -> str:
        recebidas.append(list(opcoes))
        return "tesoura"

    monkeypatch.setattr(random, "choice", _choice_falso)
    jogo.realizar_jogada_computador()
    assert jogo.jogada_computador == "tesoura"
    # O sorteio é entre as três opções, não um recorte delas.
    assert recebidas == [["pedra", "papel", "tesoura"]]


# ---------------------------------------------------------------------------
# determinar_vencedor
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("jogada", ["pedra", "papel", "tesoura"])
def test_determinar_vencedor_empate(jogo: PedraPapelTesoura, jogada: str) -> None:
    jogo.jogada_usuario = jogada
    jogo.jogada_computador = jogada

    resultado = jogo.determinar_vencedor()

    assert "EMPATE" in resultado
    assert jogo.pontos_usuario == 0
    assert jogo.pontos_computador == 0


@pytest.mark.parametrize(
    ("jogada_usuario", "jogada_computador"),
    [("pedra", "tesoura"), ("papel", "pedra"), ("tesoura", "papel")],
)
def test_determinar_vencedor_usuario_vence(
    jogo: PedraPapelTesoura, jogada_usuario: str, jogada_computador: str
) -> None:
    jogo.jogada_usuario = jogada_usuario
    jogo.jogada_computador = jogada_computador

    resultado = jogo.determinar_vencedor()

    assert "VOCÊ VENCEU" in resultado
    assert jogo.pontos_usuario == 1
    assert jogo.pontos_computador == 0


@pytest.mark.parametrize(
    ("jogada_usuario", "jogada_computador"),
    [("tesoura", "pedra"), ("pedra", "papel"), ("papel", "tesoura")],
)
def test_determinar_vencedor_computador_vence(
    jogo: PedraPapelTesoura, jogada_usuario: str, jogada_computador: str
) -> None:
    jogo.jogada_usuario = jogada_usuario
    jogo.jogada_computador = jogada_computador

    resultado = jogo.determinar_vencedor()

    assert "COMPUTADOR VENCEU" in resultado
    assert jogo.pontos_usuario == 0
    assert jogo.pontos_computador == 1


def test_determinar_vencedor_acumula_placar_entre_rodadas(
    jogo: PedraPapelTesoura,
) -> None:
    """O placar não deve zerar entre rodadas — só a instância nova zera."""
    jogo.jogada_usuario = "pedra"
    jogo.jogada_computador = "tesoura"
    jogo.determinar_vencedor()

    jogo.jogada_usuario = "papel"
    jogo.jogada_computador = "tesoura"
    jogo.determinar_vencedor()

    assert jogo.pontos_usuario == 1
    assert jogo.pontos_computador == 1


# ---------------------------------------------------------------------------
# exibir_placar
# ---------------------------------------------------------------------------


def test_exibir_placar_sem_resultado_nao_mostra_ultima_rodada(
    jogo: PedraPapelTesoura, capsys: pytest.CaptureFixture[str]
) -> None:
    # Placares diferentes: trocar os dois pontos de lugar muda a linha.
    jogo.pontos_usuario = 2
    jogo.pontos_computador = 1

    jogo.exibir_placar()

    saida = capsys.readouterr().out
    assert "PLACAR: Você 2 x 1 Computador" in saida
    assert "ÚLTIMA RODADA" not in saida


def test_exibir_placar_com_resultado_mostra_as_jogadas(
    jogo: PedraPapelTesoura, capsys: pytest.CaptureFixture[str]
) -> None:
    jogo.jogada_usuario = "pedra"
    jogo.jogada_computador = "tesoura"

    jogo.exibir_placar("🎉 VOCÊ VENCEU A RODADA!")

    linhas = capsys.readouterr().out.splitlines()
    inicio = linhas.index("ÚLTIMA RODADA:")
    assert linhas[inicio + 1 : inicio + 4] == [
        "Você escolheu: PEDRA",
        "Computador escolheu: TESOURA",
        "👉 🎉 VOCÊ VENCEU A RODADA!",
    ]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_joga_ate_o_nao_e_mostra_o_placar_final(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Duas rodadas (vitória e derrota), uma resposta inválida no replay e o fim."""
    # Rodada 1: pedra contra tesoura (vitória). Rodada 2: pedra contra papel.
    sorteios = iter(["tesoura", "papel"])
    monkeypatch.setattr(random, "choice", lambda _opcoes: next(sorteios))
    _digitar(monkeypatch, "0", "0", "0", "talvez", "1")

    main()

    saida = capsys.readouterr().out
    assert "🎉 VOCÊ VENCEU A RODADA!" in saida
    assert "😢 O COMPUTADOR VENCEU A RODADA!" in saida
    assert saida.count("Resposta inválida. Digite 0 ou 1.") == 1
    assert saida.splitlines()[-2:] == [
        "Sessão encerrada com placar de 1 x 1.",
        "Até a próxima! 👋",
    ]


def test_main_sai_no_1_sem_jogar_outra_rodada(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Com "1" na primeira pergunta, a sessão acaba depois de uma rodada só."""
    monkeypatch.setattr(random, "choice", lambda _opcoes: "tesoura")
    _digitar(monkeypatch, "0", "1")

    main()

    saida = capsys.readouterr().out
    assert saida.count("Computador escolheu: TESOURA") == 1
    assert "Sessão encerrada com placar de 1 x 0." in saida
