# 🤝 Como Contribuir no Validador de CPF

Este repositório é um espaço dedicado ao aprendizado de Python, Algoritmos de Dígitos Verificadores, Funções Puras e Validação de Entrada. Sua colaboração é fundamental para fortalecer este material didático para a comunidade de desenvolvedores!

## 🚀 O que você pode aprimorar?

1.  **Refinamento de Lógica:** Sugira melhorias no cálculo dos dígitos (`calcular_digito`) ou na conferência do texto digitado (`limpar_cpf` e `conferir_cpf`).
2.  **Novas Funcionalidades:** 
    *   Implemente a validação de CNPJ, reaproveitando a soma ponderada.
    *   Adicione a validação de vários CPFs de uma vez, separados por vírgula.
3.  **Interface e UX:** Melhore a visualização da conta no modo didático e do menu ou adicione cores ao terminal utilizando a biblioteca padrão.
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
- O código deve manter a **organização em funções pequenas e puras**, com o teclado (`ler`) e o sorteio (`sortear`) entrando por parâmetro, para os testes não dependerem do teclado nem do acaso.
- Mantenha a **coerência na nomenclatura** das variáveis (sempre em português e seguindo o padrão snake_case).
- O objetivo principal é a **didática**: prefira um código legível e bem comentado a um código excessivamente complexo.
- Nos exemplos (código, testes e README), use só o CPF do exemplo da Receita Federal (`280.012.389-38`), números inválidos montados a partir dele ou números gerados com semente fixa, nunca o CPF de uma pessoa conhecida.
- Toda mudança de comportamento deve vir com o teste correspondente em `tests/test_main.py`.
