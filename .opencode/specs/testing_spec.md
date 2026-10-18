# 📋 Testing & Quality Specification — economiza-agora

Especificação de testes de software alinhada às melhores práticas de mercado,
ancorada na stack real do projeto: **Django 5.1 + DRF + SimpleJWT** (monolito
modular), **pytest + pytest-django**, PostgreSQL (Docker) com fallback SQLite.

> Este documento é a fonte de verdade da política de testes do repositório.
> Toda nova funcionalidade deve seguir o checklist da seção 11.

---

## 1. Princípios Fundamentais (Core Rules)

1. **Teste é especificação executável.** O teste documenta o comportamento
   esperado melhor que qualquer comentário. Escreva o teste primeiro quando a
   regra for nova ou ambígua (TDD é prática recomendada, não dogma).
2. **Princípio FIRST:** testes devem ser **F**ast, **I**ndependente,
   **R**epeatable, **S**elf-validating e **T**imely.
   - *Fast:* a suíte de unidade roda em segundos; nada de rede/banco real nela.
   - *Independente:* a ordem de execução nunca altera o resultado.
   - *Repeatable:* mesmo resultado em qualquer máquina, qualquer vez.
   - *Self-validating:* o teste termina em pass/fail booleano — nunca "imprimir
     e conferir".
   - *Timely:* escrito junto com o código, não como tarefa de "depois".
3. **Testar o que pode quebrar.** Priorize regras de negócio, validações e
   fronteiras sobre detalhes de implementação. Um teste que quebra a cada
   refatoração sem quebra real de comportamento é dívida.
4. **Cobertura não é qualidade.** 100% de cobertura com asserts fracos não
   protege nada. Cada teste deve afirmar um comportamento observável.
5. **Reproduzir bug = teste de regressão primeiro.** Antes de corrigir, escreva
   um teste que falha reproduzindo o bug; depois corrija (Red → Green).

---

## 2. Pirâmide de Testes para esta API

Adaptada de uma API Django/DRF monolítica (não microserviços):

| Camada | O que cobre | Ferramenta | Velocidade |
|---|---|---|---|
| **Unidade** | Serializers, validadores, utilitários, tokens, regras puras | pytest puro | ~ms |
| **Integração** | Models/managers, signals, queries, permissões, throttles | pytest-django + `django_db` | ~ms/s |
| **Feature (API)** | Endpoints DRF de ponta a ponta (request → serializer → view → response) | `rest_framework.test.APIClient` | ~s |
| **E2E / Smoke** | Jornada crítica real em ambiente de staging local (ex: registro → login → me) | `APIClient` contra servidor real ou `pytest` + requests | s/min |
| **Regressão** | Bug corrigido nunca volta | Qualquer camada acima | — |

**Proporção alvo:** maioria esmagadora em unidade/integração/feature (rápidas,
em transação); E2E restrito à jornada crítica (contagem de dígitos: < 10 testes
E2E para centenas de testes de camada).

### 2.1. Testes de Unidade

- **Objetivo:** lógica de negócio pura — serializers, validações de senha,
  geração/parse de tokens, regras de permissão lógica, utilitários.
- **Regra:** sem acesso a banco, disco ou rede. Se o teste precisa de
  `@pytest.mark.django_db`, ele **não** é de unidade — mova para integração.
- **Padrão de escrita:** Arrange → Act → Assert (AAA), uma única ação por teste.
- **Nomenclatura:** `test_[comportamento]_[condicao]_[resultado]` em PT-BR
  (ex.: `test_registro_email_duplicado_rejeitado`).

```python
def test_serializer_rejeita_senhas_diferentes() -> None:
    """password_confirm diferente de password deve falhar na validação."""
    data = {
        "email": "novo@example.com",
        "password": "SenhaForte123",
        "password_confirm": "OutraSenha123",
    }

    serializer = RegisterSerializer(data=data)

    assert serializer.is_valid() is False
    assert "password_confirm" in serializer.errors
```

### 2.2. Testes de Integração

- **Objetivo:** comportamento que depende do banco real — `User.objects.create_user`,
  managers customizados, constraints de unicidade, signals, `check_password`,
  fluxos de refresh/blacklist do SimpleJWT.
- **Técnica:** sempre com `@pytest.mark.django_db` (pytest-django roda em
  transação de rollback — rápido e isolado). Nunca usar mocks do ORM.
- **Banco:** o mesmo engine do ambiente alvo (PostgreSQL via Docker em CI;
  SQLite como fallback local). Diferenças de engine (ex: collation, `JSONField`)
  só aparecem rodando contra o Postgres de verdade — mantenha um job de CI com
  Postgres.

