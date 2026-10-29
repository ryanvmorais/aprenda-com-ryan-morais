"""Testes para o README.en.md.

O `README.en.md` é uma tradução do `README.md`, e tradução se desalinha: uma seção
nova no `README.md` que ninguém leva para o inglês deixa quem lê em inglês com um
material mais antigo que o do projeto. Os testes comparam a estrutura, nunca as
palavras: a ordem dos títulos, a tabela de tecnologias, os blocos de código, os
desafios, o link de troca entre os dois arquivos e os arquivos do repositório para
onde a versão em inglês aponta.

Estratégia de isolamento: só os dois READMEs e a existência dos arquivos que eles
linkam são lidos; fora de uma árvore com os dois, os testes são pulados.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# A pasta do projeto, um nível acima de tests/.
_RAIZ = Path(__file__).resolve().parents[1]
# Os dois arquivos comparados; sem um deles na árvore, os testes são pulados.
_PORTUGUES = _RAIZ / "README.md"
_INGLES = _RAIZ / "README.en.md"

# Alvo de um link ou imagem Markdown: o texto entre "](" e o parêntese que fecha.
_ALVO = re.compile(r"\]\(([^)\s]+)\)")

# Título ATX; a sequência de "#" é o nível.
_TITULO = re.compile(r"^(#{1,6}) ")

# Os dois READMEs são necessários em todos os testes abaixo.
_precisa_dos_dois = pytest.mark.skipif(
    not (_PORTUGUES.is_file() and _INGLES.is_file()),
    reason="os dois READMEs não estão nesta árvore",
)


# ---------------------------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------------------------


def _fora_dos_blocos(caminho: Path) -> list[str]:
    """Lê um arquivo Markdown e descarta as linhas de dentro de blocos de código.

    Args:
        caminho (Path): O arquivo Markdown.

    Returns:
        list[str]: As linhas restantes, para que um comentário `#` num bloco de
            shell não seja confundido com um título.
    """
    mantidas: list[str] = []
    dentro_do_bloco = False
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith(("```", "    ```")):
            dentro_do_bloco = not dentro_do_bloco
        elif not dentro_do_bloco:
            mantidas.append(linha)
    return mantidas


def _niveis(caminho: Path) -> list[int]:
    """Lista os níveis dos títulos de um README, na ordem.

    Args:
        caminho (Path): O arquivo Markdown.

    Returns:
        list[int]: Um nível (1 a 6) por título.
    """
    achados = (_TITULO.match(linha) for linha in _fora_dos_blocos(caminho))
    return [len(m.group(1)) for m in achados if m]


def _linhas_da_tabela(caminho: Path, primeira_celula: str) -> int:
    """Conta as linhas de dados da tabela cujo cabeçalho começa por uma célula.

    Args:
        caminho (Path): O arquivo Markdown.
        primeira_celula (str): O texto da primeira célula do cabeçalho.

    Returns:
        int: As linhas abaixo do cabeçalho, sem contar ele nem o separador.
    """
    linhas = _fora_dos_blocos(caminho)
    inicio = next(
        i for i, linha in enumerate(linhas) if linha.startswith(f"| {primeira_celula} ")
    )
    total = 0
    for linha in linhas[inicio + 2 :]:
        if not linha.startswith("|"):
            break
        total += 1
    return total


def _blocos_de_codigo(caminho: Path) -> int:
    """Conta os blocos de código cercados de um README.

    Args:
        caminho (Path): O arquivo Markdown.

    Returns:
        int: A quantidade de blocos, abertos por três crases (recuados ou não).
    """
    texto = caminho.read_text(encoding="utf-8")
    return len(re.findall(r"^\s*```\w+", texto, flags=re.MULTILINE))


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


@_precisa_dos_dois
def test_os_dois_readmes_tem_os_mesmos_titulos_na_mesma_ordem() -> None:
    assert _niveis(_INGLES) == _niveis(_PORTUGUES)


@_precisa_dos_dois
def test_os_dois_readmes_tem_as_mesmas_linhas_na_tabela_de_tecnologias() -> None:
    assert _linhas_da_tabela(_INGLES, "Tool") == _linhas_da_tabela(
        _PORTUGUES, "Ferramenta"
    )


@_precisa_dos_dois
def test_os_dois_readmes_tem_a_mesma_quantidade_de_blocos_de_codigo() -> None:
    assert _blocos_de_codigo(_INGLES) == _blocos_de_codigo(_PORTUGUES)


@_precisa_dos_dois
def test_os_dois_readmes_tem_a_mesma_quantidade_de_desafios() -> None:
    ingles = _INGLES.read_text(encoding="utf-8").count("**What you learn:**")
    portugues = _PORTUGUES.read_text(encoding="utf-8").count("**O Aprendizado:**")

    assert ingles == portugues
    assert portugues > 0


@_precisa_dos_dois
def test_cada_readme_linka_o_outro_nas_primeiras_linhas() -> None:
    ingles = "\n".join(_fora_dos_blocos(_INGLES)[:6])
    portugues = "\n".join(_fora_dos_blocos(_PORTUGUES)[:6])

    assert "(README.md)" in ingles
    assert "(README.en.md)" in portugues


@_precisa_dos_dois
def test_os_links_do_readme_em_ingles_apontam_para_arquivos_que_existem() -> None:
    texto = _INGLES.read_text(encoding="utf-8")
    relativos = [
        alvo
        for alvo in _ALVO.findall(texto)
        if not alvo.startswith(("https://", "#", "mailto:"))
    ]

    ausentes = [a for a in relativos if not (_RAIZ / a.split("#")[0]).exists()]

    assert relativos
    assert ausentes == []
