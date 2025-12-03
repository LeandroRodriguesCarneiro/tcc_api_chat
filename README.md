# API do Chatbot - TCC

A API responsável por receber perguntas dos usuários, consultar o banco vetorial (ChromaDB) e retornar respostas contextualizadas utilizando a LLM. Diferente das APIs de ingestão e autenticação, esta API não processa documentos, não realiza ingestão e não gerencia pipelines Kafka. Seu foco é exclusivamente fornecer uma interface rápida, segura e escalável para interação com o chatbot do projeto.

## Tecnologias Utilizadas

- **Python + FastAPI** desenvolvimento leve e eficiente de APIs REST.
- **Cohere** LLM utilizada para gerar respostas contextualizadas.
- **ChromaDB** banco vetorial que armazena embeddings usados para recuperar contexto relevante.
- **PostgreSQL** armazenamento de históricos de chat e metadados de conversações.
- **Docker & Docker Compose** containerização e orquestração dos serviços.
- **Autenticação via API externa** integração com a API de autenticação do projeto.

## Como Utilizar
-   OBS: precisa ter clonado e fazer build da imagem da API de autenticação antes de seguir: https://github.com/LeandroRodriguesCarneiro/tcc_api_autenticacao
-   OBS: precisa ter clonado e fazer build da imagem da API de ingestão antes de seguir: https://github.com/LeandroRodriguesCarneiro/tcc_api_ingestao_dados
1. **Gerar chave secreta:**

   - **No Linux:**
     
     - Base64, 32 bytes (256 bits):
     
       ```
       openssl rand -base64 32
       ```

     - Ou (sem OpenSSL):

       ```
       head -c 32 /dev/urandom | base64
       ```

   - **No Windows (PowerShell):**

     ```
     $bytes = New-Object byte[] 32
     [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
     [Convert]::ToBase64String($bytes)
     ```

2. Criar **.env.auth** com as seuguintes variaveis:
      ```
     SECRET_KEY=Colar aqui a chave gerada
     ALGORITHM=HS256
     ```

3. Criar **.env.chroma** com as seuguintes variaveis:
    ```
    CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthServerProvider
    CHROMA_SERVER_AUTH_CREDENTIALS=Gerar e colcar aqui outra chave
    CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token.TokenAuthServerProvider
     ```
4. **Alterar o docker compose**
    - **Alterar a imagem da API de autenticação**:
      - Para a imagem construida localmente ou utilizar a imagem do meu docker hub
      api_autenticacao:
    ```
    api_chat:
    image: docker push leandrorodriguescarneiro/tcc_api_chat:latest
    container_name: api_chat
    ports:
      - "8003:8000"
    environment:
      DB_HOST: postgres_tcc
      DB_PORT: 5432
      DB_USER: postgres
      DB_PSW: postgres
      DB_DATABASE: postgres
      KAFKA_BOOTSTRAP_SERVERS: kafka_tcc:9092
      URL_API_AUTH: http://api_autenticacao:8000
      DB_VECTOR_HOST: chromadb
      DB_VECTOR_PORT: 8000
      LLM_KEY: eCdfJ6C5VIGQEIj3WCQnNShJXiKcseSSjyiAIxtm
    env_file:
      - .env.chroma
    depends_on:
      postgres_tcc:
        condition: service_healthy
      api_autenticacao:
        condition: service_healthy
      kafka_tcc:
        condition: service_healthy
    networks:
      - test_net
      ```

  5. Rodar o comando:
       ```
        docker compose up -d
       ```

  6. Acesse a documentação interativa da API (Swagger UI) navegando para `http://localhost:8000/docs`.

## Principais Funcionalidades
- O usuário envia uma pergunta à API.
- A API verifica o token de autenticação com a API externa.
- A pergunta é transformada em embedding.
- O embedding é usado para buscar contexto no ChromaDB.
- A API envia pergunta + contexto para a LLM (Cohere).
- A resposta é retornada ao usuário.

## Importância no Projeto
A tcc_api_chat é o ponto de entrada para que usuários interajam com o sistema de IA.
- centraliza o fluxo de perguntas e respostas;
- une autenticação, histórico e contexto vetorial;
- garante respostas consistentes, alinhadas ao domínio e atualizadas com o banco vetorial;
- oferece uma interface unificada para integrações externas (website, chatbot corporativo, etc.).
- Sem ela, o projeto não teria um ponto de consumo confiável para o conteúdo ingerido na base vetorial.

## Desenvolvimento Futuro

Armazenar métricas de uso das conversas

Suporte a modelos adicionais (Gemini, GPT, Mistral)

Modo de resposta alternativo (somente contexto, sem LLM)

Filtros de segurança baseados em políticas da empresa

## Contatos e Contribuições

Contribuições são bem-vindas! Para sugestões, melhorias ou relatórios de bug, abra uma issue ou envie um pull request.

Leandro Rodrigues Carneiro  

[GitHub](https://github.com/LeandroRodriguesCarneiro) | Contato: leandrorodrigues131531@gmail.com
