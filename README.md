# Audio Transcription and LLM Analysis with IBM STT + LLaMA on WatsonX.ai

Ferramenta em Python desenvolvida para:

1. **Transcrever** áudios de atendimento (.mp3) usando IBM Speech-to-Text  
2. **Gerar análises estruturadas em JSON** usando WatsonX LLM  
3. **Exportar automaticamente** os resultados em arquivos `.txt` e `.json`

O objetivo do projeto é automatizar a transformação de gravações de chamadas em textos estruturados, facilitando documentação, auditoria e criação de base de conhecimento.

Para acompanhar a evolucao tecnica do projeto e os proximos passos, veja tambem o [DIARIO_ESTUDO.md](/Users/eduardagama/Downloads/watsonx-transcription-llm-analysis/DIARIO_ESTUDO.md).

Para um historico objetivo das mudancas implementadas, veja o [CHANGELOG.md](/Users/eduardagama/Downloads/watsonx-transcription-llm-analysis/CHANGELOG.md).


## Funcionalidades

- **Transcrição automática** via IBM STT  
- **Análise textual inteligente** com WatsonX LLM  
- **Geração de transcrição limpa, análise estruturada e Q&A**  
- **Exportação de Q&A em TXT, CSV simples e CSV consolidado**  
- **Arquivos de saída organizados**  


## Stack utilizada

- **Python 3.13**
- **IBM Speech to Text**
- **WatsonX ModelInference**
- **Meta LLaMA 3.3 70B Instruct**
- **Argparse**
- **Pathlib**


## Estrutura do projeto
```text
│ audio-to-text-analyser/
│
├── app.py                          # Script principal
├── prompts/
│   └── qa_prompt.txt               # Template do prompt de analise
├── watsonx_analysis/
│   ├── __init__.py                 # Pacote principal da aplicacao
│   ├── config.py                   # Configuracao e resolucao de parametros
│   ├── observability.py            # Logs e mensagens de etapa no terminal
│   ├── parsing.py                  # Parsing e validacao da resposta do LLM
│   ├── prompt_utils.py             # Carregamento e montagem do prompt
│   ├── services.py                 # Integracoes com IBM STT e watsonx
│   ├── storage.py                  # Gravacao e montagem dos outputs
│
├── output/                         # Saídas automáticas
│   ├── <nome_audio>_01_transcricao.txt
│   ├── <nome_audio>_02_analise.json
│   ├── <nome_audio>_03_relatorio.txt
│   ├── <nome_audio>_04_qa.csv
│   ├── <nome_audio>_05_qa_consolidado.csv
│
└── README.md
```

## Configuração

Antes de rodar o projeto, configure suas credenciais IBM no arquivo `.env`:

```env
API_KEY_STT=
STT_URL=
STT_MODEL=
API_KEY_WX=
WATSONX_URL=
PROJECT_ID=
WATSONX_MODEL_ID=
```

## Requisitos

- Python 3.12 ou superior  
- Credenciais IBM Cloud para:
  - Speech-to-Text
  - WatsonX.ai Model Inference

### Dependências são instaladas via:

```sh
pip install ibm-watson ibm-cloud-sdk-core ibm-watsonx-ai
```

## Possíveis melhorias

- Exportação para PDF
- Exportação para Word (.docx)
- Painel de análise (Streamlit / Dash)
- Classificação automática do tipo da ligação
- Detecção de sentimento
- Processamento em lote de múltiplos arquivos ou pastas
- Testes automatizados

## Rodando localmente

Siga estes passos para executar o projeto em macOS / Linux (recomendado usar o `python3` do sistema ou instalado via Homebrew):

1. Crie (ou atualize) o arquivo `.env` com suas credenciais e preencha os valores necessários:

```env
API_KEY_STT=
STT_URL=
STT_MODEL=
API_KEY_WX=
WATSONX_URL=
PROJECT_ID=
WATSONX_MODEL_ID=
```

2. Crie e ative um ambiente virtual, instale dependências e execute a aplicação:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py path/to/audio.mp3
```

Se voce rodar `python app.py` sem informar o audio, a aplicacao lista os arquivos de audio encontrados na pasta atual para facilitar o proximo comando.

O prompt da analise agora fica em `prompts/qa_prompt.txt`. Se quiser testar outra versao sem alterar o prompt padrao, use:

```sh
python app.py path/to/audio.mp3 --prompt-file prompts/qa_prompt.txt
```

O modelo do STT pode ser sobrescrito pela CLI:

```sh
python app.py path/to/audio.mp3 --stt-model pt-BR_BroadbandModel
```

O modelo do watsonx tambem pode ser sobrescrito pela CLI:

```sh
python app.py path/to/audio.mp3 --llm-model meta-llama/llama-3-3-70b-instruct
```

3. Helper rápido: torne o `run.sh` executável e rode diretamente (ele criará o venv e instalará dependências automaticamente):

```sh
chmod +x run.sh
./run.sh path/to/audio.mp3
```

Observações:
- O script usa `python3` por padrão; se você quiser usar um binário diferente, exporte a variável `PYTHON` antes de executar o `run.sh`.
- Se nenhum audio for informado, o script lista os arquivos de audio da pasta atual.
- O `content_type` do STT agora e detectado automaticamente pela extensao do arquivo.
- Formatos mapeados no momento: `.mp3`, `.wav`, `.m4a`, `.flac` e `.ogg`.
- O modelo STT segue esta ordem de precedencia: `--stt-model`, `STT_MODEL` no `.env`, depois `pt-BR_NarrowbandModel`.
- O modelo do watsonx segue esta ordem de precedencia: `--llm-model`, `WATSONX_MODEL_ID` no `.env`, depois `meta-llama/llama-3-3-70b-instruct`.
- O arquivo de prompt padrao fica em `prompts/qa_prompt.txt` e deve conter o marcador `{{TRANSCRICAO}}`.
- `app.py` exige as variáveis de ambiente: `API_KEY_STT`, `STT_URL`, `API_KEY_WX`, `WATSONX_URL` e `PROJECT_ID`.
- A saida estruturada inclui transcricao bruta, transcricao limpa, resumo, motivo do contato, proximos passos, categoria, subcategoria, sentimento do cliente, pendencias, Q&A, follow-up e confirmacao de dados.
- O JSON de saida tambem registra `tempo_transcricao_segundos`, `tempo_inferencia_segundos` e `tempo_total_segundos`.
- Os metadados do JSON agora incluem `content_type`, `stt_model`, `llm_model`, `quantidade_perguntas_respostas`, `tamanho_arquivo_bytes` e `data_processamento`.
- O Q&A tambem e exportado em CSV, com uma linha por pergunta e resposta.
- O Q&A tambem e exportado em um CSV consolidado com metadados e uma linha por pergunta e resposta.
- O terminal agora mostra mensagens de inicio e fim das etapas principais do fluxo.
