from fastapi import FastAPI, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.services.llm_service import LLMService
from app.settings import Settings
from app.database import Database
from app.loggin import logger, attach_db_handler

origins = [
    "http://localhost:3000",
    "https://front.tcc.com.br",
]

tags_metadata = [
    { "name": "Chat", "description": "Endpoints do chatbot" },
    { "name": "V1",   "description": "Versão 1" },
]

attach_db_handler(Database.get_instance().get_session)

@asynccontextmanager
async def lifespan(app: FastAPI):

    db = Database.get_instance()
    db_uri = db.database_url+'?sslmode=disable'

    with PostgresStore.from_conn_string(db_uri) as store, \
         PostgresSaver.from_conn_string(db_uri) as saver:

        store.setup()
        saver.setup()

        llm_service = LLMService(store=store, saver=saver)

        app.state.llm_service = llm_service

        yield

app = FastAPI(
    title="API do chatbot",
    description="API para um chatbot corporativo",
    version="alpha 0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import v1_router
app.include_router(v1_router, prefix="/api/v1")
