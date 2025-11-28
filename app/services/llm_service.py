from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_cohere import ChatCohere
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.prompts import ChatPromptTemplate
import operator

from ..database import VectorDataBase
from ..settings import Settings
from ..loggin import logger

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str
    question: str

class LLMService:
    def __init__(self):

        self.llm = ChatCohere(
            model="command-a-03-2025",
            cohere_api_key=Settings.LLM_KEY
        )

        self.vector_db = VectorDataBase()

        self.rag_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Você é um assistente especializado que responde APENAS com base nos documentos fornecidos.

                CONTEXTO:
                {context}

                REGRAS:
                1. Responda SOMENTE com base no contexto acima.
                2. Se a resposta não estiver nos documentos, diga: "Não encontrei informações relevantes."
                3. Responda de forma objetiva e profissional.
                """
            ),
            ("human", "{question}")
        ])

        self.memory_saver = InMemorySaver()

        self.workflow = self._create_rag_workflow()

    def _create_rag_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_response)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile(checkpointer=self.memory_saver)

    def _retrieve_documents(self, state: AgentState) -> AgentState:
        question = state["question"]

        results = self.vector_db.semantic_search(question, n_results=4)

        context = self._build_context(results)

        return {
            "messages": state["messages"],
            "context": context,
            "question": question
        }

    def _generate_response(self, state: AgentState) -> AgentState:

        prompt_messages = self.rag_prompt.format_messages(
            context=state["context"],
            question=state["question"]
        )

        response = self.llm.invoke(prompt_messages)

        return {
            "messages": state["messages"] + [AIMessage(content=response.content)],
            "context": state["context"],
            "question": state["question"]
        }

    def _build_context(self, results: list) -> str:
        if not results:
            return "Nenhum documento relevante encontrado."

        parts = []
        for i, item in enumerate(results, 1):
            similarity = 1 - item["distance"]
            doc = item["document"].replace("\n", " ")

            parts.append(
                f"📄 Documento {i} (similaridade: {similarity:.2f})\n"
                f"{doc[:900]}...\n"
                f"Fonte: {item.get('metadata', {}).get('document_name', 'N/A')}\n"
            )

        return "\n".join(parts)

    def query(self, user_message: str, thread_id: str) -> str:
        config = {"configurable": {"thread_id": thread_id}}

        result = self.workflow.invoke(
            {
                "messages": [HumanMessage(content=user_message)],
                "question": user_message
            },
            config=config
        )

        return result["messages"][-1].content
