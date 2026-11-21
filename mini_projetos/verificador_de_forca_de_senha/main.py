"""Verificador de força de senha via terminal — projeto educacional de regras e nota.

Material de estudo para prática de três ideias: regras escritas com `any()` e os
métodos de string (`islower`, `isupper` e `isdigit`), que dizem que tipos de
caractere a senha tem; o módulo `re`, que acha as repetições (`aaa`), ao lado
das janelas que acham as sequências (`abc`, `123`, `qwe`); e o `getpass`, que lê
a senha sem mostrá-la na tela. A nota, de 0 a 4, sai da entropia estimada, a
mesma conta do `gerador_de_senhas`, com a lista portuguesa de senhas comuns do
SecLists como trava. Python puro (sem dependências externas), e a senha digitada
não é guardada, não é mostrada e não sai do computador.

ESTRUTURA DO CÓDIGO (BASEADA EM FUNÇÕES):
1. TIPOS (Leitor, Analise): O parâmetro injetável e o resultado da verificação.
2. CONSTANTES (TIPOS, SEQUENCIAS, REPETICAO, LIMITES, NOMES, TAMANHO_MINIMO,
   NOTA_MAXIMA_CURTA, ARQUIVO_SENHAS_COMUNS, EXEMPLOS, OPCOES).
3. REGRAS (classificar, achar_repeticoes, achar_sequencias, juntar_trechos,
   contar_caracteres, carregar_senhas_comuns): O que a senha tem.
4. NOTA (calcular_entropia, descrever_entropia, dar_nota, analisar,
   faltam_caracteres): A conta, a nota e a análise inteira.
5. TEXTOS (juntar_nomes, sugerir, descrever_analise, descrever_exemplos): O
   resultado, as sugestões e os exemplos, devolvidos como texto.
6. PERGUNTAS (eh_numero, conferir_opcao): A escolha do menu, conferida.
7. OPÇÕES (opcao_verificar): O pedido da senha e a verificação.
8. INTERFACE (limpar_tela, exibir_tela): A limpeza e o desenho do quadro.
9. LOOP PRINCIPAL (main): O menu em laço e a saída com Ctrl+C.
"""

from __future__ import annotations

import getpass
import math
import os
import re
import string
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

# No Windows, stdout sem console UTF-8 (saída redirecionada/pipe, alguns
# executores de CI) cai para cp1252 e quebra os acentos, os emojis e os símbolos
# da conta (× e ≈) com UnicodeEncodeError; reconfigurar para UTF-8 evita o crash
# em qualquer ambiente.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


# `main` recebe `ler` (que vale `input`) e `ler_senha` (que vale
# `getpass.getpass`). O `input` e o `getpass.getpass` têm a mesma assinatura:
# recebem o texto do pedido e devolvem o que foi digitado. Quem usa o programa
# não percebe diferença; os testes passam um teclado falso. O `type` dá um nome
# curto a um tipo comprido, para as assinaturas abaixo ficarem legíveis.
type Leitor = Callable[[str], str]


class Analise(NamedTuple):
    """O que pesou na nota de uma senha, sem a senha.

    Só números, nomes de tipos e verdadeiro ou falso: como a senha não fica
    guardada aqui, nenhum texto montado a partir da análise consegue mostrá-la.

    Attributes:
        tamanho (int): Quantos caracteres a senha tem.
        contam (int): Quantos contam na entropia, com cada trecho previsível
            valendo um.
        tipos (list[str]): Os nomes dos tipos presentes, na ordem de `TIPOS`.
        alfabeto (int): A soma dos tamanhos dos tipos presentes.
        bits (float): A entropia estimada.
        repeticao (bool): True se a senha tem 3 ou mais caracteres iguais
            seguidos.
        sequencia (bool): True se a senha tem 3 ou mais caracteres em
            sequência.
        comum (bool): True se a senha inteira está na lista de senhas comuns.
        nota (int): De 0 a 4.
    """

    tamanho: int
    contam: int
    tipos: list[str]
    alfabeto: int
    bits: float
    repeticao: bool
    sequencia: bool
    comum: bool
    nota: int


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------


