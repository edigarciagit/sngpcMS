Guia Técnico: Vinculação de Registros MS e Listas de Controle Especial (Portaria 344/98)

Fonte base para localizar os arquivos e executar: https://dados.anvisa.gov.br/dados/SNGPC/Industrializados/

1. Escopo e Objetivos Técnicos

Este guia estabelece os parâmetros arquiteturais para a integração sistemática entre a base de registros de medicamentos da Anvisa e os dispositivos de controle sanitário da Portaria 344/98. A correlação precisa entre o número de registro no Ministério da Saúde (MS) e as listas de substâncias controladas é um requisito crítico para a conformidade regulatória, impactando diretamente a validade jurídica da dispensação e a integridade das transmissões de arquivos XML ao Sistema Nacional de Gerenciamento de Produtos Controlados (SNGPC). A estruturação desses dados permite a implementação de travas lógicas em sistemas de ERP farmacêutico e assegura a rastreabilidade em toda a cadeia de suprimentos.

Os principais objetivos deste guia técnico são:

* Precisão e Integridade de Dados: Garantir o mapeamento inequívoco entre o SKU comercial e sua respectiva classificação de controle (A1, A2, A3, B1, B2, C1, C2, C3, C4, C5 e Adendos).
* Automação de Workflow Regulatório: Reduzir a latência na identificação de novos produtos controlados através da monitoração automatizada dos repositórios de dados abertos.
* Suporte à Auditoria e Gestão de Risco: Viabilizar o cruzamento célere entre estoques físicos, prescrições retidas e escrituração eletrônica para fins de fiscalização sanitária.

2. Mapeamento do Repositório de Dados Abertos da Anvisa

Para a construção do pipeline de dados, o arquiteto deve consumir os arquivos listados no repositório oficial. A tabela abaixo detalha as fontes de dados e os metadados necessários para o processamento:

Nome do Arquivo	Função no Processamento	Metadados Relevantes
DADOS_ABERTOS_MEDICAMENTOS.csv	Base Master de Registros.	NU_REGISTRO_PRODUTO, NO_PRODUTO, ID_PRODUTO, CO_MES_ANO_VALIDADE_REGISTRO.
TA_RESTRICAO_MEDICAMENTO.csv	Tabela de Atributos de Controle.	ID_PRODUTO, DS_RESTRICAO_VENDA, TP_LCV (Tipo de Lista de Controle de Venda).
TA_FABRICANTE_MEDICAMENTO_IFA.CSV	Validação de Insumos (IFA).	CO_IFA, NO_FABRICANTE, ID_PRODUTO (Secundário).
CICLO_ANALISE_PETICOES_MEDICAMENTO.csv	Monitoramento de Novos Registros.	NU_PROCESSO, DS_ASSUNTO, ST_SITUACAO_FILA.
Documentacao_e_Dicionario_SNGPC	Dicionários Técnicos (PDF).	Esquemas XML, Definições de Campos para Industrializados vs. Manipulados.

3. Arquitetura da Chave de Ligação (Número de Registro MS)

A chave primária de ligação entre a base master de produtos e a tabela de restrições é o Número de Registro MS. Na arquitetura de dados da Anvisa, este campo é identificado como NU_REGISTRO_PRODUTO.

Para garantir a integridade do join (unificação), o analista de dados deve observar as seguintes premissas técnicas:

1. Tipagem de Dado: O campo deve ser tratado obrigatoriamente como VARCHAR/STRING para preservar os zeros à esquerda e evitar truncamento.
2. Normalização de 13 Dígitos: Embora existam registros simplificados de 9 dígitos em sistemas legados, o padrão regulamentar atual exige o formato de 13 dígitos. Deve-se aplicar funções de limpeza (Regex) para remover caracteres não numéricos.
3. Chave Substituta (Surrogate Key): O campo ID_PRODUTO atua como chave de ligação interna entre a tabela master e a tabela TA_RESTRICAO_MEDICAMENTO.csv, sendo vital para mapear restrições a nível de apresentação/concentração específica.

4. Categorização por Listas de Controle (Portaria 344/98)

A interpretação das listas de controle exige o cruzamento entre o campo DS_RESTRICAO_VENDA e as definições contidas nos dicionários de dados. É fundamental distinguir as regras de negócio para medicamentos Industrializados (conforme Documentacao_e_Dicionario_de_Dados_SNGPC_Industrializados.pdf) e Manipulados (Documentacao_e_Dicionario_de_Dados_SNGPC_Manipulados.pdf), visto que possuem estruturas de transmissão distintas.

