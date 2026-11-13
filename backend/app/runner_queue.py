import json, logging
from .config import settings
logger=logging.getLogger("codemaster.runner")
class ExecutionQueue:
    def enqueue(self, job_id: str) -> bool:
        if not settings.runner_enabled: logger.warning("Runner disabled; job=%s remains unavailable",job_id); return False
        try:
            import redis
            redis.Redis.from_url(settings.redis_url,decode_responses=True).rpush(settings.runner_queue_name,json.dumps({"job_id":job_id})); return True
        except Exception: logger.exception("Execution queue unavailable"); return False
queue=ExecutionQueue()
