![Gerador de Senhas em Python: animação de uma sessão que gera uma senha forte com a entropia, recusa um tamanho fora da faixa e monta uma senha personalizada sem símbolos e sem os caracteres parecidos, sorteia uma frase-senha de 5 palavras e mostra o random repetindo a mesma senha com a mesma semente, até sair](assets/gerador-de-senhas-python-terminal-sessao.svg)

# 🔐 Gerador de Senhas em Python | Exercício de Lógica de Programação

[English](README.en.md) · **Português (Brasil)**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Rodar agora:** com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e, dentro de `mini_projetos/gerador_de_senhas`, rode `uv run main.py`.

Esta pasta contém o **Gerador de Senhas em Python**, projetado como material de estudo para desenvolvedores iniciantes. Com um Enter, o programa gera uma senha forte de 16 caracteres; numa senha personalizada, você escolhe o tamanho, os tipos de caractere e se quer evitar os que se confundem, como o zero e o O. Ele também sorteia frases-senha com palavras em português e mostra, a cada senha, a entropia em bits com a conta. O foco principal é a aplicação prática de **fundamentos da programação**: um sorteio seguro, a matemática por trás da força de uma senha e as funções pequenas que se testam sem teclado nem sorte.

### 🎯 Objetivo do Projeto:

Demonstrar a diferença entre o **`random` e o `secrets`**, o uso das **constantes do módulo `string`** e o cálculo da **entropia com `math.log2`** em Python. É um projeto prático ideal para estudantes que desejam entender por que um sorteio que parece aleatório pode ser previsível, e o que de fato deixa uma senha difícil de adivinhar.

---

### 📚 O que você vai aprender com este projeto?

Este exercício foi estruturado para consolidar conceitos essenciais de algoritmos:

- **O Módulo `secrets`:** o sorteio feito para segurança, que usa a fonte aleatória do sistema operacional, e por que o `random` não serve para senha.
- **As Constantes do Módulo `string`:** `ascii_lowercase`, `ascii_uppercase`, `digits` e `punctuation` montam os 94 caracteres da senha, sem nenhum alfabeto digitado à mão.
- **Entropia com `math.log2`:** a força de uma senha em bits, calculada a partir do tamanho e da quantidade de caracteres possíveis, e por que cada bit a mais dobra o trabalho de quem tenta adivinhar.
- **Funções como Parâmetro:** o sorteio entra como `escolher`, e a mesma função gera a senha de verdade (com o `secrets`), a da demonstração e a dos testes (com o `random` de semente fixa).
- **`any` e `all`:** a regra "pelo menos um de cada tipo" cabe numa linha que combina as duas funções.
- **Interação Multiplataforma com o SO:** uso de `os.system` para detectar o sistema operacional (`cls` no Windows ou `clear` em Unix/Mac) e manter a interface do terminal limpa e profissional.

---

### 🧠 Guia de Implementação (A Lógica por trás do Código):

Para quem está começando, o maior desafio não é a sintaxe, mas a **montagem do raciocínio**. Confira o passo a passo da construção deste programa:

