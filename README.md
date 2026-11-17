# forma.

Landing page para a forma., um espaço de trabalho minimalista para revisão de áudio lossless. O projeto separa a interface Next.js da API de captura de leads em FastAPI.

## Executar localmente

Requisitos: Python 3.11 ou superior, Node.js 18 ou superior e PostgreSQL.

1. Copie `backend/.env.example` para `backend/.env` e configure o PostgreSQL, as origens permitidas e a chave da Resend. O backend carrega esse arquivo usando um caminho relativo a `backend/core/config.py`, independentemente da pasta atual.
2. Na raiz do repositório, instale as dependências da API com `pip install -r backend/requirements.txt` e inicie-a com `uvicorn backend.main:app --reload`.
3. Copie `frontend/.env.local.example` para `frontend/.env.local`.
4. Na pasta `frontend/`, execute `npm install` e depois `npm run dev`.

A API cria a tabela de leads ao iniciar. O rate limit guarda chaves IP em memória e vale por processo; use um único worker ou substitua-o por uma solução compartilhada, como Redis, ao escalar. O backend usa o endereço direto do cliente ASGI e não confia em cabeçalhos de IP encaminhado por proxy.

## Estrutura

- `frontend/src/app`: rotas App Router, metadados, fontes e estilos globais.
- `frontend/src/components`: seções da landing page; os componentes de formulário, player, FAQ e hero usam estado no cliente.
- `frontend/src/lib/api-client.ts`: envio de leads pelo navegador. A URL pública da API é a única variável `NEXT_PUBLIC_`.
- `frontend/public/og-image.svg`: imagem de compartilhamento Open Graph da marca.
- `backend/api/v1`: endpoint de leads e envio de boas-vindas em tarefa de background.
- `backend/core`: configurações de ambiente, sessão SQLAlchemy assíncrona e limite de requisições.
- `backend/models` e `backend/schemas`: modelo SQLAlchemy e contrato Pydantic estrito.

## Segurança e privacidade

- CORS aceita somente as origens de `ALLOWED_ORIGINS`, separadas por vírgula, e libera `POST`/`OPTIONS` com `Content-Type`.
- O endpoint aplica uma janela móvel de até cinco requisições por minuto por IP, inclusive antes da validação do corpo. O campo honeypot preenchido recebe uma resposta de sucesso simulada sem persistência.
- Schemas Pydantic rejeitam campos desconhecidos. E-mails são validados e normalizados; consultas usam expressões SQLAlchemy parametrizadas.
- E-mails duplicados recebem uma resposta neutra. O endereço IP bruto não é persistido; somente seu SHA-256 é gravado para auditoria antiabuso.
- Logs mascaram endereços de e-mail e não registram payloads. Erros internos retornam mensagens genéricas.
- A API define cabeçalhos contra clickjacking, MIME sniffing, exposição de referrer e permissões desnecessárias. A chave Resend fica somente no ambiente do backend.
- `.gitignore` exclui ambientes virtuais, dependências, artefatos de build, logs e arquivos `.env`; os exemplos de ambiente permanecem versionáveis.

## Operação e limites da demonstração

- Configure PostgreSQL e uma chave Resend válida antes de capturar leads reais. Sem a chave, o envio de e-mail é ignorado.
- A criação automática de tabelas atende à versão inicial; adote migrações antes de evoluir o schema em produção.
- O rate limit é local ao processo. Para múltiplos workers, use um armazenamento compartilhado.
- O player cria um tom discreto via Web Audio API para demonstrar a interação; não reproduz os arquivos de áudio exibidos no mockup.
- Planos, nomes de estúdios, capacidades e afirmações comerciais refletem a especificação fornecida e devem ser confirmados antes do lançamento público.
