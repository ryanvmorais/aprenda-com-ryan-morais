"""Testes para main.py.

Estratégia de isolamento: quase todas as funções do programa são puras, e os
testes as chamam com um valor e conferem o que elas devolvem. O sorteio do
gerador entra por parâmetro: os testes passam `random.Random(2026).randrange`,
de semente fixa, ou um sorteador falso que devolve uma sequência escolhida, sem
`monkeypatch` em `random`. O teclado de `main()` é um `LeitorFalso` (devolve as
respostas na ordem e guarda cada pedido), sem `monkeypatch` em `input`, e a
saída se confere com o `capsys`. O único `monkeypatch` da suíte troca
`limpar_tela` por um no-op, porque ela chama `os.system`, um efeito de terminal.

Os CPFs dos testes são só o exemplo da Receita Federal (280.012.389-38),
variações inválidas dele, as sequências repetidas e os gerados pela semente fixa,
nunca o CPF de uma pessoa conhecida.
"""

from __future__ import annotations

import ast
import random
import unicodedata
from collections.abc import Iterator
from pathlib import Path

import pytest

import main as modulo_main
from main import (
    AVISO_GERADO,
    OPCOES,
    REGIOES_FISCAIS,
    Conferencia,
    Conta,
    calcular_digito,
    calcular_digitos,
    conferir_cpf,
    conferir_opcao,
    descrever_conta,
    descrever_gerado,
    descrever_regiao,
    descrever_resultado,
    eh_sequencia_repetida,
    exibir_tela,
    explicar_validacao,
    formatar_cpf,
    gerar_cpf,
    limpar_cpf,
    main,
)

# A largura máxima de cada linha do programa, para o quadro caber num terminal
# estreito.
LARGURA_MAXIMA = 54

# O exemplo resolvido do Anexo II do ADE Cofis nº 41/2017, da Receita Federal.
BASE_RECEITA = [2, 8, 0, 0, 1, 2, 3, 8, 9]
CPF_RECEITA = "28001238938"


def algarismos(texto: str) -> list[int]:
    """Converte um texto de algarismos numa lista de `int`.

    Args:
        texto (str): Só algarismos de 0 a 9.

    Returns:
        list[int]: Um `int` por algarismo, na mesma ordem.
    """
    return [int(caractere) for caractere in texto]


def digito_forma_divulgada(numeros: list[int]) -> int:
    """Calcula um dígito verificador pela forma mais divulgada.

    Pesos de 10 a 2 (1º dígito) ou de 11 a 2 (2º dígito), e o dígito é 11 menos
    o resto, com 10 e 11 valendo 0. Serve de referência para o teste de
    equivalência com a forma da Receita Federal.

    Args:
        numeros (list[int]): Os 9 ou 10 algarismos da conta.

    Returns:
        int: O dígito verificador.
    """
    pesos = range(len(numeros) + 1, 1, -1)
    soma = sum(numero * peso for numero, peso in zip(numeros, pesos))
    digito = 11 - soma % 11
    return 0 if digito >= 10 else digito


class SorteadorFalso:
    """Simula o sorteio: devolve os valores na ordem e guarda cada `n` recebido.

    Attributes:
        pedidos (list[int]): O `n` de cada sorteio pedido, na ordem.
    """

    def __init__(self, *valores: int) -> None:
        """Guarda os valores a devolver.

        Args:
            *valores (int): Valores a devolver, um por chamada.
        """
        self._valores: Iterator[int] = iter(valores)
        self.pedidos: list[int] = []

    def __call__(self, n: int) -> int:
        """Registra o pedido e devolve o próximo valor.

        Args:
            n (int): O limite do sorteio (o valor sai de 0 a `n - 1`).

        Returns:
            int: O próximo valor da sequência.
        """
        self.pedidos.append(n)
        return next(self._valores)


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

    Os caracteres largos (como ✅ e 🎲) ocupam duas colunas, e o seletor de
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


@pytest.fixture(autouse=True)
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte.

    `limpar_tela` chama `os.system`, que limparia o terminal de quem roda os testes.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


