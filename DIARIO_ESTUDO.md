# Diario de Estudo do Projeto

Este documento registra o estado atual da aplicacao, os principais aprendizados tecnicos, os riscos percebidos e as proximas evolucoes recomendadas.

Ele funciona como um diario de estudo do projeto: um lugar para documentar o que existe hoje, o que precisa melhorar e o que foi aprendido ao longo da evolucao.

## Objetivo do projeto

Automatizar o processamento de gravacoes de chamadas para:

- transcrever o audio com IBM Speech to Text
- analisar o conteudo com watsonx
- transformar a ligacao em material util para consulta e base de conhecimento

## Como a aplicacao funciona hoje

Atualmente o fluxo principal esta concentrado em [`app.py`](/Users/eduardagama/Downloads/watsonx-transcription-llm-analysis/app.py):

1. Recebe um arquivo de audio pela linha de comando.
2. Se nenhum arquivo for informado, lista os audios encontrados na pasta atual para orientar a execucao.
3. Carrega credenciais do `.env`.
4. Carrega um template de prompt a partir de arquivo.
5. Envia o audio para o IBM Speech to Text.
6. Junta os trechos da transcricao em um texto unico.
7. Insere a transcricao no template de prompt.
8. Envia o prompt final para um modelo no watsonx.
9. Gera uma resposta estruturada em JSON.
10. Salva a transcricao bruta, a analise estruturada, um relatorio textual com Q&A, um CSV simples e um CSV consolidado com metadados.

## Leitura tecnica do estado atual

O projeto esta funcional e resolve um fluxo completo de ponta a ponta. Para uma primeira versao, isso e positivo: o objetivo esta claro e o resultado final e util.

Ao mesmo tempo, a base ainda esta muito concentrada em um unico script. Isso nao e um problema para validar a ideia, mas passa a limitar a manutencao, os testes e a evolucao do projeto conforme surgirem novas necessidades.

## Pontos observados na analise

### 1. Acoplamento alto em um unico arquivo

Status atual:

- resolvido na primeira etapa

Grande parte da responsabilidade esta centralizada em `app.py`: parsing de argumentos, carregamento de configuracao, transcricao, chamada ao LLM, escrita de arquivos e tratamento de erros.

Impacto:

- dificulta testes unitarios
- aumenta o risco de regressao ao fazer mudancas
- deixa a evolucao mais lenta conforme o projeto cresce

Melhoria aplicada:

- o fluxo foi modularizado em arquivos separados por responsabilidade
- `app.py` permaneceu como ponto de entrada e orquestracao
- a logica passou a ser distribuida dentro do pacote `watsonx_analysis`
- o pacote agora concentra configuracao, observabilidade, prompt, parsing, servicos externos e armazenamento

Beneficios atuais:

- o codigo ficou mais facil de navegar
- a separacao prepara melhor o projeto para testes
- cada modulo agora tem um comentario inicial explicando papel e conexoes

### 2. Parametros tecnicos fixos

Status atual:

- resolvido

Hoje alguns valores estao fixos no codigo, como:

- `content_type` do audio
- `model` do STT
- `model_id` do watsonx

Impacto:

- reduz flexibilidade
- dificulta experimentacao
- pode prejudicar a qualidade em outros tipos de audio

Observacao:

Se os audios forem realmente telefonicos, o modelo narrowband pode fazer sentido. Se houver audios com outra caracteristica, vale validar se esse modelo continua sendo o melhor.

Melhoria aplicada:

- o `content_type` nao e mais fixo como `audio/mp3`
- a aplicacao agora detecta o MIME pelo tipo de arquivo de entrada
- se a extensao nao estiver no mapa suportado, o erro orienta quais formatos sao aceitos
- o modelo do STT agora pode ser configurado
- a aplicacao segue esta ordem de precedencia para o STT:
  - `--stt-model`
  - `STT_MODEL` no `.env`
  - `pt-BR_NarrowbandModel` como padrao
- o modelo do watsonx agora pode ser configurado
- a aplicacao segue esta ordem de precedencia para o modelo do watsonx:
  - `--llm-model`
  - `WATSONX_MODEL_ID` no `.env`
  - `meta-llama/llama-3-3-70b-instruct` como padrao

Impacto positivo desta etapa:

- reduz necessidade de editar codigo para testar modelos de transcricao
- facilita comparacao entre cenarios telefonicos e nao telefonicos
- melhora usabilidade para experimentacao controlada
- permite experimentar modelos diferentes no watsonx sem alterar a implementacao

