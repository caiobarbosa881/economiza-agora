---
name: testing-guide
description: Diretrizes para criação e execução de testes automatizados com pytest.
---

# Padrões de Testes Automatizados

1. **Framework Base:** Utilize `pytest` como executor principal de testes.
2. **Organização:** Espelhe a estrutura de `src/` dentro do diretório `tests/` (ex: `src/services/user.py` -> `tests/services/test_user.py`).
3. **Fixtures:** Centralize setup de banco, mocks e dados reutilizáveis em `tests/conftest.py`.
4. **Uso de Mocks:** Isole chamadas externas (APIs, bancos de dados, serviços de terceiros) usando `unittest.mock` ou `pytest-mock`.
5. **Convenção de Nome:** Todo arquivo deve começar com `test_` e todas as funções de teste com `test_`.
