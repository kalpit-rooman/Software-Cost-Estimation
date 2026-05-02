from __future__ import annotations

import logging
import time
from collections import OrderedDict
from threading import Lock

import core.config as cfg
from schemas.request_response import (
    NormalizedUniversalPredictionRequest,
    RouteInferenceMetadata,
)

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - optional dependency in local dev
    redis = None  # type: ignore[assignment]

    class RedisError(Exception):
        pass


logger = logging.getLogger(__name__)


class IntakeContextStore:
    """
    Stores Stage-1 intake context for Stage-2 prediction assembly.

    Redis is used when REDIS_URL is configured and reachable. If Redis is not
    available, a process-local in-memory fallback is used to keep local/dev
    flows working.
    """

    def __init__(self, *, ttl_seconds: int, max_cached_intakes: int) -> None:
        self._ttl_seconds = max(1, int(ttl_seconds))
        self._max_cached_intakes = max(1, int(max_cached_intakes))

        self._metadata_cache: OrderedDict[str, tuple[float, RouteInferenceMetadata]] = OrderedDict()
        self._payload_cache: OrderedDict[str, tuple[float, NormalizedUniversalPredictionRequest]] = OrderedDict()
        self._lock = Lock()

        self._redis_client = self._build_redis_client()

    def _build_redis_client(self):
        redis_url = cfg.REDIS_URL.strip()
        if not redis_url:
            logger.info("REDIS_URL not configured. Using in-memory intake cache.")
            return None

        if redis is None:
            logger.warning("REDIS_URL is configured, but redis package is not installed.")
            return None

        try:
            client = redis.Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            client.ping()
            logger.info("Using Redis-backed intake cache.")
            return client
        except RedisError as exc:
            logger.warning("Failed to connect to Redis. Falling back to in-memory cache: %s", exc)
            return None

    def _metadata_key(self, intake_id: str) -> str:
        return f"intake:meta:{intake_id}"

    def _payload_key(self, intake_id: str) -> str:
        return f"intake:payload:{intake_id}"

    def cache_context(
        self,
        metadata: RouteInferenceMetadata,
        normalized_payload: NormalizedUniversalPredictionRequest,
    ) -> None:
        if self._redis_client is not None:
            try:
                pipe = self._redis_client.pipeline()
                pipe.setex(self._metadata_key(metadata.intake_id), self._ttl_seconds, metadata.model_dump_json())
                pipe.setex(self._payload_key(metadata.intake_id), self._ttl_seconds, normalized_payload.model_dump_json())
                pipe.execute()
                return
            except RedisError as exc:
                logger.warning("Redis write failed. Falling back to in-memory cache: %s", exc)

        self._cache_context_in_memory(metadata, normalized_payload)

    def get_context(
        self,
        intake_id: str,
    ) -> tuple[RouteInferenceMetadata, NormalizedUniversalPredictionRequest]:
        if self._redis_client is not None:
            try:
                redis_hit = self._get_context_from_redis(intake_id)
                if redis_hit is not None:
                    return redis_hit
            except RedisError as exc:
                logger.warning("Redis read failed. Falling back to in-memory cache: %s", exc)

        return self._get_context_from_in_memory(intake_id)

    def _get_context_from_redis(
        self,
        intake_id: str,
    ) -> tuple[RouteInferenceMetadata, NormalizedUniversalPredictionRequest] | None:
        metadata_json = self._redis_client.get(self._metadata_key(intake_id))
        payload_json = self._redis_client.get(self._payload_key(intake_id))

        if metadata_json is None or payload_json is None:
            return None

        try:
            metadata = RouteInferenceMetadata.model_validate_json(metadata_json)
            normalized_payload = NormalizedUniversalPredictionRequest.model_validate_json(payload_json)
        except Exception:
            # Corrupted or incompatible payloads should not remain in cache.
            self._redis_client.delete(self._metadata_key(intake_id), self._payload_key(intake_id))
            return None

        return metadata, normalized_payload

    def _cache_context_in_memory(
        self,
        metadata: RouteInferenceMetadata,
        normalized_payload: NormalizedUniversalPredictionRequest,
    ) -> None:
        now = time.time()
        with self._lock:
            self._prune_expired_locked(now)
            if len(self._metadata_cache) >= self._max_cached_intakes:
                oldest_key = next(iter(self._metadata_cache))
                self._metadata_cache.pop(oldest_key, None)
                self._payload_cache.pop(oldest_key, None)
            self._metadata_cache[metadata.intake_id] = (now, metadata)
            self._payload_cache[metadata.intake_id] = (now, normalized_payload)

    def _get_context_from_in_memory(
        self,
        intake_id: str,
    ) -> tuple[RouteInferenceMetadata, NormalizedUniversalPredictionRequest]:
        now = time.time()
        with self._lock:
            self._prune_expired_locked(now)

            metadata_entry = self._metadata_cache.get(intake_id)
            payload_entry = self._payload_cache.get(intake_id)
            if metadata_entry is None or payload_entry is None:
                raise KeyError(intake_id)

            self._metadata_cache.move_to_end(intake_id)
            self._payload_cache.move_to_end(intake_id)

            return metadata_entry[1], payload_entry[1]

    def _prune_expired_locked(self, now: float) -> None:
        expired_keys = [
            intake_id
            for intake_id, (stored_at, _) in self._metadata_cache.items()
            if now - stored_at >= self._ttl_seconds
        ]
        for intake_id in expired_keys:
            self._metadata_cache.pop(intake_id, None)
            self._payload_cache.pop(intake_id, None)


intake_context_store = IntakeContextStore(
    ttl_seconds=cfg.INTAKE_CACHE_TTL_SECONDS,
    max_cached_intakes=cfg.MAX_CACHED_INTAKES,
)
