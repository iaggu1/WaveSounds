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

Requisitos: Python 3.11 ou superior, Node.js 24 ou superior, PostgreSQL e Redis disponíveis localmente.

1. Copie `backend/.env.example` para `backend/.env` e configure as conexões PostgreSQL e Redis, CORS e Resend. Para iniciar um Redis local descartável, execute `docker run --rm -p 6379:6379 redis:7-alpine` em outro terminal.
2. Na raiz, instale a API com `pip install -r backend/requirements.txt`, aplique `alembic -c backend/alembic.ini upgrade head` e execute `uvicorn backend.main:app --reload`.
3. Em outro terminal, entre em `frontend/`, copie `.env.local.example` para `.env.local`, execute `npm ci` e `npm run dev`.
4. Abra **http://localhost:3000**. O Next.js encaminha `/api/v1/*` para `http://127.0.0.1:8000` por padrão.

## Validação automática

O GitHub Actions executa em cada pull request para `main` e em pushes para `main` e `feat/forma-landing-page`. O pipeline instala dependências do frontend pelo lockfile e executa ESLint, checagem TypeScript e build de produção. No backend, compila os módulos Python e aplica as migrações em um PostgreSQL descartável. O workflow usa permissões somente de leitura e fixa as GitHub Actions por SHA.

Para repetir as verificações do frontend localmente, execute na pasta `frontend/`:

