# Specs — Lista de Tarefas

Este projeto usa spec-driven development: cada feature é documentada em
`specs/NNN-nome/` como três arquivos Markdown agnósticos de ferramenta —
`requirements.md` (o quê/porquê), `design.md` (como) e `tasks.md` (quebra
executável e rastreável). O fluxo de 4 fases (`requirements → design → tasks
→ implementação`), com portão de aprovação humana em cada uma, é
o fluxo de toda spec deste projeto.

## Convenções

- **Numeração:** `NNN` sequencial de 3 dígitos (`001`, `002`, ...), nome
  curto em kebab-case.
- **Frontmatter** (idêntico nos três arquivos de uma spec):
  ```yaml
  ---
  feature: <título legível>
  status: rascunho | aprovado | em andamento | concluído
  date: AAAA-MM-DD
  related:
    - NNN-outra/requirements.md
  origin: concepção | engenharia reversa
  ---
  ```
- **Critério de aceite:** Given/When/Then, um `### RF-NN` (heading, linkável)
  por requisito funcional; `### RNF-NN` para não funcional.
- **Rastreabilidade:** toda tarefa em `tasks.md` cita o(s) requisito(s) e/ou
  ADR que satisfaz (`— RF-01, ADR-2`); a última tarefa de cada etapa é o
  portão de qualidade, com o resultado real anotado ao executar.
- **Idioma:** português — projeto educacional (ver `CLAUDE.md`).

## Workflow

```
requirements.md (rascunho) --[aprovação]--> (aprovado)
        |
        v
design.md (aprovado) --[aprovação]--> status dos requirements avança
        |
        v
tasks.md (aprovado) --[aprovação]--> em andamento
        |
        v
implementação, tarefa a tarefa --[portão de qualidade]--> concluído
```

## Índice / Roadmap

| Spec | Escopo | Entrega | Status |
|---|---|---|---|
| [001-lista-de-tarefas](001-lista-de-tarefas/requirements.md) | O programa completo: adicionar, concluir ou reabrir, editar e remover tarefas com a data de criação, lista sempre à vista, gravação atômica em JSON a cada alteração, cópia do arquivo corrompido, limpeza de tela multiplataforma | — | concluído |

## Notas de manutenção

Uma armadilha entre specs: o formato do `tarefas.json`. Uma spec que mude
os campos das tarefas precisa continuar abrindo os arquivos gravados pelas
versões anteriores, ou o programa os trata como corrompidos (RF-02). Ao
adicionar uma feature nova (ver "Atividades para praticar" no `README.md`),
abra uma spec nova em vez de estender `001` diretamente.

Use `001-lista-de-tarefas/` como padrão de formato para as próximas specs
deste projeto.
