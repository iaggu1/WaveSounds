# forma.

Landing page para a forma., um espaço de trabalho minimalista para revisão de áudio lossless. O navegador acessa frontend e API pela mesma origem; o Next.js encaminha `/api/v1/*` ao FastAPI na rede interna.

## Iniciar tudo com um comando

Requisitos: Docker Desktop com Docker Compose ativo.

O frontend usa Node.js 24 LTS em uma imagem Debian slim. A imagem instala as dependências com `npm ci` e o `package-lock.json` para reproduzir a árvore de pacotes.

No PowerShell, na raiz do projeto:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Abra **http://localhost:3000**. O Compose sobe PostgreSQL, FastAPI e Next.js; somente a porta `3000` é publicada no computador. O arquivo `.env` contém uma senha fictícia para uso local: troque-a antes de expor o serviço em qualquer rede.

Se já houver uma imagem antiga do frontend, reconstrua-a com `docker compose build --no-cache frontend` e inicie os serviços com `docker compose up`.

Para encerrar, pressione `Ctrl+C` e execute `docker compose down`. O volume do PostgreSQL é preservado.

O envio do formulário persiste o lead no PostgreSQL. Para enviar a mensagem de boas-vindas, configure `RESEND_API_KEY` e `EMAIL_FROM` no `.env`; sem uma chave, a aplicação mantém o cadastro e ignora o e-mail.

## Executar os serviços separadamente

Requisitos: Python 3.11 ou superior, Node.js 24 ou superior e PostgreSQL local.

1. Copie `backend/.env.example` para `backend/.env` e configure a conexão PostgreSQL, CORS e Resend.
2. Na raiz, instale a API com `pip install -r backend/requirements.txt` e execute `uvicorn backend.main:app --reload`.
3. Em outro terminal, entre em `frontend/`, copie `.env.local.example` para `.env.local`, execute `npm ci` e `npm run dev`.
4. Abra **http://localhost:3000**. O Next.js encaminha `/api/v1/*` para `http://127.0.0.1:8000` por padrão.

## Estrutura

- `frontend/src/app`: rotas App Router, metadados, fontes e estilos globais.
- `frontend/src/components`: seções da landing page; formulário, player, FAQ e hero usam estado no cliente.
- `frontend/src/components/ThemeProvider.tsx` e `ThemeToggle.tsx`: seletor entre modo claro e noturno, com preferência salva no navegador.
- `frontend/src/lib/api-client.ts`: envio de leads pela mesma origem do site.
- `frontend/proxy.ts`: remove qualquer `X-Forma-Client-IP` enviado pelo navegador para que o cliente não escolha o IP usado no rate limit.
- `backend/api/v1`: endpoint de leads e envio de boas-vindas em background.
- `backend/core`: configurações, sessão SQLAlchemy assíncrona e rate limit.
- `backend/models` e `backend/schemas`: modelo SQLAlchemy e contrato Pydantic estrito.
- `compose.yaml` e os Dockerfiles: ambiente local integrado com somente a porta web publicada.

## Segurança e operação

- CORS aceita apenas `ALLOWED_ORIGINS`; a chamada browser do setup integrado permanece na origem `localhost:3000`.
- O backend rejeita campos desconhecidos, valida e normaliza e-mails, mascara PII em logs e retorna erros internos genéricos.
- SQLAlchemy executa consultas parametrizadas. E-mails duplicados recebem resposta neutra. O IP não é persistido em texto claro; seu SHA-256 é usado para auditoria antiabuso.
- O rate limit permite cinco requisições por minuto por endereço. O backend só considera `X-Forma-Client-IP` quando a conexão vem de um IP listado em `TRUSTED_PROXY_IPS`. O Next.js não encaminha um IP informado pelo navegador; no Compose local, isso faz as chamadas compartilharem o IP do proxy até que a extração de IP seja configurada no ingress confiável. A API não publica sua porta no host.
- O frontend usa Next.js 16, React 19, ESLint 9 e `npm ci` com lockfile. O comando `npm run lint` executa ESLint diretamente, conforme o CLI atual do Next.js.
- O rate limit é mantido em memória por processo. Em produção com réplicas, use um armazenamento compartilhado e configure a cadeia de proxies confiáveis no ingress.
- Os headers da API protegem contra clickjacking, MIME sniffing, exposição desnecessária de referrer e permissões de browser não usadas.
- O tema claro/noturno pode ser alternado pela navegação e a escolha fica salva no `localStorage`.
- `.gitignore` exclui ambientes virtuais, dependências, artefatos de build, logs e arquivos `.env`, mantendo os exemplos de configuração versionáveis.

## Limites da demonstração

- A seção de fluxo lista WAV, MP3 e FLAC como formatos de envio, mas esta landing page não implementa upload de arquivos.
- O player gera um tom discreto via Web Audio API para demonstrar a interação; não reproduz os arquivos indicados no mockup.
- A tabela é criada ao iniciar a API. Adote migrações antes de evoluir o schema em produção.
- Planos, nomes de estúdios, capacidades e afirmações comerciais vieram da especificação e devem ser confirmados antes do lançamento público.

