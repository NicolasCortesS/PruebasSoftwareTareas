"""Interface package initializer.

This file makes the `interface` directory a Python package so tests and
imports like `import interface.validations` work when running pytest from
the repository root.
"""

# Expose submodules via package if desired. Keep minimal to avoid import side-effects.
__all__ = []
