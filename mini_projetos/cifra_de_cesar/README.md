![Cifra de César em Python: animação de uma sessão que cifra a frase "O segredo da mensagem está nas letras." com a chave 7, com o aviso de que os acentos foram tirados, e depois quebra o texto cifrado pela frequência das letras, que acha a chave 7 e mostra a frase de volta, até sair](assets/cifra-de-cesar-python-terminal-sessao.svg)

# 🔐 Cifra de César em Python | Exercício de Lógica de Programação

[English](README.en.md) · **Português (Brasil)**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
[![CI](https://img.shields.io/github/actions/workflow/status/ryanvmorais/aprenda-com-ryan-morais/ci.yml?label=CI&logo=githubactions&logoColor=white)](https://github.com/ryanvmorais/aprenda-com-ryan-morais/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-green?logo=opensourceinitiative&logoColor=white)

**Rodar agora:** com o [uv](https://docs.astral.sh/uv/) instalado, clone o repositório e, dentro de `mini_projetos/cifra_de_cesar`, rode `uv run main.py`.

Esta pasta contém a **Cifra de César em Python**, projetada como material de estudo para desenvolvedores iniciantes. Você digita um texto e uma chave de 1 a 25, e o programa anda cada letra essa quantidade de posições no alfabeto: com a chave 3, o A vira D, e o Z volta para o C. Ele também decifra com a chave e quebra um texto cifrado sem ela, de dois jeitos: testando as 25 chaves (a força bruta) ou contando as letras e comparando com as mais comuns do português. O foco principal é a aplicação prática de **fundamentos da programação**: a conta com os códigos das letras, o resto da divisão e a contagem com o `Counter`. O texto digitado não é guardado nem sai do computador.

> ⚠️ **A cifra de César não protege nada:** com só 25 chaves possíveis, qualquer texto cifrado cai em segundos, como o próprio programa mostra. Ela serve para entender como uma cifra funciona e por que esta é fraca; para proteger uma mensagem de verdade, use um programa de criptografia moderna.

### 🎯 Objetivo do Projeto:

Demonstrar como trocar letras com **`ord`, `chr` e o resto da divisão (`%`)**, como aplicar a troca ao texto inteiro com o **`str.maketrans`** e como quebrar a cifra pela **força bruta** e pela **frequência das letras**, contadas com o **`collections.Counter`**, em Python. É um projeto prático ideal para estudantes que desejam entender o que é uma chave, por que o tamanho dela importa e como um padrão da língua entrega um texto cifrado.

---

### 📚 O que você vai aprender com este projeto?

Este exercício foi estruturado para consolidar conceitos essenciais de algoritmos:

- **Os Códigos das Letras com `ord` e `chr`:** o `ord` devolve o número de uma letra (`ord("a")` é 97), e o `chr` faz o caminho de volta, então a letra vira uma conta.
- **Aritmética Modular com `%`:** o resto da divisão por 26 faz o Z voltar para o A, e a chave negativa anda para trás para decifrar.
- **Tabelas de Tradução com `str.maketrans`:** as 52 letras trocadas de uma vez, com o resto do texto (espaço, número, pontuação e emoji) passando sem mudança.
- **Acentos com o Módulo `unicodedata`:** a forma NFD separa a letra do acento, para o `ã` virar `a` antes de cifrar.
- **Força Bruta:** um laço que testa as 25 chaves possíveis, e por que uma chave de verdade não se testa assim.
- **Contagem com `collections.Counter`:** quantas vezes cada letra aparece, as três mais comuns com `most_common` e uma pontuação que acha a chave mais provável.
- **Interação Multiplataforma com o SO:** uso de `os.system` para detectar o sistema operacional (`cls` no Windows ou `clear` em Unix/Mac) e manter a interface do terminal limpa e profissional.

---

### 🧠 Guia de Implementação (A Lógica por trás do Código):

Para quem está começando, o maior desafio não é a sintaxe, mas a **montagem do raciocínio**. Confira o passo a passo da construção deste programa:

1. **A Posição da Letra, com `ord` e `chr`:** cada caractere tem um número, e as letras de `a` a `z` vêm em sequência, de 97 a 122. A posição de uma letra no alfabeto é o número dela menos o do `a`: o `c` é `99 - 97`, a posição 2. Andar a chave é somar à posição, e o `chr` transforma o número de volta em letra. Para as maiúsculas, a base é o `A` em vez do `a`, e a letra sai maiúscula como entrou.
2. **O `% 26` e a Volta do Z para o A:** o `z` está na posição 25, e com a chave 3 a conta daria 28, fora do alfabeto. O resto da divisão por 26 resolve: `(25 + 3) % 26` é 2, o `c`. É a mesma conta de um relógio, em que 3 horas depois das 11 dá 2. Por isso a chave vai de 1 a 25: a 0 e a 26 deixam o texto igual, e a 27 cifra como a 1.
3. **Decifrar é Andar para Trás:** decifrar usa a mesma função, com a chave negativa. O `a` com a chave -3 dá `(0 - 3) % 26`, e no Python o resto de um número negativo por 26 fica entre 0 e 25: dá 23, o `x`. Cuidado ao levar a conta para outra linguagem: em C e em JavaScript, o `%` de um número negativo dá um resultado negativo, e a conta precisaria somar 26 antes.
4. **A Tabela do `str.maketrans`:** em vez de fazer a conta caractere por caractere num laço, o programa faz a conta uma vez para cada uma das 52 letras, minúsculas e maiúsculas, e guarda o resultado numa tabela com o `str.maketrans`. O `translate` aplica a tabela ao texto inteiro, e tudo o que não está nela (espaço, número, pontuação, emoji, uma letra de outro alfabeto como o `ß`) passa sem mudança, sem nenhum `if`. `Ola, Mundo!` com a chave 3 vira `Rod, Pxqgr!`.
5. **Os Acentos, com o `unicodedata`:** a tabela só tem as 26 letras sem acento, então o `ã` passaria sem cifrar e entregaria a palavra. Antes de cifrar, a forma NFD separa cada letra acentuada na letra base mais a marca do acento (`ã` vira `a` + `~`, e `ç` vira `c` + a cedilha), e as marcas saem do texto. É a mesma função do Jogo da Forca. Por isso, decifrar devolve `A acao comecou` em vez de `A ação começou`, e o resultado avisa quando os acentos foram tirados.
6. **A Força Bruta, com as 25 Chaves:** quem não tem a chave pode testar todas. O programa decifra o texto com cada chave de 1 a 25 e mostra uma linha por chave, cortada para caber no terminal; a chave certa é a da linha que dá para ler. Isso só funciona porque as chaves são poucas. Uma cifra moderna usa uma chave de 128 bits, com 2¹²⁸ possibilidades (um número de 39 algarismos): testando um trilhão de chaves por segundo, levaria mais de 10 bilhões de bilhões de anos, perto de um bilhão de vezes a idade do universo.
7. **A Frequência das Letras, com o `Counter`:** no português, o A, o E e o O aparecem muito mais que o K, o W e o Y. O `Counter` conta as letras do texto, e o `most_common(3)` devolve as três que mais aparecem. Para cada chave, o programa decifra o texto e dá uma pontuação: cada letra vale o percentual dela no português, vezes quantas vezes aparece. O texto certo, cheio de A, E e O, soma mais que os errados, cheios de letras raras, e a chave de maior soma é a mais provável:
    ```text
    📊 Mais comuns no texto: L (6), Z (5) e H (5)
       No português, as mais comuns são A, E e O.
    🔓 Chave mais provável: 7
    O segredo da mensagem esta nas letras.
    ```
8. **A Medição e a Fonte da Tabela:** a soma dos produtos foi escolhida por uma medição com trechos de "Dom Casmurro", de Machado de Assis (em domínio público): ela acertou a chave em 96,5% dos trechos de 20 letras, 99,1% dos de 30 e 99,9% dos de 50. Supor que a letra mais comum do texto cifrado é o A acertou entre 39% e 59%, porque o A e o E estão próximos no português. O qui-quadrado, um método estatístico comum, parou entre 92% e 96%: ele divide pela frequência esperada, e uma só letra rara, como o K de um nome próprio, pesava mais que o resto do texto. Os 26 percentuais vêm da tabela 1.2.1 do estudo [Análise de Freqüências de Línguas](https://www.lockabit.coppe.ufrj.br/sites/lockabit.coppe.ufrj.br/files/publicacoes/lockabit/analise_freq.pdf), de Bruno da Rocha Braga (COPPE/UFRJ, 2003), que contou 1,1 MB de textos de autores brasileiros, sem acentos e com o Ç como C, o mesmo tratamento que o programa dá ao texto.
9. **O Aviso de Texto Curto:** com poucas letras, a contagem engana: uma palavra curta pode ter mais letras raras que comuns. Abaixo de 30 letras, o primeiro tamanho em que a chave mais provável acertou mais de 99% dos trechos na medição, o resultado avisa e sugere conferir na força bruta. O aviso conta só as letras, porque espaço, número e pontuação não ajudam a achar a chave, e o `total()` do `Counter` as soma. O resultado também mostra a segunda e a terceira chaves mais prováveis, onde a certa costuma estar quando a primeira erra. `Ctrl+C` encerra o programa em qualquer ponto, inclusive no pedido do texto ou da chave, com uma despedida e sem stack trace.

> 💡 **Dica de estudo:** cifre `Bom dia` com a chave 3 e quebre o resultado, `Erp gld`, pela frequência: a chave mais provável é a 11, com `Tge vas`, e a certa aparece só em segundo lugar, junto do aviso de texto curto. Depois, quebre o mesmo texto pela força bruta: a linha da chave 3 é a única que dá para ler. Por fim, cifre um texto com a chave 3 e cifre o resultado com a chave 23: o texto volta ao original, porque 3 + 23 dá 26, a volta inteira no alfabeto.

---

### 🛠️ Tecnologias e Ferramentas:

Para garantir a melhor experiência de aprendizado, o projeto utiliza as seguintes tecnologias:

| Ferramenta | Descrição |
| :--- | :--- |
| **Python 3.12+** | Linguagem principal do projeto. O programa usa só a biblioteca padrão (`string`, `unicodedata`, `collections`, `os`, `sys`), sem dependências externas. |
| **uv** | Gerenciador de dependências e ambientes virtuais: cria o ambiente e roda o programa com um único comando. |
| **Terminal** | Interface onde o resultado aparece e recebe as escolhas do usuário (CMD, PowerShell ou o terminal do VS Code/PyCharm). |

As ferramentas de qualidade (Ruff, Black, Mypy e Pytest) estão em [Qualidade e testes](#qualidade-e-testes). Para o porquê de cada escolha, veja [docs/stack.md](docs/stack.md).

---

### ⚙️ Como rodar o projeto localmente:

**Pré-requisitos:** [Python 3.12+](https://www.python.org/downloads/) e [uv](https://docs.astral.sh/uv/getting-started/installation/). Para conferir, rode `python --version` e `uv --version`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ryanvmorais/aprenda-com-ryan-morais.git
    cd aprenda-com-ryan-morais/mini_projetos/cifra_de_cesar
    ```
2.  **Execute o programa:** no terminal (CMD, PowerShell ou o do VS Code/PyCharm), dentro da pasta do projeto. O `uv` cria o ambiente virtual sozinho na primeira execução.
    ```bash
    uv run main.py
    ```
3.  **Prefere dois cliques? Use o atalho:** no Windows, abra o `iniciar_cifra.bat`; no Linux/macOS, execute o `iniciar_cifra.sh` no terminal. Os scripts detectam se você tem `uv` (preferido) ou `python`/`python3` instalado antes de abrir a cifra.

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

1. **🔑 A Cifra de Vigenère:** troque a chave numérica por uma palavra-chave, em que cada letra da palavra dá o deslocamento de uma letra do texto (com a palavra `cafe`, a primeira letra anda 2, a segunda 0, a terceira 5 e a quarta 4, e a palavra recomeça).
   - **O Aprendizado:** reaproveitar a `deslocar_letra` com uma chave diferente a cada letra, percorrer a palavra-chave em círculo com o `itertools.cycle`, e ver por que a força bruta das 25 chaves e a contagem do texto inteiro deixam de funcionar.
2. **🔢 Os Números Também:** desloque os algarismos de 0 a 9 pela mesma chave, para um texto como `Encontro às 19h` não entregar o horário.
   - **O Aprendizado:** acrescentar os 10 algarismos à tabela do `str.maketrans`, com a mesma conta do resto da divisão, agora por 10, e ajustar o teste que hoje confere que os números passam sem mudança.
3. **📏 O Qui-Quadrado ao Lado:** escreva uma segunda pontuação pelo qui-quadrado, que soma `(contagem - esperada)² / esperada` letra a letra e escolhe a menor soma, e compare as duas com frases que tenham K, W ou Y.
   - **O Aprendizado:** calcular a contagem esperada de cada letra a partir do tamanho do texto, comparar dois métodos com os mesmos textos e entender por que uma letra rara pesa tanto quando a conta divide por um número pequeno.

---

### 🧭 Continue praticando:

Este projeto faz parte de uma trilha de exercícios de lógica de programação em Python. Depois deste, experimente:

- **[Verificador de Força de Senha em Python](../verificador_de_forca_de_senha/):** as regras com `any()`, as expressões regulares e a entropia estimada, a mesma ideia de contar possibilidades da força bruta.
- **[Jogo da Forca em Python](../jogo_da_forca/):** as strings, os conjuntos e os acentos tirados com o `unicodedata`, como aqui.

Veja todos os projetos e vídeos do canal em [aprenda-com-ryan-morais](https://github.com/ryanvmorais/aprenda-com-ryan-morais).

---

### 💡 Ficou com alguma dúvida ou tem sugestões?

Aprender algo novo tem seus desafios, mas estou aqui para caminharmos juntos! Se você encontrou algum erro, teve dificuldade em rodar o programa ou pensou numa melhoria que tornaria este material ainda mais didático:

- **Abra uma [Issue](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues):** descreva sua dúvida ou sugestão. É a melhor forma de trocarmos conhecimento e ajudarmos outras pessoas que tenham a mesma dúvida.
- **Contribua com código:** quer propor uma melhoria? Veja o passo a passo no [CONTRIBUTING.md](../../CONTRIBUTING.md) do repositório. Neste projeto, a `FREQUENCIAS` é a cópia sem alteração da tabela 1.2.1 do estudo da COPPE/UFRJ, e um teste confere as 26 letras e a soma; trocar o método de pontuação pede uma nova medição e a revisão do mínimo de 30 letras do aviso de texto curto (ADR-5 e ADR-6 da spec); e o `main.py` não lê nem grava arquivo, não usa a rede e não recebe texto pela linha de comando, o que um teste confere.
- **Me mande um e-mail:** se preferir algo mais privado, escreva para [**contato@ryanmorais.com.br**](mailto:contato@ryanmorais.com.br).

Ficarei muito feliz em ver seu progresso e receber seu feedback para melhorar cada vez mais nossos materiais de estudo! 🤝

---

### ⚖️ Licença

Este projeto está sob a **Licença MIT**. Isso significa que você pode usar, copiar e modificar o código à vontade, inclusive nos seus projetos. Os percentuais da tabela de frequência das letras vêm do estudo da COPPE/UFRJ citado no Guia de Implementação, com a fonte registrada no `main.py`. Os detalhes da licença estão no arquivo [LICENSE](LICENSE).
