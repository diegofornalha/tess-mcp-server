# Pacote de ferramentas para o CLI TESS
"""
Este pacote contém ferramentas e utilitários para o CLI TESS.
"""

import warnings

# Emitir aviso de depreciação ao importar este módulo
warnings.warn(
    "O módulo src.tools está depreciado. "
    "Use infrastructure.mcp_client para novas implementações.",
    DeprecationWarning,
    stacklevel=2
)