# ---------------------------------------------------------------------------
# calcular_digito e calcular_digitos
# ---------------------------------------------------------------------------


def test_calcular_digito_mostra_cada_passo_do_exemplo_da_receita() -> None:
    assert calcular_digito(BASE_RECEITA) == Conta(
        algarismos=BASE_RECEITA,
        pesos=[1, 2, 3, 4, 5, 6, 7, 8, 9],
        produtos=[2, 16, 0, 0, 5, 12, 21, 64, 81],
        soma=201,
        resto=3,
        digito=3,
    )


def test_calcular_digito_usa_os_pesos_de_0_a_9_no_segundo_digito() -> None:
    conta = calcular_digito(BASE_RECEITA + [3])
    assert conta.pesos == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert conta.produtos == [0, 8, 0, 0, 4, 10, 18, 56, 72, 27]
    assert (conta.soma, conta.resto, conta.digito) == (195, 8, 8)


def test_calcular_digitos_do_exemplo_da_receita_da_38() -> None:
    primeira, segunda = calcular_digitos(BASE_RECEITA)
    assert (primeira.digito, segunda.digito) == (3, 8)
    assert segunda.algarismos == BASE_RECEITA + [3]


# Bases montadas a partir da base da Receita, trocando um algarismo, para cair
# em cada resto que pede atenção.
@pytest.mark.parametrize(
    ("base", "resto", "digito"),
    [
        ("280012385", 0, 0),
        ("280012359", 1, 1),
        ("280012380", 10, 0),
    ],
)
def test_calcular_digito_nos_restos_0_1_e_10(
    base: str, resto: int, digito: int
) -> None:
    conta = calcular_digito(algarismos(base))
    assert (conta.resto, conta.digito) == (resto, digito)


def test_forma_da_receita_equivale_a_forma_mais_divulgada() -> None:
    # 10.000 bases de semente fixa: a mesma lista em toda execução.
    sorteio = random.Random(2026)
    for _ in range(10_000):
        base = [sorteio.randrange(10) for _ in range(9)]
        primeira, segunda = calcular_digitos(base)
        assert primeira.digito == digito_forma_divulgada(base)
        assert segunda.digito == digito_forma_divulgada(base + [primeira.digito])


# ---------------------------------------------------------------------------
# limpar_cpf
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "entrada",
    [
        "28001238938",
        "280.012.389-38",
        "280 012 389 38",
        "  280.012.389-38  ",
        "2.8-0 0.1-2 3.8-9 3.8",
    ],
)
def test_limpar_cpf_aceita_com_ou_sem_pontuacao(entrada: str) -> None:
    assert limpar_cpf(entrada) == Conferencia(CPF_RECEITA, "")


@pytest.mark.parametrize(
    ("entrada", "caractere"),
    [
        ("280.012.389-3a", "a"),
        ("280.012.389/38", "/"),
        ("280.012.389-3²", "²"),
        ("280.012.389-3٣", "٣"),
    ],
)
def test_limpar_cpf_recusa_o_caractere_que_nao_e_algarismo(
    entrada: str, caractere: str
) -> None:
    assert limpar_cpf(entrada) == Conferencia(
        "", f'❌ CPF inválido\n   "{caractere}" não é um algarismo.'
    )


@pytest.mark.parametrize(
    ("entrada", "quantidade"),
    [("2800123893", 10), ("280.012.389-380", 12)],
)
def test_limpar_cpf_recusa_a_quantidade_errada_sem_completar_com_zeros(
    entrada: str, quantidade: int
) -> None:
    assert limpar_cpf(entrada) == Conferencia(
        "", f"❌ CPF inválido\n   Um CPF tem 11 algarismos, e este tem {quantidade}."
    )


@pytest.mark.parametrize("entrada", ["", "   ", ".-.-", " . - "])
def test_limpar_cpf_avisa_que_nenhum_cpf_foi_digitado(entrada: str) -> None:
    assert limpar_cpf(entrada) == Conferencia("", "⚠️ Nenhum CPF digitado.")


def test_limpar_cpf_recusa_o_caractere_antes_da_quantidade() -> None:
    # Curto e com letra: a letra é o motivo, como na ordem do design.
    assert '"x" não é um algarismo' in limpar_cpf("12x").recusa


