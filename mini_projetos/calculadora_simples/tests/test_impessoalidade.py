"""Testes de impessoalidade dos arquivos versionados do repositório.

Tudo o que é versionado fala com quem clonou o repositório, não com quem o
mantém. Os testes guardam duas regras: o nome do mantenedor não aparece em prosa,
comentário ou código fora dos arquivos de autoria e de canal, e as instruções para
o Claude (`CLAUDE.md` e `.claude/`) não apontam para skills pessoais, que quem
clona não tem.

Estratégia de isolamento: a lista de arquivos vem de `git ls-files` na raiz do
repositório (sempre o repositório inteiro, não só esta pasta); fora de uma árvore
git, ou sem o git instalado, os testes são pulados. Este arquivo é idêntico nos
quatro projetos de `mini_projetos/`.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path, PurePosixPath

import pytest

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# O nome do mantenedor como palavra inteira; o domínio, o perfil e o nome do
# repositório (`ryanmorais.com.br`, `ryanvmorais`, `aprenda-com-ryan-morais`) ficam
# de fora porque a busca distingue maiúsculas.
_NOME = re.compile(r"\bRyan\b")

# Onde o nome é metadado legítimo: autoria (licença e `pyproject.toml`, em qualquer
# pasta) e o nome do canal nos READMEs da raiz do repositório.
_NOME_PERMITIDO_POR_ARQUIVO = {"LICENSE", "pyproject.toml"}
_NOME_PERMITIDO_POR_CAMINHO = {"README.md", "README.en.md"}

# Skills do mantenedor: um comando `/nome` delas em `CLAUDE.md` ou `.claude/` não
# funciona para quem clonou. O lookbehind evita casar caminhos (`docs/stack.md`).
_SKILL_PESSOAL = re.compile(
    r"(?<![\w./-])/(idioma|spec|estilo-arquivos|fechar-sessao|atualizar-docs"
    r"|atualizar-dependencias|revisar-dependabot|nova-interface|stack"
    r"|novo-projeto|qualidade-python)\b"
)

# Extensões binárias, sem texto para conferir.
_BINARIAS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf"}

# Lockfiles são gerados; o nome do mantenedor nunca é escrito à mão neles.
_GERADOS = {"uv.lock"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _arquivos_versionados() -> tuple[Path, list[str]]:
    """Lista os arquivos versionados do repositório inteiro.

    Returns:
        tuple[Path, list[str]]: a raiz do repositório e os caminhos relativos a
        ela, com `/` como separador. Os dois vazios se não houver git.
    """
    try:
        raiz = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            cwd=Path(__file__).parent,
            text=True,
        ).stdout.strip()
        saida = subprocess.run(
            ["git", "ls-files", "-z"],
            capture_output=True,
            check=True,
            cwd=raiz,
            text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return Path(), []
    return Path(raiz), [caminho for caminho in saida.split("\0") if caminho]


def _eh_texto(caminho: str) -> bool:
    """Diz se o arquivo é texto conferível (nem binário, nem gerado).

    Args:
        caminho (str): caminho relativo à raiz do repositório.

    Returns:
        bool: `True` se o arquivo deve ser lido pelos testes.
    """
    posix = PurePosixPath(caminho)
    return posix.suffix.lower() not in _BINARIAS and posix.name not in _GERADOS


def _eh_instrucao_claude(caminho: str) -> bool:
    """Diz se o arquivo instrui o Claude de quem contribui.

    Args:
        caminho (str): caminho relativo à raiz do repositório.

    Returns:
        bool: `True` para `CLAUDE.md` e para qualquer arquivo sob `.claude/`.
    """
    partes = PurePosixPath(caminho).parts
    return partes[-1] == "CLAUDE.md" or ".claude" in partes


_RAIZ, _ARQUIVOS = _arquivos_versionados()

# Sem git (ou fora de uma árvore git) não há o que conferir.
_precisa_do_git = pytest.mark.skipif(
    not _ARQUIVOS, reason="sem git ou fora de um repositório git"
)


# ---------------------------------------------------------------------------
# Nome do mantenedor
# ---------------------------------------------------------------------------


@_precisa_do_git
def test_nome_do_mantenedor_so_aparece_nos_arquivos_de_autoria() -> None:
    """O nome fica em autoria e canal; em prosa e código, vale o papel."""
    ocorrencias: list[str] = []
    for caminho in _ARQUIVOS:
        nome = PurePosixPath(caminho).name
        if not _eh_texto(caminho) or nome == "test_impessoalidade.py":
            continue
        if (
            nome in _NOME_PERMITIDO_POR_ARQUIVO
            or caminho in _NOME_PERMITIDO_POR_CAMINHO
        ):
            continue
        texto = (_RAIZ / caminho).read_text(encoding="utf-8", errors="ignore")
        for numero, linha in enumerate(texto.splitlines(), start=1):
            if _NOME.search(linha):
                ocorrencias.append(f"{caminho}:{numero}")
    assert not ocorrencias, f"nome do mantenedor fora da autoria: {ocorrencias}"


# ---------------------------------------------------------------------------
# Instruções para o Claude
# ---------------------------------------------------------------------------


@_precisa_do_git
def test_instrucoes_do_claude_nao_citam_skills_pessoais() -> None:
    """`CLAUDE.md` e `.claude/` descrevem o projeto, não o fluxo de quem mantém."""
    ocorrencias: list[str] = []
    for caminho in _ARQUIVOS:
        if not _eh_instrucao_claude(caminho):
            continue
        texto = (_RAIZ / caminho).read_text(encoding="utf-8", errors="ignore")
        for numero, linha in enumerate(texto.splitlines(), start=1):
            if _SKILL_PESSOAL.search(linha):
                ocorrencias.append(f"{caminho}:{numero}")
    assert not ocorrencias, f"skills pessoais nas instruções: {ocorrencias}"
