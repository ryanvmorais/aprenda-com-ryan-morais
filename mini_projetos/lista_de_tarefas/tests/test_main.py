"""Testes para main.py.

Estratégia de isolamento: o teclado, o relógio e o caminho do arquivo entram nas
funções do programa por parâmetro. Cada teste usa a pasta vazia do `tmp_path`
(o `tarefas.json` de quem usa o programa nunca é tocado), um relógio falso que
devolve sempre o mesmo momento e, para o teclado, um `LeitorFalso` (devolve as
respostas na ordem e guarda cada pedido), sem `monkeypatch` em `input` ou
`datetime`. A saída se confere com o `capsys`. O único `monkeypatch` da suíte
troca `limpar_tela` por um no-op, porque ela chama `os.system`, um efeito de
terminal.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import date, datetime
from pathlib import Path

import pytest

import main as modulo_main
from main import (
    OPCOES,
    SEM_TAREFAS,
    TAMANHO_MAXIMO,
    Conferencia,
    Leitor,
    Tarefa,
    adicionar,
    alternar_conclusao,
    carregar_tarefas,
    conferir_numero,
    conferir_opcao,
    conferir_texto,
    confirmar,
    editar,
    exibir_tela,
    formatar_data,
    formatar_tarefa,
    ler_numero,
    ler_texto,
    main,
    remover,
    salvar_tarefas,
    validar_tarefas,
)

# O momento fixo do relógio falso: 20/11/2026, 15:30:00.
MOMENTO = datetime(2026, 11, 20, 15, 30, 0)


def relogio_falso() -> datetime:
    """Simula o relógio: devolve sempre o mesmo momento.

    Returns:
        datetime: `MOMENTO`.
    """
    return MOMENTO


def nova_tarefa(
    texto: str = "Estudar pathlib",
    concluida: bool = False,
    criada_em: str = "2026-11-20",
) -> Tarefa:
    """Monta uma tarefa válida, com valores padrão para os campos.

    Args:
        texto (str, optional): Texto da tarefa. Padrão: "Estudar pathlib".
        concluida (bool, optional): Situação. Padrão: False.
        criada_em (str, optional): Data de criação. Padrão: "2026-11-20".

    Returns:
        Tarefa: A tarefa montada.
    """
    return {"texto": texto, "concluida": concluida, "criada_em": criada_em}


@pytest.fixture
def arquivo(tmp_path: Path) -> Path:
    """O caminho do tarefas.json numa pasta temporária, ainda sem o arquivo.

    Args:
        tmp_path (Path): Pasta vazia do pytest, uma por teste.

    Returns:
        Path: `tmp_path / "tarefas.json"`.
    """
    return tmp_path / "tarefas.json"


@pytest.fixture(autouse=True)
def _sem_tela(monkeypatch: pytest.MonkeyPatch) -> None:
    """Substitui a limpeza de tela por um no-op em toda a suíte.

    `limpar_tela` chama `os.system`, que limparia o terminal de quem roda os testes.
    """
    monkeypatch.setattr(modulo_main, "limpar_tela", lambda: None)


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


class LeitorQueInterrompe:
    """Simula o usuário saindo: devolve as respostas e, no fim, lança a exceção.

    Attributes:
        excecao (type[BaseException]): Exceção lançada depois das respostas.
    """

    def __init__(self, excecao: type[BaseException], *respostas: str) -> None:
        """Guarda a exceção e as respostas que vêm antes dela.

        Args:
            excecao (type[BaseException]): `KeyboardInterrupt` ou `EOFError`.
            *respostas (str): Respostas a devolver antes da exceção.
        """
        self.excecao = excecao
        self._respostas: Iterator[str] = iter(respostas)

    def __call__(self, pedido: str) -> str:
        """Devolve a próxima resposta, ou lança a exceção quando elas acabam.

        Args:
            pedido (str): Texto do pedido (ignorado).

        Returns:
            str: A próxima resposta da sequência.

        Raises:
            BaseException: A exceção guardada, como o Ctrl+C ou o fim da entrada.
        """
        resposta = next(self._respostas, None)
        if resposta is None:
            raise self.excecao
        return resposta


# ---------------------------------------------------------------------------
# validar_tarefas
# ---------------------------------------------------------------------------


def test_validar_tarefas_devolve_a_lista_valida() -> None:
    dados = [nova_tarefa(), nova_tarefa("Comprar pão", True, "2026-11-19")]
    assert validar_tarefas(dados) == dados


def test_validar_tarefas_aceita_a_lista_vazia() -> None:
    assert validar_tarefas([]) == []


@pytest.mark.parametrize(
    "dados",
    [
        pytest.param({}, id="objeto em vez de lista"),
        pytest.param("tarefas", id="texto em vez de lista"),
        pytest.param([1, 2], id="item que não é dicionário"),
        pytest.param([{"texto": "Estudar", "concluida": False}], id="chave faltando"),
        pytest.param([{**nova_tarefa(), "prazo": "2026-12-01"}], id="chave a mais"),
        pytest.param([nova_tarefa(texto="")], id="texto vazio"),
        pytest.param([nova_tarefa(texto="   ")], id="texto só com espaços"),
        pytest.param(
            [{"texto": 42, "concluida": False, "criada_em": "2026-11-20"}],
            id="texto que não é str",
        ),
        pytest.param(
            [{"texto": "Estudar", "concluida": "sim", "criada_em": "2026-11-20"}],
            id="situação que não é bool",
        ),
        pytest.param(
            [{"texto": "Estudar", "concluida": 1, "criada_em": "2026-11-20"}],
            id="situação 1 em vez de true",
        ),
        pytest.param([nova_tarefa(criada_em="20/11/2026")], id="data fora do ISO"),
        pytest.param([nova_tarefa(criada_em="2026-02-30")], id="data que não existe"),
        pytest.param(
            [{"texto": "Estudar", "concluida": False, "criada_em": 20261120}],
            id="data que não é str",
        ),
    ],
)
def test_validar_tarefas_recusa_a_forma_errada(dados: object) -> None:
    with pytest.raises(ValueError):
        validar_tarefas(dados)


# ---------------------------------------------------------------------------
# carregar_tarefas
# ---------------------------------------------------------------------------


def test_carregar_tarefas_sem_arquivo_comeca_vazia_sem_criar_nada(
    arquivo: Path,
) -> None:
    assert carregar_tarefas(arquivo, relogio_falso) == ([], "")
    assert list(arquivo.parent.iterdir()) == []


def test_carregar_tarefas_le_o_arquivo_valido_com_acentos(arquivo: Path) -> None:
    tarefas = [nova_tarefa("Comprar pão e maçã"), nova_tarefa(concluida=True)]
    arquivo.write_text(json.dumps(tarefas, ensure_ascii=False), encoding="utf-8")
    assert carregar_tarefas(arquivo, relogio_falso) == (tarefas, "")


@pytest.mark.parametrize(
    "conteudo",
    [
        pytest.param(b"[{", id="JSON pela metade"),
        pytest.param(b"", id="arquivo vazio"),
        pytest.param('[{"texto": "pão"}]'.encode("latin-1"), id="não é UTF-8"),
        pytest.param(b"{}", id="JSON com a forma errada"),
    ],
)
def test_carregar_tarefas_guarda_o_corrompido_e_comeca_vazia(
    arquivo: Path, conteudo: bytes
) -> None:
    """O arquivo ilegível vira cópia com a data e a hora, e a lista começa vazia."""
    arquivo.write_bytes(conteudo)
    tarefas, aviso = carregar_tarefas(arquivo, relogio_falso)

    copia = arquivo.parent / "tarefas.corrompido-20261120-153000.json"
    assert tarefas == []
    assert not arquivo.exists()
    assert copia.read_bytes() == conteudo
    assert "tarefas.json estava corrompido" in aviso
    assert copia.name in aviso


def test_carregar_tarefas_preserva_a_copia_anterior(arquivo: Path) -> None:
    """Dois corrompidos no mesmo segundo: o segundo ganha o sufixo -2."""
    anterior = arquivo.parent / "tarefas.corrompido-20261120-153000.json"
    anterior.write_text("cópia anterior", encoding="utf-8")
    arquivo.write_text("[{", encoding="utf-8")

    _, aviso = carregar_tarefas(arquivo, relogio_falso)

    nova = arquivo.parent / "tarefas.corrompido-20261120-153000-2.json"
    assert anterior.read_text(encoding="utf-8") == "cópia anterior"
    assert nova.read_text(encoding="utf-8") == "[{"
    assert nova.name in aviso


def test_carregar_tarefas_conta_ate_achar_um_nome_livre(arquivo: Path) -> None:
    """Com o nome e o -2 ocupados, a cópia vai para o -3."""
    pasta = arquivo.parent
    (pasta / "tarefas.corrompido-20261120-153000.json").write_text("1")
    (pasta / "tarefas.corrompido-20261120-153000-2.json").write_text("2")
    arquivo.write_text("[{", encoding="utf-8")

    carregar_tarefas(arquivo, relogio_falso)

    assert (pasta / "tarefas.corrompido-20261120-153000-3.json").exists()


# ---------------------------------------------------------------------------
# salvar_tarefas
# ---------------------------------------------------------------------------


def test_salvar_e_carregar_devolve_a_mesma_lista(arquivo: Path) -> None:
    tarefas = [nova_tarefa(), nova_tarefa("Comprar pão", True, "2026-11-19")]
    salvar_tarefas(tarefas, arquivo)
    assert carregar_tarefas(arquivo, relogio_falso) == (tarefas, "")


def test_salvar_tarefas_grava_os_acentos_legiveis_e_indentados(
    arquivo: Path,
) -> None:
    salvar_tarefas([nova_tarefa("Comprar pão")], arquivo)
    texto = arquivo.read_text(encoding="utf-8")
    assert '"texto": "Comprar pão"' in texto
    assert "\\u" not in texto
    assert texto.startswith('[\n  {\n    "texto"')


def test_salvar_tarefas_nao_deixa_temporario(arquivo: Path) -> None:
    salvar_tarefas([nova_tarefa()], arquivo)
    assert [caminho.name for caminho in arquivo.parent.iterdir()] == ["tarefas.json"]


def test_salvar_tarefas_mantem_o_arquivo_anterior_se_a_gravacao_falhar(
    arquivo: Path,
) -> None:
    """A falha no temporário não toca no tarefas.json gravado antes (RF-03)."""
    salvar_tarefas([nova_tarefa("Versão anterior")], arquivo)
    antes = arquivo.read_bytes()
    # Uma pasta com o nome do temporário faz a gravação dele falhar, como uma
    # queda no meio.
    (arquivo.parent / "tarefas.json.tmp").mkdir()

    with pytest.raises(OSError):
        salvar_tarefas([nova_tarefa("Versão nova")], arquivo)

    assert arquivo.read_bytes() == antes


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------


def test_formatar_data_converte_para_dia_mes_ano() -> None:
    assert formatar_data("2026-11-20") == "20/11/2026"
    assert formatar_data("2027-01-05") == "05/01/2027"


@pytest.mark.parametrize(
    ("numero", "tarefa", "linha"),
    [
        pytest.param(
            1, nova_tarefa(), " 1. [ ] 20/11/2026  Estudar pathlib", id="pendente"
        ),
        pytest.param(
            2,
            nova_tarefa("Comprar pão", True, "2026-11-19"),
            " 2. [x] 19/11/2026  Comprar pão",
            id="concluída",
        ),
        pytest.param(
            12, nova_tarefa(), "12. [ ] 20/11/2026  Estudar pathlib", id="dois dígitos"
        ),
    ],
)
def test_formatar_tarefa(numero: int, tarefa: Tarefa, linha: str) -> None:
    assert formatar_tarefa(numero, tarefa) == linha


# ---------------------------------------------------------------------------
# Entrada validada
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entrada", ["1", "3", " 5 "])
def test_conferir_opcao_aceita_o_numero_do_menu(entrada: str) -> None:
    assert conferir_opcao(entrada) == int(entrada)


@pytest.mark.parametrize("entrada", ["", "  ", "0", "6", "9", "abc", "-1", "1.5", "²"])
def test_conferir_opcao_recusa_o_resto(entrada: str) -> None:
    assert conferir_opcao(entrada) is None


def test_conferir_opcao_vai_ate_o_tamanho_do_menu() -> None:
    assert conferir_opcao(str(len(OPCOES))) == len(OPCOES)
    assert conferir_opcao(str(len(OPCOES) + 1)) is None


def test_conferir_texto_aceita_e_tira_os_espacos_das_pontas() -> None:
    assert conferir_texto("  Gravar o vídeo  ") == Conferencia("Gravar o vídeo", "")


def test_conferir_texto_aceita_o_tamanho_maximo() -> None:
    texto = "a" * TAMANHO_MAXIMO
    assert conferir_texto(texto) == Conferencia(texto, "")


@pytest.mark.parametrize(
    "entrada",
    [
        pytest.param("", id="vazio"),
        pytest.param("    ", id="só espaços"),
        pytest.param("a" * (TAMANHO_MAXIMO + 1), id="longo demais"),
    ],
)
def test_conferir_texto_recusa_e_explica_o_limite(entrada: str) -> None:
    conferencia = conferir_texto(entrada)
    assert conferencia.valor == ""
    assert f"1 a {TAMANHO_MAXIMO} caracteres" in conferencia.recusa


@pytest.mark.parametrize("entrada", ["1", " 2 ", "3"])
def test_conferir_numero_aceita_o_numero_da_lista(entrada: str) -> None:
    assert conferir_numero(entrada, 3) == Conferencia(entrada.strip(), "")


@pytest.mark.parametrize("entrada", ["", "   ", "0", "4", "abc", "-1", "²"])
def test_conferir_numero_recusa_e_explica_o_intervalo(entrada: str) -> None:
    assert conferir_numero(entrada, 3) == Conferencia(
        "", "❌ Digite um número de 1 a 3."
    )


# ---------------------------------------------------------------------------
# exibir_tela
# ---------------------------------------------------------------------------


def test_exibir_tela_mostra_lista_contagem_menu_e_mensagem_nessa_ordem(
    capsys: pytest.CaptureFixture[str],
) -> None:
    tarefas = [nova_tarefa(), nova_tarefa("Comprar pão", True, "2026-11-19")]
    exibir_tela(tarefas, "✅ Tarefa concluída: Comprar pão")
    linhas = capsys.readouterr().out.splitlines()

    assert linhas[0] == "======== LISTA DE TAREFAS ========"
    posicoes = [
        linhas.index(" 1. [ ] 20/11/2026  Estudar pathlib"),
        linhas.index(" 2. [x] 19/11/2026  Comprar pão"),
        linhas.index("Pendentes: 1 | Concluídas: 1"),
        linhas.index("1 : Adicionar"),
        linhas.index("5 : Sair"),
        linhas.index("✅ Tarefa concluída: Comprar pão"),
    ]
    assert posicoes == sorted(posicoes)
    assert linhas[-1] == "✅ Tarefa concluída: Comprar pão"


def test_exibir_tela_numera_o_menu_inteiro(capsys: pytest.CaptureFixture[str]) -> None:
    exibir_tela([], "")
    saida = capsys.readouterr().out
    for numero, opcao in enumerate(OPCOES, start=1):
        assert f"{numero} : {opcao}" in saida


def test_exibir_tela_com_a_lista_vazia(capsys: pytest.CaptureFixture[str]) -> None:
    exibir_tela([], "")
    saida = capsys.readouterr().out
    assert "Nenhuma tarefa por aqui" in saida
    assert "Pendentes: 0 | Concluídas: 0" in saida


def test_exibir_tela_sem_mensagem_termina_no_menu(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exibir_tela([nova_tarefa()], "")
    linhas = [linha for linha in capsys.readouterr().out.splitlines() if linha]
    assert linhas[-1] == "5 : Sair"


# ---------------------------------------------------------------------------
# Leitura do teclado
# ---------------------------------------------------------------------------


def test_ler_texto_pede_de_novo_ate_o_texto_valido(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("", "a" * (TAMANHO_MAXIMO + 1), "  Estudar  ")
    assert ler_texto(leitor, "Texto: ") == "Estudar"
    assert leitor.pedidos == ["Texto: "] * 3
    assert capsys.readouterr().out.count("caracteres") == 2


def test_ler_numero_pede_de_novo_e_devolve_o_indice(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("0", "abc", "2")
    assert ler_numero(leitor, 3) == 1
    assert leitor.pedidos == ["Número da tarefa (1 a 3): "] * 3
    assert capsys.readouterr().out.count("❌ Digite um número de 1 a 3.") == 2


@pytest.mark.parametrize(
    ("resposta", "esperado"),
    [("s", True), ("S", True), (" s ", True), ("n", False), ("N", False)],
)
def test_confirmar_aceita_s_e_n(resposta: str, esperado: bool) -> None:
    assert confirmar(LeitorFalso(resposta), "Remover?") is esperado


def test_confirmar_repete_a_pergunta_na_resposta_invalida(
    capsys: pytest.CaptureFixture[str],
) -> None:
    leitor = LeitorFalso("talvez", "", "s")
    assert confirmar(leitor, "Remover?") is True
    assert leitor.pedidos == ["Remover? (s/n): "] * 3
    assert capsys.readouterr().out.count("Responda s (sim) ou n (não)") == 2


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------


def test_adicionar_poe_a_tarefa_pendente_com_a_data_de_hoje(arquivo: Path) -> None:
    tarefas = [nova_tarefa("Primeira", criada_em="2026-11-19")]
    mensagem = adicionar(
        tarefas, arquivo, LeitorFalso("  Comprar pão  "), date(2026, 11, 20)
    )

    assert tarefas == [
        nova_tarefa("Primeira", criada_em="2026-11-19"),
        nova_tarefa("Comprar pão", False, "2026-11-20"),
    ]
    assert "Comprar pão" in mensagem
    assert carregar_tarefas(arquivo, relogio_falso) == (tarefas, "")


def test_alternar_conclusao_conclui_e_reabre(arquivo: Path) -> None:
    tarefas = [nova_tarefa("Primeira"), nova_tarefa("Segunda")]

    mensagem = alternar_conclusao(tarefas, arquivo, LeitorFalso("2"))
    assert tarefas[1]["concluida"] is True
    assert "concluída" in mensagem
    assert carregar_tarefas(arquivo, relogio_falso)[0][1]["concluida"] is True

    mensagem = alternar_conclusao(tarefas, arquivo, LeitorFalso("2"))
    assert tarefas[1]["concluida"] is False
    assert "reaberta" in mensagem
    assert carregar_tarefas(arquivo, relogio_falso)[0][1]["concluida"] is False


def test_editar_troca_so_o_texto(arquivo: Path) -> None:
    tarefas = [nova_tarefa("Comprar pao", True, "2026-11-19")]
    mensagem = editar(tarefas, arquivo, LeitorFalso("1", "", "Comprar pão"))

    assert tarefas == [nova_tarefa("Comprar pão", True, "2026-11-19")]
    assert "Comprar pão" in mensagem
    assert carregar_tarefas(arquivo, relogio_falso) == (tarefas, "")


@pytest.mark.parametrize("resposta", ["s", "S"])
def test_remover_com_s_tira_a_tarefa_e_renumera(arquivo: Path, resposta: str) -> None:
    tarefas = [nova_tarefa("Primeira"), nova_tarefa("Gravar o vídeo")]
    tarefas.append(nova_tarefa("Terceira"))
    leitor = LeitorFalso("2", resposta)

    mensagem = remover(tarefas, arquivo, leitor)

    assert [tarefa["texto"] for tarefa in tarefas] == ["Primeira", "Terceira"]
    assert leitor.pedidos[1] == 'Remover "Gravar o vídeo"? (s/n): '
    assert "Gravar o vídeo" in mensagem
    assert carregar_tarefas(arquivo, relogio_falso) == (tarefas, "")


@pytest.mark.parametrize("resposta", ["n", "N"])
def test_remover_com_n_nao_muda_nada(arquivo: Path, resposta: str) -> None:
    tarefas = [nova_tarefa("Primeira"), nova_tarefa("Segunda")]
    mensagem = remover(tarefas, arquivo, LeitorFalso("1", resposta))

    assert [tarefa["texto"] for tarefa in tarefas] == ["Primeira", "Segunda"]
    assert "Nada foi removido" in mensagem
    assert not arquivo.exists()


@pytest.mark.parametrize("acao", [alternar_conclusao, editar, remover])
def test_acao_com_a_lista_vazia_nao_pede_numero_nem_grava(
    arquivo: Path, acao: Callable[[list[Tarefa], Path, Leitor], str]
) -> None:
    leitor = LeitorFalso()
    assert acao([], arquivo, leitor) == SEM_TAREFAS
    assert leitor.pedidos == []
    assert not arquivo.exists()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_sessao_grava_e_reabre_com_a_mesma_lista(
    arquivo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Adiciona duas tarefas, conclui a primeira e sai.
    leitor = LeitorFalso("1", "Estudar pathlib", "1", "Comprar pão", "2", "1", "5")
    main(leitor, relogio_falso, arquivo)
    assert "Até a próxima" in capsys.readouterr().out

    main(LeitorFalso("5"), relogio_falso, arquivo)
    saida = capsys.readouterr().out
    assert " 1. [x] 20/11/2026  Estudar pathlib" in saida
    assert " 2. [ ] 20/11/2026  Comprar pão" in saida
    assert "Pendentes: 1 | Concluídas: 1" in saida


def test_main_avisa_do_arquivo_corrompido_na_primeira_tela(
    arquivo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    arquivo.write_text("[{", encoding="utf-8")
    main(LeitorFalso("5"), relogio_falso, arquivo)

    saida = capsys.readouterr().out
    assert "tarefas.json estava corrompido" in saida
    assert "tarefas.corrompido-20261120-153000.json" in saida
    assert "Nenhuma tarefa por aqui" in saida
    assert (arquivo.parent / "tarefas.corrompido-20261120-153000.json").exists()


@pytest.mark.parametrize("entrada", ["", "0", "9", "abc"])
def test_main_recusa_a_opcao_invalida(
    arquivo: Path, capsys: pytest.CaptureFixture[str], entrada: str
) -> None:
    main(LeitorFalso(entrada, "5"), relogio_falso, arquivo)
    assert "Opção inválida" in capsys.readouterr().out


@pytest.mark.parametrize("excecao", [KeyboardInterrupt, EOFError])
def test_main_sai_sem_stack_trace_e_sem_mudar_o_arquivo(
    arquivo: Path,
    capsys: pytest.CaptureFixture[str],
    excecao: type[BaseException],
) -> None:
    salvar_tarefas([nova_tarefa()], arquivo)
    antes = arquivo.read_bytes()

    # Escolhe Adicionar e sai no meio, quando o texto é pedido.
    main(LeitorQueInterrompe(excecao, "1"), relogio_falso, arquivo)

    assert "Lista encerrada" in capsys.readouterr().out
    assert arquivo.read_bytes() == antes