```powershell
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

O pipeline não publica imagens nem faz deploy. A exigência de aprovação de checks antes do merge deve ser ativada nas regras de proteção da branch `main` do GitHub.

## Estrutura

- `frontend/src/app`: rotas App Router, metadados, fontes e estilos globais.
- `frontend/src/components`: seções da landing page; formulário, player, FAQ e hero usam estado no cliente.
- `frontend/src/components/ThemeProvider.tsx` e `ThemeToggle.tsx`: seletor entre modo claro e noturno, com preferência salva no navegador.
- `frontend/src/lib/api-client.ts`: envio de leads pela mesma origem do site.
- `frontend/src/proxy.ts`: sanitiza `X-Forma-Client-IP`, gera o nonce CSP para páginas e aplica os headers de segurança.
- `backend/api/v1`: endpoint de captura de leads e enfileiramento transacional de boas-vindas.
- `backend/core`: configurações, sessão SQLAlchemy assíncrona, cliente Redis e rate limit compartilhado.
- `backend/migrations`: migrações Alembic executadas antes de iniciar o backend.
- `backend/workers/email_worker.py`: worker PostgreSQL para processar e-mails de boas-vindas fora da requisição web.
- `backend/scripts`: comandos administrativos interativos para exclusão e limpeza por período, sem imprimir e-mails.
- `backend/models` e `backend/schemas`: modelo SQLAlchemy e contrato Pydantic estrito.
- `compose.yaml` e os Dockerfiles: ambiente local integrado com somente a porta web publicada.

## Segurança e operação

- CORS aceita apenas `ALLOWED_ORIGINS`; a chamada browser do setup integrado permanece na origem `localhost:3000`.
- O backend rejeita campos desconhecidos, valida e normaliza e-mails, mascara PII em logs e retorna erros internos genéricos.
- O cadastro do lead e a criação do envio de boas-vindas são confirmados na mesma transação PostgreSQL. O worker processa a fila com lease recuperável, backoff exponencial, limite de cinco tentativas e chave de idempotência do Resend. A fila guarda apenas referência ao lead e estado operacional; não duplica e-mail ou conteúdo, remove jobs concluídos e é removida em cascata quando o lead é apagado. Uma exclusão aguarda eventual envio já iniciado, limitado pelo timeout HTTP de oito segundos.
- SQLAlchemy executa consultas parametrizadas. E-mails duplicados recebem resposta neutra. O IP não é persistido no banco; somente uma chave derivada é mantida temporariamente no Redis para rate limit e expira em 60 segundos.
- O rate limit permite cinco requisições por minuto por endereço, usando contador Redis atômico e compartilhado entre processos. Se Redis falhar, o endpoint rejeita novos envios com HTTP 503 para não desativar silenciosamente a proteção. O Redis não publica porta no host pelo Compose e o health check da API verifica Redis e PostgreSQL. O Compose reserva IPs fixos para frontend (`172.28.0.2`), backend (`172.28.0.3`), banco (`172.28.0.4`), Redis (`172.28.0.5`) e worker de e-mail (`172.28.0.6`).
- O backend só considera `X-Forma-Client-IP` quando a conexão vem de um IP listado em `TRUSTED_PROXY_IPS`. No padrão local, o Next.js remove esse header e chamadas compartilham o IP do proxy. Para per-client rate limit em produção, ative `TRUSTED_INGRESS_CLIENT_IP=true` somente atrás de um ingress que remove qualquer header recebido do cliente e escreve o IP de conexão; restrinja a rede para que apenas esse ingress alcance o Next.js. A API não publica sua porta no host.
- O frontend usa Next.js 16, React 19, ESLint 10 e `npm ci` com lockfile. O comando `npm run lint` executa ESLint diretamente, conforme o CLI atual do Next.js.
- O frontend envia CSP com nonce por resposta, além de proteção contra MIME sniffing e clickjacking, política de referrer e permissões restritas. O nonce exige renderização dinâmica da página e desabilita cache compartilhado para HTML; os assets imutáveis são excluídos do proxy. Configure HSTS no ingress que termina TLS quando o domínio estiver servido somente por HTTPS.
- A auditoria npm em 18/11/2026 reportou 19 alertas altos pelos caminhos transitivos até `picomatch` (GHSA-fc5q-39xc-vjpf). O aviso atual não lista versão corrigida. A cadeia pertence às ferramentas de build/lint; reexecute `npm audit` após atualização upstream e antes de publicar.
- O Redis compartilhado mantém a janela de rate limit entre processos. Em produção, use Redis gerenciado com TLS/autenticação, monitore disponibilidade e configure a origem do IP somente por ingress confiável.
- Para atender uma solicitação confirmada de exclusão, verifique a identidade por um canal independente e execute `docker compose exec backend python -m backend.scripts.delete_lead`; o e-mail é digitado sem eco e a confirmação exige `EXCLUIR`.
- Para avaliar retenção, execute `docker compose exec backend python -m backend.scripts.purge_expired_leads --older-than-days <dias>` primeiro sem `--execute`. Após aprovar o prazo aplicável, repita com `--execute`. Não há exclusão automática nem prazo legal presumido; exclusões em backups seguem a política do operador.
- Os headers da API protegem contra clickjacking, MIME sniffing, exposição desnecessária de referrer e permissões de browser não usadas.
- O tema claro/noturno pode ser alternado pela navegação e a escolha fica salva no `localStorage`.
- Sem `RESEND_API_KEY`, os envios permanecem pendentes. Configure a chave no `.env` e recrie o worker com `docker compose up -d email-worker`; acompanhe o processamento com `docker compose logs -f email-worker`. Falhas temporárias são repetidas com espera crescente; após cinco falhas, o job fica em estado `failed` para análise operacional.
- `.gitignore` exclui ambientes virtuais, dependências, artefatos de build, logs e arquivos `.env`, mantendo os exemplos de configuração versionáveis.

## Limites da demonstração

- A seção de fluxo lista WAV, MP3 e FLAC como formatos de envio, mas esta landing page não implementa upload de arquivos.
- O player gera um tom discreto via Web Audio API para demonstrar a interação; não reproduz os arquivos indicados no mockup.
- O schema é gerenciado por migrações Alembic executadas antes da API. Dados existentes são mantidos; a migração remove apenas a coluna de hash de IP persistido.
- Planos, nomes de estúdios, capacidades e afirmações comerciais vieram da especificação e devem ser confirmados antes do lançamento público.

