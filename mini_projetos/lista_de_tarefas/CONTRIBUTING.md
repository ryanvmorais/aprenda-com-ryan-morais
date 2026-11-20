# 🤝 Como Contribuir na Lista de Tarefas

Este repositório é um espaço dedicado ao aprendizado de Python, Arquivos JSON, `pathlib` e Validação de Entrada. Sua colaboração é fundamental para fortalecer este material didático para a comunidade de desenvolvedores!

## 🚀 O que você pode aprimorar?

1.  **Refinamento de Lógica:** Sugira melhorias na conferência do arquivo (`validar_tarefas`) ou na validação das entradas (`conferir_texto` e `conferir_numero`).
2.  **Novas Funcionalidades:** 
    *   Implemente o filtro que mostra só as pendentes ou só as concluídas.
    *   Adicione o prazo opcional da tarefa, sem quebrar as listas já gravadas.
3.  **Interface e UX:** Melhore a visualização da lista e do menu ou adicione cores ao terminal utilizando a biblioteca padrão.
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
- O código deve manter a **organização em funções pequenas**, com o teclado (`ler`), o relógio (`agora`) e o caminho do arquivo entrando por parâmetro, para os testes não dependerem do teclado, da data nem da sua lista.
- Mantenha a **coerência na nomenclatura** das variáveis (sempre em português e seguindo o padrão snake_case).
- O objetivo principal é a **didática**: prefira um código legível e bem comentado a um código excessivamente complexo.
- Mudança no formato do `tarefas.json` precisa continuar abrindo os arquivos gravados antes dela, ou eles passam a ser tratados como corrompidos.
- Toda mudança de comportamento deve vir com o teste correspondente em `tests/test_main.py`.