# ---------------------------------------------------------------------------
# eh_sequencia_repetida e conferir_cpf
# ---------------------------------------------------------------------------


SEQUENCIAS = [algarismo * 11 for algarismo in "0123456789"]


@pytest.mark.parametrize("cpf", SEQUENCIAS)
def test_eh_sequencia_repetida_nas_dez_sequencias(cpf: str) -> None:
    assert eh_sequencia_repetida(cpf)


def test_eh_sequencia_repetida_falso_com_um_algarismo_diferente() -> None:
    assert not eh_sequencia_repetida("11111111112")


@pytest.mark.parametrize("cpf", SEQUENCIAS)
def test_conferir_cpf_recusa_a_sequencia_repetida_que_passa_na_conta(
    cpf: str,
) -> None:
    # A conta confere nas dez sequências: a recusa vem só da regra do RF-05.
    primeira, segunda = calcular_digitos(algarismos(cpf[:9]))
    assert cpf[9:] == f"{primeira.digito}{segunda.digito}"

    assert conferir_cpf(cpf) == Conferencia(
        "",
        f"❌ CPF inválido: {formatar_cpf(cpf)}\n"
        "   Sequência repetida: passa na conta, mas é recusada.",
    )


@pytest.mark.parametrize("entrada", ["28001238938", "280.012.389-38"])
def test_conferir_cpf_aceita_o_exemplo_da_receita(entrada: str) -> None:
    assert conferir_cpf(entrada) == Conferencia(CPF_RECEITA, "")


@pytest.mark.parametrize(
    ("entrada", "formatado"),
    [
        ("28001238948", "280.012.389-48"),
        ("280.012.389-39", "280.012.389-39"),
        ("28001238983", "280.012.389-83"),
    ],
)
def test_conferir_cpf_recusa_o_digito_errado_sem_dar_os_certos(
    entrada: str, formatado: str
) -> None:
    # A mensagem traz só o número digitado: nada do "38" que seria o certo.
    assert conferir_cpf(entrada) == Conferencia(
        "",
        f"❌ CPF inválido: {formatado}\n   Os dígitos verificadores não conferem.",
    )


def test_conferir_cpf_repassa_a_recusa_da_limpeza() -> None:
    assert conferir_cpf("280.012.389-3a") == limpar_cpf("280.012.389-3a")


# ---------------------------------------------------------------------------
# formatar_cpf e descrever_regiao
# ---------------------------------------------------------------------------


def test_formatar_cpf_com_pontos_e_hifen() -> None:
    assert formatar_cpf(CPF_RECEITA) == "280.012.389-38"


def test_formatar_cpf_mantem_o_zero_a_esquerda() -> None:
    assert formatar_cpf("00000000000") == "000.000.000-00"


# A tabela fica escrita aqui, e não lida do `REGIOES_FISCAIS`: comparar o
# programa com ele mesmo deixaria passar duas regiões trocadas.
@pytest.mark.parametrize(
    ("regiao", "estados"),
    [
        (0, "RS"),
        (1, "DF, GO, MS, MT e TO"),
        (2, "AC, AM, AP, PA, RO e RR"),
        (3, "CE, MA e PI"),
        (4, "AL, PB, PE e RN"),
        (5, "BA e SE"),
        (6, "MG"),
        (7, "ES e RJ"),
        (8, "SP"),
        (9, "PR e SC"),
    ],
)
def test_descrever_regiao_pelo_nono_algarismo(regiao: int, estados: str) -> None:
    cpf = f"28001238{regiao}38"
    assert descrever_regiao(cpf) == f"Região fiscal {regiao}: {estados}"


def test_descrever_regiao_do_exemplo_da_receita() -> None:
    assert descrever_regiao(CPF_RECEITA) == "Região fiscal 9: PR e SC"


def test_regioes_fiscais_cobrem_os_27_estados() -> None:
    siglas = [
        sigla
        for estados in REGIOES_FISCAIS.values()
        for sigla in estados.replace(" e ", ", ").split(", ")
    ]
    assert len(siglas) == len(set(siglas)) == 27


