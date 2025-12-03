from typing import List
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_cohere import ChatCohere
from langgraph.graph import StateGraph, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import SystemMessage
from ..database import VectorDataBase
from ..settings import Settings
from ..loggin import logger
from ..prompts import RAG_PROMPT, TITLE_PROMPT

class RAGState(MessagesState):
    context: str
    question: str

class LLMService:
    def __init__(self, store, saver):
        """
        store: instancia válida de PostgresStore (já com setup feito)
        checkpointer: instancia válida de PostgresSaver (já com setup feito)
        """
        self.store = store
        self.checkpointer = saver

        self.llm = ChatCohere(
            model="command-a-03-2025",
            cohere_api_key=Settings.LLM_KEY,
            temperature=0.7
        )
        self.vector_db = VectorDataBase()
        self.rag_prompt = RAG_PROMPT

        workflow = StateGraph(RAGState)
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_response)
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        self.graph = workflow.compile(
            store=self.store,
            checkpointer=self.checkpointer
        )

    def _retrieve_documents(self, state: RAGState) -> RAGState:
        last_message = state["messages"][-1]
        question = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

        results = self.vector_db.semantic_search(question, n_results=4)
        context = self._build_context(results)

        logger.info(context)

        return {
            "messages": state["messages"],
            "context": context,
            "question": question
        }

    def _generate_response(self, state: RAGState) -> RAGState:
        history_messages = state["messages"][-20:] if state.get("messages") else []

        prompt_messages = [
            SystemMessage(content=self.rag_prompt.format(
                context=state["context"],
                messages="",
            ))
        ]

        for m in history_messages:
            if isinstance(m, HumanMessage):
                prompt_messages.append(HumanMessage(content=m.content))
            elif isinstance(m, AIMessage):
                prompt_messages.append(AIMessage(content=m.content))

        prompt_messages.append(HumanMessage(content=state["question"]))

        logger.info(prompt_messages)

        response: AIMessage = self.llm.invoke(prompt_messages)

        return {
            "messages": state["messages"] + [response],
            "context": state["context"],
            "question": state["question"]
        }

    def _build_context(self, results: List[dict]) -> str:
        if not results:
            return "Nenhum documento relevante encontrado."

        parts = []

        for i, item in enumerate(results, 1):
            document_text = item["document"].replace("\n", " ")
            metadata = item.get("metadata", {})

            # Monta os metadados (todos os campos dinâmicos)
            if metadata:
                metadata_str = "\n".join(
                    f"• {key}: {value}" for key, value in metadata.items()
                )
            else:
                metadata_str = "Nenhum metadado disponível."

            doc_name = f'📄 Documento {i}' 
            parts.append(
                f"📄 {metadata.get('document_name', doc_name)})\n"
                f"{document_text}\n\n"
                f"🔎 Metadados:\n"
                f"{metadata_str}\n"
                f"{'-'*40}\n"
            )

        return "\n".join(parts)

    def generate_title(self, first_message: str) -> str:
        """Gera um título curto usando o modelo LLM e o TITLE_PROMPT."""
        try:
            prompt_messages = TITLE_PROMPT.format_messages(
                message=first_message
            )

            response = self.llm.invoke(prompt_messages)

            title = response.content.strip()

            if not title:
                return "Nova conversa"

            return title[:70]

        except Exception as e:
            logger.error(f"Erro ao gerar título: {e}")
            return "Nova conversa"

    def query(self, user_message: str, thread_id: str) -> str:
        user_msg_object = HumanMessage(content=user_message)

        result = self.graph.invoke(
            {
                "messages": [user_msg_object],
                "question": user_message
            },
            {
                "configurable": {"thread_id": thread_id}
            }
        )

        last_message = result["messages"][-1]
        return last_message.content
