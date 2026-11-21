![Verificador de Força de Senha em Python: animação de uma sessão que verifica Senha@123, com nota 2 de 4 por causa da sequência, e uma frase-senha de quatro palavras, com nota 4 de 4, sem que a senha apareça ao ser digitada, e depois mostra os exemplos comentados, das notas 0 a 4, até sair](assets/verificador-de-forca-de-senha-python-terminal-sessao.svg)

# 🔎 Verificador de Força de Senha em Python | Exercício de Lógica de Programação

[English](README.en.md) · **Português (Brasil)**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Rodar agora:** com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e, dentro de `mini_projetos/verificador_de_forca_de_senha`, rode `uv run main.py`.

Esta pasta contém o **Verificador de Força de Senha em Python**, projetado como material de estudo para desenvolvedores iniciantes. Você digita uma senha, que não aparece na tela, e o programa dá uma nota de 0 a 4, de muito fraca a forte. Junto da nota, ele mostra o que pesou: o tamanho, os tipos de caractere, as repetições e sequências (como `aaa` e `123`), a presença numa lista de senhas comuns e a entropia estimada, com a conta. Depois, sugere o que mudar para a senha melhorar. O foco principal é a aplicação prática de **fundamentos da programação**: regras escritas com funções pequenas, expressões regulares e a leitura de um texto sem mostrá-lo.