1. **Por que o `secrets`, e não o `random`:** a documentação do módulo `random` avisa que os geradores dele não devem ser usados para fins de segurança, e aponta o `secrets` para isso. O `random` é um gerador pseudoaleatório: cada número sai de uma conta feita sobre o anterior, a partir de uma semente. Quem descobre a semente, ou vê números seguidos do mesmo gerador, consegue prever os próximos. O `secrets` usa a fonte aleatória do sistema operacional, feita para segurança. A opção 4 do menu mostra a diferença na tela: duas senhas geradas com o `random` e a mesma semente saem idênticas, e duas com o `secrets` saem diferentes.
2. **O Sorteio Entra por Parâmetro:** o `secrets.choice` e o `choice` de um `random.Random(semente)` têm a mesma assinatura: recebem uma sequência e devolvem um item dela. Por isso, toda função que sorteia recebe `escolher`, que vale `secrets.choice` quando o programa roda. A demonstração e os testes passam o `random` com semente fixa, e a função que monta a senha é a mesma nos três casos: o problema do `random` não está no código da senha, e sim no sorteador.
3. **Os Alfabetos Vêm do Módulo `string`:** `string.ascii_lowercase` (26 letras), `string.ascii_uppercase` (26), `string.digits` (10) e `string.punctuation` (32 símbolos) somam 94 caracteres. Ao evitar os parecidos (`0 O 1 l I |`), sobram 88. Cada tipo escolhido vira um grupo: a junção dos grupos é o que se sorteia, e cada grupo, separado, é o que a regra do próximo passo confere.
4. **"Um de Cada Tipo" Sorteia de Novo:** muitos sites exigem pelo menos uma letra maiúscula, um número e um símbolo. A tentação é forçar um caractere de cada tipo numa posição, mas isso deixa a senha mais previsível. Aqui, a senha inteira é sorteada e, se faltar um tipo, ela é descartada e sorteada outra vez. Assim, toda senha que cumpre a regra tem a mesma chance de sair. A conferência cabe numa linha: `all(any(c in grupo for c in senha) for grupo in grupos)`. Com 16 caracteres, cerca de 4 em cada 5 senhas sorteadas já servem de primeira; com 8, cerca de metade.
5. **A Entropia, com a Conta:** a entropia é o tamanho da senha vezes o log2 da quantidade de caracteres possíveis. O log2 diz quantos bits cada caractere vale, e cada bit a mais dobra as tentativas de quem tenta adivinhar. O programa mostra a conta junto da senha:
    ```text
    Entropia: 16 × log2(94) ≈ 104,9 bits
    Cada bit a mais dobra as tentativas de adivinhar.
    ```
    A entropia mostrada é a da fórmula, um pouco acima da real: a regra "um de cada tipo" descarta algumas senhas, o que tira no máximo 1,3 bit com 8 caracteres e 0,4 bit com 16. A diferença é pequena, e a fórmula é a que se lê e se confere de cabeça. A vírgula decimal é trocada com `replace`, sem o módulo `locale`, para o resultado sair igual em qualquer sistema.
