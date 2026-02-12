# SNGPC - Data Pipeline

Este projeto contém o pipeline de dados para integração com o SNGPC da Anvisa.

## Estrutura

- `sngpc/`: Código fonte Python.
  - `etl/`: Scripts de extração e transformação.
  - `anvisa/`: Conectores com a Anvisa.
  - `core/`: Regras de negócio da Portaria 344/98.
  - `models/`: Modelos de dados.
- `data/`: Armazenamento local de arquivos.
  - `raw/`: Arquivos CSV originais baixados da Anvisa.
  - `processed/`: Dados limpos e enriquecidos.
- `docs/anvisa/`: Documentação técnica e dicionários de dados.
- `config/`: Arquivos de configuração.

## Como Executar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure o arquivo `config/config.yaml` se necessário.
3. Execute o script principal (a ser implementado).

## Fontes de Dados

- [Dados Abertos Anvisa - Industrializados](https://dados.anvisa.gov.br/dados/SNGPC/Industrializados/)
