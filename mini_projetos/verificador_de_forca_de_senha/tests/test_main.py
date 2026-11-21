"""Testes para main.py.

Estratégia de isolamento: quase todas as funções do programa são puras, e os
testes as chamam com um valor e conferem o que elas devolvem. As duas leituras
do teclado entram por parâmetro: o menu e a senha são `LeitorFalso` (devolvem as
respostas na ordem e guardam cada pedido), sem `monkeypatch` em `input` nem em
`getpass`, e a saída se confere com o `capsys`. A lista de senhas comuns também
entra por parâmetro: os testes de `main()` passam uma lista curta, e os da lista
lêem o `senhas_comuns.txt` de verdade. O único `monkeypatch` da suíte troca
`limpar_tela` por um no-op, porque ela chama `os.system`, um efeito de terminal.

As senhas dos testes são inventadas ou da lista de senhas comuns, nunca uma
senha em uso.
"""

from __future__ import annotations

import ast
import getpass
import hashlib
import inspect
import unicodedata
from collections.abc import Iterator
from pathlib import Path

import pytest

import main as modulo_main
from main import (
    ARQUIVO_SENHAS_COMUNS,
    EXEMPLOS,
    LIMITES,
    NOMES,
    OPCOES,
    TIPOS,
    Analise,
    achar_repeticoes,
    achar_sequencias,
    analisar,
    calcular_entropia,
    carregar_senhas_comuns,
    classificar,
    conferir_opcao,
    contar_caracteres,
    dar_nota,
    descrever_analise,
    descrever_entropia,
    descrever_exemplos,
    exibir_tela,
    faltam_caracteres,
    juntar_nomes,
    juntar_trechos,
    main,
    opcao_verificar,
    sugerir,
)

# A largura máxima de cada linha do programa, para o quadro caber num terminal
# estreito.
LARGURA_MAXIMA = 54

# O SHA-256 do `Portugese_Pwdb_common-password-list-top-150.txt` do repositório
# `danielmiessler/SecLists`, no commit fef30127d19485fb91f390a3c8c535aefbd50047.
SHA256_SENHAS_COMUNS = (
    "e827d8607d9812e0140be005fcff49d1a0a151cfa853e392127ae79d61fdaf38"
)

# Uma lista curta para os testes de `main()`, com a senha comum dos exemplos.
COMUNS_TESTE = {"123mudar", "flamengo", "brasil"}

# No formato da senha forte padrão do `gerador_de_senhas`: 16 caracteres com os
# quatro tipos, sem repetição nem sequência (16 × log2(94) ≈ 104,9 bits).
SENHA_FORTE = "Xk#9vQ2!mZp$7wL&"

# O pedido da senha, igual ao do `main.py`.
PEDIDO_SENHA = "Digite a senha (ela não aparece na tela): "

