# Specs — Cifra de César

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
| [001-cifra-de-cesar](001-cifra-de-cesar/requirements.md) | O programa completo: cifrar e decifrar com uma chave de 1 a 25 por `ord`, `chr` e o resto da divisão por 26, acentos e cedilha tirados com o `unicodedata`, quebra por força bruta com as 25 chaves e pela frequência das letras com o `Counter` e a tabela do português da COPPE/UFRJ, aviso de texto curto, limpeza de tela multiplataforma | — | em andamento |

## Notas de manutenção

Uma armadilha entre specs: a pontuação da frequência. O `MINIMO_LETRAS` do
aviso de texto curto saiu da medição do método da soma dos produtos (ADR-5 e
ADR-6 de [`001-cifra-de-cesar`](001-cifra-de-cesar/design.md)); uma spec que
troque o método ou a tabela de frequência mede de novo e revê o mínimo junto.
Ao adicionar uma feature nova (ver "Atividades para praticar" no `README.md`),
abra uma spec nova em vez de estender `001` diretamente.

Use `001-cifra-de-cesar/` como padrão de formato para as próximas specs deste
projeto.