A lógica de filtragem para identificação de substâncias da Portaria 344/98 deve seguir este protocolo:

1. Venda sob Prescrição Médica: Identificar registros onde DS_RESTRICAO_VENDA não seja "Venda Livre" ou "Isento de Registro".
2. Retenção de Receita (Controle Especial): Filtrar pelo atributo TP_LCV ou descritores que contenham "Retenção de Receita" ou "Controle Especial". Isso abrange as listas C1, C2, C4 e C5.
3. Notificação de Receita: Identificar via códigos de restrição a obrigatoriedade de Notificação de Receita "A" (Entorpecentes/Amarela) ou "B" (Psicotrópicos/Azul), correlacionando com as listas A1, A2, A3, B1 e B2.

5. Procedimento Operacional de Cruzamento de Dados (Data Merging)

5.1. Carga e Ingestão de Dados

Carregar os arquivos CSV para o ambiente de processamento. Recomenda-se a verificação de checksum para garantir que os arquivos como DADOS_ABERTOS_MEDICAMENTOS.csv (versão 11/02/2026) foram baixados integralmente.

5.2. Limpeza e Padronização (Cleaning)

Transformar o campo NU_REGISTRO_PRODUTO em uma string numérica pura de 13 posições. Em casos de 9 dígitos, deve-se realizar o preenchimento conforme a regra de formação do registro Anvisa.

5.3. Execução do Left Join

Realizar um Left Join entre a tabela de medicamentos (esquerda) e a de restrições (direita). Esta abordagem é estratégica: ela mantém a visibilidade de todo o portfólio de medicamentos registrados; registros que retornarem null nos campos de restrição são classificados por padrão como "Venda Livre" ou "Prescrição Simples", enquanto os demais recebem a flag de "Controle Especial".

5.4. Mapeamento de Status e Exigências

Integrar o resultado com o dicionário de campos para atribuir o tipo de receituário (A, B, ou Especial). Validar se o IFA (Insumo Farmacêutico Ativo) mapeado em TA_FABRICANTE_MEDICAMENTO_IFA.CSV corresponde à substância listada nos anexos da Portaria 344/98.

6. Validação e Referências de Consultas

A integridade do cruzamento deve ser validada contra o campo Situacao_Registro para evitar a categorização de produtos com registro cancelado ou caduco.

Lista de Referência e Leitura Técnica (Dados Anvisa):

* Documentacao_e_Dicionario_de_Dados_MEDICAMENTOS.pdf (Modificado em 21/11/2023).
* Documentacao_e_Dicionario_Restricao_Medicamento_V1.pdf (Modificado em 27/12/2023).
* CONSULTA_SITUCAO_FILA.csv (Modificado em 11/02/2026): Essencial para validar o status real do registro.
* CICLO_ANALISE_PETICOES_MEDICAMENTO.csv (Modificado em 11/02/2026): Utilizar para monitorar medicamentos em fase de renovação ou alteração de pós-registro que possam mudar de categoria de controle.
* Dicionario_de_Dados_Painel_SNGPC_Venda_de_Industrializados.pdf (Modificado em 27/09/2020).

7. Diretrizes para Retenção de Receita e SNGPC

A obrigatoriedade de escrituração no SNGPC é derivada diretamente do cruzamento positivo com o arquivo TA_RESTRICAO_MEDICAMENTO.csv. Se o produto possuir um código de restrição vinculado a listas de controle especial, o sistema de inventário deve bloquear a finalização da venda sem a captura dos dados da receita (CRM do prescritor, nome do paciente e lote do medicamento).

Atenção à Situação Cadastral: O fato de um registro constar na base de medicamentos não garante sua comercialização. Sempre verifique o campo de situação do registro; produtos "Caducos" não devem ser escriturados no SNGPC. Risco IFA: Para substâncias de alto risco (Entorpecentes), utilize a TA_FABRICANTE_MEDICAMENTO_IFA.CSV como camada adicional de segurança para validar se o fabricante do insumo está devidamente habilitado. Exceção Cannabis: Medicamentos à base de Cannabis (registrados via RDC 327/2019 e listados em TA_DA_PRODUTO_CANNABIS.CSV) possuem regras de notificação específicas que muitas vezes não seguem o padrão clássico das listas A/B/C; trate-os como uma regra de exceção no seu motor de regras de negócio. Variação de Apresentação: Um mesmo registro base (primeiros 9 dígitos) pode ter restrições diferentes para dosagens distintas. A vinculação deve ser sempre pelo ID_PRODUTO ou pelos 13 dígitos completos para evitar erros de dispensação.