# O nome de cada tipo de caractere e de quantos caracteres ele tem, com os
# tamanhos do módulo `string`, os mesmos do `gerador_de_senhas`. Juntos, são 94.
TIPOS: dict[str, int] = {
    "minúsculas": len(string.ascii_lowercase),
    "maiúsculas": len(string.ascii_uppercase),
    "números": len(string.digits),
    "símbolos": len(string.punctuation),
}

# O alfabeto, os números e as três fileiras do teclado QWERTY (iguais no ABNT2 e
# no americano), lidos para a frente; o contrário de cada um sai do `[::-1]`.
SEQUENCIAS = (
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
)

# Lida peça por peça: `(.)` pega um caractere qualquer e o guarda no grupo 1;
# `\1` é "o mesmo caractere que o grupo 1 pegou"; `{2,}` pede pelo menos mais
# duas cópias dele. Juntos, 3 ou mais caracteres iguais seguidos. Com o
# IGNORECASE, `aAa` também conta.
REPETICAO = re.compile(r"(.)\1{2,}", re.IGNORECASE)

# Os bits a partir dos quais a nota sobe para 1, 2, 3 e 4: a nota é quantos
# destes limites a entropia alcança, e a máxima, 4, é quantos limites existem.
# A senha mínima do gerador (8 caracteres, 52,4 bits) fica em 2, a de 12
# caracteres (78,7 bits) em 3 e a forte padrão (16 caracteres, 104,9 bits) em 4.
LIMITES = (28, 36, 60, 80)

# O nome de cada nota, pelo índice: NOMES[2] é o nome da nota 2.
NOMES = ("muito fraca", "fraca", "razoável", "boa", "forte")

# Abaixo de 8 caracteres, a nota não passa de 1: sem a trava, 7 caracteres com
# os quatro tipos (45,9 bits) dariam razoável.
TAMANHO_MINIMO = 8
NOTA_MAXIMA_CURTA = 1

# Ao lado do `main.py`, de onde quer que o programa seja chamado.
ARQUIVO_SENHAS_COMUNS = Path(__file__).parent / "senhas_comuns.txt"

# Os exemplos comentados: senhas inventadas ou da lista de senhas comuns, nunca
# uma senha em uso. A nota de cada uma é calculada na hora, por `analisar`.
EXEMPLOS: list[tuple[str, str]] = [
    ("123mudar", "Está na lista das senhas mais usadas."),
    ("Gato@7", "Tem os quatro tipos, mas só 6 caracteres."),
    ("Senha@123", "Os quatro tipos, mas o 123 é uma sequência."),
    ("girassol-azul", "Só minúsculas e o hífen: o tamanho faz a força."),
    ("sotaque-haver-abreviar-briga", "Quatro palavras sorteadas: longa e fácil."),
]

# O menu, numerado a partir de 1 na tela.
OPCOES = ["Verificar uma senha", "Ver exemplos comentados", "Sair"]


# ---------------------------------------------------------------------------
# Regras
# ---------------------------------------------------------------------------


def classificar(senha: str) -> list[str]:
    """Diz que tipos de caractere a senha tem.

    Cada caractere entra em um tipo só: a letra acentuada passa no `islower` ou
    no `isupper`, e o que não é letra nem número (o espaço inclusive) é símbolo.

    Args:
        senha (str): A senha digitada.

    Returns:
        list[str]: Os nomes dos tipos presentes, na ordem de `TIPOS`.
    """
    # Um `any()` por tipo: para assim que acha o primeiro caractere dele.
    presentes = {
        "minúsculas": any(c.islower() for c in senha),
        "maiúsculas": any(c.isupper() for c in senha),
        "números": any(c.isdigit() for c in senha),
        "símbolos": any(not (c.islower() or c.isupper() or c.isdigit()) for c in senha),
    }
    return [tipo for tipo in TIPOS if presentes[tipo]]


def achar_repeticoes(senha: str) -> list[tuple[int, int]]:
    """Acha os trechos de 3 ou mais caracteres iguais seguidos, como `aaa`.

    A repetição usa a expressão regular `REPETICAO`, porque a referência ao
    grupo (`\\1`, "o mesmo caractere de antes") diz a regra numa linha; as
    sequências, em `achar_sequencias`, usam o operador `in`.

    Args:
        senha (str): A senha digitada.

    Returns:
        list[tuple[int, int]]: O início e o fim de cada trecho, como o `span()`
            de um `re.Match`.
    """
    return [m.span() for m in REPETICAO.finditer(senha)]