# ---------------------------------------------------------------------------
# gerar_cpf
# ---------------------------------------------------------------------------


def test_gerar_cpf_sempre_passa_na_conferencia() -> None:
    sortear = random.Random(2026).randrange
    for _ in range(1_000):
        cpf = gerar_cpf(sortear)
        assert conferir_cpf(cpf) == Conferencia(cpf, "")


def test_gerar_cpf_sorteia_de_novo_a_base_repetida() -> None:
    # Nove 7 seguidos formam uma base repetida; a segunda base é a da Receita.
    sortear = SorteadorFalso(*([7] * 9), *BASE_RECEITA)
    assert gerar_cpf(sortear) == CPF_RECEITA
    assert sortear.pedidos == [10] * 18


def test_aviso_gerado_nao_chama_o_numero_de_ficticio() -> None:
    assert "pessoa real" in AVISO_GERADO
    assert "fictício" not in AVISO_GERADO


# ---------------------------------------------------------------------------
# descrever_resultado e descrever_gerado
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada", ["28001238938", "280.012.389-38"])
def test_descrever_resultado_do_cpf_valido_com_a_regiao(entrada: str) -> None:
    assert descrever_resultado(entrada) == (
        "✅ CPF válido: 280.012.389-38\nRegião fiscal 9: PR e SC"
    )


@pytest.mark.parametrize(
    "entrada",
    ["280.012.389-39", "111.111.111-11", "2800123893", "280.012.389-3a", "", "-"],
)
def test_descrever_resultado_repassa_cada_motivo_de_recusa(entrada: str) -> None:
    assert descrever_resultado(entrada) == conferir_cpf(entrada).recusa


def test_descrever_gerado_com_o_numero_a_regiao_e_o_aviso() -> None:
    assert descrever_gerado(CPF_RECEITA) == (
        "🎲 CPF gerado: 280.012.389-38\n" "Região fiscal 9: PR e SC\n" f"{AVISO_GERADO}"
    )


# ---------------------------------------------------------------------------
# descrever_conta e explicar_validacao
# ---------------------------------------------------------------------------


def test_descrever_conta_do_primeiro_digito_da_receita() -> None:
    primeira, _ = calcular_digitos(BASE_RECEITA)
    assert descrever_conta(primeira, 3, 1).splitlines() == [
        "1º dígito verificador",
        "Algarismos   2   8   0   0   1   2   3   8   9",
        "Pesos        1   2   3   4   5   6   7   8   9",
        "Produtos     2  16   0   0   5  12  21  64  81",
        "Soma 201 ÷ 11 = 18, resto 3 → dígito 3",
        "Digitado: 3 ✅ confere",
    ]


def test_descrever_conta_do_segundo_digito_da_receita() -> None:
    _, segunda = calcular_digitos(BASE_RECEITA)
    assert descrever_conta(segunda, 8, 2).splitlines() == [
        "2º dígito verificador",
        "Algarismos   2   8   0   0   1   2   3   8   9   3",
        "Pesos        0   1   2   3   4   5   6   7   8   9",
        "Produtos     0   8   0   0   4  10  18  56  72  27",
        "Soma 195 ÷ 11 = 17, resto 8 → dígito 8",
        "Digitado: 8 ✅ confere",
    ]


def test_descrever_conta_marca_o_digito_que_nao_confere() -> None:
    primeira, _ = calcular_digitos(BASE_RECEITA)
    assert descrever_conta(primeira, 4, 1).endswith("Digitado: 4 ❌ não confere")


def test_descrever_conta_explica_o_resto_10() -> None:
    conta = calcular_digito(algarismos("280012380"))
    assert "resto 10 → dígito 0 (10 vale 0)" in descrever_conta(conta, 0, 1)


def test_explicar_validacao_mostra_as_duas_contas_e_o_resultado() -> None:
    texto = explicar_validacao("280.012.389-38")
    primeira, segunda = calcular_digitos(BASE_RECEITA)
    assert texto == "\n\n".join(
        [
            descrever_conta(primeira, 3, 1),
            descrever_conta(segunda, 8, 2),
            descrever_resultado(CPF_RECEITA),
        ]
    )


