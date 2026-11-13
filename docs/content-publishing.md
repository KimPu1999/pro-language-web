# Content publishing

Only organization owners and admins can publish in the current implementation. The server revalidates tenant membership, revision ownership, approval status, and publication idempotency at request time. Scheduled publishing requires a future worker and is not claimed as active.
