# Este modulo concentra configuracoes e resolucao de parametros do pipeline.
# Aqui ficam os defaults, o mapeamento de formatos de audio e a logica que
# decide qual modelo usar com base em CLI, `.env` e fallback do codigo.

import os
from pathlib import Path

AUDIO_EXTENSOES = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
AUDIO_CONTENT_TYPES = {
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
}
PROMPT_PADRAO = Path("prompts/qa_prompt.txt")
STT_MODEL_PADRAO = "pt-BR_NarrowbandModel"
LLM_MODEL_PADRAO = "meta-llama/llama-3-3-70b-instruct"


def listar_audios_disponiveis(diretorio: Path) -> list[Path]:
    """Lista arquivos de audio na pasta informada."""
    return sorted(
        arquivo for arquivo in diretorio.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() in AUDIO_EXTENSOES
    )


def detectar_content_type(caminho_audio: Path) -> str:
    """Resolve o content type do audio a partir da extensao."""
    extensao = caminho_audio.suffix.lower()
    content_type = AUDIO_CONTENT_TYPES.get(extensao)
    if not content_type:
        extensoes_suportadas = ", ".join(sorted(AUDIO_CONTENT_TYPES))
        raise RuntimeError(
            "❌ Formato de audio nao suportado: "
            f"{extensao or 'sem extensao'}. "
            f"Use um destes formatos: {extensoes_suportadas}"
        )
    return content_type


def resolver_stt_model(stt_model_cli: str | None) -> str:
    """Resolve o modelo do STT pela ordem CLI -> .env -> default."""
    if stt_model_cli:
        return stt_model_cli

    stt_model_env = os.getenv("STT_MODEL")
    if stt_model_env:
        return stt_model_env

    return STT_MODEL_PADRAO


def resolver_llm_model(llm_model_cli: str | None) -> str:
    """Resolve o modelo do watsonx pela ordem CLI -> .env -> default."""
    if llm_model_cli:
        return llm_model_cli

    llm_model_env = os.getenv("WATSONX_MODEL_ID")
    if llm_model_env:
        return llm_model_env

    return LLM_MODEL_PADRAO