def test_explicar_validacao_marca_o_digito_errado_e_recusa() -> None:
    texto = explicar_validacao("280.012.389-48")
    assert "Digitado: 4 ❌ não confere" in texto
    assert "Digitado: 8 ✅ confere" in texto
    assert texto.endswith(conferir_cpf("280.012.389-48").recusa)


def test_explicar_validacao_da_sequencia_repetida_confere_e_recusa() -> None:
    texto = explicar_validacao("111.111.111-11")
    assert texto.count("✅ confere") == 2
    assert "❌ não confere" not in texto
    assert texto.endswith("Sequência repetida: passa na conta, mas é recusada.")


@pytest.mark.parametrize("entrada", ["280.012.389-3a", "2800123893", ""])
def test_explicar_validacao_da_entrada_recusada_sem_conta(entrada: str) -> None:
    assert explicar_validacao(entrada) == limpar_cpf(entrada).recusa


# ---------------------------------------------------------------------------
# conferir_opcao
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("opcao", range(1, len(OPCOES) + 1))
def test_conferir_opcao_aceita_cada_opcao(opcao: int) -> None:
    assert conferir_opcao(f" {opcao} ") == opcao


# O "0" e o "5" ficam um passo fora de cada ponta do menu.
@pytest.mark.parametrize("entrada", ["", "  ", "0", "5", "9", "abc", "²", "-1", "1.0"])
def test_conferir_opcao_recusa_o_resto(entrada: str) -> None:
    assert conferir_opcao(entrada) is None


# ---------------------------------------------------------------------------
# Largura das linhas
# ---------------------------------------------------------------------------


def textos_do_programa() -> list[str]:
    """Junta um texto de cada tipo que o programa mostra entre o título e o menu.

    Returns:
        list[str]: Os resultados, as contas e os CPFs gerados.
    """
    entradas = [
        "280.012.389-38",
        "280.012.389-48",
        "280.012.389-39",
        "111.111.111-11",
        "2800123893",
        "280.012.389-3a",
        "",
    ]
    textos = [descrever_resultado(entrada) for entrada in entradas]
    textos += [explicar_validacao(entrada) for entrada in entradas]
    # O resto 10 dá a linha mais longa da conta.
    textos.append(explicar_validacao("28001238038"))
    sortear = random.Random(2026).randrange
    textos += [descrever_gerado(gerar_cpf(sortear)) for _ in range(100)]
    return textos


def test_nenhuma_linha_dos_textos_passa_da_largura_maxima() -> None:
    for texto in textos_do_programa():
        for linha in texto.splitlines():
            assert colunas(linha) <= LARGURA_MAXIMA, linha


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
    return saida[saida.rindex("VALIDADOR DE CPF") :]


def test_main_mostra_titulo_resultado_e_menu_nessa_ordem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("1", "280.012.389-38", "4")
    main(leitor, random.Random(2026).randrange)

    tela = ultima_tela(capsys.readouterr().out)
    assert tela.index("✅ CPF válido: 280.012.389-38") < tela.index("1 : Validar")
    assert tela.index("Região fiscal 9: PR e SC") < tela.index("4 : Sair")
    assert leitor.pedidos == [
        "Escolha uma opção: ",
        "Digite o CPF: ",
        "Escolha uma opção: ",
    ]


def test_main_primeira_tela_sem_resultado(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("4"), random.Random(2026).randrange)
    saida = capsys.readouterr().out
    assert saida.startswith("======== VALIDADOR DE CPF ========\n\n1 : Validar um CPF")


def test_main_modo_didatico_mostra_a_conta(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("2", "28001238938", "4"), random.Random(2026).randrange)
    tela = ultima_tela(capsys.readouterr().out)
    assert explicar_validacao("28001238938") in tela


