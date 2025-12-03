from langchain_core.prompts import ChatPromptTemplate

TITLE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
    """
    Sua tarefa é analisar o texto da conversa fornecido abaixo e gerar um título curto, desciso e envolvente.
    O título deve resumir o tópico principal ou a intenção da primeira mensagem do usuário.
    Gere APENAS o título, sem qualquer texto introdutório, aspas ou pontuação final.

    TEXTO DA CONVERSA:
    {message}

    REGRAS:
    1. O título deve ter no máximo 7 palavras.
    2. Use o mesmo idioma do "TEXTO DA CONVERSA".
    3. Gere APENAS o título final.
    """),
    ("human", "Gere um título excelente.")
])
