# Este modulo centraliza as mensagens de observabilidade do terminal.
# Ele nao executa nenhuma regra de negocio; apenas padroniza como as
# etapas iniciadas e finalizadas aparecem para quem roda o pipeline.


def log_etapa_inicio(nome_etapa: str, detalhes: str | None = None):
    """Imprime no terminal o inicio de uma etapa do fluxo."""
    mensagem = f"\n▶ Iniciando: {nome_etapa}"
    if detalhes:
        mensagem += f"\n   {detalhes}"
    print(mensagem)


def log_etapa_fim(nome_etapa: str, detalhes: str | None = None):
    """Imprime no terminal a conclusao de uma etapa do fluxo."""
    mensagem = f"✔ Finalizado: {nome_etapa}"
    if detalhes:
        mensagem += f"\n   {detalhes}"
    print(mensagem)