def test_main_gera_um_cpf_valido_com_o_aviso(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main(LeitorFalso("3", "4"), random.Random(2026).randrange)
    tela = ultima_tela(capsys.readouterr().out)
    esperado = gerar_cpf(random.Random(2026).randrange)
    assert descrever_gerado(esperado) in tela
    assert conferir_cpf(esperado).valor == esperado


@pytest.mark.parametrize("entrada", ["", "0", "9", "abc", "²"])
def test_main_recusa_a_opcao_invalida(
    capsys: pytest.CaptureFixture[str], entrada: str
) -> None:
    main(LeitorFalso(entrada, "4"), random.Random(2026).randrange)
    tela = ultima_tela(capsys.readouterr().out)
    assert "❌ Opção inválida. Digite um número de 1 a 4." in tela


def test_main_sai_pelo_menu_com_despedida(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("4"), random.Random(2026).randrange)
    assert capsys.readouterr().out.endswith("Até a próxima! 👋\n")


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
@pytest.mark.parametrize("respostas", [(), ("1",), ("2",)])
def test_main_sai_sem_stack_trace(
    capsys: pytest.CaptureFixture[str],
    excecao: type[BaseException],
    respostas: tuple[str, ...],
) -> None:
    # Interrompe no menu ou no meio, quando o CPF é pedido: `main` volta sem
    # deixar a exceção escapar.
    main(LeitorQueInterrompe(excecao, *respostas), random.Random(2026).randrange)
    saida = capsys.readouterr().out
    assert saida.endswith("\nValidador encerrado. Até a próxima! 👋\n")


# ---------------------------------------------------------------------------
# O CPF não sai da tela
# ---------------------------------------------------------------------------


# O `os` e o `sys` também abrem caminho para o disco (`os.open`, `os.popen`,
# `os.remove`) e para a linha de comando (`sys.argv`): deles, só o que o
# programa usa para limpar a tela e reconfigurar a saída.
ATRIBUTOS_PREVISTOS = {("os", "name"), ("os", "system"), ("sys", "stdout")}


def inventariar(fonte: str) -> tuple[set[str], set[str], set[tuple[str, str]]]:
    """Lista os módulos, as chamadas por nome e os atributos de `os` e `sys`.

    Args:
        fonte (str): O código Python a examinar.

    Returns:
        tuple[set[str], set[str], set[tuple[str, str]]]: Os módulos importados,
            os nomes chamados direto (como `open`) e cada par (módulo, nome)
            de `os` e `sys`, lido como `os.popen` ou importado com
            `from os import popen`.
    """
    modulos: set[str] = set()
    chamadas: set[str] = set()
    atributos: set[tuple[str, str]] = set()
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.Import):
            modulos.update(apelido.name for apelido in no.names)
        elif isinstance(no, ast.ImportFrom):
            modulos.add(no.module or "")
            atributos.update((no.module or "", apelido.name) for apelido in no.names)
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            chamadas.add(no.func.id)
        elif isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name):
            atributos.add((no.value.id, no.attr))
    return modulos, chamadas, {par for par in atributos if par[0] in ("os", "sys")}


def test_inventariar_acusa_o_que_abre_arquivo_ou_le_a_linha_de_comando() -> None:
    # O controle do teste abaixo: cada forma que ele recusa aparece aqui.
    fonte = (
        "import os\n"
        "import sys\n"
        "from os import remove\n"
        "open('cpf.txt', 'w')\n"
        "os.popen('echo')\n"
        "os.open('cpf.txt', os.O_CREAT)\n"
        "print(sys.argv)\n"
    )
    modulos, chamadas, atributos = inventariar(fonte)
    assert modulos == {"os", "sys"}
    assert "open" in chamadas
    assert atributos == {
        ("os", "remove"),
        ("os", "popen"),
        ("os", "open"),
        ("os", "O_CREAT"),
        ("sys", "argv"),
    }


def test_main_py_so_importa_os_modulos_previstos_e_nao_abre_arquivo() -> None:
    fonte = Path(modulo_main.__file__).read_text(encoding="utf-8")
    modulos, chamadas, atributos = inventariar(fonte)

    previstos = {"__future__", "collections.abc", "os", "random", "sys", "typing"}
    assert modulos <= previstos
    assert "open" not in chamadas
    assert atributos <= ATRIBUTOS_PREVISTOS