### 2.3. Testes de Feature (API)

- **Objetivo:** contrato HTTP completo de cada endpoint: status, corpo,
  headers, efeitos colaterais no banco e nos e-mails.
- **Técnica:** `APIClient` do DRF + `reverse("accounts:register")` (nunca URLs
  hardcoded). Verificar **efeitos** (usuário persistido, e-mail enviado), não
  apenas status code.
- **Matriz obrigatória por endpoint:**
  - caminho feliz (200/201 + payload correto);
  - entrada inválida (400 + campo de erro apontado);
  - não autenticado (401);
  - sem permissão / estado insuficiente (403 ou 400 conforme a regra);
  - recurso inexistente (404), quando aplicável;
  - efeitos colaterais (banco/e-mail) conferidos no caminho feliz.

```python
@pytest.mark.django_db
def test_registro_cria_usuario_e_envia_email(api_client, mailoutbox):
    """Registro válido cria o usuário não verificado e dispara 1 e-mail."""
    payload = {...}

    response = api_client.post(REGISTER_URL, payload)

    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=payload["email"])
    assert user.is_email_verified is False
    assert len(mailoutbox) == 1
```

### 2.4. Testes E2E / Smoke

- **Objetivo:** validar o empacotamento real (settings, URLs, middlewares,
  migrações) — não reescrever todos os testes de feature em E2E.
- **Escopo mínimo:** `GET /api/health/` + jornada crítica (registro → login →
  uso autenticado → logout).
- **Regra:** sem mocks de infraestrutura local; apenas serviços de terceiros
  pagos por uso (ex: gateway de SMS/e-mail transacional) podem ser simulados.

### 2.5. Testes de Regressão

- Todo bug corrigido ganha um teste que falhava antes do fix.
- Nomeie o teste pelo comportamento (não pelo número da issue), para sobreviver
  a refatorações.

---

## 3. Convenções de Código e Estrutura

1. **Espelhamento:** `src/apps/<app>/X.py` → `tests/apps/<app>/test_X.py`.
   Ex.: `src/apps/accounts/serializers.py` → `tests/apps/accounts/test_serializers.py`.
2. **Nomes:** arquivo `test_*.py`; função `test_<descrição_em_pt_br_snake_case>`;
   constantes de URL via `reverse()`; senhas/fixtures como constantes no topo
   (ex.: `PASSWORD = "SenhaForte123"`).
3. **Docstring obrigatória** em todo teste — descreve a **intenção** do
   comportamento, não a implementação.
4. **Type hints** nas assinaturas (`-> None`) e nas fixtures.
5. **Um comportamento por teste.** Cenários distintos = testes distintos (ou
   `@pytest.mark.parametrize`, nunca um teste gigante com 10 asserts de coisas
   diferentes).
6. **Parametrização** para variações do mesmo comportamento:

```python
@pytest.mark.django_db
@pytest.mark.parametrize("email", ["sem-arroba", "a@", "@b.com", ""])
def test_registro_email_invalido_rejeitado(api_client, email):
    """E-mails malformados devem falhar na validação."""
    ...
```

7. **Markers:** use `@pytest.mark.django_db` quando tocar o banco. Para testes
   lentos/E2E, marque com `@pytest.mark.e2e` e filtre na execução (seção 8).
8. **Imports:** sempre de `apps.*` (o `pytest.ini` já configura
   `pythonpath = src`). Não usar imports relativos entre apps.

---

## 4. Dados de Teste (Fixtures & Factories)

1. **Fixtures compartilhadas** ficam no `tests/conftest.py` mais próximo
   (raiz → `tests/`, por app → `tests/apps/<app>/conftest.py`).
   Padrão atual do projeto (manter):
   - `api_client` — cliente DRF limpo;
   - `user` / `verified_user` — estados mínimos de usuário;
   - `auth_client` / `verified_client` — cliente já autenticado;
   - `_reset_state` (autouse) — limpa cache de throttle e força e-mail locmem.
2. **Fixtures locais** (usadas por um único arquivo) vão no próprio módulo de
   teste, não na raiz — evita `conftest.py` monolítico.
3. **Factories (recomendado — a instalar):** à medida que o domínio crescer
   (metas, gastos, categorias…), adotar **factory-boy** com
   `factory.django.DjangoModelFactory` para criar objetos com defaults
   sobrescrevíveis. Evita "Object Mother" gigante e frágil.
   > Ferramenta extra: `factory-boy` — instalar em `requirements.txt` quando
   > houver > 1 model com criação recorrente em testes.
4. **Defaults válidos, overrides pontuais:** a fixture/factory fornece o menor
   estado válido; cada teste sobrescreve só o que testa.
