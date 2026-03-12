# Changelog

Todas as mudancas relevantes deste projeto estao registradas aqui.

## 2026-03-12

### Adicionado

- Diario tecnico em `DIARIO_ESTUDO.md` para registrar aprendizados, riscos e proximos passos.
- Template de prompt externo em `prompts/qa_prompt.txt`.
- Suporte a `--prompt-file` para testar variacoes de prompt sem editar o codigo.
- Modularizacao do projeto em modulos separados por responsabilidade.
- Saida estruturada em `output/<audio>_02_analise.json`.
- Relatorio textual dedicado a Q&A em `output/<audio>_03_relatorio.txt`.
- Exportacao de Q&A em `output/<audio>_04_qa.csv`.
- Exportacao de Q&A consolidado com metadados em `output/<audio>_05_qa_consolidado.csv`.
- Medicao de `tempo_transcricao_segundos`, `tempo_inferencia_segundos` e `tempo_total_segundos`.
- Mensagens de inicio e fim das etapas principais no terminal.
- Suporte a `--stt-model` para escolher o modelo do IBM Speech to Text.
- Suporte a `--llm-model` para escolher o modelo do watsonx.
- Metadados adicionais no JSON de saida, incluindo tipo de audio, modelos usados, tamanho do arquivo, data de processamento e quantidade de Q&A.

### Alterado

- O audio deixou de ser fixo no codigo.
- Quando nenhum audio e informado, a CLI lista os arquivos disponiveis na pasta atual.
- O `content_type` do audio passou a ser detectado automaticamente pela extensao do arquivo.
- O modelo STT passou a seguir a precedencia:
  - `--stt-model`
  - `STT_MODEL` no `.env`
  - `pt-BR_NarrowbandModel`
- O modelo do watsonx passou a seguir a precedencia:
  - `--llm-model`
  - `WATSONX_MODEL_ID` no `.env`
  - `meta-llama/llama-3-3-70b-instruct`
- A analise deixou de ser texto livre e passou a ser validada como JSON estruturado.
- O prompt foi ajustado para manter o formato de Q&A dentro da estrutura JSON.
- O `03_relatorio.txt` passou a conter apenas perguntas e respostas.
- A estrutura do projeto passou a ser distribuida em modulos menores e especializados.
- Os modulos da aplicacao passaram a ficar agrupados no pacote `watsonx_analysis`.
- O parser da resposta do modelo ficou mais robusto para lidar com texto extra apos o JSON.
- O JSON de saida passou a incluir metadados de tempo de execucao.
- O JSON de saida passou a incluir metadados operacionais mais ricos para rastreabilidade.
- O terminal passou a exibir logs mais claros de etapa, contexto e conclusao do processamento.

### Corrigido

- Documentacao alinhada para usar apenas `.env`.
- Salvamento da resposta bruta do modelo quando o parsing JSON falha.
- Mensagens de erro mais claras para formatos de audio nao suportados.
