# Este modulo concentra as chamadas aos servicos externos da IBM.
# Ele encapsula a comunicacao com Speech to Text e watsonx para que
# `app.py` coordene o fluxo sem carregar detalhes de integracao.

from pathlib import Path

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference


def transcrever_audio_ibm(
    caminho_audio: Path,
    api_key: str,
    url: str,
    content_type: str,
    stt_model: str,
) -> str:
    """Transcreve audio usando IBM Speech-to-Text."""
    print(f"🎙️ Transcrevendo áudio: {caminho_audio}")

    try:
        authenticator = IAMAuthenticator(api_key)
        stt = SpeechToTextV1(authenticator=authenticator)
        stt.set_service_url(url)

        with open(caminho_audio, "rb") as audio:
            resultado = stt.recognize(
                audio=audio,
                content_type=content_type,
                model=stt_model
            ).get_result()

        texto = " ".join(
            item["alternatives"][0]["transcript"]
            for item in resultado["results"]
        )

        return texto.strip()

    except Exception as e:
        raise RuntimeError(f"❌ Erro ao transcrever áudio: {e}")


def analisar_ligacao(
    prompt: str,
    api_key: str,
    url: str,
    project_id: str,
    llm_model: str,
) -> str:
    """Envia o prompt para o watsonx e retorna a resposta textual bruta."""
    try:
        creds = Credentials(url=url, api_key=api_key)

        model = ModelInference(
            model_id=llm_model,
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