5. **Nunca compartilhar estado mutável** entre testes (nada de cache de
   módulo, singletons preenchidos globalmente ou banco não limpo).

---

## 5. Isolamento e Determinismo

1. **Banco:** `@pytest.mark.django_db` em todo teste que persiste. O
   pytest-django envolve cada teste em transação com rollback — não use
   `TransactionTestCase`/`django_db(transaction=True)` sem necessidade real
   (testes que exigem conexão real entre transações, ex: NOTIFY).
2. **Cache:** limpo automaticamente pelo fixture autouse `_reset_state`
   (essencial para não vazar estado de throttle entre testes).
3. **E-mail:** sempre o backend `locmem` (já forçado no conftest); asserts
   via fixture `mailoutbox` — nunca um backend real.
4. **Tempo:** qualquer teste que dependa de `timezone.now()` numérico (tokens
   expirados, janelas de rate limit, "vencimento em X dias") deve congelar o
   tempo com `freezegun` — nunca `time.sleep`.
   > Ferramenta extra: `freezegun` — adicionar ao requirements quando surgir a
   > primeira regra temporal.
5. **Aleatoriedade:** se usar valores aleatórios, fixe a seed — o mesmo teste
   deve falhar da mesma forma em qualquer execução.
6. **Ordem:** a suíte deve passar com `pytest -p no:randomly` e com ordem
   aleatória; se falhar em uma ordem, há acoplamento oculto — corrija.

---

## 6. O que Mockar (e o que NÃO Mockar)

| Mockar (fronteira externa) | NUNCA mockar |
|---|---|
| HTTP de terceiros (APIs pagas, gateways) | ORM / banco (`django_db` resolve) |
| Webhooks/SMS/transações pagas por request | Serializers, views, URLs do próprio projeto |
| Sistemas fora do controle (ex: CAPTCHA) | `mailoutbox` (use a fixture real do Django) |
| | `reverse()` e cliente DRF |

- **Regra de bolso:** mock apenas o que é pago, lento, instável ou inacessível
  em CI. Se é do próprio projeto, teste de verdade.
- Ferramenta preferida: `unittest.mock` (stdlib) ou `pytest-mock` (fixture
  `mocker` — a instalar se preferir API de fixture).

---

## 7. Cobertura de Código

1. **Ferramenta:** `pytest-cov` (wrapper do `coverage.py`), já instalado e
   habilitado no `pytest.ini` (`addopts = --cov --cov-report=term-missing
   --cov-fail-under=85`). O `​.coveragerc` omite ruído (migrations, admin,
   settings, asgi/wsgi).

2. **Meta de qualidade (gate de CI):** ≥ **85% de cobertura de linhas** em
   `src/` (medido com as omissões do `.coveragerc`). Queda abaixo da meta
   quebra o pipeline (`--cov-fail-under`).

3. **Cobertura de branches** habilitada (`--cov-branch`) — detecta `if`s sem
   else testado.

4. **Cobertura como radar, não como meta final:** o relatório
   (`term-missing`) serve para **encontrar lacunas**, não para inflar números
   com asserts vazios. Revisar lacunas em todo milestone.

5. **Mutação testing (prática avançada, opcional):** `mutmut` introduz bugs
   sintáticos no código e verifica se os testes pegam. Rodar periodicamente
   (não em CI a cada commit — lento).
   > Ferramenta extra: `mutmut` — adotar quando a suíte estiver estável.

---

## 8. Execução dos Testes

Sem Makefile no projeto — os comandos reais são do pytest:

```powershell
# suíte completa (o que o CI roda)
pytest

# apenas um app
pytest tests/apps/accounts

# filtro por nome
pytest -k "register"

# apenas unidade (sem banco) — rápido para TDD
pytest -m "not django_db"

# um único arquivo/teste, com verbose
pytest tests/apps/accounts/test_register.py -v

# com relatório de cobertura
pytest --cov=apps --cov-report=term-missing

# E2E isolado (quando existirem markers e2e)
pytest -m e2e
```

1. **Ordem de execução no fluxo de trabalho:** unidade → integração → feature
   → E2E. No dia a dia, rode o escopo alterado (`pytest tests/apps/<app>`)
   e a suíte completa antes de commitar/pushar.
2. **Paralelismo (a instalar):** `pytest-xdist` → `pytest -n auto` quando a
   suíte passar de ~1 minuto. Requer Postgres real (não SQLite) e atenção a
   ports/throttles.
3. **`pytest.ini`** já resolve: `DJANGO_SETTINGS_MODULE`,
   `pythonpath = src`, `testpaths = tests`. Mantenha-o assim.