### 3. Prompt embutido diretamente no codigo

Status atual:

- resolvido na primeira etapa

O prompt de analise saiu da funcao de negocio e foi movido para um arquivo dedicado em `prompts/qa_prompt.txt`.

Problema anterior:

- dificulta iteracao de prompt
- atrapalha versionamento
- mistura regra de negocio com implementacao

Melhoria aplicada:

- o prompt passou a ser lido a partir de arquivo
- a aplicacao agora aceita `--prompt-file`
- o template usa o marcador `{{TRANSCRICAO}}` para montagem do prompt final

Beneficios atuais:

- editar o prompt ficou mais simples
- testar variacoes ficou mais pratico
- a instrucao de negocio ficou separada da implementacao Python
- erros de arquivo ausente ou mal formatado ficaram mais claros

### 4. Saida do LLM sem estrutura formal

Status atual:

- resolvido na primeira etapa

A resposta do modelo deixou de ser tratada apenas como texto livre e passou a ser validada como JSON.

Problema anterior:

- dificulta reutilizacao posterior
- complica criacao de dashboards
- torna integracoes futuras menos confiaveis

Melhoria aplicada:

- a aplicacao agora pede uma estrutura JSON fixa ao modelo
- a resposta e convertida e validada antes de ser salva
- a saida final passou a incluir:
  - transcricao bruta
  - transcricao limpa
  - resumo
  - motivo do contato
  - proximos passos
  - categoria
  - subcategoria
  - sentimento do cliente
  - ha pendencias
  - lista de pendencias
  - perguntas e respostas
  - necessita followup
  - houve confirmacao dos dados

Beneficios atuais:

- facilita reaproveitamento em outros setores
- prepara a base para dashboards e integracoes
- reduz dependencia de leitura manual da analise
- melhora consistencia entre execucoes
- preserva o formato de Q&A como base de conhecimento reutilizavel
- adiciona um formato simples para planilhas, BI e operacao
- adiciona um formato consolidado que conecta Q&A com metadados do processamento

### 5. Ausencia de testes automatizados

O projeto ainda nao tem testes unitarios nem testes de integracao com mocks.

Impacto:

- menor seguranca para refatorar
- maior dependencia de testes manuais
- maior risco de quebrar o fluxo sem perceber

### 6. Observabilidade limitada

Status atual:

- parcialmente resolvido

Hoje a aplicacao informa progresso basico por `print` e passou a registrar tempos de execucao no JSON de saida.

Exemplos do que seria util medir:

- tempo de transcricao
- tempo de inferencia
- arquivo processado
- modelo utilizado
- falhas por etapa

Melhoria aplicada:

- a aplicacao agora mede `tempo_transcricao_segundos`
- a aplicacao agora mede `tempo_inferencia_segundos`
- a aplicacao agora mede `tempo_total_segundos`
- esses valores sao exibidos no terminal ao final da execucao
- esses valores tambem sao persistidos em `metadados` no arquivo `02_analise.json`
- o terminal agora mostra mensagens de inicio e fim das etapas principais
- as mensagens incluem contexto util como arquivo processado e modelos utilizados
- o JSON agora tambem registra:
  - `content_type`
  - `stt_model`
  - `llm_model`
  - `quantidade_perguntas_respostas`
  - `tamanho_arquivo_bytes`
  - `data_processamento`

### 7. Documentacao parcialmente desalinhada

Status atual:

- corrigido

O projeto agora usa apenas `.env` como fonte de configuracao documentada.

Problema anterior:

- havia mencao a `.env.example` em parte da documentacao
- isso criava uma instrucao duplicada e desnecessaria para quem esta aprendendo o fluxo

Ajuste realizado:

- a documentacao foi simplificada para orientar apenas o preenchimento do arquivo `.env`
- as instrucoes antigas foram removidas para evitar ambiguidade

Licao:

Quando o codigo evolui, a documentacao precisa evoluir junto. Isso e parte da manutencao real do projeto.

## Melhorias tecnicas recomendadas

### Prioridade 1. Modularizar a aplicacao

Status atual:

- resolvido

Separar responsabilidades em modulos, por exemplo:

- `config.py`
- `transcription.py`
- `analysis.py`
- `storage.py`
- `cli.py`

Beneficios:

- codigo mais legivel
- testes mais simples
- manutencao mais segura

### Prioridade 2. Estruturar a saida do modelo

Status atual:

