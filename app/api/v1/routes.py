from fastapi import APIRouter, status

from .controllers.chat_controller import ChatController

router = APIRouter()

indec_document_controller= ChatController()

router.include_router(
    indec_document_controller.router,
    prefix='/Auth',
    tags=['V1', 'Chat']
    )

@router.get(
    '/health', 
    tags=['V1'],
    status_code=status.HTTP_200_OK,
    summary="Verificar se a API está online",
    description="Verificar se a API está online e operando",
    responses={
        200: {"description": "ok"}
    }
)
def health():
    return {"status": "ok"}