---

## 9. CI / Quality Gates

Pipeline mínimo (GitHub Actions, GitLab CI ou equivalente):

1. **Job único, passos em ordem rápida→lenta:**
   a) lint (ex.: `ruff` — recomendado adotar);
   b) `pytest -m "not django_db"` (unidade pura);
   c) `pytest` completo com `--cov` contra **PostgreSQL de serviço** no CI
      (serviço `postgres` no workflow — igual ao produção);
   d) gate de cobertura: falha o build abaixo de 80% em `src/apps/`.
2. **Merge bloqueado** se qualquer teste falhar ou cair a cobertura.
3. **Suíte deve ser determinística:** flaky test = bug de teste — corrija ou
   remova, nunca "retry" como solução permanente.
4. **Seed de dados de CI:** não usar fixtures que dependam de dados do
   ambiente; tudo criado no próprio teste.

---

## 10. Anti-padrões Proibidos

- ❌ `time.sleep(...)` para "esperar algo acontecer" — congele o tempo ou
  injete a dependência temporal.
- ❌ Teste que depende do resultado/estado de outro teste (ordem importa).
- ❌ Teste que só asserta `status_code == 200` sem validar corpo/efeitos.
- ❌ "Teste de cadeia": um teste cobrindo 10 regras distintas no mesmo método.
- ❌ Mockar o que é do próprio projeto (serializers, managers, views).
- ❌ URLs hardcoded (`"/api/auth/login/"`) em vez de `reverse()`.
- ❌ Acessar `User.objects.create()` direto em teste de unidade.
- ❌ Commitar teste desabilitado (`@pytest.mark.skip` sem data/justificativa).
- ❌ Dados sensíveis reais (senhas, tokens, CPFs) em fixtures — use
  valores sintéticos obviamente falsos.
- ❌ Testar detalhe de implementação (chamadas internas, ordem de imports).

---

## 11. Checklist de PR / Definition of Done (testes)

Antes de abrir/aceitar um PR, verificar:

- [ ] Toda rota/regra nova tem ao menos: caminho feliz + 1 caso negativo.
- [ ] Testes usam `reverse()` e fixtures existentes do `conftest.py`.
- [ ] Nenhum teste novo exige ordem de execução ou estado externo.
- [ ] `pytest` completo passa localmente (suíte verde).
- [ ] Cobertura de `src/apps/` não caiu (ideal: aumentou).
- [ ] Bugfix inclui teste de regressão que falhava antes.
- [ ] Nenhum `sleep`, skip injustificado ou mock de componente interno.
- [ ] Docstrings dos testes descrevem comportamento, não implementação.

---

## 12. Prompting de Testes (para Assistentes de IA)

Quando uma funcionalidade for solicitada via Spec-Driven Development, a IA
deve seguir este fluxo automaticamente:

1. **Extrair cenários** do pedido: happy path, validações (inválidos/vazios/
   limites), permissões (anônimo/não verificado/autor), efeitos colaterais
   (banco, e-mail).
2. **Escrever o teste falho primeiro** (Red) — unidade ou feature conforme a
   camada.
3. **Escrever o mínimo de código para passar** (Green).
4. **Refatorar** mantendo a suíte verde (Refactor), respeitando as regras
   arquiteturais (apps isolados, inversão via serializers/permissions).
5. **Cobrir persistência** com teste de integração (`django_db`) e
   **endpoint** com teste de feature (`APIClient`).
6. **Rodar a suíte completa** (`pytest`) antes de declarar a tarefa concluída.
7. Se o pedido envolver regra temporal, incluir `freezegun`; se envolver
   terceiro pago por uso, incluir mock documentado na fronteira.

---

## Ferramentas — resumo

| Ferramenta | Papel | Status no projeto |
|---|---|---|
| `pytest` + `pytest-django` | base da suíte | ✅ instalado |
| `rest_framework.test.APIClient` | testes de feature | ✅ em uso |
| `mailoutbox` (Django) | asserts de e-mail | ✅ em uso |
| `pytest-cov` | relatório/gate de cobertura | ✅ instalado e ativo no `pytest.ini` |
| `factory-boy` | factories de models | 🔧 a instalar (quando >1 model recorrente) |
| `freezegun` | congelamento de tempo | 🔧 a instalar (quando houver regra temporal) |
| `pytest-xdist` | paralelismo | 🔧 a instalar (quando suíte > 1 min) |
| `mutmut` | mutation testing | 🔧 opcional/avançado |
| `pytest-mock` | fixture `mocker` | 🔧 opcional (stdlib já cobre) |
