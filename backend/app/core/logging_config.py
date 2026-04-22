"""
Configuración de logging para la aplicación.
"""
import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura el logging de la aplicación.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configurado
    """
    # Crear logger
    logger = logging.getLogger("flintrex")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Evitar duplicar handlers si se llama múltiples veces
    if logger.handlers:
        return logger

    # Formato detallado para desarrollo
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "flintrex") -> logging.Logger:
    """Obtiene un logger para un módulo específico."""
    return logging.getLogger(f"flintrex.{name}")


# Logger por defecto
default_logger = setup_logging()