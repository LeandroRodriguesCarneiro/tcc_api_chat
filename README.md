# tcc_api_chat

Esta API gerencia operações de inserção de documentos na base vetorial do projeto, integrando-se com a API de autenticação para garantir que apenas usuários autorizados possam adicionar dados. Também inicia e monitora pipelines Kafka, fornecendo identificadores e atualizando o status de cada documento enviado. A arquitetura foi pensada para lidar com múltiplos tipos de arquivo, como PDF, DOCX, TXT, HTML e Markdown, direcionando tarefas conforme sua complexidade.

## Tecnologias Utilizadas

- **Python** com o framework **FastAPI** para desenvolvimento rápido e eficiente da API REST.
- **Cohere** como a llm principal do chatbot.
- **PostgreSQL** como banco de dados relacional para armazenamento seguro e consistente dos status dos documentos.
- **Docker** para containerização, garantindo ambientes controlados e consistentes para desenvolvimento, teste e produção.
- **Docker Compose** Para gerenciar e integrar tudo para as fazes de desenvolvimento.

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
- Autenticação e autorização integrada.
- Envio de documentos de diversos formatos para a base vetorial.
- Recebimento de ID único para cada documento e consulta ao status do processamento.
- Pipeline escalável via Kafka, direcionando tarefas a workers especializados conforme o tipo de arquivo.

## Importância para o Projeto

Garante alta disponibilidade, escalabilidade e controle dos dados processados por IA. Sem autenticação e orquestração apropriada, o sistema estaria vulnerável, não garantindo conformidade nem governança dos documentos tratados.

## Desenvolvimento Futuro

Monitoramento avançado das pipelines.

Suporte a autenticação via OAuth/OpenID Connect.

Logging e rastreamento detalhados para auditoria.

## Contatos e Contribuições

Contribuições são bem-vindas! Para sugestões, melhorias ou relatórios de bug, abra uma issue ou envie um pull request.

Leandro Rodrigues Carneiro  

[GitHub](https://github.com/LeandroRodriguesCarneiro) | Contato: leandrorodrigues131531@gmail.com
