#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exceções de domínio.

Este módulo contém as exceções de domínio utilizadas na aplicação.
"""


class DomainException(Exception):
    """Exceção base para todas as exceções de domínio."""
    pass


class ToolNotFoundError(DomainException):
    """Exceção lançada quando uma ferramenta não é encontrada."""
    pass


class ToolExecutionError(DomainException):
    """Exceção lançada quando ocorre um erro na execução de uma ferramenta."""
    pass


class ValidationError(DomainException):
    """Exceção lançada quando ocorre um erro de validação em uma entidade."""
    pass


class AuthenticationError(DomainException):
    """Exceção lançada quando ocorre um erro de autenticação."""
    pass


class ConfigurationError(DomainException):
    """Exceção lançada quando ocorre um erro de configuração."""
    pass 