6. **A Frase-senha e a Lista do BIP-39:** a frase-senha sorteia palavras, com reposição, de uma lista de 2048 palavras. Como 2048 é 2 elevado a 11, cada palavra vale 11 bits, e as 7 palavras do padrão dão 77 bits, com o hífen entre elas. A lista é a portuguesa do BIP-39, um padrão de carteiras de bitcoin (arquivo `bip-0039/portuguese.txt` do repositório [bitcoin/bips](https://github.com/bitcoin/bips), sob a Licença MIT): palavras de 4 a 8 letras, sem acento, com a mesma grafia no Brasil e em Portugal. O `palavras.txt` é uma cópia sem alteração, e um teste confere o SHA-256 dele; a origem, o commit e os autores estão no [LICENSE](LICENSE). O programa acha o arquivo por `Path(__file__).parent`, de qualquer pasta de onde for chamado.
7. **Respostas Conferidas e Saída Limpa:** cada pergunta aceita Enter para o padrão (entre colchetes) e repete a pergunta quando a resposta não serve, sem voltar ao menu. Os números passam por `isascii()` e `isdecimal()` antes do `int()`, o que dispensa o `try` e recusa algarismos de outras escritas, como o "٣" árabe. `Ctrl+C` encerra o programa em qualquer ponto, com uma despedida e sem stack trace.
8. **Nenhuma Senha é Guardada:** o programa não grava arquivo, não usa a rede e não recebe nada pela linha de comando, que ficaria gravada no histórico do shell. A senha gerada só fica na tela até a próxima opção, sozinha na linha, para ser selecionada e copiada inteira.

> 💡 **Dica de estudo:** escolha a opção 4 várias vezes: as duas senhas do `random` saem sempre as mesmas, e as do `secrets` mudam a cada vez. Depois, compare a entropia de uma senha personalizada de 8 caracteres só com números (`8 × log2(10) ≈ 26,6 bits`) com a de uma frase-senha de 5 palavras (`5 × log2(2048) = 55 bits`): a frase, mais fácil de lembrar, vale mais que o dobro.

---

### 🛠️ Tecnologias e Ferramentas:

Para garantir a melhor experiência de aprendizado, o projeto utiliza as seguintes tecnologias:

| Ferramenta | Descrição |
| :--- | :--- |
| **Python 3.12+** | Linguagem principal do projeto. O programa usa só a biblioteca padrão (`secrets`, `random`, `string`, `math`, `pathlib`, `os`, `sys`), sem dependências externas. |
| **uv** | Gerenciador de dependências e ambientes virtuais: cria o ambiente e roda o programa com um único comando. |
| **Terminal** | Interface onde o resultado aparece e recebe as escolhas do usuário (CMD, PowerShell ou o terminal do VS Code/PyCharm). |

As ferramentas de qualidade (Ruff, Black, Mypy e Pytest) estão em [Qualidade e testes](#qualidade-e-testes). Para o porquê de cada escolha, veja [docs/stack.md](docs/stack.md).

---

### ⚙️ Como rodar o projeto localmente:

**Pré-requisitos:** [Python 3.12+](https://www.python.org/downloads/) e [uv](https://docs.astral.sh/uv/getting-started/installation/). Para conferir, rode `python --version` e `uv --version`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/gerador_de_senhas
    ```
2.  **Execute o programa:** no terminal (CMD, PowerShell ou o do VS Code/PyCharm), dentro da pasta do projeto. O `uv` cria o ambiente virtual sozinho na primeira execução.
    ```bash
    uv run main.py
    ```
3.  **Prefere dois cliques? Use o atalho:** no Windows, abra o `iniciar_gerador.bat`; no Linux/macOS, execute o `iniciar_gerador.sh` no terminal. Os scripts detectam se você tem `uv` (preferido) ou `python`/`python3` instalado antes de abrir o gerador.

> ⚠️ **Nota:** sem o `uv`, `python main.py` funciona igual, porque o programa não tem nenhuma dependência externa. Ele também detecta se você está no Windows, Linux ou macOS para limpar a tela do jeito certo. Para sair, escolha a opção 5 ou aperte `Ctrl+C` a qualquer momento.

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

1. **🔁 Várias Senhas de uma Vez:** acrescente uma pergunta à senha personalizada, "quantas senhas?", e mostre uma senha por linha, com a entropia uma vez só no fim.
   - **O Aprendizado:** reaproveitar `gerar_senha` num laço sem mudar a função, e ver que a entropia de cada senha não muda com a quantidade gerada.
2. **🔠 Frase-senha com Maiúscula e Número:** dê à frase-senha a opção de sortear uma palavra para começar com letra maiúscula e um algarismo para o fim da frase, somando os bits de cada escolha à entropia.
   - **O Aprendizado:** a entropia de escolhas independentes se soma: sortear qual palavra vira maiúscula vale `log2(quantidade)` bits, e o algarismo, `log2(10)`.
3. **🎯 A Entropia Exata:** calcule a entropia real da senha personalizada, contando só as senhas que têm um caractere de cada tipo, e mostre a diferença para a da fórmula.
   - **O Aprendizado:** o princípio da inclusão e exclusão, com `itertools.combinations` para percorrer os grupos de tipos que podem faltar, e por que a diferença diminui quando a senha cresce.

---

### 🧭 Continue praticando:

Este projeto faz parte de uma trilha de exercícios de lógica de programação em Python. Depois deste, experimente:

- **[Validador de CPF em Python](../validador_de_cpf/):** o algoritmo dos dígitos verificadores, o resto da divisão e as funções puras.
- **[Lista de Tarefas em Python](../lista_de_tarefas/):** arquivo JSON, `pathlib` e gravação atômica.

Veja todos os projetos e vídeos do canal em [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Ficou com alguma dúvida ou tem sugestões?

Aprender algo novo tem seus desafios, mas estou aqui para caminharmos juntos! Se você encontrou algum erro, teve dificuldade em rodar o programa ou pensou numa melhoria que tornaria este material ainda mais didático:

- **Abra uma [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** descreva sua dúvida ou sugestão. É a melhor forma de trocarmos conhecimento e ajudarmos outras pessoas que tenham a mesma dúvida.
- **Contribua com código:** quer propor uma melhoria? Veja o passo a passo no [CONTRIBUTING.md](../../CONTRIBUTING.md) do repositório. Neste projeto, todo sorteio de senha passa pelo `escolher`, com o `secrets.choice` como padrão, e o `random` só aparece na demonstração; a regra "um de cada tipo" sorteia a senha inteira de novo, nunca força a posição; o `palavras.txt` não se edita, porque é a cópia exata da lista do BIP-39; e, nos exemplos, use só senhas geradas com semente fixa, nunca uma senha em uso.
- **Me mande um e-mail:** se preferir algo mais privado, escreva para [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

Ficarei muito feliz em ver seu progresso e receber seu feedback para melhorar cada vez mais nossos materiais de estudo! 🤝

---

### ⚖️ Licença

Este projeto está sob a **Licença MIT**. Isso significa que você pode usar, copiar e modificar o código à vontade, inclusive nos seus projetos. A lista de palavras (`palavras.txt`) é a lista portuguesa do BIP-39, também sob a Licença MIT, com a origem e os autores registrados no arquivo [LICENSE](LICENSE), onde estão também os detalhes da licença.
