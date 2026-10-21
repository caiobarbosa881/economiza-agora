---
name: security-standards
description: Diretrizes e boas práticas de segurança defensiva, autenticação e proteção de dados em Python.
---

# Diretrizes de Segurança do Código

Sempre siga estas práticas de segurança ao criar, revisar ou refatorar código no projeto:

1. **Gestão de Segredos e Credenciais:**
   - NUNCA grave chaves de API, senhas, tokens ou certificados hardcoded no código.
   - Utilize variáveis de ambiente gerenciadas via `pydantic-settings` ou `python-dotenv`.
   - Adicione `.env` e arquivos `.pem`/`.key` ao `.gitignore`.

2. **Sanitização e Validação de Entradas:**
   - Valide rigorosamente todos os schemas de entrada usando Pydantic.
   - Previna SQL Injection utilizando ORMs (ex: SQLAlchemy) ou queries parametrizadas. Nunca concatene strings em SQL.
   - Previna XSS e Injeção de Comandos ao manusear entradas de usuários ou comandos no terminal.

3. **Criptografia e Hashing:**
   - Armazene senhas utilizando algoritmos robustos de hash com salt (ex: `bcrypt` ou `argon2`).
   - Utilize HTTPS/TLS para tráfego em rede e criptografia para dados sensíveis em repouso.

4. **Controle de Acesso e Autenticação:**
   - Implemente verificação de tokens JWT com expiração adequada e rotação de chaves.
   - Aplique o princípio do menor privilégio (Least Privilege) em rotas, escopos e acesso a recursos.

5. **Tratamento de Erros e Logs:**
   - Não exponha stack traces ou detalhes internos do sistema para o cliente final.
   - Em logs de aplicação, sanitize informações sensíveis (PII, tokens, senhas).
