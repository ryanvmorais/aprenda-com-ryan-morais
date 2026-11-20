![Lista de Tarefas em Python: animação de uma sessão que abre a lista gravada em dias anteriores, adiciona "Comprar pão" com a data de hoje, recusa o número 7 numa lista de três tarefas, conclui "Estudar pathlib" e remove "Revisar o README" depois de confirmar, até sair](assets/lista-de-tarefas-python-terminal-sessao.svg)

# 📝 Lista de Tarefas em Python | Exercício de Lógica de Programação

[English](README.en.md) · **Português (Brasil)**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Rodar agora:** com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e, dentro de `mini_projetos/lista_de_tarefas`, rode `uv run main.py`.

Esta pasta contém a **Lista de Tarefas em Python**, projetada como material de estudo para desenvolvedores iniciantes. Você adiciona, conclui, edita e remove tarefas num menu do terminal, e a lista continua lá quando você fecha e abre o programa de novo, porque cada alteração é gravada num arquivo JSON. O foco principal é a aplicação prática de **fundamentos da programação**: ler e gravar um arquivo, guardar os dados numa lista de dicionários e tratar o que pode dar errado com o arquivo.

### 🎯 Objetivo do Projeto:

Demonstrar a aplicação de **arquivos JSON**, **caminhos com `pathlib`** e **gravação atômica** em Python. É um projeto prático ideal para estudantes que desejam entender como um programa guarda o que o usuário fez entre uma execução e outra, sem perder a lista quando o arquivo some, estraga ou o programa cai no meio da gravação.

---

### 📚 O que você vai aprender com este projeto?

Este exercício foi estruturado para consolidar conceitos essenciais de algoritmos:

- **Arquivo JSON (`json`):** `json.dumps` transforma a lista em texto e `json.loads` faz o caminho de volta; com `ensure_ascii=False` e `indent=2`, o arquivo fica legível num editor, com os acentos escritos como letras.
- **Caminhos com `pathlib`:** `Path(__file__).parent / "tarefas.json"` monta o caminho do arquivo com o separador de cada sistema, e `read_text`, `write_text`, `exists`, `rename` e `replace` fazem o resto, sempre com `encoding="utf-8"`.
- **Lista de dicionários:** cada tarefa é um dicionário com o texto, a situação e a data de criação, e a lista inteira é o "banco de dados" do programa. O `TypedDict` conta ao `mypy` quais chaves cada tarefa tem.
- **Tratamento de Erros:** um `except ValueError` só pega o JSON inválido, o arquivo que não é UTF-8 e a lista com a forma errada, porque os três erros são da mesma família.
- **Gravação Atômica:** o texto vai primeiro para um arquivo temporário, que depois substitui o arquivo de verdade numa operação só.
- **Interação Multiplataforma com o SO:** uso de `os.system` para detectar o sistema operacional (`cls` no Windows ou `clear` em Unix/Mac) e manter a interface do terminal limpa e profissional.

---

### 🧠 Guia de Implementação (A Lógica por trás do Código):

Para quem está começando, o maior desafio não é a sintaxe, mas a **montagem do raciocínio**. Confira o passo a passo da construção deste programa:

1. **A Tarefa (Dicionário Tipado):** cada tarefa é um dicionário com três chaves: `texto` (o que fazer, de 1 a 80 caracteres), `concluida` (`False` para pendente, `True` para concluída) e `criada_em` (a data de criação). A lista de tarefas é uma `list` comum, e o número que aparece na tela é a posição na lista mais 1.
2. **Onde Fica o Arquivo (`pathlib`):** a lista é gravada no `tarefas.json`, na mesma pasta do `main.py`. O caminho vem de `Path(__file__).parent`, e não de `Path("tarefas.json")`: com o caminho relativo, rodar o programa de outra pasta criaria uma segunda lista, vazia. O `tarefas.json` está no `.gitignore`, então a sua lista nunca entra num commit.
3. **O Formato do Arquivo (JSON):** uma lista no topo, um objeto por tarefa, com a data em ISO 8601 (`AAAA-MM-DD`), que a tela mostra como `20/11/2026`:
    ```json
    [
      {
        "texto": "Comprar pão",
        "concluida": false,
        "criada_em": "2026-11-20"
      }
    ]
    ```
4. **Primeira Execução e Arquivo Corrompido:** se o arquivo não existe, a lista começa vazia, e o arquivo só nasce na primeira alteração. Se ele existe mas não é uma lista de tarefas (JSON inválido, outra codificação, uma chave a mais ou a menos), o programa não apaga nada: renomeia o arquivo para uma cópia com a data e a hora no nome, como `tarefas.corrompido-20261120-153000.json`, avisa na primeira tela e começa com a lista vazia. A cópia fica lá para você abrir e recuperar o que der.
5. **Por que a Gravação é Atômica:** `write_text` esvazia o arquivo antes de escrever. Se o programa caísse nesse meio, a lista ficaria pela metade. Por isso o texto vai primeiro para `tarefas.json.tmp`, na mesma pasta, e `Path.replace` troca um arquivo pelo outro numa operação só: o `tarefas.json` é sempre a lista antiga inteira ou a nova inteira, nunca um pedaço.
6. **O Coração do Programa (Laço `while`):** o menu roda até você escolher Sair. A cada volta ele segue sempre esta ordem: `limpa a tela` -> `mostra a lista, a contagem e o menu` -> `lê a opção` -> `faz a ação` -> `grava o arquivo`. Como cada ação grava logo depois de alterar, um `Ctrl+C` ou o terminal fechado não perdem nada.
7. **Proteção contra Erros (Entrada Validada):** e se o usuário digitar "7" numa lista de três tarefas, "abc" no menu ou um texto vazio? As funções `conferir_*` recusam e explicam o motivo, e o programa pede de novo sem limpar a tela. Repare no `isdecimal()` antes do `int()`: o `isdigit()` aceitaria o "²", que o `int()` recusa com erro. Remover é a única ação que apaga dado gravado, então ela pergunta antes (`s`/`n`).
8. **Teclado, Relógio e Arquivo por Parâmetro:** `main` recebe quem lê o teclado (`ler`), quem diz a data e a hora (`agora`) e o caminho do arquivo, com `input`, `datetime.now` e o `tarefas.json` como padrão. Quem usa o programa não percebe a diferença, mas os testes passam um teclado e um relógio falsos e uma pasta temporária, e nunca tocam na sua lista.

