"""
Rate limiting para proteger el servidor de abuse.
Implementación in-memory con sliding window.
"""
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from app.core.config import MAX_CONCURRENT_JOBS


@dataclass
class RateLimitConfig:
    """Configuración de rate limit para un endpoint."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int


# Límites por defecto
DEFAULT_RATE_LIMITS = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=500,
    requests_per_day=2000
)

# Límites estrictos para operaciones pesadas
HEAVY_RATE_LIMITS = RateLimitConfig(
    requests_per_minute=10,
    requests_per_hour=50,
    requests_per_day=200
)

# Límites por endpoint
ENDPOINT_RATE_LIMITS = {
    "upload": RateLimitConfig(requests_per_minute=30, requests_per_hour=200, requests_per_day=500),
    "merge": RateLimitConfig(requests_per_minute=10, requests_per_hour=50, requests_per_day=150),
    "harmonize": RateLimitConfig(requests_per_minute=10, requests_per_hour=50, requests_per_day=150),
    "detect_duplicates": RateLimitConfig(requests_per_minute=20, requests_per_hour=100, requests_per_day=300),
    "transform": RateLimitConfig(requests_per_minute=20, requests_per_hour=100, requests_per_day=300),
}


class SlidingWindowCounter:
    """Contador con ventana deslizante."""

    def __init__(self, window_seconds: int):
        self.window_seconds = window_seconds
        self.requests: list[float] = []

    def add_request(self) -> None:
        """Registra una request."""
        now = time.time()
        self.requests.append(now)
        self._cleanup(now)

    def _cleanup(self, now: float) -> None:
        """Elimina requests fuera de la ventana."""
        cutoff = now - self.window_seconds
        self.requests = [ts for ts in self.requests if ts > cutoff]

    def count(self) -> int:
        """Cuenta requests en la ventana actual."""
        self._cleanup(time.time())
        return len(self.requests)

    def is_allowed(self, limit: int) -> tuple[bool, int]:
        """
        Verifica si se permite una nueva request.

        Returns:
            (es_permitida, requests_restantes)
        """
        current = self.count()
        return current < limit, limit - current


class RateLimiter:
    """Rate limiter con múltiples ventanas temporales."""

    def __init__(self):
        self._buckets: dict[str, dict[str, SlidingWindowCounter]] = defaultdict(lambda: {
            "minute": SlidingWindowCounter(60),
            "hour": SlidingWindowCounter(3600),
            "day": SlidingWindowCounter(86400),
        })
        # Track jobs activos por usuario para limitar concurrencia
        self._active_jobs: dict[str, int] = defaultdict(int)

    def _get_bucket(self, key: str) -> dict[str, SlidingWindowCounter]:
        """Obtiene el bucket para una key (IP o user ID)."""
        return self._buckets[key]

    def check_rate_limit(
        self,
        key: str,
        config: Optional[RateLimitConfig] = None
    ) -> tuple[bool, str]:
        """
        Verifica si se permite una request.

        Args:
            key: Identificador (IP, user_id, etc.)
            config: Configuración de límites (None = usa DEFAULT)

        Returns:
            (es_permitido, mensaje)
        """
        if config is None:
            config = DEFAULT_RATE_LIMITS

        bucket = self._get_bucket(key)

        # Verificar minuto
        allowed, remaining = bucket["minute"].is_allowed(config.requests_per_minute)
        if not allowed:
            return False, f"Rate limit alcanzado: {remaining} requests restantes en el próximo minuto"

        # Verificar hora
        allowed, remaining = bucket["hour"].is_allowed(config.requests_per_hour)
        if not allowed:
            return False, f"Rate limit alcanzado: {remaining} requests restantes en la próxima hora"

        # Verificar día
        allowed, remaining = bucket["day"].is_allowed(config.requests_per_day)
        if not allowed:
            return False, f"Rate limit alcanzado: {remaining} requests restantes hoy"

        return True, "OK"

    def record_request(self, key: str) -> None:
        """Registra una request exitosas."""
        bucket = self._get_bucket(key)
        bucket["minute"].add_request()
        bucket["hour"].add_request()
        bucket["day"].add_request()

    def check_concurrency_limit(self, key: str, max_jobs: int = MAX_CONCURRENT_JOBS) -> tuple[bool, int]:
        """
        Verifica límite de jobs concurrentes.

        Returns:
            (es_permitido, slots_disponibles)
        """
        current = self._active_jobs[key]
        return current < max_jobs, max_jobs - current

    def increment_jobs(self, key: str) -> None:
        """Incrementa contador de jobs activos."""
        self._active_jobs[key] += 1

    def decrement_jobs(self, key: str) -> None:
        """Decrementa contador de jobs activos."""
        if self._active_jobs[key] > 0:
            self._active_jobs[key] -= 1

    def get_status(self, key: str) -> dict:
        """Obtiene el estado actual de límites para una key."""
        bucket = self._get_bucket(key)
        return {
            "requests_last_minute": bucket["minute"].count(),
            "requests_last_hour": bucket["hour"].count(),
            "requests_last_day": bucket["day"].count(),
            "active_jobs": self._active_jobs[key]
        }


# Instancia global
rate_limiter = RateLimiter()