> ⚠️ **A nota é uma estimativa didática, não uma auditoria:** o programa aplica regras simples, que qualquer pessoa consegue ler no código. Estimadores como o [zxcvbn](https://github.com/dropbox/zxcvbn), usado em muitas páginas de cadastro, reconhecem palavras de dicionário, nomes, datas e trocas de letra por número (`s3nh4`), que estas regras não reconhecem.

### 🎯 Objetivo do Projeto:

Demonstrar como escrever **regras com `any()` e os métodos de string**, como achar padrões com o **módulo `re`** e como ler uma senha sem eco com o **`getpass`** em Python. É um projeto prático ideal para estudantes que desejam entender por que uma senha com letras, números e símbolos ainda pode ser fraca, e o que de fato a deixa difícil de adivinhar.

---

### 📚 O que você vai aprender com este projeto?

Este exercício foi estruturado para consolidar conceitos essenciais de algoritmos:

- **Regras com `any()`:** `islower`, `isupper` e `isdigit` dizem, cada um numa linha, se a senha tem pelo menos um caractere de cada tipo.
- **Expressões Regulares com o Módulo `re`:** a expressão `(.)\1{2,}` acha um caractere repetido três vezes ou mais, com a referência a um grupo (`\1`).
- **Janelas e o Operador `in`:** cada trecho de 3 caracteres é procurado no alfabeto, nos números e nas fileiras do teclado, para a frente e para trás.
- **Entropia Estimada com `math.log2`:** a mesma conta do Gerador de Senhas, aplicada a uma senha feita à mão, e por que ela precisa de descontos.
- **O Módulo `getpass`:** a senha é lida sem aparecer na tela, e o programa nunca a mostra, nem um trecho dela.
- **Interação Multiplataforma com o SO:** uso de `os.system` para detectar o sistema operacional (`cls` no Windows ou `clear` em Unix/Mac) e manter a interface do terminal limpa e profissional.

---

### 🧠 Guia de Implementação (A Lógica por trás do Código):

Para quem está começando, o maior desafio não é a sintaxe, mas a **montagem do raciocínio**. Confira o passo a passo da construção deste programa:

1. **Os Tipos de Caractere, com `any()`:** cada tipo é uma pergunta sobre a senha inteira: "algum caractere é minúsculo?". O `any()` responde percorrendo a senha e para no primeiro que serve: `any(c.islower() for c in senha)`. O mesmo vale para `isupper` e `isdigit`, e o que não é letra nem número conta como símbolo. Uma letra acentuada (`é`) conta como letra comum, e o espaço, como símbolo. O tamanho de cada tipo vem do módulo `string`, como no Gerador de Senhas: 26 minúsculas, 26 maiúsculas, 10 números e 32 símbolos.
2. **As Repetições, com `(.)\1{2,}`:** lida peça por peça, a expressão diz: `(.)` guarda um caractere qualquer num grupo; `\1` é "o mesmo caractere do grupo 1"; e `{2,}` pede que ele apareça mais duas vezes ou mais. Assim, `aaa` e `1111` casam, e `aa` não. Com `re.IGNORECASE`, `aAa` também conta como repetição. O `finditer` devolve cada trecho achado, e o `span()` de cada um diz onde ele começa e termina.
3. **As Sequências, com Janelas de 3:** o programa olha a senha de 3 em 3 caracteres (`Sen`, `enh`, `nha`…) e confere, com o operador `in`, se a janela está dentro de uma das sequências conhecidas: o alfabeto, os números de 0 a 9 e as fileiras do teclado (`qwertyuiop`, `asdfghjkl` e `zxcvbnm`). O contrário de cada sequência sai do fatiamento `[::-1]`, então `cba` e `987` também são achados. A comparação é em minúsculas, para `ABC` contar como `abc`.
4. **Cada Trecho Previsível Vale um Caractere:** quem usa `aaaa` ou `1234` escolheu um caractere e uma regra; o resto se adivinha quase de graça. Por isso, os trechos achados que se sobrepõem são juntados (as janelas `abc` e `bcd` de `abcd` viram um trecho), e cada trecho conta como um caractere só. Em `Senha@123`, os 9 caracteres viram 7 na conta: o `123` vale um.
5. **A Entropia Estimada, com a Conta:** a fórmula é a do Gerador de Senhas, o número de caracteres que contam vezes o log2 do tamanho do alfabeto, que é a soma dos tipos presentes. O programa mostra a conta junto da nota:
    ```text
    Entropia estimada: 7 × log2(94) ≈ 45,9 bits
    ```
    A fórmula supõe que cada caractere foi sorteado, o que uma senha inventada por uma pessoa quase nunca é. Por isso ela se chama entropia **estimada**, e as repetições, as sequências e a lista de senhas comuns corrigem os casos mais previsíveis.
6. **A Nota, com Faixas e Duas Travas:** a nota é quantas faixas a entropia alcança: 28, 36, 60 e 80 bits levam a nota para 1, 2, 3 e 4. As faixas conversam com o Gerador de Senhas: a senha mínima dele (8 caracteres, 52,4 bits) é razoável, e a senha forte padrão (16 caracteres, 104,9 bits) é forte. Duas travas valem por cima da conta: uma senha da lista de senhas comuns tira 0, e uma senha com menos de 8 caracteres não passa de 1.
7. **A Lista de Senhas Comuns:** são as 150 senhas mais usadas por falantes de português, como `123mudar` e `102030`, tiradas de vazamentos reais pelo projeto Pwdb-Public. O `senhas_comuns.txt` é uma cópia sem alteração do arquivo `Portugese_Pwdb_common-password-list-top-150.txt` do [SecLists](https://github.com/danielmiessler/SecLists), sob a Licença MIT, e um teste confere o SHA-256 dele; a origem, o commit e os avisos de copyright estão no [LICENSE](LICENSE). A comparação é com a senha inteira, em minúsculas, e o programa acha o arquivo por `Path(__file__).parent`, de qualquer pasta de onde for chamado.
8. **A Senha Lida com o `getpass`:** o `getpass.getpass` recebe o pedido e devolve o que foi digitado, como o `input`, mas sem mostrar nada na tela enquanto você digita. O espaço no começo ou no fim também conta, porque a senha não passa pelo `strip()`. Num ambiente que não é um terminal de verdade, como o IDLE, o `getpass` não consegue esconder o que se digita: o Python avisa com um `GetPassWarning` e a senha aparece. Por isso, rode o programa no terminal. `Ctrl+C` encerra o programa em qualquer ponto, inclusive no pedido da senha, com uma despedida e sem stack trace.
9. **Nenhuma Senha é Guardada nem Mostrada:** a senha só passa por duas funções, a que pede e a que analisa. A análise devolve números, nomes de tipos e verdadeiro ou falso, nunca o texto digitado, então nenhuma mensagem do programa consegue mostrar a senha, nem a sequência achada nela. O programa não grava arquivo, não usa a rede e não recebe nada pela linha de comando, que ficaria gravada no histórico do shell.

> 💡 **Dica de estudo:** verifique `Senha@123`: ela tem os quatro tipos de caractere e tira só 2, com 45,9 bits, porque o `123` é uma sequência e o tamanho é pequeno. Uma frase-senha como `girassol-azul`, só com minúsculas e o hífen, tira 3. Depois, verifique `Flamengo@2026`: ela tira 4 nestas regras, com 85,2 bits, mas é um nome conhecido seguido de um ano e de um símbolo, exatamente o tipo de senha que alguém testa cedo. O zxcvbn, por exemplo, reconhece o `2026` como um ano e procura a palavra em dicionários; estas regras veem só 13 caracteres com os quatro tipos.

---

### 🛠️ Tecnologias e Ferramentas:

Para garantir a melhor experiência de aprendizado, o projeto utiliza as seguintes tecnologias:

| Ferramenta | Descrição |
| :--- | :--- |
| **Python 3.12+** | Linguagem principal do projeto. O programa usa só a biblioteca padrão (`getpass`, `re`, `string`, `math`, `pathlib`, `os`, `sys`), sem dependências externas. |
| **uv** | Gerenciador de dependências e ambientes virtuais: cria o ambiente e roda o programa com um único comando. |
| **Terminal** | Interface onde o resultado aparece e recebe as escolhas do usuário (CMD, PowerShell ou o terminal do VS Code/PyCharm). |

As ferramentas de qualidade (Ruff, Black, Mypy e Pytest) estão em [Qualidade e testes](#qualidade-e-testes). Para o porquê de cada escolha, veja [docs/stack.md](docs/stack.md).

---

### ⚙️ Como rodar o projeto localmente:

**Pré-requisitos:** [Python 3.12+](https://www.python.org/downloads/) e [uv](https://docs.astral.sh/uv/getting-started/installation/). Para conferir, rode `python --version` e `uv --version`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/verificador_de_forca_de_senha
    ```
2.  **Execute o programa:** no terminal (CMD, PowerShell ou o do VS Code/PyCharm), dentro da pasta do projeto. O `uv` cria o ambiente virtual sozinho na primeira execução.
    ```bash
    uv run main.py
    ```
3.  **Prefere dois cliques? Use o atalho:** no Windows, abra o `iniciar_verificador.bat`; no Linux/macOS, execute o `iniciar_verificador.sh` no terminal. Os scripts detectam se você tem `uv` (preferido) ou `python`/`python3` instalado antes de abrir o verificador.

> ⚠️ **Nota:** sem o `uv`, `python main.py` funciona igual, porque o programa não tem nenhuma dependência externa. Ele também detecta se você está no Windows, Linux ou macOS para limpar a tela do jeito certo. Para sair, escolha a opção 3 ou aperte `Ctrl+C` a qualquer momento.

---

### Qualidade e testes

O projeto tem uma suíte de testes automatizados (`pytest`) e um portão de qualidade que roda no CI a cada push e a cada PR:

```bash
# Instala as dependências de desenvolvimento
uv sync

# Lint + ordem de imports
uv run ruff check .

# Formatação
uv run black --check .

# Checagem de tipos
uv run mypy

# Testes
uv run pytest
```

Para o mapa de cada tecnologia da stack (o que é, por que foi escolhida, o que estudar), veja [docs/stack.md](docs/stack.md). Para o comportamento esperado do programa e o histórico de decisões, veja [specs/](specs/). Para o detalhamento de arquitetura e convenções, veja [CLAUDE.md](CLAUDE.md).

---

### 📋 Atividades para praticar (Desafios de Evolução):

Para exercitar o que aprendeu, tente modificar o código e implementar estas novas funcionalidades:

1. **📅 Anos como Trecho Previsível:** acrescente uma regra que ache anos de 1900 a 2099 (`1998`, `2026`) e os desconte como as sequências, valendo um caractere cada.
   - **O Aprendizado:** escrever uma expressão regular com grupos alternativos (`(19|20)\d\d`) e encaixar uma regra nova no formato de trecho que `juntar_trechos` já trata, sem mudar a função.
2. **🔤 Trocas de Letra por Número:** antes de comparar com a lista de senhas comuns, desfaça as trocas mais usadas (`4` por `a`, `3` por `e`, `0` por `o`, `1` por `i`, `@` por `a`), para `s3nh4` ser reconhecida como `senha`.
   - **O Aprendizado:** montar uma tabela de tradução com `str.maketrans` e aplicá-la com `str.translate`, e ver por que trocar letras por números quase não deixa a senha mais difícil de adivinhar.
3. **⏱️ O Tempo para Adivinhar:** mostre, junto da entropia, quanto tempo um computador que testa 10 bilhões de senhas por segundo levaria, no pior caso, para chegar à senha.
   - **O Aprendizado:** converter bits em tentativas com `2 ** bits`, dividir em anos, dias e horas com `divmod`, e escolher a unidade certa para um número que vai de segundos a bilhões de anos.

---

### 🧭 Continue praticando:

Este projeto faz parte de uma trilha de exercícios de lógica de programação em Python. Depois deste, experimente:

- **[Gerador de Senhas em Python](../gerador_de_senhas/):** o `secrets` contra o `random`, as constantes do módulo `string` e a mesma conta da entropia.
- **[Validador de CPF em Python](../validador_de_cpf/):** o algoritmo dos dígitos verificadores, o resto da divisão e as funções puras.

Veja todos os projetos e vídeos do canal em [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Ficou com alguma dúvida ou tem sugestões?

Aprender algo novo tem seus desafios, mas estou aqui para caminharmos juntos! Se você encontrou algum erro, teve dificuldade em rodar o programa ou pensou numa melhoria que tornaria este material ainda mais didático:

- **Abra uma [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** descreva sua dúvida ou sugestão. É a melhor forma de trocarmos conhecimento e ajudarmos outras pessoas que tenham a mesma dúvida.
- **Contribua com código:** quer propor uma melhoria? Veja o passo a passo no [CONTRIBUTING.md](../../CONTRIBUTING.md) do repositório. Neste projeto, a senha só passa por `opcao_verificar` e `analisar`, e uma regra nova devolve o que achou como número ou verdadeiro ou falso na `Analise`, nunca o trecho da senha; o `senhas_comuns.txt` não se edita, porque é a cópia exata da lista do SecLists; a nota dos exemplos comentados é calculada, nunca escrita à mão; e, nos exemplos, use só senhas inventadas ou da lista de senhas comuns, nunca uma senha em uso.
- **Me mande um e-mail:** se preferir algo mais privado, escreva para [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

Ficarei muito feliz em ver seu progresso e receber seu feedback para melhorar cada vez mais nossos materiais de estudo! 🤝

---

### ⚖️ Licença

Este projeto está sob a **Licença MIT**. Isso significa que você pode usar, copiar e modificar o código à vontade, inclusive nos seus projetos. A lista de senhas comuns (`senhas_comuns.txt`) vem do SecLists, também sob a Licença MIT, com a origem e os avisos de copyright registrados no arquivo [LICENSE](LICENSE), onde estão também os detalhes da licença.
