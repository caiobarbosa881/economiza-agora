"""Ponto de entrada de linha de comando do Django.

Insere o diretório ``src`` no ``sys.path`` para permitir a estrutura
modular (``config`` e ``apps`` fora da raiz).
"""

import os
import sys
from pathlib import Path


def main() -> None:
    """Executa tarefas administrativas do Django."""
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir / "src"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Verifique se ele está "
            "instalado e se o ambiente virtual está ativado."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
