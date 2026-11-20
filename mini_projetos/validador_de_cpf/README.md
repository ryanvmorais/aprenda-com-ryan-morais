![Validador de CPF em Python: animação de uma sessão que valida o exemplo da Receita Federal com pontuação, recusa o mesmo número com o último dígito trocado, gera um CPF para teste com o aviso e mostra a conta dos dois dígitos verificadores no modo didático, até sair](assets/validador-de-cpf-python-terminal-sessao.svg)

# 🔢 Validador de CPF em Python | Exercício de Lógica de Programação

[English](README.en.md) · **Português (Brasil)**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Rodar agora:** com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e, dentro de `mini_projetos/validador_de_cpf`, rode `uv run main.py`.

Esta pasta contém o **Validador de CPF em Python**, projetado como material de estudo para desenvolvedores iniciantes. Você digita um CPF, com ou sem pontuação, e o programa diz se ele é válido pelo cálculo dos dois dígitos verificadores, mostra o número no formato `000.000.000-00` e a região fiscal. Um modo didático mostra a conta passo a passo, e um gerador monta números válidos para testar formulários. O foco principal é a aplicação prática de **fundamentos da programação**: um algoritmo de verdade, a limpeza do texto digitado e as funções pequenas e puras.

### 🎯 Objetivo do Projeto:

Demonstrar a aplicação da **soma ponderada com o resto da divisão**, da **conferência de texto com `str.isdigit`** e das **funções puras** em Python. É um projeto prático ideal para estudantes que desejam entender como um número de documento se confere sozinho, sem consultar nenhum serviço, e por que separar o cálculo da tela deixa o código fácil de testar.

---

### 📚 O que você vai aprender com este projeto?

Este exercício foi estruturado para consolidar conceitos essenciais de algoritmos:

- **Soma Ponderada e Resto da Divisão (`%`):** cada algarismo é multiplicado por um peso, os produtos são somados, e o resto da soma dividida por 11 dá o dígito verificador.
- **List Comprehension:** `[algarismo * peso for algarismo, peso in zip(algarismos, pesos)]` monta os produtos numa linha, e outra list comprehension descarta a pontuação do CPF digitado.
- **Conferência de Texto (`str.isdigit` e `str.isascii`):** o `isdigit()` sozinho aceita caracteres que não são os algarismos de 0 a 9, e o `isascii()` junto dele fecha a porta.
- **Funções Puras:** as funções do cálculo e da conferência recebem um valor e devolvem outro, sem ler o teclado nem imprimir nada, e por isso se testam com uma linha.
- **`NamedTuple`:** a `Conta` guarda cada passo da conta (algarismos, pesos, produtos, soma, resto e dígito), e o modo didático mostra na tela a mesma conta que decidiu o resultado.
- **Interação Multiplataforma com o SO:** uso de `os.system` para detectar o sistema operacional (`cls` no Windows ou `clear` em Unix/Mac) e manter a interface do terminal limpa e profissional.

---

### 🧠 Guia de Implementação (A Lógica por trás do Código):

Para quem está começando, o maior desafio não é a sintaxe, mas a **montagem do raciocínio**. Confira o passo a passo da construção deste programa:

1. **O CPF é Texto, não Número:** um CPF tem 11 algarismos, os 9 da base e os 2 dígitos verificadores. Ele fica como `str` do começo ao fim, porque, guardado como `int`, perderia o zero à esquerda: `int("01234567890")` vira `1234567890`. A lista de `int` só existe dentro da conta, e por isso 10 algarismos não viram um CPF com um zero na frente: o programa pede os 11.
2. **Limpar o que foi Digitado:** uma list comprehension descarta os pontos, o hífen e os espaços, em qualquer posição, para quem digita não precisar acertar a máscara. Cada caractere que sobra precisa ser um algarismo de 0 a 9. Repare no `isascii()` ao lado do `isdigit()`: sozinho, o `isdigit()` aceita o "²", que o `int()` recusa com erro, e algarismos de outras escritas, como o "٣" árabe, que o `int()` lê como 3. Qualquer outro caractere recusa o CPF, e o resultado mostra qual foi.
3. **A Conta do 1º Dígito (Soma Ponderada):** cada algarismo da base, da esquerda para a direita, é multiplicado pelos pesos de 1 a 9, os produtos são somados, e o dígito é o resto da soma dividida por 11 (o resto 10 vale 0, porque o dígito é um algarismo só). É a forma publicada pela Receita Federal no Anexo II do Ato Declaratório Executivo Cofis nº 41/2017, que traz um exemplo resolvido com a base `280012389`. O modo didático mostra assim:
    ```text
    1º dígito verificador
    Algarismos   2   8   0   0   1   2   3   8   9
    Pesos        1   2   3   4   5   6   7   8   9
    Produtos     2  16   0   0   5  12  21  64  81
    Soma 201 ÷ 11 = 18, resto 3 → dígito 3
    ```