- resolvido

Em vez de salvar apenas texto livre, gerar uma resposta estruturada com campos como:

- `resumo`
- `categoria`
- `sentimento`
- `perguntas_respostas`
- `acoes_recomendadas`

Beneficios:

- facilita reuso
- permite dashboards
- melhora integracao com outras ferramentas

### Prioridade 3. Melhorar a qualidade do pipeline de transcricao

Evolucoes sugeridas:

- detectar tipo de arquivo automaticamente
- aceitar formatos diferentes de audio
- permitir escolha do modelo STT via CLI
- avaliar qualidade da transcricao por tipo de ligacao

### Prioridade 4. Criar testes

Primeiros testes sugeridos:

- validacao das variaveis de ambiente
- criacao de arquivos de saida
- montagem do prompt
- comportamento em erro nas chamadas externas

Ferramentas uteis:

- `pytest`
- `unittest.mock`

### Prioridade 5. Evoluir a interface de linha de comando

Opcoes uteis para adicionar:

- `--output-dir`
- `--model-id`
- `--stt-model`
- `--format txt|json`
- `--skip-transcription`
- `--skip-analysis`

### Prioridade 6. Processamento em lote

Hoje o fluxo esta orientado a um audio por execucao. Uma evolucao de alto valor e permitir:

- processar uma pasta inteira
- gerar saidas padronizadas por arquivo
- consolidar resultados em um indice ou relatorio

## Melhorias de produto com melhor retorno

- classificacao automatica do tipo de ligacao
- extracao da intencao do cliente
- resumo executivo da chamada
- deteccao de sentimento
- identificacao de risco de insatisfacao
- exportacao em `json` e `csv`
- interface simples com Streamlit para upload e consulta

## Ordem de evolucao recomendada

Se a ideia for evoluir com seguranca e sem aumentar complexidade cedo demais, a sequencia recomendada e:

1. testes com mocks
2. CLI mais completa
3. processamento em lote
4. consolidado unico para multiplos arquivos
5. dashboard ou camada visual leve

Essa ordem prepara o projeto para crescer sem virar um script dificil de manter.

## Aprendizados deste estudo

- Um script funcional nao e o mesmo que uma aplicacao pronta para crescer.
- Integracao com servicos externos exige pensar em estrutura, falhas e observabilidade.
- Prompt tambem e parte da arquitetura quando influencia diretamente a qualidade da saida.
- Saida estruturada aumenta muito o valor do sistema.
- Documentacao tecnica deve registrar decisoes, riscos e proximos passos, nao apenas como executar.

## Diario de evolucao

### Entrada 1 - Analise inicial da arquitetura

Data: 2026-03-12

Resumo:

- a aplicacao ja entrega valor com um fluxo ponta a ponta
- o maior gargalo atual e a concentracao de responsabilidades em um unico arquivo
- a maior oportunidade tecnica e transformar o resultado em estrutura reutilizavel

Decisoes sugeridas:

- extrair modulos antes de adicionar muitas novas features
- tratar saida estruturada como prioridade
- comecar a escrever testes antes de expandir o escopo do projeto

### Entrada 2 - Remocao do audio fixo e melhoria de usabilidade no CLI

Data: 2026-03-12

Contexto:

- a aplicacao dependia anteriormente de um arquivo padrao fixo no codigo
- isso deixava o comportamento pouco flexivel e escondia uma dependencia implicita da execucao

Mudanca realizada:

- o codigo deixou de depender de um audio padrao embutido
- quando o usuario executa `python app.py` sem argumento, o sistema lista os arquivos de audio encontrados na pasta atual
- a saida agora orienta o usuario com um exemplo de comando para a proxima tentativa

Exemplo de comportamento:

```text
❌ Nenhum arquivo de audio foi informado.

Arquivos de audio encontrados na pasta atual:
- antecipacao4.mp3
- cessao1.mp3

Exemplo de uso:
python app.py antecipacao4.mp3
```

Aprendizado:

- remover defaults escondidos melhora a clareza do fluxo
- uma mensagem de erro pode tambem servir como apoio de usabilidade
- pequenas melhorias de CLI ja tornam a aplicacao mais amigavel sem aumentar muito a complexidade

Impacto no roadmap:

- esta melhoria resolve o primeiro ajuste de usabilidade identificado no estudo
- o proximo passo relacionado ao pipeline de entrada e validar formato e tipo de audio, em vez de assumir sempre `audio/mp3`

