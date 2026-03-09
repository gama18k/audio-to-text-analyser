# Audio Transcription and LLM Analysis with IBM STT + LLaMA on WatsonX.ai

Ferramenta em Python desenvolvida para:

1. **Transcrever** áudios de atendimento (.mp3) usando IBM Speech-to-Text  
2. **Gerar análises em formato Q&A** usando WatsonX LLM  
3. **Exportar automaticamente** os resultados em arquivos `.txt`

O objetivo do projeto é automatizar a transformação de gravações de chamadas em textos estruturados, facilitando documentação, auditoria e criação de base de conhecimento.


## Funcionalidades

- **Transcrição automática** via IBM STT  
- **Análise textual inteligente** com WatsonX LLM  
- **Geração de Q&A** a partir da transcrição  
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
│
├── output/                         # Saídas automáticas
│   ├── <nome_audio>_01_transcricao.txt
│   ├── <nome_audio>_02_analise.txt
│
└── README.md
```

## Configuração

Antes de rodar o projeto, adicione suas credenciais IBM no arquivo `app.py`:

```python
STT_URL = "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/<ID>"
API_KEY = "SUA_API_KEY"
WATSONX_URL = "https://au-syd.ml.cloud.ibm.com"
PROJECT_ID = "<ID_DO_PROJETO>"
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
- Melhor pós-processamento da transcrição
