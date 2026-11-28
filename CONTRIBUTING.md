# 🤝 Como contribuir

Este repositório é um laboratório de estudo: mini projetos, cursos e tutoriais pensados para quem está aprendendo programação. Sua colaboração mantém o material correto, atual e didático para a comunidade de desenvolvedores!

## 🚀 O que você pode aprimorar?

1.  **Correções:** Aponte ou corrija um erro de código, um comando que não roda mais ou um trecho do README que não ficou claro.
2.  **Novas Funcionalidades:** Implemente uma das "Atividades para praticar" do README de um mini projeto ou proponha um desafio novo.
3.  **Testes:** Cubra um caso que a suíte ainda não testa, como uma entrada inválida ou um limite.
4.  **Documentação:** Enriqueça as Docstrings, os comentários didáticos ou a versão em inglês do README (`README.en.md`).

## 🛠️ Como enviar sua sugestão:

1.  Faça o **Fork** do repositório para sua conta pessoal.
2.  Crie uma branch específica para sua modificação: `git checkout -b feature/nome-da-melhoria`.
3.  Realize seus commits seguindo o padrão **Conventional Commits** (ex: `feat:`, `fix:`, `docs:`).
4.  Antes de abrir o PR, rode a suíte de testes e o portão de qualidade do projeto que você alterou, descritos na seção "Qualidade e testes" do README dele (por exemplo, [Validador de CPF → Qualidade e testes](mini_projetos/validador_de_cpf/README.md#qualidade-e-testes)). O mesmo roda automaticamente no CI a cada PR.
5.  Envie suas alterações para o seu fork: `git push origin feature/nome-da-melhoria`.
6.  Abra um **Pull Request** detalhando o que foi alterado e o impacto pedagógico da mudança.

## 📜 Diretrizes de qualidade:

- O objetivo principal é a **didática**: prefira um código legível e bem comentado a um código excessivamente complexo.
- Mantenha a **coerência na nomenclatura** das variáveis e funções (sempre em português e seguindo o padrão snake_case).
- Siga a organização que o projeto já tem (funções pequenas ou classe, conforme o caso); cada README lista, em "Ficou com alguma dúvida ou tem sugestões?", as regras próprias daquele projeto.
- Toda mudança de comportamento deve vir com o teste correspondente em `tests/test_main.py`.
- Todo teste novo ou alterado é **visto falhando uma vez** antes do commit: quebre de propósito a linha do `main.py` que ele protege (troque o valor, inverta a condição), confira que o teste fica vermelho e desfaça a quebra. A descrição do PR conta o que foi quebrado e o resultado.
- Dúvidas vão pelas [Issues](https://github.com/ryanvmorais/aprenda-com-ryan-morais/issues). Falhas de segurança, nunca: siga o [SECURITY.md](SECURITY.md). A convivência segue o [Código de Conduta](CODE_OF_CONDUCT.md).
