# CT-MRC-010 — Caça-string "KOVR": classificação MARCA × IDENTIFICADOR

Medido em 13/08/2026 (live no CITNET KOVR HML `/citnet/` + evidências em disco dos CTs 002/003/007).
Regra: **MARCA** (nome exibido ao usuário) deve ter virado KEV; **IDENTIFICADOR técnico** deve permanecer KOVR.

## (a) MARCA exibida ao usuário — DEVE ser "KEV SEGUROS S.A."

| # | Ocorrência exata | Onde | Fonte | Correto? |
|---|------------------|------|-------|----------|
| a1 | `KOVR Seguradora - Averbação - Diária` | Cabeçalho do protocolo de averbação | live (tab PrintProtocolo) + disk CT-002/007 | ✗ deveria ser KEV |
| a2 | `...efetuado através do site da KOVR Seguradora sob o número de protocolo...` | Corpo do protocolo de averbação | live | ✗ deveria ser KEV |
| a3 | `KOVR Seguradora - CONSULTA DE AVERBAÇÕES` | Cabeçalho do relatório Consulta de Averbações (Nacional/RCV) | disk CT-003 | ✗ deveria ser KEV |
| a4 | `KOVR Seguradora - CONSULTA DE AVERBAÇÕES INTERNACIONAIS - Exportação` | Cabeçalho do relatório Consulta de Averbações Internacionais | disk CT-007 | ✗ deveria ser KEV |
| a5 | `KOVR Seguradora- CitNet` | `<title>` da página `/citnet/` (aba do navegador) | live (document.title) | ✗ deveria ser KEV |

Todas do tipo (a) têm a MESMA causa raiz: nome resolvido de `web.KOVR.config` → `infoCliente` índice 2 = "KOVR Seguradora" (não migrado). Já registrado no **Bug #8121**.
Onde o nome é hardcoded no RDLC (3 certificados) a marca JÁ está correta = "KEV SEGUROS S.A." (CT-006).

## (b) IDENTIFICADOR técnico — CORRETO que permaneça "KOVR"

| # | Ocorrência | Tipo | Correto? |
|---|-----------|------|----------|
| b1 | `LogoKOVR.png` / `LogoKOVR.jpg` (conteúdo servido = logo KEV) | nome de arquivo de logo | ✓ permanece |
| b2 | `smt-hom-citweb-kovr` | nome da base de dados | ✓ permanece |
| b3 | `kovr-hml-faturamento.nsseg.com.br` | URL do ambiente | ✓ permanece |
| b4 | `Empresa=KOVR`, `infoCliente[0]=KOVR`, `infoCliente[4]=KOVR` | chaves de configuração | ✓ permanece |
| b5 | `web.KOVR.config`, `*_KOVR.rdlc` | nomes de arquivos de config/report | ✓ permanece |

## Veredito

**REPROVADO** — persistem 5 ocorrências de "KOVR Seguradora" como MARCA exibida (a1–a5), mesma causa raiz do **Bug #8121** (`infoCliente[2]` não migrado). NÃO abrir bug novo. Os identificadores técnicos (b1–b5) estão corretamente preservados — a implementação NÃO apagou "KOVR" indevidamente.

> Achado adicional para o #8121: o `<title>` do navegador em `/citnet/` (a5) é uma superfície de marca não listada originalmente e também exibe "KOVR Seguradora".
