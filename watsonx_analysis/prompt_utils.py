# Este modulo cuida apenas do prompt do LLM.
# Ele le o template em disco e monta o prompt final com a transcricao,
# mantendo a instrucao desacoplada da orquestracao principal em `app.py`.

from pathlib import Path


def carregar_template_prompt(caminho_prompt: Path) -> str:
    """Carrega o template do prompt a partir de um arquivo."""
    if not caminho_prompt.exists():
        raise RuntimeError(f"❌ Arquivo de prompt nao encontrado: {caminho_prompt}")

    try:
        return caminho_prompt.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"❌ Erro ao ler arquivo de prompt {caminho_prompt}: {e}") from e


def montar_prompt(template: str, transcricao: str) -> str:
    """Monta o prompt final substituindo o placeholder da transcricao."""
    marcador = "{{TRANSCRICAO}}"
    if marcador not in template:
        raise RuntimeError(
            f"❌ O arquivo de prompt deve conter o marcador {marcador}"
        )
    return template.replace(marcador, transcricao)
