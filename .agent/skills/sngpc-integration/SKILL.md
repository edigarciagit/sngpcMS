---
name: sngpc-integration
description: Expert knowledge on Anvisa's SNGPC (Sistema Nacional de Gerenciamento de Produtos Controlados) and Portaria 344/98 regulations.
---

# SNGPC Integration Skill

## Overview

This skill provides specific logic and regulatory knowledge for integrating pharmaceutical product data with Anvisa's SNGPC system. It covers the parsing of registration numbers, identification of controlled substances (Portaria 344/98), and data validation rules.

## Core Concepts

### 1. Registration Number (NU_REGISTRO_PRODUTO)

- **Format**: 13 digits (numeric).
- **Validation**:
  - Must be strictly numeric.
  - If a 9-digit number is encountered, it must be padded or treated according to legacy rules (but 13 is the standard).
  - Used as the Primary Key for joining with `TA_RESTRICAO_MEDICAMENTO.csv`.

### 2. Control Lists (Portaria 344/98)

The system must classify products into the following lists based on `CS_LISTA` or `DS_RESTRICAO_VENDA`:

- **List A (A1, A2, A3)**: Entorpecentes / Psychotropics (Yellow Prescription / Notification A).
- **List B (B1, B2)**: Psychotropics (Blue Prescription / Notification B).
- **List C (C1, C2, C4, C5)**: White Prescription (Controlada / Retinoids / Anabolics / Immunosuppressants).
  - *Note*: C3 is Thalidomide (Special regulation).
- **Antimicrobials**: Often require retention but have specific validities.

### 3. Data Sources & Mapping

- **Master Data**: `DADOS_ABERTOS_MEDICAMENTOS.csv`
- **Restrictions**: `TA_RESTRICAO_MEDICAMENTO.csv`
  - Join Key: `NU_REGISTRO_PRODUTO` (or `ID_PRODUTO` as surrogate).
- **IFA Validation**: `TA_FABRICANTE_MEDICAMENTO_IFA.csv` (Check active pharmaceutical ingredients).

## Validation Rules

1. **Status Check**: Always verify `SITUACAO_REGISTRO` != "Caduco" or "Cancelado" before processing.
2. **Sale Restriction**:
   - If `DS_RESTRICAO_VENDA` contains "VENDA LIVRE", skip SNGPC controls.
   - If `TP_LCV` indicates "Retenção de Receita", enable inventory locks.

## Common Tasks

- **Parsing**: Cleaning non-numeric chars from `NU_REGISTRO`.
- **Classification**: Determining the specific list (e.g., A1 vs C1) for correct XML generation.
- **Auditing**: Cross-referencing current stock with regulatory status changes (via `CICLO_ANALISE_PETICOES_MEDICAMENTO.csv`).
