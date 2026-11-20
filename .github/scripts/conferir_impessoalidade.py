"""Confere a impessoalidade dos arquivos versionados do repositório.

Tudo o que é versionado fala com quem clonou o repositório, não com quem o
mantém. O script guarda três regras e vale para o repositório inteiro (mini
projetos, cursos, tutoriais e arquivos da raiz):

1. O nome do mantenedor não aparece em prosa, comentário ou código fora dos
   arquivos de autoria e de canal (`_NOME_PERMITIDO_POR_ARQUIVO` e
   `_NOME_PERMITIDO_POR_CAMINHO`).
2. As instruções para o Claude (`CLAUDE.md` e `.claude/`) e as specs (`specs/`),
   em qualquer pasta, não apontam para skills pessoais, que quem clona não tem.
3. Nenhum arquivo aponta para o que só existe na máquina de quem mantém (pastas
   e configuração pessoal) nem para um link de sessão do Claude.

Roda só com a biblioteca padrão, sem ambiente virtual: `python3
.github/scripts/conferir_impessoalidade.py`, de qualquer pasta do repositório. A
lista de arquivos vem de `git ls-files` na raiz. Sai com código 0 se estiver tudo
limpo, 1 com as ocorrências (`caminho:linha`) e 2 sem git ou fora de um
repositório git. O CI roda este script a cada PR.
"""

import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

# ---------------------------------------------------------------------------
# Escopo
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
# funciona para quem clonou. As famílias (`atualizar-*`, `auditoria-*`) vão por
# padrão, para a skill nova da família não passar. O lookbehind evita casar
# caminhos (`docs/stack.md`).
_SKILL_PESSOAL = re.compile(
    r"(?<![\w./-])/(idioma|spec|estilo-arquivos|fechar-sessao|atualizar-[a-z]+"
    r"|auditoria-[a-z]+|revisar-dependabot|nova-interface|stack|novo-projeto"
    r"|qualidade-python|qualidade|limpar-branches|preparar-release"
    r"|enxugar-memoria)\b"
)

# Caminhos que só existem na máquina de quem mantém e o link de uma página publicada
# numa sessão do Claude: quem clonou não tem nenhum dos dois.
_SO_NA_MAQUINA = re.compile(
    r"CLAUDE\.md global|regra global|~[/\\]\.claude\b"
    r"|[A-Za-z]:[/\\]+Users[/\\]+ryanv\b|orientacoes-pessoais"
    r"|claude\.ai/(code/)?artifacts?/",
    re.IGNORECASE,
)

# Extensões binárias, sem texto para conferir.
_BINARIAS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf"}

# Lockfiles são gerados; o nome do mantenedor nunca é escrito à mão neles.
_GERADOS = {"uv.lock"}

