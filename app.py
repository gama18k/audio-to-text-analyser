import argparse
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

# IBM SPEECH TO TEXT
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# IBM WATSONX
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# SALVAR ARQUIVOS
def salvar_texto(texto: str, caminho: Path):
    """Salva texto em arquivo, criando pastas se necessário."""
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"✔ Arquivo salvo: {caminho}")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo {caminho}: {e}")


# 1. TRANSCRIÇÃO COM IBM STT
def transcrever_audio_ibm(caminho_audio: Path, api_key: str, url: str) -> str:
    """Transcreve áudio usando IBM Speech-to-Text."""

    print(f"🎙️ Transcrevendo áudio: {caminho_audio}")

    try:
        authenticator = IAMAuthenticator(api_key)
        stt = SpeechToTextV1(authenticator=authenticator)
        stt.set_service_url(url)

        with open(caminho_audio, "rb") as audio:
            resultado = stt.recognize(
                audio=audio,
                content_type="audio/mp3",
                model="pt-BR_NarrowbandModel"
            ).get_result()

        texto = " ".join(
            item["alternatives"][0]["transcript"]
            for item in resultado["results"]
        )

        return texto.strip()

    except Exception as e:
        raise RuntimeError(f"❌ Erro ao transcrever áudio: {e}")


# 2. ANÁLISE Q&A COM WATSONX
def analisar_ligacao(transcricao: str, api_key: str, url: str, project_id: str) -> str:
    """Gera análise Q&A da ligação em TEXTO NORMAL."""

    prompt = f"""
Você é um especialista em atendimento ao cliente da Stellantis Financiamentos.

Sua tarefa é analisar a transcrição de uma ligação entre cliente e atendente e transformar o conteúdo em uma base de conhecimento no formato de perguntas e respostas (Q&A).

Regras:
- Extraia as principais dúvidas do cliente.
- Converta cada dúvida em uma pergunta clara.
- Escreva a resposta baseada no que foi explicado pelo atendente.
- Use linguagem clara e institucional.
- Se o cliente mencionou um processo da empresa, transforme isso em um guia explicativo.

Formato da resposta:

Pergunta:
<pergunta clara sobre o processo>

Resposta:
<explicação completa e institucional sobre como realizar o processo>

TRANSCRIÇÃO:
{transcricao}
"""

    try:
        creds = Credentials(url=url, api_key=api_key)

        model = ModelInference(
            model_id="meta-llama/llama-3-3-70b-instruct",
            credentials=creds,
            project_id=project_id
        )

        resposta = model.generate_text(
            prompt=prompt,
            params={
                "decoding_method": "greedy",
                "temperature": 0,
                "max_new_tokens": 1200
            }
        )

        return resposta.strip()

    except Exception as e:
        raise RuntimeError(f"❌ Erro ao gerar análise: {e}")


# MAIN

def main():
    parser = argparse.ArgumentParser(description="Transcrever e analisar ligação")
    parser.add_argument("audio", nargs="?", default="antecipacao2.mp3")
    args = parser.parse_args()

    caminho_audio = Path(args.audio)

    if not caminho_audio.exists():
        print(f"❌ Arquivo não encontrado: {caminho_audio}")
        return 1

    # CONFIGURAÇÕES (carregadas do .env)
    API_KEY_STT = os.getenv("API_KEY_STT")
    STT_URL = os.getenv("STT_URL")
    API_KEY_WX = os.getenv("API_KEY_WX")
    WATSONX_URL = os.getenv("WATSONX_URL")
    PROJECT_ID = os.getenv("PROJECT_ID")

    if not all([API_KEY_STT, STT_URL, API_KEY_WX, WATSONX_URL, PROJECT_ID]):
        print("❌ Configure as variáveis no arquivo .env (use .env.example como referência)")
        return 1

    try:
        # 1) TRANSCRIÇÃO BRUTA
        transcricao_bruta = transcrever_audio_ibm(caminho_audio, API_KEY_STT, STT_URL)
        salvar_texto(transcricao_bruta, Path(f"output/{caminho_audio.stem}_01_transcricao.txt"))

        # 2) ANÁLISE Q&A DIRETA
        analise = analisar_ligacao(
            transcricao_bruta,
            API_KEY_WX,
            WATSONX_URL,
            PROJECT_ID
        )
        salvar_texto(analise, Path(f"output/{caminho_audio.stem}_02_analise.txt"))

        print("\n🎉 Processo concluído com sucesso!\n")

    except RuntimeError as e:
        print(str(e))
        return 1

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())