---
name: python-standards
description: Regras e padrões de código para desenvolvimento em Python no projeto.
---

# Diretrizes de Código Python

Sempre siga estes padrões ao gerar ou refatorar código Python:

1. **Tipagem Estática:** Utilize type hints em todas as assinaturas de funções e métodos (`def func(param: str) -> bool:`).
2. **Estilo e Formatação:** Respeite as diretrizes da PEP 8. Utilize nomes descritivos em snake_case para funções/variáveis e PascalCase para classes.
3. **Tratamento de Exceções:** Crie exceções customizadas herdando da classe base da aplicação em vez de disparar `Exception` genéricas.
4. **Gerenciamento de Dependências:** Mantenha o `requirements.txt` atualizado e utilize variáveis de ambiente (`pydantic-settings` ou `python-dotenv`) para configurações sensíveis.
5. **Docstrings e Documentação:** Escreva docstrings sintéticas no formato Google Style para módulos e funções públicas principais.