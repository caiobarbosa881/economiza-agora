# economiza-agora

Projeto Django (com Django REST Framework) estruturado de forma modular.

## Stack

- Python 3.13
- Django 5.1
- Django REST Framework
- SQLite (desenvolvimento)
- pytest + pytest-django

## Estrutura

```
.
├── manage.py
├── requirements.txt
├── pytest.ini
├── .env.example
├── src/
│   ├── config/            # configuração do projeto Django
│   │   ├── settings/      # base / development / production
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── apps/
│       └── core/          # app base (health check, exceções comuns)
└── tests/                 # espelha src/ (ver .opencode/skills/testing-guide.md)
```

## Como rodar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Health check: `GET http://127.0.0.1:8000/api/health/`

## Testes

```powershell
pytest
```

## Configuração

As configurações sensíveis são lidas de variáveis de ambiente (`.env`, não versionado).
Use `.env.example` como referência. Nunca grave segredos no código.
