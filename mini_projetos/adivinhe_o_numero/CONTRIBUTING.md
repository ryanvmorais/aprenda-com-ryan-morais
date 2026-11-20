# 🤝 Como Contribuir no Adivinhe o Número

Este repositório é um espaço dedicado ao aprendizado de Python, Laços de Repetição e Validação de Entrada. Sua colaboração é fundamental para fortalecer este material didático para a comunidade de desenvolvedores!

## 🚀 O que você pode aprimorar?

1.  **Refinamento de Lógica:** Sugira melhorias na tabela de níveis (`NIVEIS`) ou na validação dos palpites.
2.  **Novas Funcionalidades:** 
    *   Implemente o histórico dos palpites de cada partida.
    *   Adicione a dica de "quente" ou "frio" conforme a distância até o número sorteado.
3.  **Interface e UX:** Melhore a visualização das dicas e do resumo de recordes ou adicione cores ao terminal utilizando a biblioteca padrão.
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
