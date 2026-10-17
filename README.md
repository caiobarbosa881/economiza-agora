# economiza-agora

Projeto Django (com Django REST Framework) estruturado de forma modular.

## Stack

- Python 3.13
- Django 5.1
- Django REST Framework
- SimpleJWT (autenticação JWT)
- PostgreSQL (via Docker) com fallback para SQLite
- pytest + pytest-django

## Estrutura

```
.
├── manage.py
├── requirements.txt
├── pytest.ini
├── docker-compose.yml     # PostgreSQL para desenvolvimento
├── .env.example
├── src/
│   ├── config/            # configuração do projeto Django
│   │   ├── settings/      # base / development / production
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── apps/
│       ├── core/          # app base (health check, exceções comuns)
│       └── accounts/      # usuário customizado + autenticação (JWT)
└── tests/                 # espelha src/ (ver .opencode/skills/testing-guide.md)
```

## Autenticação (JWT)

O usuário é autenticado por **e-mail** (modelo customizado `accounts.User`).
Os tokens usam access + refresh com rotação e blacklist (SimpleJWT).

| Método | Rota | Acesso |
|---|---|---|
| POST | `/api/auth/register/` | público |
| POST | `/api/auth/login/` | público → `{access, refresh, user}` |
| POST | `/api/auth/refresh/` | público → `{access, refresh, user}` |
| POST | `/api/auth/logout/` | autenticado (blacklist do refresh) |
| GET/PATCH | `/api/auth/me/` | autenticado |
| POST | `/api/auth/password/change/` | autenticado |
| POST | `/api/auth/password/reset/` | público |
| POST | `/api/auth/password/reset/confirm/` | público |
| POST | `/api/auth/email/verify/` | público |
| POST | `/api/auth/email/resend/` | autenticado |

Requisições autenticadas usam o header `Authorization: Bearer <access>`.

Em desenvolvimento os e-mails (verificação e reset) são exibidos no
**console** (`EMAIL_BACKEND=console`). A permissão `accounts.IsEmailVerified`
está disponível para proteger endpoints que exijam e-mail confirmado.

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py runserver
```

Health check: `GET http://127.0.0.1:8000/api/health/`

## Banco de dados (Docker)

O projeto usa PostgreSQL em desenvolvimento via Docker Compose. Inicie o
Docker Desktop e suba o container:

```powershell
docker compose up -d db
python manage.py migrate
```

Se `POSTGRES_DB` não estiver definido no `.env`, o projeto usa SQLite
(`db.sqlite3`) automaticamente, sem precisar do container.

> **Porta:** o Postgres do Docker é publicado na porta `55433` do host
> (`POSTGRES_PORT`) para não conflitar com instalações nativas do
> PostgreSQL no Windows. Defina `POSTGRES_PORT` no `.env` se precisar
> alterar.

Para parar/remover o container:

```powershell
docker compose down          # mantém os dados
docker compose down -v       # remove o volume (apaga os dados)
```

## Testes

```powershell
pytest
```

Os testes usam o banco configurado no `.env` (PostgreSQL) ou SQLite como
fallback.

## Configuração

As configurações sensíveis são lidas de variáveis de ambiente (`.env`, não versionado).
Use `.env.example` como referência. Nunca grave segredos no código.