### Entrada 3 - Extracao do prompt para arquivo dedicado

Data: 2026-03-12

Contexto:

- o prompt estava embutido diretamente na funcao de analise
- qualquer ajuste de texto exigia editar a logica Python
- isso dificultava manutencao, versionamento e experimentacao

Mudanca realizada:

- o prompt atual foi extraido para `prompts/qa_prompt.txt`
- a aplicacao passou a carregar esse template antes de chamar o watsonx
- o template usa o marcador `{{TRANSCRICAO}}` para inserir a transcricao
- foi adicionada a opcao `--prompt-file` para permitir testes com prompts alternativos

Beneficio de usabilidade:

- editar prompt ficou mais simples
- testar variacoes nao exige mexer na funcao principal
- o erro agora fica mais claro se o arquivo de prompt nao existir ou estiver mal formado

Beneficio de manutencao:

- regra de instrucao ficou separada da implementacao
- o prompt pode ser versionado como artefato proprio
- a base ficou melhor preparada para ter multiplos prompts por caso de uso

Proximo passo natural:

- criar uma segunda versao de prompt para comparar resultados
- depois disso, considerar separar a logica de carregamento do prompt em um modulo proprio quando a modularizacao comecar

Observacao de estudo:

- esta foi uma melhoria pequena no codigo, mas importante para usabilidade e manutencao
- ela prepara o projeto para experimentacao controlada de prompts, que tende a ser uma parte central da evolucao da analise

### Entrada 4 - Alinhamento da documentacao para usar apenas .env

Data: 2026-03-12

Contexto:

- a aplicacao ja usava `.env` como fonte principal de configuracao
- parte da documentacao ainda mencionava `.env.example`
- isso gerava ruido para quem esta estudando ou executando o projeto pela primeira vez

Mudanca realizada:

- o `README` foi atualizado para orientar apenas o preenchimento do `.env`
- o fluxo de configuracao ficou mais direto e sem instrucoes redundantes

Beneficio de usabilidade:

- reduz duvidas na configuracao inicial
- evita que a pessoa fique procurando qual dos dois arquivos deve usar

Beneficio de manutencao:

- documentacao mais coerente com o comportamento real da aplicacao
- menos pontos para manter sincronizados no futuro


### Entrada 5 - Estruturacao da saida do modelo em JSON

Data: 2026-03-12

Contexto:

- a analise era salva apenas como texto livre
- isso limitava reuso da informacao fora do caso de uso atual
- havia interesse explicito em gerar uma estrutura reaproveitavel por outros setores

Mudanca realizada:

- o prompt passou a exigir resposta em JSON valido
- a aplicacao agora extrai e valida a resposta estruturada do modelo
- a saida final foi organizada com:
  - `transcricao.bruta`
  - `transcricao.limpa`
  - `analise.resumo`
  - `analise.motivo_contato`
  - `analise.proximos_passos`
  - `analise.categoria`
  - `analise.subcategoria`
  - `analise.sentimento_cliente`
  - `analise.ha_pendencias`
  - `analise.pendencias`
  - `analise.perguntas_respostas`
  - `analise.necessita_followup`
  - `analise.houve_confirmacao_dados`

Arquivos gerados:

- `output/<audio>_01_transcricao.txt`
- `output/<audio>_02_analise.json`
- `output/<audio>_03_relatorio.txt`

Beneficio de usabilidade:

- a pessoa continua tendo um relatorio legivel em texto
- o relatorio final ficou focado apenas no Q&A para consulta rapida
- ao mesmo tempo passa a existir um JSON pronto para reuso

Beneficio de manutencao:

- a aplicacao agora falha cedo quando o modelo nao devolve estrutura valida
- o contrato da saida ficou mais claro e testavel

Observacao complementar:

- a feature foi concluida preservando dois objetivos ao mesmo tempo:
  - estruturacao para sistemas
  - formato de perguntas e respostas para base de conhecimento

Proximo passo natural:

- adicionar metadados como versao do prompt, modelo e data de processamento
- depois disso, considerar exportacao complementar em CSV para consumo analitico

## Proxima sessao de estudo

Sugestao objetiva para a proxima iteracao:

1. criar uma segunda versao de prompt para comparar estilo e qualidade da resposta
2. validar extensao ou tipo MIME do audio de entrada
3. depois disso, iniciar a extracao de modulos para preparar testes

Quando essa etapa estiver pronta, o proximo passo natural e mudar a analise para JSON estruturado.