# A análise de uma senha forte, para os testes de `sugerir` trocarem um campo
# de cada vez com o `_replace`.
ANALISE_FORTE = Analise(
    tamanho=16,
    contam=16,
    tipos=list(TIPOS),
    alfabeto=94,
    bits=calcular_entropia(16, 94),
    repeticao=False,
    sequencia=False,
    comum=False,
    nota=4,
)


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

    Os caracteres largos (como 🔎 e 💡) ocupam duas colunas, e o seletor de
    emoji (U+FE0F, o que faz o ⚠ virar ⚠️) alarga o caractere anterior para duas.

    Args:
        linha (str): Uma linha de texto, sem "\\n".

    Returns:
        int: A largura da linha em colunas.
    """
    total = 0
    for caractere in linha:
        if caractere == "\ufe0f":
            total += 1
        elif unicodedata.east_asian_width(caractere) in ("W", "F"):
            total += 2
        elif not unicodedata.combining(caractere):
            total += 1
    return total


@pytest.fixture(autouse=True)
def sem_limpar_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Troca `limpar_tela` por um no-op, para os testes não chamarem `os.system`.

    Args:
        monkeypatch (pytest.MonkeyPatch): A fixture que desfaz a troca no fim.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


@pytest.fixture(scope="module")
def comuns() -> set[str]:
    """Lê a lista de senhas comuns de verdade, uma vez para o módulo.

    Returns:
        set[str]: As senhas do `senhas_comuns.txt`, em minúsculas.
    """
    return carregar_senhas_comuns(ARQUIVO_SENHAS_COMUNS)


# ---------------------------------------------------------------------------
# classificar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("abc", ["minúsculas"]),
        ("ABC", ["maiúsculas"]),
        ("123", ["números"]),
        ("@#!", ["símbolos"]),
        ("çãé", ["minúsculas"]),
        ("ÇÃÉ", ["maiúsculas"]),
        (" ", ["símbolos"]),
        ("!aZ9", ["minúsculas", "maiúsculas", "números", "símbolos"]),
        ("", []),
    ],
)
def test_classificar_acha_cada_tipo_na_ordem_dos_tipos(
    senha: str, esperado: list[str]
) -> None:
    assert classificar(senha) == esperado


def test_os_tipos_somam_94_caracteres() -> None:
    assert TIPOS == {"minúsculas": 26, "maiúsculas": 26, "números": 10, "símbolos": 32}


# ---------------------------------------------------------------------------
# Repetições e sequências
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("aaa", [(0, 3)]),
        ("1111", [(0, 4)]),
        ("aAa", [(0, 3)]),
        ("xaaay", [(1, 4)]),
        ("aaabbb", [(0, 3), (3, 6)]),
        ("aa", []),
        ("ab", []),
    ],
)
def test_achar_repeticoes(senha: str, esperado: list[tuple[int, int]]) -> None:
    assert achar_repeticoes(senha) == esperado


@pytest.mark.parametrize(
    "senha", ["abc", "cba", "123", "987", "qwe", "asd", "zxc", "ABC", "Abc", "ewq"]
)
def test_achar_sequencias_acha_cada_sequencia_e_o_contrario(senha: str) -> None:
    assert achar_sequencias(senha) == [(0, 3)]


@pytest.mark.parametrize(
    ("senha", "esperado"),
    [
        ("abcd", [(0, 3), (1, 4)]),
        ("x123y", [(1, 4)]),
        ("ab", []),
        ("aa", []),
        ("aaa", []),
        ("acb", []),
        ("", []),
    ],
)
def test_achar_sequencias_janelas(senha: str, esperado: list[tuple[int, int]]) -> None:
    assert achar_sequencias(senha) == esperado


@pytest.mark.parametrize(
    ("trechos", "esperado"),
    [
        ([(2, 5), (0, 3)], [(0, 5)]),
        ([(0, 3), (1, 4)], [(0, 4)]),
        ([(0, 3), (3, 6)], [(0, 3), (3, 6)]),
        ([(0, 6), (2, 5)], [(0, 6)]),
        ([], []),
    ],
)
def test_juntar_trechos(
    trechos: list[tuple[int, int]], esperado: list[tuple[int, int]]
) -> None:
    assert juntar_trechos(trechos) == esperado


def test_contar_caracteres_vale_um_por_trecho() -> None:
    assert contar_caracteres(10, [(0, 3), (5, 9)]) == 5
    assert contar_caracteres(10, []) == 10


@pytest.mark.parametrize(
    ("senha", "contam"),
    [
        ("aaa", 1),
        ("1111", 1),
        ("abc", 1),
        ("cba", 1),
        ("123", 1),
        ("987", 1),
        ("qwe", 1),
        ("asd", 1),
        ("ABC", 1),
        ("aAa", 1),
        ("aaabc", 1),
        ("aaabbb", 2),
        ("aa", 2),
        ("ab", 2),
        ("xabcdy", 3),
    ],
)
def test_analisar_desconta_os_trechos_previsiveis(senha: str, contam: int) -> None:
    analise = analisar(senha, set())
    assert analise.contam == contam
    # A conta mostrada é a do tamanho que conta.
    assert f"{contam} × log2(" in descrever_analise(analise)


# ---------------------------------------------------------------------------
# Lista de senhas comuns
# ---------------------------------------------------------------------------


def test_senhas_comuns_txt_e_a_copia_exata_da_lista() -> None:
    conteudo = ARQUIVO_SENHAS_COMUNS.read_bytes()
    assert hashlib.sha256(conteudo).hexdigest() == SHA256_SENHAS_COMUNS
    assert len(conteudo.decode("utf-8").splitlines()) == 150


def test_carregar_senhas_comuns_devolve_as_linhas_em_minusculas(
    comuns: set[str],
) -> None:
    linhas = ARQUIVO_SENHAS_COMUNS.read_text(encoding="utf-8").splitlines()
    assert comuns == {linha.lower() for linha in linhas}
    assert "123mudar" in comuns
    assert all(senha == senha.lower() for senha in comuns)


# ---------------------------------------------------------------------------
# Entropia e nota
# ---------------------------------------------------------------------------


def test_calcular_entropia() -> None:
    assert calcular_entropia(16, 94) == pytest.approx(104.87, abs=0.01)
    assert calcular_entropia(5, 32) == 25


@pytest.mark.parametrize(
    ("quantidade", "alfabeto", "esperado"),
    [
        (16, 94, "Entropia estimada: 16 × log2(94) ≈ 104,9 bits"),
        (7, 94, "Entropia estimada: 7 × log2(94) ≈ 45,9 bits"),
        (10, 62, "Entropia estimada: 10 × log2(62) ≈ 59,5 bits"),
        (5, 32, "Entropia estimada: 5 × log2(32) = 25 bits"),
    ],
)
def test_descrever_entropia(quantidade: int, alfabeto: int, esperado: str) -> None:
    assert descrever_entropia(quantidade, alfabeto) == esperado


@pytest.mark.parametrize(
    ("bits", "nota"),
    [
        (0, 0),
        (27.9, 0),
        (28, 1),
        (35.9, 1),
        (36, 2),
        (59.9, 2),
        (60, 3),
        (79.9, 3),
        (80, 4),
        (200, 4),
    ],
)
def test_dar_nota_nas_fronteiras_das_faixas(bits: float, nota: int) -> None:
    assert dar_nota(bits, 16, comum=False) == nota


def test_dar_nota_zero_para_a_senha_comum() -> None:
    assert dar_nota(200, 16, comum=True) == 0


@pytest.mark.parametrize(("bits", "nota"), [(45.9, 1), (28, 1), (27.9, 0)])
def test_dar_nota_limita_a_senha_curta(bits: float, nota: int) -> None:
    assert dar_nota(bits, 7, comum=False) == nota


def test_os_nomes_cobrem_cada_nota() -> None:
    assert len(NOMES) == len(LIMITES) + 1
    assert NOMES[4] == "forte"


@pytest.mark.parametrize("senha", ["flamengo", "FLAMENGO", "Flamengo", "123mudar"])
def test_analisar_senha_da_lista_tira_zero_sem_diferenca_de_caixa(
    senha: str, comuns: set[str]
) -> None:
    analise = analisar(senha, comuns)
    assert analise.comum
    assert analise.nota == 0


def test_analisar_senha_que_so_contem_uma_da_lista_nao_e_comum(
    comuns: set[str],
) -> None:
    analise = analisar("flamengo2026x", comuns)
    assert not analise.comum
    assert analise.nota == 3


def test_analisar_conta_os_espacos_da_senha() -> None:
    analise = analisar(" girassol ", set())
    assert analise.tamanho == 10
    assert analise.tipos == ["minúsculas", "símbolos"]


def test_analisar_senha_forte_do_gerador_tira_quatro(comuns: set[str]) -> None:
    analise = analisar(SENHA_FORTE, comuns)
    assert analise == ANALISE_FORTE


def test_analisar_senha_de_sete_caracteres_fica_em_um() -> None:
    analise = analisar("Xk#9vQ2", set())
    assert analise.bits == pytest.approx(45.9, abs=0.1)
    assert analise.nota == 1


def test_a_analise_nao_guarda_a_senha() -> None:
    assert SENHA_FORTE not in repr(analisar(SENHA_FORTE, set()))


@pytest.mark.parametrize(
    ("senha", "faltam"),
    [("Senha@123", 6), ("Gato@7", 7), (SENHA_FORTE, 0)],
)
def test_faltam_caracteres(senha: str, faltam: int) -> None:
    assert faltam_caracteres(analisar(senha, set())) == faltam


def test_faltam_caracteres_logo_abaixo_de_80_bits_e_um() -> None:
    assert faltam_caracteres(ANALISE_FORTE._replace(bits=79.9)) == 1


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("nomes", "esperado"),
    [
        (["símbolos"], "símbolos"),
        (["maiúsculas", "números"], "maiúsculas e números"),
        (list(TIPOS), "minúsculas, maiúsculas, números e símbolos"),
    ],
)
def test_juntar_nomes(nomes: list[str], esperado: str) -> None:
    assert juntar_nomes(nomes) == esperado


def test_sugerir_senha_comum_so_manda_trocar() -> None:
    analise = ANALISE_FORTE._replace(comum=True, sequencia=True, nota=0)
    assert sugerir(analise) == [
        "- Troque de senha: ela está entre as mais usadas,\n"
        "  e é das primeiras que alguém testa."
    ]


@pytest.mark.parametrize(
    ("repeticao", "sequencia", "esperado"),
    [
        (True, False, "- Tire a repetição: ela quase não soma força."),
        (False, True, "- Tire a sequência: ela quase não soma força."),
        (
            True,
            True,
            "- Tire a repetição e a sequência:\n  elas quase não somam força.",
        ),
    ],
)
def test_sugerir_tirar_o_trecho_previsivel_mesmo_com_nota_4(
    repeticao: bool, sequencia: bool, esperado: str
) -> None:
    analise = ANALISE_FORTE._replace(repeticao=repeticao, sequencia=sequencia)
    assert sugerir(analise) == [esperado]


def test_sugerir_quantos_caracteres_faltam_e_a_frase_senha() -> None:
    sugestoes = sugerir(analisar("Senha@123", set()))
    assert sugestoes == [
        "- Tire a sequência: ela quase não soma força.",
        "- Com mais 6 caracteres, a senha passa de 80 bits.\n"
        "  Uma frase-senha é longa e fácil de decorar.",
    ]


def test_sugerir_um_caractere_no_singular() -> None:
    analise = ANALISE_FORTE._replace(bits=79.9, nota=3)
    assert sugerir(analise)[0].startswith("- Com mais 1 caractere, a senha")


def test_sugerir_nada_quando_a_nota_e_4_sem_trecho_previsivel() -> None:
    assert sugerir(ANALISE_FORTE) == ["- Nada, pelas regras deste programa."]


def test_descrever_analise_mostra_cada_item_na_ordem() -> None:
    assert descrever_analise(analisar("Senha@123", set())) == (
        "🔎 Nota: 2 de 4, razoável\n"
        "Tamanho: 9 caracteres, 7 contam na entropia\n"
        "Entropia estimada: 7 × log2(94) ≈ 45,9 bits\n"
        "Tem: minúsculas, maiúsculas, números e símbolos\n"
        "✅ Sem repetição (como aaa ou 111)\n"
        "❌ Tem sequência (como abc, 123 ou qwe)\n"
        "✅ Fora da lista de senhas comuns\n"
        "\n"
        "💡 O que melhorar:\n"
        "- Tire a sequência: ela quase não soma força.\n"
        "- Com mais 6 caracteres, a senha passa de 80 bits.\n"
        "  Uma frase-senha é longa e fácil de decorar."
    )


def test_descrever_analise_mostra_os_tipos_que_faltam() -> None:
    texto = descrever_analise(analisar("girassol-azul", set()))
    assert "Tem: minúsculas e símbolos\nFalta: maiúsculas e números\n" in texto


def test_descrever_analise_sem_falta_quando_tem_os_quatro_tipos() -> None:
    assert "Falta:" not in descrever_analise(ANALISE_FORTE)


def test_descrever_analise_da_senha_comum(comuns: set[str]) -> None:
    texto = descrever_analise(analisar("Brasil", comuns))
    assert texto.startswith("🔎 Nota: 0 de 4, muito fraca\n")
    assert "❌ Está na lista de senhas comuns" in texto
    assert "- Troque de senha" in texto


def test_descrever_analise_de_um_caractere_no_singular() -> None:
    texto = descrever_analise(analisar("x", set()))
    assert "Tamanho: 1 caractere, 1 conta na entropia" in texto


def test_descrever_analise_com_repeticao() -> None:
    texto = descrever_analise(analisar("Tq7#zzzLp2@Vx9!", set()))
    assert "❌ Tem repetição (como aaa ou 111)" in texto
    assert "✅ Sem sequência (como abc, 123 ou qwe)" in texto


# Senhas inventadas, misturando tipos, para nenhum trecho de 3 caracteres delas
# coincidir com uma palavra fixa dos textos.
SENHAS_SIGILOSAS = [
    "Tq7#Lp2@Vx9!",
    "kW3$zR8&mN",
    "zzz#Q4wP",
    "Ghj%876xY",
    "  Rb5^ ",
    "Mç@4Ü",
    "BRASIL",
    SENHA_FORTE,
]


@pytest.mark.parametrize("senha", SENHAS_SIGILOSAS)
def test_o_resultado_nao_mostra_nenhum_trecho_da_senha(
    senha: str, comuns: set[str]
) -> None:
    texto = opcao_verificar(LeitorFalso(senha), comuns)
    assert texto.startswith("🔎 Nota:")
    trechos = {senha[i : i + 3] for i in range(len(senha) - 2)}
    for trecho in trechos | {senha}:
        assert trecho not in texto, trecho


def test_descrever_exemplos_cobre_as_notas_de_0_a_4(comuns: set[str]) -> None:
    notas = [analisar(senha, comuns).nota for senha, _ in EXEMPLOS]
    assert sorted(notas) == [0, 1, 2, 3, 4]


def test_os_exemplos_tem_uma_comum_uma_sequencia_e_uma_com_os_4_tipos(
    comuns: set[str],
) -> None:
    analises = [analisar(senha, comuns) for senha, _ in EXEMPLOS]
    assert any(analise.comum for analise in analises)
    assert any(analise.sequencia for analise in analises)
    assert any(len(analise.tipos) == 4 and analise.nota < 4 for analise in analises)


def test_descrever_exemplos_mostra_a_nota_calculada_e_a_explicacao(
    comuns: set[str],
) -> None:
    texto = descrever_exemplos(comuns)
    for senha, explicacao in EXEMPLOS:
        nota = analisar(senha, comuns).nota
        assert f"🔑 {senha}: {nota} de 4, {NOMES[nota]}\n   {explicacao}" in texto
    assert texto.endswith(
        "A nota é uma estimativa por regras. Uma palavra\n"
        "conhecida com um número e um símbolo no fim\n"
        "continua fácil de adivinhar, mesmo com os quatro\n"
        "tipos de caractere."
    )


def test_descrever_exemplos_igual_ao_quadro_do_design(comuns: set[str]) -> None:
    linhas = descrever_exemplos(comuns).splitlines()
    assert linhas[0:10:2] == [
        "🔑 123mudar: 0 de 4, muito fraca",
        "🔑 Gato@7: 1 de 4, fraca",
        "🔑 Senha@123: 2 de 4, razoável",
        "🔑 girassol-azul: 3 de 4, boa",
        "🔑 sotaque-haver-abreviar-briga: 4 de 4, forte",
    ]


# ---------------------------------------------------------------------------
# Perguntas e opções
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("entrada", "opcao"), [("1", 1), (" 2 ", 2), ("3", 3)])
def test_conferir_opcao_aceita_o_numero_de_cada_opcao(entrada: str, opcao: int) -> None:
    assert conferir_opcao(entrada) == opcao


@pytest.mark.parametrize("entrada", ["", "   ", "0", "4", "9", "abc", "1.0", "-1", "٣"])
def test_conferir_opcao_recusa_o_resto(entrada: str) -> None:
    assert conferir_opcao(entrada) is None


def test_opcao_verificar_pede_a_senha_avisando_que_ela_nao_aparece() -> None:
    leitor = LeitorFalso("Senha@123")
    texto = opcao_verificar(leitor, set())
    assert leitor.pedidos == [PEDIDO_SENHA]
    assert texto == descrever_analise(analisar("Senha@123", set()))


def test_opcao_verificar_senha_vazia() -> None:
    assert opcao_verificar(LeitorFalso(""), set()) == "⚠️ Nenhuma senha foi digitada."


def test_opcao_verificar_nao_tira_os_espacos() -> None:
    texto = opcao_verificar(LeitorFalso("  "), set())
    assert "Tamanho: 2 caracteres" in texto


# ---------------------------------------------------------------------------
# Largura das linhas
# ---------------------------------------------------------------------------


def textos_do_programa(comuns: set[str]) -> list[str]:
    """Junta os textos que o programa mostra entre o título e o menu.

    Args:
        comuns (set[str]): A lista de senhas comuns, em minúsculas.

    Returns:
        list[str]: O resultado de várias senhas, os exemplos e os avisos.
    """
    senhas = [*SENHAS_SIGILOSAS, "x", "aaabc", "Senha@123", "girassol-azul", "a" * 64]
    return [
        *(opcao_verificar(LeitorFalso(senha), comuns) for senha in senhas),
        descrever_analise(ANALISE_FORTE._replace(repeticao=True, sequencia=True)),
        descrever_analise(ANALISE_FORTE._replace(bits=79.9, nota=3)),
        descrever_exemplos(comuns),
        opcao_verificar(LeitorFalso(""), comuns),
        f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}.",
    ]


def test_nenhuma_linha_dos_textos_passa_da_largura_maxima(comuns: set[str]) -> None:
    for texto in textos_do_programa(comuns):
        for linha in texto.splitlines():
            assert colunas(linha) <= LARGURA_MAXIMA, linha


def test_nenhum_pedido_passa_da_largura_maxima() -> None:
    for pedido in [PEDIDO_SENHA, "Escolha uma opção: "]:
        assert colunas(pedido) <= LARGURA_MAXIMA, pedido


def test_nenhuma_linha_do_quadro_passa_da_largura_maxima(
    capsys: pytest.CaptureFixture[str], comuns: set[str]
) -> None:
    for texto in textos_do_programa(comuns):
        exibir_tela(texto)
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
    return saida[saida.rindex("VERIFICADOR DE FORÇA DE SENHA") :]


def test_main_primeira_tela_sem_resultado(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("3"), LeitorFalso(), COMUNS_TESTE)
    assert capsys.readouterr().out.startswith(
        "====== VERIFICADOR DE FORÇA DE SENHA ======\n\n"
        "1 : Verificar uma senha\n"
        "2 : Ver exemplos comentados\n"
        "3 : Sair\n\n"
    )


def test_main_mostra_titulo_resultado_e_menu_nessa_ordem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ler = LeitorFalso("1", "3")
    ler_senha = LeitorFalso("Senha@123")
    main(ler, ler_senha, COMUNS_TESTE)

    tela = ultima_tela(capsys.readouterr().out)
    assert tela.startswith("VERIFICADOR DE FORÇA DE SENHA ======\n\n🔎 Nota:")
    assert tela.index("Uma frase-senha") < tela.index("1 : Verificar uma senha")
    assert tela.index("1 : Verificar uma senha") < tela.index("3 : Sair")
    assert ler.pedidos == ["Escolha uma opção: "] * 2
    assert ler_senha.pedidos == [PEDIDO_SENHA]


def test_main_verifica_a_senha_sem_mostra_la(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main(LeitorFalso("1", "3"), LeitorFalso(SENHA_FORTE), COMUNS_TESTE)
    saida = capsys.readouterr().out
    assert descrever_analise(analisar(SENHA_FORTE, COMUNS_TESTE)) in ultima_tela(saida)
    assert SENHA_FORTE not in saida


def test_main_senha_vazia_volta_ao_menu(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("1", "3"), LeitorFalso(""), COMUNS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert "⚠️ Nenhuma senha foi digitada.\n\n1 : Verificar uma senha" in tela


def test_main_mostra_os_exemplos(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("2", "3"), LeitorFalso(), COMUNS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert descrever_exemplos(COMUNS_TESTE) in tela


def test_main_le_a_lista_do_arquivo_quando_nao_e_passada(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # "102030" está no `senhas_comuns.txt`, mas não na `COMUNS_TESTE`.
    main(LeitorFalso("1", "3"), LeitorFalso("102030"))
    tela = ultima_tela(capsys.readouterr().out)
    assert "❌ Está na lista de senhas comuns" in tela


@pytest.mark.parametrize("entrada", ["", "0", "4", "9", "abc", "٣"])
def test_main_recusa_a_opcao_invalida(
    capsys: pytest.CaptureFixture[str], entrada: str
) -> None:
    main(LeitorFalso(entrada, "3"), LeitorFalso(), COMUNS_TESTE)
    tela = ultima_tela(capsys.readouterr().out)
    assert "❌ Opção inválida. Digite um número de 1 a 3." in tela


def test_main_sessao_completa_volta_ao_menu_a_cada_opcao(
    capsys: pytest.CaptureFixture[str],
) -> None:
    ler = LeitorFalso("1", "x", "1", "2", "1", "3")
    ler_senha = LeitorFalso("123mudar", "", "Senha@123")
    main(ler, ler_senha, COMUNS_TESTE)
    saida = capsys.readouterr().out
    assert saida.count("VERIFICADOR DE FORÇA DE SENHA") == 6
    assert ler_senha.pedidos == [PEDIDO_SENHA] * 3
    assert "razoável" in ultima_tela(saida)


def test_main_sai_pelo_menu_com_despedida(capsys: pytest.CaptureFixture[str]) -> None:
    main(LeitorFalso("3"), LeitorFalso(), COMUNS_TESTE)
    assert capsys.readouterr().out.endswith("3 : Sair\n\nAté a próxima! 👋\n")


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
@pytest.mark.parametrize("respostas", [(), ("1",), ("2",), ("x",)])
def test_main_sai_sem_stack_trace_no_menu(
    capsys: pytest.CaptureFixture[str],
    excecao: type[BaseException],
    respostas: tuple[str, ...],
) -> None:
    ler = LeitorQueInterrompe(excecao, *respostas)
    main(ler, LeitorFalso("Senha@123"), COMUNS_TESTE)
    saida = capsys.readouterr().out
    assert saida.endswith("\nVerificador encerrado. Até a próxima! 👋\n")


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
def test_main_sai_sem_stack_trace_no_pedido_da_senha(
    capsys: pytest.CaptureFixture[str], excecao: type[BaseException]
) -> None:
    ler_senha = LeitorQueInterrompe(excecao)
    main(LeitorFalso("1"), ler_senha, COMUNS_TESTE)
    assert ler_senha.pedidos == [PEDIDO_SENHA]
    saida = capsys.readouterr().out
    assert saida.endswith("\nVerificador encerrado. Até a próxima! 👋\n")


def test_main_le_a_senha_com_o_getpass_por_padrao() -> None:
    parametros = inspect.signature(main).parameters
    assert parametros["ler_senha"].default is getpass.getpass
    assert parametros["ler"].default is input


# ---------------------------------------------------------------------------
# A senha não sai do computador
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
        if isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name):
            atributos.add((no.value.id, no.attr))

    previstos = {
        "__future__",
        "collections.abc",
        "getpass",
        "math",
        "os",
        "pathlib",
        "re",
        "string",
        "sys",
        "typing",
    }
    assert modulos <= previstos
    assert not chamadas & {"open", "write_text", "write_bytes"}
    assert ("sys", "argv") not in atributos