> 💡 **Dica de estudo:** depois de adicionar algumas tarefas, abra o `tarefas.json` num editor de texto. Troque um `false` por `true`, salve e abra o programa: a tarefa aparece concluída. Agora apague uma vírgula e abra de novo, para ver o aviso de arquivo corrompido e a cópia que ele deixa.

---

### 🛠️ Tecnologias e Ferramentas:

Para garantir a melhor experiência de aprendizado, o projeto utiliza as seguintes tecnologias:

| Ferramenta | Descrição |
| :--- | :--- |
| **Python 3.12+** | Linguagem principal do projeto. O programa usa só a biblioteca padrão (`json`, `pathlib`, `datetime`), sem dependências externas. |
| **uv** | Gerenciador de dependências e ambientes virtuais: cria o ambiente e roda o programa com um único comando. |
| **Terminal** | Interface onde a lista aparece e recebe as escolhas do usuário (CMD, PowerShell ou o terminal do VS Code/PyCharm). |

As ferramentas de qualidade (Ruff, Black, Mypy e Pytest) estão em [Qualidade e testes](#qualidade-e-testes). Para o porquê de cada escolha, veja [docs/stack.md](docs/stack.md).

---

### ⚙️ Como rodar o projeto localmente:

**Pré-requisitos:** [Python 3.12+](https://www.python.org/downloads/) e [uv](https://docs.astral.sh/uv/getting-started/installation/). Para conferir, rode `python --version` e `uv --version`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/lista_de_tarefas
    ```
2.  **Execute o programa:** no terminal (CMD, PowerShell ou o do VS Code/PyCharm), dentro da pasta do projeto. O `uv` cria o ambiente virtual sozinho na primeira execução.
    ```bash
    uv run main.py
    ```
3.  **Prefere dois cliques? Use o atalho:** no Windows, abra o `iniciar_lista.bat`; no Linux/macOS, execute o `iniciar_lista.sh` no terminal. Os scripts detectam se você tem `uv` (preferido) ou `python`/`python3` instalado antes de abrir a lista.

> ⚠️ **Nota:** sem o `uv`, `python main.py` funciona igual, porque o programa não tem nenhuma dependência externa. Ele também detecta se você está no Windows, Linux ou macOS para limpar a tela do jeito certo. Para sair, escolha a opção 5 ou aperte `Ctrl+C` a qualquer momento: o que você já fez está gravado.

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

1. **🔎 Filtrar a Lista:** acrescente uma opção que mostra só as pendentes ou só as concluídas, mantendo o número de cada tarefa igual ao da lista completa.
   - **O Aprendizado:** numerar com `enumerate` antes de filtrar, para o número não mudar, e montar a lista filtrada com uma list comprehension.
2. **📅 Prazo da Tarefa:** deixe a tarefa ter um prazo opcional, mostrado ao lado do texto, sem que as listas gravadas antes da mudança passem a ser tratadas como corrompidas.
   - **O Aprendizado:** evoluir o formato de um arquivo sem quebrar os antigos: aceitar a chave nova como opcional no `validar_tarefas` e ler com `tarefa.get("prazo")`.
3. **↕️ Pendentes Primeiro:** acrescente uma opção que reordena a lista, com as pendentes antes das concluídas e a ordem de criação mantida dentro de cada grupo.
   - **O Aprendizado:** `list.sort(key=...)` com uma chave `bool` (`False` vem antes de `True`) e a ordenação estável do Python, que não embaralha os iguais.

---

### 🧭 Continue praticando:

Este projeto faz parte de uma trilha de exercícios de lógica de programação em Python. Depois deste, experimente:

- **[Jogo da Forca em Python](../jogo_da_forca/):** strings, conjuntos e acentos com `unicodedata`.
- **[Jogo da Cobrinha em Python](../jogo_da_cobrinha/):** listas dinâmicas e game loop com a biblioteca `curses`.

Veja todos os projetos e vídeos do canal em [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Ficou com alguma dúvida ou tem sugestões?

Aprender algo novo tem seus desafios, mas estou aqui para caminharmos juntos! Se você encontrou algum erro, teve dificuldade em rodar o programa ou pensou numa melhoria que tornaria este material ainda mais didático:

- **Abra uma [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** descreva sua dúvida ou sugestão. É a melhor forma de trocarmos conhecimento e ajudarmos outras pessoas que tenham a mesma dúvida.
- **Contribua com código:** quer propor uma melhoria? Veja o passo a passo no [CONTRIBUTING.md](CONTRIBUTING.md).
- **Me mande um e-mail:** se preferir algo mais privado, escreva para [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

Ficarei muito feliz em ver seu progresso e receber seu feedback para melhorar cada vez mais nossos materiais de estudo! 🤝

---

### ⚖️ Licença

Este projeto está sob a **Licença MIT**. Isso significa que você pode usar, copiar e modificar o código à vontade, inclusive nos seus projetos. Para mais detalhes, consulte o arquivo [LICENSE](LICENSE).
