# Sandbox security boundary

Student code must never execute in the web/API process. A production runner must use a separately deployed, short-lived worker with a defense-in-depth sandbox such as gVisor, Firecracker, or an equivalent isolated runtime. The worker should run as an unprivileged user, use read-only images, deny network access by default, apply CPU/memory/process/output limits, expire jobs, and destroy the workspace after completion.

Runtime images must be reviewed and pinned by immutable digest. Do not mount the Docker socket, host filesystem, cloud credentials, or application secrets into a runner. Treat compiler and interpreter output as untrusted text. The API stores source and results with ownership checks and never accepts client-calculated scores or progress.

The repository does not claim ordinary Docker isolation is sufficient and does not include a local subprocess fallback.