4. **A Conta do 2º Dígito (a Mesma Função):** o 1º dígito entra no fim da base, e a conta se repete com os 10 algarismos e os pesos de 0 a 9: a soma dá 195, o resto dá 8, e o CPF do exemplo fica `280.012.389-38`. Nas duas contas o último algarismo leva o peso 9, então `range(10 - len(algarismos), 10)` monta os pesos dos dois dígitos, e uma função só, `calcular_digito`, serve aos dois.
5. **A Forma mais Divulgada Dá o Mesmo Resultado:** muitos sites ensinam os pesos de 10 a 2 (e de 11 a 2 no 2º dígito), com o dígito valendo 11 menos o resto, e 10 e 11 valendo 0. Cada peso de lá é 11 menos o peso daqui, então a soma de lá deixa o resto "11 menos o resto daqui", e 11 menos isso volta a ser o resto daqui. Um teste compara as duas formas em 10.000 bases sorteadas.
6. **A Sequência Repetida:** um CPF com os 11 algarismos iguais passa na conta, mas é recusado mesmo assim: é a convenção dos validadores de cadastro, porque são os números que se digitam para pular o campo. A conferência cabe numa linha: `len(set(cpf)) == 1`, já que o conjunto guarda cada algarismo uma vez só. No modo didático, a conta aparece conferindo, seguida da recusa.
7. **A Região Fiscal (9º Dígito):** o 9º algarismo indica a região fiscal do cadastro inicial, pela tabela do folheto "CPF" da Educação Fiscal da Receita Federal (no exemplo, o 9 é PR e SC). Ela diz onde o CPF foi emitido, não onde a pessoa mora hoje.
8. **Funções Puras, Teclado e Sorteio por Parâmetro:** as funções do cálculo, da conferência e dos textos recebem um valor e devolvem outro, sem ler o teclado nem imprimir; só `main` e `exibir_tela` tocam no terminal. `main` recebe quem lê o teclado (`ler`) e quem sorteia (`sortear`), com `input` e `random.randrange` como padrão. Quem usa o programa não percebe a diferença, mas os testes passam um teclado falso e um sorteio de semente fixa.
9. **O Gerador e a Privacidade:** o gerador sorteia os 9 algarismos da base (de novo, se saírem todos iguais) e calcula os dois dígitos com as mesmas funções da validação. O número passa no cálculo, mas pode coincidir com o CPF de uma pessoa real, porque há cerca de 1 bilhão de combinações válidas e centenas de milhões de CPFs emitidos: use só para testar um sistema. E nenhum CPF digitado ou gerado é guardado: o programa não grava arquivo nem usa a rede, e o resultado só fica na tela até a próxima ação.

> 💡 **Dica de estudo:** no modo didático, digite `280.012.389-39`, com o último algarismo trocado: o 1º dígito confere e o 2º não. Agora digite `280.012.389-48`: o 1º não confere, e o 2º confere, porque a conta dele usa o 1º dígito calculado, e não o digitado. Por fim, digite onze vezes o mesmo algarismo, para ver a conta conferindo e a sequência repetida sendo recusada.

---

### 🛠️ Tecnologias e Ferramentas:

Para garantir a melhor experiência de aprendizado, o projeto utiliza as seguintes tecnologias:

| Ferramenta | Descrição |
| :--- | :--- |
| **Python 3.12+** | Linguagem principal do projeto. O programa usa só a biblioteca padrão (`random`, `os`, `sys`, `typing`), sem dependências externas. |
| **uv** | Gerenciador de dependências e ambientes virtuais: cria o ambiente e roda o programa com um único comando. |
| **Terminal** | Interface onde o resultado aparece e recebe as escolhas do usuário (CMD, PowerShell ou o terminal do VS Code/PyCharm). |

