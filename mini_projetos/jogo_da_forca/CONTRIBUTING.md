# 🤝 Como Contribuir no Jogo da Forca

Este repositório é um espaço dedicado ao aprendizado de Python, Strings, Conjuntos e Validação de Entrada. Sua colaboração é fundamental para fortalecer este material didático para a comunidade de desenvolvedores!

## 🚀 O que você pode aprimorar?

1.  **Refinamento de Lógica:** Sugira melhorias na remoção de acentos (`remover_acentos`) ou na validação das letras (`conferir_entrada`).
2.  **Novas Funcionalidades:** 
    *   Implemente a dica que revela uma das letras que faltam.
    *   Adicione o menu para escolher o tema antes da partida.
3.  **Interface e UX:** Melhore o desenho da forca e a visualização do placar ou adicione cores ao terminal utilizando a biblioteca padrão.
4.  **Documentação:** Enriqueça as Docstrings das funções ou corrija trechos do README que possam gerar dúvidas.

## 🛠️ Como enviar sua sugestão:

1.  Faça o **Fork** do projeto para sua conta pessoal.
2.  Crie uma branch específica para sua modificação: `git checkout -b feature/nome-da-melhoria`.
3.  Realize seus commits seguindo o padrão **Conventional Commits** (ex: `feat:`, `fix:`, `docs:`).
4.  Antes de abrir o PR, rode a suíte de testes e o portão de qualidade —
    veja [README → Qualidade e testes](README.md#qualidade-e-testes). O
    mesmo roda automaticamente no CI a cada PR.
5.  Envie suas alterações para o seu fork: `git push origin feature/nome-da-melhoria`.
6.  Abra um **Pull Request** detalhando tecnicamente o que foi alterado e o impacto pedagógico da mudança.

## 📜 Diretrizes de Qualidade:
- O código deve manter a **organização em funções pequenas**, com o teclado (`ler`) e o sorteio (`sortear`) entrando por parâmetro, para os testes não dependerem do teclado nem da sorte.
- Mantenha a **coerência na nomenclatura** das variáveis (sempre em português e seguindo o padrão snake_case).
- O objetivo principal é a **didática**: prefira um código legível e bem comentado a um código excessivamente complexo.
- Toda mudança de comportamento deve vir com o teste correspondente em `tests/test_main.py`.