def achar_sequencias(senha: str) -> list[tuple[int, int]]:
    """Acha os trechos de 3 caracteres em sequência, como `abc`, `987` ou `qwe`.

    A sequência é "este trecho está dentro daquela string", e o operador `in`
    diz isso direto, sem uma expressão regular com todas as janelas possíveis.
    Uma sequência de 4 (`abcd`) devolve duas janelas que se sobrepõem, juntadas
    depois por `juntar_trechos`.

    Args:
        senha (str): A senha digitada.

    Returns:
        list[tuple[int, int]]: O início e o fim de cada janela em sequência, no
            mesmo formato de `achar_repeticoes`.
    """
    trechos = []
    for i in range(len(senha) - 2):
        # Em minúsculas, para `ABC` e `Abc` também contarem.
        janela = senha[i : i + 3].lower()
        if any(janela in s or janela in s[::-1] for s in SEQUENCIAS):
            trechos.append((i, i + 3))
    return trechos


def juntar_trechos(trechos: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Junta os trechos que se sobrepõem, para cada um valer um caractere só.

    Uma repetição que encosta numa sequência (`aaabc`) vira um trecho; dois
    trechos vizinhos sem sobreposição (`aaabbb`) continuam dois.

    Args:
        trechos (list[tuple[int, int]]): O início e o fim de cada trecho, em
            qualquer ordem.

    Returns:
        list[tuple[int, int]]: Os trechos juntados, em ordem.
    """
    juntos: list[tuple[int, int]] = []
    for inicio, fim in sorted(trechos):
        # Começa antes de o último terminar: os dois viram um só.
        if juntos and inicio < juntos[-1][1]:
            juntos[-1] = (juntos[-1][0], max(juntos[-1][1], fim))
        else:
            juntos.append((inicio, fim))
    return juntos


def contar_caracteres(tamanho: int, trechos: list[tuple[int, int]]) -> int:
    """Conta quantos caracteres valem na entropia.

    Args:
        tamanho (int): Quantos caracteres a senha tem.
        trechos (list[tuple[int, int]]): Os trechos previsíveis, já juntados.

    Returns:
        int: O tamanho menos os caracteres dentro dos trechos, mais um por
            trecho.
    """
    return tamanho - sum(fim - inicio for inicio, fim in trechos) + len(trechos)


def carregar_senhas_comuns(arquivo: Path) -> set[str]:
    """Lê a lista de senhas comuns, uma por linha.

    Args:
        arquivo (Path): O arquivo da lista, como o `ARQUIVO_SENHAS_COMUNS`.

    Returns:
        set[str]: As senhas em minúsculas, para a comparação não diferenciar
            maiúsculas de minúsculas.
    """
    # Um conjunto, porque a pergunta é só "está ou não está?", e o `in` num
    # conjunto não percorre as 150 senhas.
    return {linha.lower() for linha in arquivo.read_text(encoding="utf-8").splitlines()}


# ---------------------------------------------------------------------------
# Nota
# ---------------------------------------------------------------------------


def calcular_entropia(quantidade: int, tamanho_alfabeto: int) -> float:
    """Calcula a entropia, em bits, a mesma conta do `gerador_de_senhas`.

    A conta supõe que cada caractere foi sorteado, o que uma senha feita à mão
    não é: por isso o resultado é uma estimativa.

    Args:
        quantidade (int): Quantos caracteres contam.
        tamanho_alfabeto (int): Entre quantos caracteres cada um poderia estar.

    Returns:
        float: A quantidade vezes o log2 do tamanho do alfabeto.
    """
    return quantidade * math.log2(tamanho_alfabeto)


def descrever_entropia(quantidade: int, tamanho_alfabeto: int) -> str:
    """Monta a linha da entropia, com a conta.

    Args:
        quantidade (int): Quantos caracteres contam.
        tamanho_alfabeto (int): Entre quantos caracteres cada um poderia estar.

    Returns:
        str: A conta, como "Entropia estimada: 7 × log2(94) ≈ 45,9 bits".
    """
    bits = calcular_entropia(quantidade, tamanho_alfabeto)
    if bits.is_integer():
        resultado = f"= {int(bits)}"
    else:
        # `:.1f` arredonda para uma casa decimal com ponto; o `replace` troca
        # pela vírgula, sem depender do `locale` do sistema.
        resultado = "≈ " + f"{bits:.1f}".replace(".", ",")
    return (
        f"Entropia estimada: {quantidade} × log2({tamanho_alfabeto}) "
        f"{resultado} bits"
    )


def dar_nota(bits: float, tamanho: int, comum: bool) -> int:
    """Dá a nota de 0 a 4 pela entropia, com as duas travas.

    Args:
        bits (float): A entropia estimada.
        tamanho (int): Quantos caracteres a senha tem.
        comum (bool): True se a senha está na lista de senhas comuns.

    Returns:
        int: 0 para a senha comum; senão, quantos `LIMITES` os bits alcançam,
            no máximo `NOTA_MAXIMA_CURTA` abaixo do `TAMANHO_MINIMO`.
    """
    # A senha comum é das primeiras que alguém testa, qualquer que seja a conta.
    if comum:
        return 0
    # Cada `bits >= limite` vale True (1) ou False (0), e a soma conta os True.
    nota = sum(bits >= limite for limite in LIMITES)
    if tamanho < TAMANHO_MINIMO:
        nota = min(nota, NOTA_MAXIMA_CURTA)
    return nota


def analisar(senha: str, comuns: set[str]) -> Analise:
    """Aplica as regras à senha e dá a nota.

    É a última função que recebe a senha: a `Analise` devolvida não a guarda.

    Args:
        senha (str): A senha digitada, não vazia.
        comuns (set[str]): A lista de senhas comuns, em minúsculas.

    Returns:
        Analise: O que pesou na nota, e a nota.
    """
    tipos = classificar(senha)
    repeticoes = achar_repeticoes(senha)
    sequencias = achar_sequencias(senha)
    contam = contar_caracteres(len(senha), juntar_trechos(repeticoes + sequencias))
    alfabeto = sum(TIPOS[tipo] for tipo in tipos)
    bits = calcular_entropia(contam, alfabeto)
    # A senha inteira, nunca uma parte dela, como pede a NIST.
    comum = senha.lower() in comuns
    return Analise(
        tamanho=len(senha),
        contam=contam,
        tipos=tipos,
        alfabeto=alfabeto,
        bits=bits,
        repeticao=bool(repeticoes),
        sequencia=bool(sequencias),
        comum=comum,
        nota=dar_nota(bits, len(senha), comum),
    )


def faltam_caracteres(analise: Analise) -> int:
    """Conta quantos caracteres a mais, com o mesmo alfabeto, levam a 80 bits.

    Args:
        analise (Analise): A análise da senha.

    Returns:
        int: Os caracteres que faltam, ou 0 quando a entropia já chegou lá.
    """
    if analise.bits >= LIMITES[-1]:
        return 0
    # Cada caractere a mais soma o log2 do alfabeto; o `ceil` arredonda para
    # cima, porque meio caractere não existe.
    return math.ceil((LIMITES[-1] - analise.bits) / math.log2(analise.alfabeto))


# ---------------------------------------------------------------------------
# Textos
# ---------------------------------------------------------------------------


def juntar_nomes(nomes: list[str]) -> str:
    """Junta os nomes com vírgula e, no último, com "e".

    Args:
        nomes (list[str]): Os nomes, pelo menos um.

    Returns:
        str: Como "minúsculas, números e símbolos".
    """
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def sugerir(analise: Analise) -> list[str]:
    """Monta as sugestões do que melhorar, da mais importante para a menos.

    Args:
        analise (Analise): A análise da senha.

    Returns:
        list[str]: Uma sugestão por item, cada uma com o hífen na frente.
    """
    # A senha comum troca todas as outras: nenhum ajuste a salva.
    if analise.comum:
        return [
            "- Troque de senha: ela está entre as mais usadas,\n"
            "  e é das primeiras que alguém testa."
        ]
    sugestoes = []
    if analise.repeticao and analise.sequencia:
        sugestoes.append(
            "- Tire a repetição e a sequência:\n  elas quase não somam força."
        )
    elif analise.repeticao:
        sugestoes.append("- Tire a repetição: ela quase não soma força.")
    elif analise.sequencia:
        sugestoes.append("- Tire a sequência: ela quase não soma força.")
    if analise.nota < len(LIMITES):
        faltam = faltam_caracteres(analise)
        palavra = "caractere" if faltam == 1 else "caracteres"
        sugestoes.append(
            f"- Com mais {faltam} {palavra}, a senha passa de {LIMITES[-1]} bits.\n"
            "  Uma frase-senha é longa e fácil de decorar."
        )
    if not sugestoes:
        sugestoes.append("- Nada, pelas regras deste programa.")
    return sugestoes


def descrever_analise(analise: Analise) -> str:
    """Monta o resultado da verificação, sem a senha.

    A função só recebe a análise, que não guarda a senha: nenhuma linha daqui
    consegue mostrá-la, nem um trecho dela.

    Args:
        analise (Analise): A análise da senha.

    Returns:
        str: A nota, o tamanho, a entropia, os tipos, as três conferências e as
            sugestões.
    """
    caracteres = "caractere" if analise.tamanho == 1 else "caracteres"
    contam = "conta" if analise.contam == 1 else "contam"
    linhas = [
        f"🔎 Nota: {analise.nota} de {len(LIMITES)}, {NOMES[analise.nota]}",
        f"Tamanho: {analise.tamanho} {caracteres}, "
        f"{analise.contam} {contam} na entropia",
        descrever_entropia(analise.contam, analise.alfabeto),
        f"Tem: {juntar_nomes(analise.tipos)}",
    ]
    faltam = [tipo for tipo in TIPOS if tipo not in analise.tipos]
    if faltam:
        linhas.append(f"Falta: {juntar_nomes(faltam)}")
    # Os exemplos entre parênteses são sempre os mesmos, nunca o trecho achado.
    linhas += [
        ("❌ Tem" if analise.repeticao else "✅ Sem") + " repetição (como aaa ou 111)",
        ("❌ Tem" if analise.sequencia else "✅ Sem")
        + " sequência (como abc, 123 ou qwe)",
        (
            "❌ Está na lista de senhas comuns"
            if analise.comum
            else "✅ Fora da lista de senhas comuns"
        ),
    ]
    return "\n".join([*linhas, "", "💡 O que melhorar:", *sugerir(analise)])


def descrever_exemplos(comuns: set[str]) -> str:
    """Monta os exemplos comentados, com a nota de cada um calculada na hora.

    É a única tela em que uma senha aparece: as dos exemplos são inventadas ou
    da lista de senhas comuns.

    Args:
        comuns (set[str]): A lista de senhas comuns, em minúsculas.

    Returns:
        str: Duas linhas por exemplo (a senha com a nota e a explicação) e o
            aviso de que a nota é uma estimativa por regras.
    """
    linhas = []
    for senha, explicacao in EXEMPLOS:
        # Calculada, nunca escrita à mão: se as regras mudarem, o exemplo segue.
        nota = analisar(senha, comuns).nota
        linhas.append(f"🔑 {senha}: {nota} de {len(LIMITES)}, {NOMES[nota]}")
        linhas.append(f"   {explicacao}")
    linhas += [
        "A nota é uma estimativa por regras. Uma palavra",
        "conhecida com um número e um símbolo no fim",
        "continua fácil de adivinhar, mesmo com os quatro",
        "tipos de caractere.",
    ]
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Perguntas
# ---------------------------------------------------------------------------


def eh_numero(texto: str) -> bool:
    """Diz se o texto é um número inteiro escrito com os algarismos de 0 a 9.

    Args:
        texto (str): O texto, já sem os espaços das pontas.

    Returns:
        bool: True para "1" ou "3"; False para "", "1.5", "-1" ou "٣".
    """
    # `isdecimal()` antes do `int()` dispensa o `try`, e o `isascii()` recusa os
    # algarismos de outras escritas, como o "٣" árabe, que o `int()` leria como 3.
    return texto.isascii() and texto.isdecimal()


def conferir_opcao(entrada: str) -> int | None:
    """Confere se a entrada é o número de uma opção do menu.

    Args:
        entrada (str): O que foi digitado no menu.

    Returns:
        int | None: O número da opção, de 1 a `len(OPCOES)`, ou None para
            qualquer outra coisa.
    """
    limpa = entrada.strip()
    if eh_numero(limpa) and 1 <= int(limpa) <= len(OPCOES):
        return int(limpa)
    return None


# ---------------------------------------------------------------------------
# Opções
# ---------------------------------------------------------------------------


def opcao_verificar(ler_senha: Leitor, comuns: set[str]) -> str:
    """Pede a senha, sem mostrá-la, e devolve o resultado da verificação.

    A senha só vive na variável local desta função e some quando ela termina.

    Args:
        ler_senha (Leitor): Função que lê a senha sem mostrá-la, como o
            `getpass.getpass`.
        comuns (set[str]): A lista de senhas comuns, em minúsculas.

    Returns:
        str: O resultado de `descrever_analise`, ou o aviso de que nenhuma
            senha foi digitada.
    """
    # Sem `strip()`: um espaço no começo ou no fim também é parte da senha.
    senha = ler_senha("Digite a senha (ela não aparece na tela): ")
    if not senha:
        return "⚠️ Nenhuma senha foi digitada."
    return descrever_analise(analisar(senha, comuns))


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


def limpar_tela() -> None:
    """Limpa o terminal, detectando o sistema operacional automaticamente."""
    # 'nt' é o identificador interno para Windows. O comando é sempre um destes
    # dois textos fixos, nunca algo digitado pelo usuário.
    comando = "cls" if os.name == "nt" else "clear"
    os.system(comando)


def exibir_tela(resultado: str) -> None:
    """Desenha o quadro: título, resultado da ação anterior e menu.

    Args:
        resultado (str): Resultado da ação anterior, ou "" se não houver.
    """
    print("====== VERIFICADOR DE FORÇA DE SENHA ======")
    print()
    if resultado:
        print(resultado)
        print()
    for numero, opcao in enumerate(OPCOES, start=1):
        print(f"{numero} : {opcao}")
    print()


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------


def main(
    ler: Leitor = input,
    ler_senha: Leitor = getpass.getpass,
    comuns: set[str] | None = None,
) -> None:
    """Roda o programa: repete o menu até o usuário sair.

    O resultado de cada opção aparece acima do menu na volta seguinte e só vive
    na variável `resultado`, que nunca contém a senha. Ctrl+C e o fim da entrada
    (Ctrl+D no Linux) encerram o programa em qualquer ponto, inclusive no pedido
    da senha, com uma despedida, sem stack trace.

    Args:
        ler (Leitor, optional): Função que lê o menu. Padrão: `input`.
        ler_senha (Leitor, optional): Função que lê a senha sem mostrá-la.
            Padrão: `getpass.getpass`.
        comuns (set[str] | None, optional): A lista de senhas comuns, em
            minúsculas. Padrão: a de `ARQUIVO_SENHAS_COMUNS`.
    """
    if comuns is None:
        comuns = carregar_senhas_comuns(ARQUIVO_SENHAS_COMUNS)
    resultado = ""
    try:
        while True:
            limpar_tela()
            exibir_tela(resultado)
            opcao = conferir_opcao(ler("Escolha uma opção: "))
            if opcao == 1:
                resultado = opcao_verificar(ler_senha, comuns)
            elif opcao == 2:
                resultado = descrever_exemplos(comuns)
            elif opcao == 3:
                break
            else:
                resultado = f"❌ Opção inválida. Digite um número de 1 a {len(OPCOES)}."

        print("Até a próxima! 👋")
    except (KeyboardInterrupt, EOFError):
        # Um só lugar trata a saída. O `getpass` devolve o terminal ao normal
        # (voltando a mostrar o que se digita) antes de repassar o Ctrl+C.
        print("\nVerificador encerrado. Até a próxima! 👋")


if __name__ == "__main__":
    main()
