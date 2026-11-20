"""Lista de Tarefas via terminal — projeto educacional de arquivo JSON e pathlib.

Material de estudo para prática de leitura e gravação de arquivo com `json` e
`pathlib` (sempre em UTF-8), da lista de dicionários como um "banco de dados"
simples e do tratamento do que pode dar errado com um arquivo: ele ainda não
existir, estar corrompido ou o programa cair no meio da gravação. Python puro
(sem dependências externas).

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. TIPOS (Tarefa, Conferencia, Leitor, Relogio): A tarefa e os parâmetros injetáveis.
2. CONSTANTES (ARQUIVO_PADRAO, TAMANHO_MAXIMO, CAMPOS, OPCOES): Arquivo e limites.
3. ARQUIVO (validar_tarefas, guardar_corrompido, carregar_tarefas, salvar_tarefas):
   Ler, conferir e gravar o tarefas.json.
4. FORMATAÇÃO (formatar_data, formatar_tarefa): A linha de cada tarefa na tela.
5. ENTRADA VALIDADA (conferir_opcao, conferir_texto, conferir_numero): O que foi
   digitado, conferido sem lançar exceção.
6. INTERFACE (limpar_tela, exibir_tela): Limpeza de tela e desenho do quadro.
7. LEITURA DO TECLADO (ler_texto, ler_numero, confirmar): Pedir de novo na recusa.
8. AÇÕES (adicionar, alternar_conclusao, editar, remover): Alterar e gravar.
9. LOOP PRINCIPAL (main): O menu em laço e a saída com Ctrl+C.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple, TypedDict

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos e os emojis abaixo com
# UnicodeEncodeError; reconfigurar para UTF-8 evita o crash em qualquer ambiente.
# Vale só para a tela: o arquivo tem o `encoding="utf-8"` próprio.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


class Tarefa(TypedDict):
    """Uma tarefa da lista: um dicionário comum, com as chaves declaradas.

    Na execução, `Tarefa` é um `dict` como outro qualquer, e é por isso que o
    `json.dumps` grava a lista como está. O `TypedDict` só conta ao mypy quais
    chaves existem e o tipo de cada uma.

    Attributes:
        texto (str): O que fazer, de 1 a 80 caracteres, sem os espaços das pontas.
        concluida (bool): False para pendente e True para concluída.
        criada_em (str): Data de criação em ISO 8601, "AAAA-MM-DD".
    """

    texto: str
    concluida: bool
    criada_em: str


class Conferencia(NamedTuple):
    """Resultado da conferência de uma entrada: o valor aceito ou o motivo da recusa.

    Só um dos dois campos vem preenchido; o outro é "".

    Attributes:
        valor (str): A entrada aceita, sem os espaços das pontas.
        recusa (str): A mensagem que explica por que a entrada foi recusada.
    """

    valor: str
    recusa: str


# As funções que leem o teclado recebem `ler` (que vale `input` em `main`), e
# `main` recebe também `agora` (que vale `datetime.now`) e o caminho do arquivo.
# Quem usa o programa não percebe diferença; os testes passam um teclado e um
# relógio falsos e uma pasta temporária, e nunca tocam no tarefas.json de
# verdade. O `type` dá um nome curto a um tipo comprido, para as assinaturas
# abaixo ficarem legíveis.
type Leitor = Callable[[str], str]
type Relogio = Callable[[], datetime]


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------


# `Path(__file__).parent` é a pasta do main.py, de onde quer que o programa seja
# chamado: com `Path("tarefas.json")`, rodar o programa de outra pasta criaria
# uma segunda lista, vazia. O `/` monta o caminho com o separador de cada
# sistema. Num programa instalado, a pasta dele pode não aceitar escrita, e o
# lugar certo seria a pasta do usuário (`Path.home()`); num projeto clonado,
# a pasta do projeto sempre aceita.
ARQUIVO_PADRAO = Path(__file__).parent / "tarefas.json"

# Cabe numa linha da tela junto com o número, a marca e a data.
TAMANHO_MAXIMO = 80

# As chaves que toda tarefa do arquivo tem que ter, nem mais nem menos.
CAMPOS = {"texto", "concluida", "criada_em"}

# O menu, numerado a partir de 1 na tela.
OPCOES = ["Adicionar", "Concluir", "Editar", "Remover", "Sair"]


# ---------------------------------------------------------------------------
# Arquivo
# ---------------------------------------------------------------------------


def validar_tarefas(dados: object) -> list[Tarefa]:
    """Confere se o conteúdo do arquivo tem a forma de uma lista de tarefas.

    Um JSON válido pode não ser uma lista de tarefas (`{}`, `[1, 2]`, uma
    tarefa sem texto): conferir aqui evita que o programa quebre mais tarde,
    longe da causa. O tamanho do texto não é conferido, porque um texto longo
    editado à mão não justifica tratar a lista inteira como corrompida.

    Args:
        dados (object): O que o `json.loads` devolveu.

    Returns:
        list[Tarefa]: A mesma lista, agora com o tipo conferido.

    Raises:
        ValueError: Se a forma estiver errada, com o motivo.
    """
    if not isinstance(dados, list):
        raise ValueError("o arquivo não guarda uma lista")

    tarefas: list[Tarefa] = []
    for numero, item in enumerate(dados, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"a tarefa {numero} não é um objeto")
        # Comparar os conjuntos pega a chave que falta e a chave a mais.
        if set(item) != CAMPOS:
            raise ValueError(f"a tarefa {numero} não tem as chaves {sorted(CAMPOS)}")

        texto = item["texto"]
        concluida = item["concluida"]
        criada_em = item["criada_em"]
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError(f"a tarefa {numero} não tem texto")
        if not isinstance(concluida, bool):
            raise ValueError(f"a tarefa {numero} não diz se está concluída")
        if not isinstance(criada_em, str):
            raise ValueError(f"a tarefa {numero} não tem a data de criação")
        # A data inválida faz o próprio `fromisoformat` lançar ValueError.
        date.fromisoformat(criada_em)

        tarefas.append({"texto": texto, "concluida": concluida, "criada_em": criada_em})
    return tarefas


def guardar_corrompido(arquivo: Path, agora: Relogio = datetime.now) -> Path:
    """Renomeia o arquivo corrompido para uma cópia com a data e a hora no nome.

    A cópia fica na mesma pasta, como `tarefas.corrompido-AAAAMMDD-HHMMSS.json`.
    Se esse nome já existir (dois arquivos corrompidos no mesmo segundo), ganha
    `-2`, `-3`, até achar um livre.

    Args:
        arquivo (Path): O arquivo corrompido.
        agora (Relogio, optional): Função que devolve a data e a hora do
            momento. Padrão: `datetime.now`.

    Returns:
        Path: O caminho da cópia.
    """
    carimbo = agora().strftime("%Y%m%d-%H%M%S")
    copia = arquivo.with_name(f"{arquivo.stem}.corrompido-{carimbo}.json")
    contador = 2
    while copia.exists():
        copia = arquivo.with_name(
            f"{arquivo.stem}.corrompido-{carimbo}-{contador}.json"
        )
        contador += 1

    # `rename`, e não `replace`: o `replace` sobrescreveria em silêncio uma
    # cópia com o mesmo nome, e a cópia anterior nunca pode se perder.
    arquivo.rename(copia)
    return copia


def carregar_tarefas(
    arquivo: Path, agora: Relogio = datetime.now
) -> tuple[list[Tarefa], str]:
    """Lê a lista do arquivo, tratando a primeira execução e o arquivo corrompido.

    Args:
        arquivo (Path): O arquivo da lista.
        agora (Relogio, optional): Função que devolve a data e a hora do
            momento, usada no nome da cópia do corrompido. Padrão:
            `datetime.now`.

    Returns:
        tuple[list[Tarefa], str]: A lista e o aviso para a primeira tela, que
            é "" quando o arquivo não existe ou é válido.
    """
    # Primeira execução: a lista começa vazia, e o arquivo só nasce na primeira
    # alteração.
    if not arquivo.exists():
        return [], ""

    try:
        tarefas = validar_tarefas(json.loads(arquivo.read_text(encoding="utf-8")))
    except ValueError:
        # Um `except` só pega os três problemas: o JSON inválido
        # (`json.JSONDecodeError`), o arquivo que não é UTF-8
        # (`UnicodeDecodeError`) e a forma errada (o `ValueError` do
        # `validar_tarefas`), porque os dois primeiros são subclasses de
        # `ValueError`.
        copia = guardar_corrompido(arquivo, agora)
        aviso = (
            f"⚠️ O arquivo {arquivo.name} estava corrompido. "
            f"A cópia ficou em {copia.name}, e a lista começou vazia."
        )
        return [], aviso
    return tarefas, ""


def salvar_tarefas(tarefas: list[Tarefa], arquivo: Path) -> None:
    """Grava a lista inteira no arquivo, de forma atômica.

    O texto vai primeiro para `tarefas.json.tmp`, na mesma pasta, que depois
    substitui o arquivo de uma vez. Gravar direto no arquivo o esvaziaria antes
    de escrever, e uma queda nesse meio deixaria a lista pela metade.

    Args:
        tarefas (list[Tarefa]): A lista a gravar.
        arquivo (Path): O arquivo da lista.
    """
    # `ensure_ascii=False` grava "pão" em vez de "pão", e `indent=2` põe
    # uma chave por linha: o arquivo se lê num editor qualquer.
    texto = json.dumps(tarefas, ensure_ascii=False, indent=2) + "\n"
    temporario = arquivo.with_name(f"{arquivo.name}.tmp")
    temporario.write_text(texto, encoding="utf-8")
    # O `replace` troca um arquivo pelo outro numa operação só, no Windows, no
    # Linux e no macOS, desde que os dois estejam no mesmo disco: por isso o
    # temporário fica na mesma pasta.
    temporario.replace(arquivo)


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------


def formatar_data(criada_em: str) -> str:
    """Converte a data do arquivo para a da tela: "2026-11-20" vira "20/11/2026".

    Args:
        criada_em (str): Data em ISO 8601, "AAAA-MM-DD".

    Returns:
        str: A mesma data em "DD/MM/AAAA".
    """
    return date.fromisoformat(criada_em).strftime("%d/%m/%Y")


def formatar_tarefa(numero: int, tarefa: Tarefa) -> str:
    """Monta a linha da tarefa: " 1. [ ] 20/11/2026  Estudar pathlib".

    A data vem antes do texto porque tem tamanho fixo: assim as colunas ficam
    alinhadas sem completar o texto com espaços.

    Args:
        numero (int): O número da tarefa na tela, a partir de 1.
        tarefa (Tarefa): A tarefa.

    Returns:
        str: A linha, com o número alinhado à direita em 2 posições.
    """
    marca = "[x]" if tarefa["concluida"] else "[ ]"
    data = formatar_data(tarefa["criada_em"])
    return f"{numero:>2}. {marca} {data}  {tarefa['texto']}"


# ---------------------------------------------------------------------------
# Entrada validada
# ---------------------------------------------------------------------------


def conferir_opcao(entrada: str) -> int | None:
    """Confere se a entrada é o número de uma opção do menu.

    Args:
        entrada (str): O que foi digitado no menu.

    Returns:
        int | None: O número da opção, de 1 a `len(OPCOES)`, ou None para
            qualquer outra coisa.
    """
    limpa = entrada.strip()
    # `isdecimal()` antes do `int()` dispensa o `try`. O `isdigit()` não serve:
    # ele aceita caracteres como "²", que o `int()` recusa com ValueError.
    if limpa.isdecimal() and 1 <= int(limpa) <= len(OPCOES):
        return int(limpa)
    return None


def conferir_texto(entrada: str) -> Conferencia:
    """Confere se o texto da tarefa tem de 1 a `TAMANHO_MAXIMO` caracteres.

    Os espaços das pontas saem antes da conferência. Textos repetidos são
    aceitos.

    Args:
        entrada (str): O texto digitado.

    Returns:
        Conferencia: O texto aceito, ou a mensagem de recusa.
    """
    texto = entrada.strip()
    if not texto or len(texto) > TAMANHO_MAXIMO:
        return Conferencia(
            "", f"❌ Digite um texto de 1 a {TAMANHO_MAXIMO} caracteres."
        )
    return Conferencia(texto, "")


def conferir_numero(entrada: str, total: int) -> Conferencia:
    """Confere se a entrada é o número de uma tarefa da lista.

    Args:
        entrada (str): O número digitado.
        total (int): Quantas tarefas a lista tem.

    Returns:
        Conferencia: O número aceito (ainda como texto), ou a mensagem de
            recusa com o intervalo válido.
    """
    limpa = entrada.strip()
    # A mesma conferência do `conferir_opcao`: `isdecimal()` antes do `int()`.
    if limpa.isdecimal() and 1 <= int(limpa) <= total:
        return Conferencia(limpa, "")
    return Conferencia("", f"❌ Digite um número de 1 a {total}.")


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def limpar_tela() -> None:
    """Limpa o terminal, detectando o sistema operacional automaticamente."""
    # 'nt' é o identificador interno para Windows. O comando é sempre um destes
    # dois textos fixos, nunca algo digitado pelo usuário.
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def exibir_tela(tarefas: list[Tarefa], mensagem: str) -> None:
    """Desenha o quadro: título, lista, contagem, menu e a mensagem anterior.

    Args:
        tarefas (list[Tarefa]): A lista de tarefas.
        mensagem (str): Resultado da ação anterior, ou "" se não houver.
    """
    print("======== LISTA DE TAREFAS ========")
    print()
    if tarefas:
        for numero, tarefa in enumerate(tarefas, start=1):
            print(formatar_tarefa(numero, tarefa))
    else:
        print("Nenhuma tarefa por aqui. Escolha 1 para adicionar a primeira.")
    print()

    # `True` conta como 1 e `False` como 0, então a soma é o total de concluídas.
    concluidas = sum(tarefa["concluida"] for tarefa in tarefas)
    print(f"Pendentes: {len(tarefas) - concluidas} | Concluídas: {concluidas}")
    print()
    for numero, opcao in enumerate(OPCOES, start=1):
        print(f"{numero} : {opcao}")
    print()
    if mensagem:
        print(mensagem)


# ---------------------------------------------------------------------------
# Leitura do teclado
# ---------------------------------------------------------------------------


def ler_texto(ler: Leitor, pedido: str) -> str:
    """Pede o texto da tarefa até ele ser aceito.

    Na recusa, a mensagem sai logo abaixo, sem limpar a tela, para a lista
    continuar à vista.

    Args:
        ler (Leitor): Função que lê o teclado.
        pedido (str): Texto mostrado antes de ler.

    Returns:
        str: O texto aceito, sem os espaços das pontas.
    """
    while True:
        conferencia = conferir_texto(ler(pedido))
        if not conferencia.recusa:
            return conferencia.valor
        print(conferencia.recusa)


def ler_numero(ler: Leitor, total: int) -> int:
    """Pede o número de uma tarefa até ele estar na lista.

    Args:
        ler (Leitor): Função que lê o teclado.
        total (int): Quantas tarefas a lista tem.

    Returns:
        int: A posição da tarefa na lista (o número digitado menos 1).
    """
    while True:
        conferencia = conferir_numero(ler(f"Número da tarefa (1 a {total}): "), total)
        if not conferencia.recusa:
            return int(conferencia.valor) - 1
        print(conferencia.recusa)


def confirmar(ler: Leitor, pergunta: str) -> bool:
    """Faz uma pergunta de sim ou não, repetindo até ouvir s ou n.

    Args:
        ler (Leitor): Função que lê o teclado.
        pergunta (str): A pergunta, sem o "(s/n)".

    Returns:
        bool: True para `s` e False para `n`, em maiúscula ou minúscula.
    """
    while True:
        resposta = ler(f"{pergunta} (s/n): ").strip().lower()
        if resposta == "s":
            return True
        if resposta == "n":
            return False
        print("❌ Responda s (sim) ou n (não).")


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------


# Cada ação altera a lista no lugar, grava logo em seguida e devolve a mensagem
# da próxima tela: um Ctrl+C ou o terminal fechado não perdem nada, porque nada
# fica só na memória. Concluir, editar e remover começam conferindo se há
# tarefas, para não pedir um número que não existe.
SEM_TAREFAS = "📭 Ainda não há tarefas. Escolha 1 para adicionar a primeira."


def adicionar(tarefas: list[Tarefa], arquivo: Path, ler: Leitor, hoje: date) -> str:
    """Acrescenta uma tarefa pendente no fim da lista e grava.

    Args:
        tarefas (list[Tarefa]): A lista, alterada no lugar.
        arquivo (Path): O arquivo da lista.
        ler (Leitor): Função que lê o teclado.
        hoje (date): A data de criação da tarefa.

    Returns:
        str: A mensagem que confirma o texto adicionado.
    """
    texto = ler_texto(ler, f"Texto da tarefa (até {TAMANHO_MAXIMO} caracteres): ")
    tarefas.append({"texto": texto, "concluida": False, "criada_em": hoje.isoformat()})
    salvar_tarefas(tarefas, arquivo)
    return f"✅ Tarefa adicionada: {texto}"


def alternar_conclusao(tarefas: list[Tarefa], arquivo: Path, ler: Leitor) -> str:
    """Conclui a tarefa pendente ou reabre a concluída, e grava.

    Args:
        tarefas (list[Tarefa]): A lista, alterada no lugar.
        arquivo (Path): O arquivo da lista.
        ler (Leitor): Função que lê o teclado.

    Returns:
        str: A mensagem que diz se a tarefa foi concluída ou reaberta.
    """
    if not tarefas:
        return SEM_TAREFAS

    tarefa = tarefas[ler_numero(ler, len(tarefas))]
    tarefa["concluida"] = not tarefa["concluida"]
    salvar_tarefas(tarefas, arquivo)
    if tarefa["concluida"]:
        return f"✅ Tarefa concluída: {tarefa['texto']}"
    return f"🔄 Tarefa reaberta: {tarefa['texto']}"


def editar(tarefas: list[Tarefa], arquivo: Path, ler: Leitor) -> str:
    """Troca o texto de uma tarefa, sem mudar a situação nem a data, e grava.

    Args:
        tarefas (list[Tarefa]): A lista, alterada no lugar.
        arquivo (Path): O arquivo da lista.
        ler (Leitor): Função que lê o teclado.

    Returns:
        str: A mensagem que confirma o texto novo.
    """
    if not tarefas:
        return SEM_TAREFAS

    tarefa = tarefas[ler_numero(ler, len(tarefas))]
    tarefa["texto"] = ler_texto(ler, f"Novo texto (até {TAMANHO_MAXIMO} caracteres): ")
    salvar_tarefas(tarefas, arquivo)
    return f"✏️ Tarefa editada: {tarefa['texto']}"


def remover(tarefas: list[Tarefa], arquivo: Path, ler: Leitor) -> str:
    """Tira uma tarefa da lista depois da confirmação, e grava.

    É a única ação que apaga dado gravado, por isso pergunta antes. As tarefas
    seguintes passam a usar o número de baixo.

    Args:
        tarefas (list[Tarefa]): A lista, alterada no lugar.
        arquivo (Path): O arquivo da lista.
        ler (Leitor): Função que lê o teclado.

    Returns:
        str: A mensagem que confirma a remoção, ou que diz que nada saiu.
    """
    if not tarefas:
        return SEM_TAREFAS

    indice = ler_numero(ler, len(tarefas))
    texto = tarefas[indice]["texto"]
    if not confirmar(ler, f'Remover "{texto}"?'):
        return "↩️ Nada foi removido."

    tarefas.pop(indice)
    salvar_tarefas(tarefas, arquivo)
    return f"🗑️ Tarefa removida: {texto}"


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main(
    ler: Leitor = input,
    agora: Relogio = datetime.now,
    arquivo: Path = ARQUIVO_PADRAO,
) -> None:
    """Roda o programa: carrega a lista e repete o menu até o usuário sair.

    Ctrl+C e o fim da entrada (Ctrl+D no Linux) encerram o programa em qualquer
    ponto com uma despedida, sem stack trace. A ação interrompida no meio
    simplesmente não acontece, e o que já foi feito está gravado.

    Args:
        ler (Leitor, optional): Função que lê o teclado. Padrão: `input`.
        agora (Relogio, optional): Função que devolve a data e a hora do
            momento. Padrão: `datetime.now`.
        arquivo (Path, optional): O arquivo da lista. Padrão: `ARQUIVO_PADRAO`.
    """
    # O aviso de arquivo corrompido, se houver, é a mensagem da primeira tela.
    tarefas, mensagem = carregar_tarefas(arquivo, agora)
    try:
        while True:
            limpar_tela()
            exibir_tela(tarefas, mensagem)
            opcao = conferir_opcao(ler("Escolha uma opção: "))
            if opcao == 1:
                mensagem = adicionar(tarefas, arquivo, ler, agora().date())
            elif opcao == 2:
                mensagem = alternar_conclusao(tarefas, arquivo, ler)
            elif opcao == 3:
                mensagem = editar(tarefas, arquivo, ler)
            elif opcao == 4:
                mensagem = remover(tarefas, arquivo, ler)
            elif opcao == 5:
                break
            else:
                mensagem = f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}."

        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída: as funções de leitura ficam só validando.
        print("\nLista encerrada. Até a próxima! 👋")


if __name__ == "__main__":
    main()