# Este script cita o nome e as skills de propósito, nas próprias regras.
_ESTE_SCRIPT = PurePosixPath(".github/scripts/conferir_impessoalidade.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _arquivos_versionados() -> tuple[Path, list[str]] | None:
    """Lista os arquivos versionados do repositório inteiro.

    Returns:
        tuple[Path, list[str]] | None: a raiz do repositório e os caminhos
        relativos a ela, com `/` como separador; `None` sem git ou fora de um
        repositório git.
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
        return None
    return Path(raiz), [caminho for caminho in saida.split("\0") if caminho]


def _eh_texto(caminho: str) -> bool:
    """Diz se o arquivo é texto conferível (nem binário, nem gerado).

    Args:
        caminho (str): caminho relativo à raiz do repositório.

    Returns:
        bool: `True` se o arquivo deve ser lido.
    """
    posix = PurePosixPath(caminho)
    return posix.suffix.lower() not in _BINARIAS and posix.name not in _GERADOS


def _eh_instrucao_ou_spec(caminho: str) -> bool:
    """Diz se o arquivo instrui o Claude de quem contribui ou é uma spec.

    Args:
        caminho (str): caminho relativo à raiz do repositório.

    Returns:
        bool: `True` para `CLAUDE.md` e para qualquer arquivo sob `.claude/` ou
        `specs/`.
    """
    partes = PurePosixPath(caminho).parts
    return partes[-1] == "CLAUDE.md" or ".claude" in partes or "specs" in partes


def _linhas_que_casam(raiz: Path, caminho: str, padrao: re.Pattern[str]) -> list[str]:
    """Procura um padrão linha a linha num arquivo versionado.

    Args:
        raiz (Path): raiz do repositório.
        caminho (str): caminho relativo à raiz.
        padrao (re.Pattern[str]): o que procurar.

    Returns:
        list[str]: uma entrada `caminho:linha` por linha que casa.
    """
    # Arquivo listado pelo git mas apagado do disco (remoção ainda não commitada)
    # não tem o que conferir.
    arquivo = raiz / caminho
    if not arquivo.is_file():
        return []
    texto = arquivo.read_text(encoding="utf-8", errors="ignore")
    return [
        f"{caminho}:{numero}"
        for numero, linha in enumerate(texto.splitlines(), start=1)
        if padrao.search(linha)
    ]


# ---------------------------------------------------------------------------
# Regras
# ---------------------------------------------------------------------------


def nome_fora_da_autoria(raiz: Path, arquivos: list[str]) -> list[str]:
    """Acha o nome do mantenedor fora dos arquivos de autoria e de canal.

    Args:
        raiz (Path): raiz do repositório.
        arquivos (list[str]): caminhos versionados, relativos à raiz.

    Returns:
        list[str]: as ocorrências, no formato `caminho:linha`.
    """
    ocorrencias: list[str] = []
    for caminho in arquivos:
        posix = PurePosixPath(caminho)
        if not _eh_texto(caminho) or posix == _ESTE_SCRIPT:
            continue
        if (
            posix.name in _NOME_PERMITIDO_POR_ARQUIVO
            or caminho in _NOME_PERMITIDO_POR_CAMINHO
        ):
            continue
        ocorrencias += _linhas_que_casam(raiz, caminho, _NOME)
    return ocorrencias


def skills_pessoais_nas_instrucoes(raiz: Path, arquivos: list[str]) -> list[str]:
    """Acha comandos de skills pessoais em `CLAUDE.md`, `.claude/` e `specs/`.

    Args:
        raiz (Path): raiz do repositório.
        arquivos (list[str]): caminhos versionados, relativos à raiz.

    Returns:
        list[str]: as ocorrências, no formato `caminho:linha`.
    """
    ocorrencias: list[str] = []
    for caminho in arquivos:
        if _eh_instrucao_ou_spec(caminho):
            ocorrencias += _linhas_que_casam(raiz, caminho, _SKILL_PESSOAL)
    return ocorrencias


def caminhos_da_maquina(raiz: Path, arquivos: list[str]) -> list[str]:
    """Acha caminhos da máquina de quem mantém e links de sessão do Claude.

    Args:
        raiz (Path): raiz do repositório.
        arquivos (list[str]): caminhos versionados, relativos à raiz.

    Returns:
        list[str]: as ocorrências, no formato `caminho:linha`.
    """
    ocorrencias: list[str] = []
    for caminho in arquivos:
        if _eh_texto(caminho) and PurePosixPath(caminho) != _ESTE_SCRIPT:
            ocorrencias += _linhas_que_casam(raiz, caminho, _SO_NA_MAQUINA)
    return ocorrencias


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------


def main() -> int:
    """Roda as três regras e relata o resultado.

    Returns:
        int: 0 sem ocorrências, 1 com ocorrências, 2 sem git.
    """
    versionados = _arquivos_versionados()
    if versionados is None:
        print("Sem git ou fora de um repositório git: nada para conferir.")
        return 2
    raiz, arquivos = versionados

    regras = {
        "nome do mantenedor fora da autoria": nome_fora_da_autoria,
        "skills pessoais nas instruções do Claude e nas specs": (
            skills_pessoais_nas_instrucoes
        ),
        "caminhos da máquina e links de sessão": caminhos_da_maquina,
    }
    falhou = False
    for descricao, regra in regras.items():
        ocorrencias = regra(raiz, arquivos)
        if ocorrencias:
            falhou = True
            print(f"FALHOU: {descricao} ({len(ocorrencias)})")
            for ocorrencia in ocorrencias:
                print(f"  {ocorrencia}")
        else:
            print(f"ok: {descricao}")
    print(f"{len(arquivos)} arquivos versionados conferidos.")
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