As ferramentas de qualidade (Ruff, Black, Mypy e Pytest) estão em [Qualidade e testes](#qualidade-e-testes). Para o porquê de cada escolha, veja [docs/stack.md](docs/stack.md).

---

### ⚙️ Como rodar o projeto localmente:

**Pré-requisitos:** [Python 3.12+](https://www.python.org/downloads/) e [uv](https://docs.astral.sh/uv/getting-started/installation/). Para conferir, rode `python --version` e `uv --version`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/validador_de_cpf
    ```
2.  **Execute o programa:** no terminal (CMD, PowerShell ou o do VS Code/PyCharm), dentro da pasta do projeto. O `uv` cria o ambiente virtual sozinho na primeira execução.
    ```bash
    uv run main.py
    ```
3.  **Prefere dois cliques? Use o atalho:** no Windows, abra o `iniciar_validador.bat`; no Linux/macOS, execute o `iniciar_validador.sh` no terminal. Os scripts detectam se você tem `uv` (preferido) ou `python`/`python3` instalado antes de abrir o validador.

> ⚠️ **Nota:** sem o `uv`, `python main.py` funciona igual, porque o programa não tem nenhuma dependência externa. Ele também detecta se você está no Windows, Linux ou macOS para limpar a tela do jeito certo. Para sair, escolha a opção 4 ou aperte `Ctrl+C` a qualquer momento.

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

1. **🏢 Validar CNPJ:** acrescente uma opção que valida um CNPJ numérico de 14 algarismos, cujos pesos vão de 2 a 9 da direita para a esquerda e recomeçam no 2, com o dígito valendo 11 menos o resto (e 0 quando o resto é 0 ou 1).
   - **O Aprendizado:** generalizar a soma ponderada, com a lista de pesos entrando por parâmetro, e ver o que muda e o que se reaproveita entre dois algoritmos parecidos.
2. **📋 Vários CPFs de uma Vez:** deixe a opção de validar receber vários CPFs separados por vírgula e mostrar um resultado por linha.
   - **O Aprendizado:** `str.split` e um laço que reaproveita `descrever_resultado` sem mudar nenhuma função pura, a prova de que elas não dependem de onde o CPF veio.
3. **🗺️ Gerar de uma Região:** faça o gerador perguntar a região fiscal (de 0 a 9) e fixar o 9º algarismo da base, sorteando só os outros oito.
   - **O Aprendizado:** acrescentar um parâmetro opcional a `gerar_cpf` sem quebrar quem já a chama, e validar a nova entrada com uma função `conferir_*`.

---

### 🧭 Continue praticando:

Este projeto faz parte de uma trilha de exercícios de lógica de programação em Python. Depois deste, experimente:

- **[Jogo da Forca em Python](../jogo_da_forca/):** strings, conjuntos e acentos com `unicodedata`.
- **[Lista de Tarefas em Python](../lista_de_tarefas/):** arquivo JSON, `pathlib` e gravação atômica.

Veja todos os projetos e vídeos do canal em [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Ficou com alguma dúvida ou tem sugestões?

Aprender algo novo tem seus desafios, mas estou aqui para caminharmos juntos! Se você encontrou algum erro, teve dificuldade em rodar o programa ou pensou numa melhoria que tornaria este material ainda mais didático:

- **Abra uma [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** descreva sua dúvida ou sugestão. É a melhor forma de trocarmos conhecimento e ajudarmos outras pessoas que tenham a mesma dúvida.
- **Contribua com código:** quer propor uma melhoria? Veja o passo a passo no [CONTRIBUTING.md](../../CONTRIBUTING.md) do repositório. Neste projeto, mantenha as funções pequenas e puras, com o teclado (`ler`) e o sorteio (`sortear`) entrando por parâmetro; e, nos exemplos, use só o CPF do exemplo da Receita Federal (`280.012.389-38`), números inválidos montados a partir dele ou números gerados com semente fixa, nunca o CPF de uma pessoa conhecida.
- **Me mande um e-mail:** se preferir algo mais privado, escreva para [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

Ficarei muito feliz em ver seu progresso e receber seu feedback para melhorar cada vez mais nossos materiais de estudo! 🤝

---

### ⚖️ Licença

Este projeto está sob a **Licença MIT**. Isso significa que você pode usar, copiar e modificar o código à vontade, inclusive nos seus projetos. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).
