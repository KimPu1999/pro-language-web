# Phase 02 — Docker Beginner-to-Professional Curriculum Plan

Status: `PLANNING ONLY`
Phase: `02`
Last verified against: Phase 01 live PostgreSQL audit and repository source
Implementation boundary: This document is a curriculum specification. It does not create lesson rows, change existing content, or publish anything.

## 1. Selection and evidence

Phase 01 identified `docker` as the first incomplete course by priority. The requested default course, Django, is therefore not selected for this phase.

| Field | Verified value |
|---|---|
| Course ID | `73b0e7ab-0035-4012-92a6-7fbfe6fdfa1f` |
| Canonical slug | `docker` |
| Current title | Docker & Containerization — From Zero to Professional DevOps |
| Proposed display title | Docker |
| Current status | Published course; quality audit `published_with_gaps` |
| Current category | DevOps & Cloud (`devops-cloud`) |
| Current technology | Docker (`docker`) |
| Current level field | `beginner` — this field is retained; the plan covers all four levels |
| Existing modules | 1 |
| Existing lessons | 8, all published |
| Existing quizzes | 8 |
| Existing exercises | 0 |
| Existing code examples | 8 |
| Published linked projects | 0 |
| Syntax references | 3 |
| Phase 01 gaps | Introduction only; missing intermediate/professional evidence; incomplete lesson sections; missing exercises; EN/MM review required |

The source seed intentionally keeps the remaining module names as a plan and creates only the authored first module. The plan below normalizes overlapping source topics so that existing lessons are reused instead of being duplicated under new module titles.

## 2. Preservation rules

The following records are inputs to Phase 03, not targets for replacement:

| Record | Existing identity | Required treatment |
|---|---|---|
| Course | `73b0e7ab-0035-4012-92a6-7fbfe6fdfa1f` / `docker` | Keep ID, slug, publication state, and existing valid metadata unless an approved metadata diff is reviewed |
| Module 1 | `ba1b4bf8-567d-4717-a252-ffb7ffbd855d` / order `1` | Keep module ID, order, and title; do not delete Introduction to Docker |
| Lesson 1 | `ffe6ecc8-7aec-4788-b7ee-8801076e4f9a` | Keep `01-what-docker-is-and-why-it-exists`, published version, progress, and attempts |
| Lesson 2 | `92d93967-c99c-4bec-b0ec-f538ab259809` | Keep `01-containers-vs-virtual-machines`, published version, progress, and attempts |
| Lesson 3 | `afaeffe0-f1ad-4fe8-bdec-6537c3d694ba` | Keep `01-install-docker-and-verify-the-engine`, published version, progress, and attempts |
| Lesson 4 | `1ef69940-6881-42d4-a366-db887ebd7f32` | Keep `01-docker-engine-architecture`, published version, progress, and attempts |
| Lesson 5 | `722ec478-53bc-41b2-8c66-989dc1a9c6cc` | Keep `01-docker-cli-fundamentals`, published version, progress, and attempts |
| Lesson 6 | `a27e3c93-8914-4e5d-8577-1a0854852755` | Keep `01-container-lifecycle`, published version, progress, and attempts |
| Lesson 7 | `a3d6719c-fb80-483c-95e8-534d915ddd8f` | Keep `01-write-a-secure-first-dockerfile`, published version, progress, and attempts |
| Lesson 8 | `9984c167-5861-4b35-9aea-cd6695d51349` | Keep `01-docker-build-run-and-clean-up`, published version, progress, and attempts |

No new module or lesson ID is assigned by this plan. Future records must be additive, ordered, draft/unpublished, and created only in Phase 03 after this plan is reviewed.

## 3. Course overview

- Full title: **Docker & Containerization — From Zero to Professional DevOps**.
- Short display title: **Docker**.
- Category: **DevOps & Cloud**.
- Technology: **Docker**, with Bash, YAML, Python, Django, Node.js, PHP/Laravel, registries, CI/CD, and Kubernetes interoperability where relevant.
- Target audience: learners who can use a terminal and want reproducible development, deployment, and operations skills; the course must remain usable by beginners while giving experienced developers production decision practice.
- Prerequisites: basic file and directory operations, a text editor, and willingness to use a disposable local Docker context. No production daemon access is required or permitted for learning activities.
- Learning objectives: explain image/container boundaries; build deterministic images; operate lifecycle, storage, and networks; compose multi-service systems; secure and observe workloads; publish and deploy through reviewed workflows; troubleshoot failures; and defend a production architecture.
- Expected outcomes: a learner can produce a reviewable Dockerfile and Compose project, explain its security and data boundaries, test it, document cleanup/recovery, and present an architecture decision record.
- Capstone expectation: an Enterprise Education Platform deployment design with Dockerfiles, Compose environments, CI/CD gates, secrets handling, observability, backup/recovery, and a migration boundary to Kubernetes. It is a learning project, not an enterprise certification or accreditation.
- Duration proposal: approximately **90 lessons × 45–75 minutes = 68–113 guided hours**, excluding project build time. The existing `duration_minutes=280` is not overwritten in Phase 02; Phase 03 must recalculate it from persisted lesson scope after review.

## 4. Content and publication states

The plan uses these states consistently:

- **Existing / published / review required**: current Module 1 records. They remain available, but Phase 03 must repair missing sections and add exercises through the review workflow rather than silently overwrite the published version.
- **Planned / not authored**: every lesson in Modules 2–12. A title or specification here is not a lesson body and must not be presented as learner-ready content.
- **Draft / unpublished**: the only permissible persisted state for new Phase 03 lesson records before review.
- **Reviewed**: a human reviewer has checked technical accuracy, EN/MM separation, safety, examples, assessments, and project mapping.
- **Published**: only after server-side validation and the existing authorization/review workflow confirm the version.

## 5. Consistent lesson blueprint for Phase 03

Every persisted lesson must use this order, with non-empty, technically specific content:

1. Introduction
2. Prerequisites
3. Learning objectives
4. Detailed theory
5. Core concepts
6. Syntax and usage
7. Practical code/examples (normally 3–5 progressive examples for coding-heavy lessons)
8. Expected output or observable result (actual output only after local verification)
9. Step-by-step explanation
10. Common mistakes
11. Best practices
12. Guided and independent exercises
13. Homework/evidence task
14. Quiz with answer explanations
15. Mini project where relevant
16. Summary
17. Further learning

Commands are instructional examples only. Phase 03 must never claim that a command was executed unless the result was actually captured in a safe, disposable local environment. No learner Docker command is executed inside the FastAPI process or on the Academy host.

## 6. Complete curriculum architecture and lesson specifications

The 12-module architecture consolidates the 40 source planning topics into distinct learning stages. Existing Module 1 is retained. The crosswalk at the end of this section shows where each source planning topic is covered.

### Module 01 — Introduction to Docker

Level: Beginner
Status: Existing, published, review required
Competency: explain containerization, verify a safe local engine, operate a disposable container, and build a first image without treating Docker as a security boundary by itself.

#### 01.1 What Docker Is and Why It Exists

- Difficulty and objectives: Beginner; define image, container, host, registry, and reproducibility; explain why packaging dependencies improves repeatability.
- Prerequisites and outline: none beyond basic files/terminal; application boundary, user-space dependencies, host kernel, reproducible artifacts, and trust assumptions.
- Syntax/API and example/output: `docker --version`, `docker run --rm hello-world`; plan a version check and an observed greeting, never inventing output.
- Exercise/homework and quiz: label the application/image/container boundary; write a one-page reproducibility note; quiz on image versus container and safety limits.
- References/projects/duration/locales: Docker Engine overview; Project 01 preparation; 35 minutes; EN/MM existing content, review required.

#### 01.2 Containers vs Virtual Machines

- Difficulty and objectives: Beginner; compare kernel sharing, guest OS, startup, resource use, and isolation assumptions; choose a boundary from a threat model.
- Prerequisites and outline: 01.1; image layers, guest OS, kernel, process isolation, compliance and workload trade-offs.
- Syntax/API and example/output: `docker run --rm alpine:3.20 uname -a` as a conceptual local example; plan a comparison table rather than claiming a VM result.
- Exercise/homework and quiz: compare a web service in a container and VM; write an isolation decision; quiz on why containers are not VMs.
- References/projects/duration/locales: Docker Engine concepts; Project 01; 35 minutes; EN/MM existing content, review required.

#### 01.3 Install Docker and Verify the Engine

- Difficulty and objectives: Beginner; distinguish client, engine, context, and permissions; verify a disposable local context without exposing a production daemon.
- Prerequisites and outline: 01.1–01.2; installation choices, `docker info`, contexts, daemon reachability, cleanup, and least privilege.
- Syntax/API and example/output: `docker info`, `docker context show`, `docker run --rm hello-world`; record actual local version/context evidence.
- Exercise/homework and quiz: create a local verification checklist; document a failed-daemon diagnosis; quiz on active contexts and daemon access.
- References/projects/duration/locales: Docker Engine install/post-install docs; Project 01; 35 minutes; EN/MM existing content, review required.

#### 01.4 Docker Engine Architecture

- Difficulty and objectives: Beginner; trace CLI → API → daemon → image/container and registry → image; identify local state mutations.
- Prerequisites and outline: 01.1–01.3; CLI, daemon, image store, runtime, registry, API boundary, provenance.
- Syntax/API and example/output: `docker build`, `docker create`, `docker start`, `docker inspect`; plan an architecture diagram and state transition evidence.
- Exercise/homework and quiz: draw the engine flow and mark trust boundaries; write which operations are read-only; quiz on daemon responsibility.
- References/projects/duration/locales: Docker Engine architecture/security; Project 01; 35 minutes; EN/MM existing content, review required.

#### 01.5 Docker CLI Fundamentals

- Difficulty and objectives: Beginner; inspect resources safely, use explicit names/labels, read logs, and avoid broad destructive cleanup.
- Prerequisites and outline: 01.3–01.4; `ps`, `images`, `inspect`, `logs`, `stats`, filters, labels, bounded cleanup.
- Syntax/API and example/output: `docker ps --all`, `docker images`, `docker inspect`, `docker logs`; expected result is a learner-collected inventory.
- Exercise/homework and quiz: make an evidence table for one disposable container; document a safe cleanup command; quiz on inspect before delete.
- References/projects/duration/locales: Docker CLI reference; Project 01; 35 minutes; EN/MM existing content, review required.

#### 01.6 Container Lifecycle

- Difficulty and objectives: Beginner; explain created/running/stopped/removed states and the difference between restart policy and health.
- Prerequisites and outline: 01.4–01.5; `run`, `create`, `start`, `stop`, `restart`, `rm`, exit codes, cleanup.
- Syntax/API and example/output: `docker run -d --name web-demo -p 8080:80 nginx:1.27`; output plan records status/logs and cleanup evidence.
- Exercise/homework and quiz: capture state changes for a disposable service; write a recovery note; quiz on stop versus remove.
- References/projects/duration/locales: Docker containers and lifecycle docs; Project 01; 35 minutes; EN/MM existing content, review required.

#### 01.7 Write a Secure First Dockerfile

- Difficulty and objectives: Beginner; identify base image, context, command, user, and port; avoid secrets, unnecessary packages, and root runtime.
- Prerequisites and outline: 01.1–01.6; `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `USER`, `EXPOSE`, `CMD`, context boundaries.
- Syntax/API and example/output: a small static service Dockerfile; output plan compares build warnings and a non-root runtime check after local verification.
- Exercise/homework and quiz: repair an insecure Dockerfile; write a Dockerfile review checklist; quiz on `COPY` context and `USER`.
- References/projects/duration/locales: Dockerfile reference and build best practices; Project 01; 45 minutes; EN/MM existing content, review required.

#### 01.8 Docker Build, Run, and Clean Up

- Difficulty and objectives: Beginner; connect build context, tag, run, port mapping, logs, and cleanup into a reproducible lab.
- Prerequisites and outline: 01.5–01.7; build/run sequence, tags, bounded ports, logs, stop/remove, image cleanup decision.
- Syntax/API and example/output: `docker build -t`, `docker run`, `docker logs`, `docker stop`, `docker rm`; output must be captured locally.
- Exercise/homework and quiz: build the Project 01 skeleton; submit commands, output, security checklist, and cleanup proof; quiz on tag versus digest.
- References/projects/duration/locales: Docker build best practices; Project 01; 45 minutes; EN/MM existing content, review required.

### Module 02 — Images, Layers, Dockerfiles, and BuildKit

Level: Beginner → Intermediate
Status: Planned, not authored
Competency: build small, reproducible, inspectable images and explain cache, layers, contexts, multi-stage output, and build policy.

#### 02.1 Image Names, Tags, Digests, and Immutability

- Difficulty and objectives: Beginner; distinguish repository, tag, digest, and mutable aliases; select a pinning policy.
- Prerequisites and outline: Module 1; image identity, tags, digests, provenance, pull policy, rollback references.
- Syntax/API and example/output: `docker image inspect`, `docker image ls`, `docker pull`; compare tag and digest evidence without claiming a live registry result.
- Exercise/homework and quiz: write a tagging/release policy; quiz on why a tag is not immutable; Project 02 image policy.
- References/projects/duration/locales: Docker image/reference docs; Project 02; 50 minutes; EN/MM planned, separate translations required.

#### 02.2 Layers, Cache, and Build Context

- Difficulty and objectives: Intermediate; explain layer invalidation and context size; reorganize a build for safe cache reuse.
- Prerequisites and outline: 02.1; instruction ordering, `.dockerignore`, context leakage, cache keys, deterministic inputs.
- Syntax/API and example/output: `docker build --progress=plain`; compare planned cache-hit/miss evidence after local execution.
- Exercise/homework and quiz: minimize a deliberately large context; submit a cache reasoning note; quiz on invalidation boundaries.
- References/projects/duration/locales: Docker build overview/best practices; Project 02; 55 minutes; EN/MM planned.

#### 02.3 Dockerfile Instructions and Build Checks

- Difficulty and objectives: Intermediate; choose `COPY`/`ADD`, `RUN`, `ARG`, `ENV`, `ENTRYPOINT`, `CMD`, `HEALTHCHECK`, and labels appropriately.
- Prerequisites and outline: 01.7–02.2; instruction semantics, shell/exec form, metadata, build checks, failure behavior.
- Syntax/API and example/output: Dockerfile variants for a web service; output plan checks image config and startup contract.
- Exercise/homework and quiz: fix a Dockerfile with incorrect command semantics; quiz on `CMD` versus `ENTRYPOINT`.
- References/projects/duration/locales: Dockerfile reference; Project 02; 60 minutes; EN/MM planned.

#### 02.4 Multi-Stage Builds

- Difficulty and objectives: Intermediate; separate build and runtime stages; copy only required artifacts; explain image-size and attack-surface trade-offs.
- Prerequisites and outline: 02.2–02.3; named stages, compiler dependencies, runtime files, artifact boundaries.
- Syntax/API and example/output: `FROM ... AS builder`, `COPY --from=builder`; output plan verifies final stage contents locally.
- Exercise/homework and quiz: convert a single-stage image into multi-stage; quiz on why build tools should not remain in runtime.
- References/projects/duration/locales: Docker multi-stage/build best practices; Project 02; 60 minutes; EN/MM planned.

#### 02.5 BuildKit, Secrets, and Cache Mounts

- Difficulty and objectives: Advanced; describe BuildKit features, avoid secret persistence, and use cache mounts without confusing cache with durable data.
- Prerequisites and outline: 02.2–02.4; BuildKit builder, secret mounts, cache mounts, provenance, reproducibility.
- Syntax/API and example/output: `RUN --mount=type=secret` and `RUN --mount=type=cache`; output plan verifies secret absence from image history.
- Exercise/homework and quiz: migrate a token-consuming build to a secret mount; quiz on why `ARG` is not secret storage.
- References/projects/duration/locales: Docker build secrets/cache docs; Project 03; 70 minutes; EN/MM planned.

#### 02.6 Image Metadata, SBOM, and Provenance

- Difficulty and objectives: Advanced; identify labels, source revision, SBOM, attestations, and provenance evidence; define release evidence.
- Prerequisites and outline: 02.1–02.5; metadata, artifact identity, SBOM, provenance, review gates.
- Syntax/API and example/output: plan `docker inspect` and builder attestation inspection; no fabricated scan output.
- Exercise/homework and quiz: design an evidence bundle for one image; quiz on provenance versus vulnerability result.
- References/projects/duration/locales: Docker build attestations and image docs; Project 03; 60 minutes; EN/MM planned.

#### 02.7 Reproducible and Portable Builds

- Difficulty and objectives: Advanced; pin dependencies, control platform assumptions, and document architecture differences.
- Prerequisites and outline: 02.1–02.6; lockfiles, base-image updates, multi-platform builds, timestamps, deterministic inputs.
- Syntax/API and example/output: plan `docker buildx build --platform`; output is a locally recorded manifest/evidence set.
- Exercise/homework and quiz: write a reproducibility checklist for amd64/arm64; Project 04 architecture note.
- References/projects/duration/locales: Docker multi-platform/build docs; Project 04; 70 minutes; EN/MM planned.

### Module 03 — Runtime, Configuration, Storage, and Data

Level: Intermediate
Status: Planned, not authored
Competency: run applications with explicit configuration, persistent storage, health signals, and data lifecycle controls.

#### 03.1 Environment Variables and Configuration Boundaries

- Difficulty and objectives: Intermediate; separate build-time and runtime configuration; prevent secrets in images and logs.
- Prerequisites and outline: Module 2; `ARG`/`ENV`, env files, precedence, defaults, validation, secret boundary.
- Syntax/API and example/output: `docker run --env`, Compose interpolation; output plan shows redacted configuration checks.
- Exercise/homework and quiz: create a configuration contract; quiz on build versus runtime values.
- References/projects/duration/locales: Docker environment/config docs; Projects 02–03; 50 minutes; EN/MM planned.

#### 03.2 Volumes and Persistent Data

- Difficulty and objectives: Intermediate; distinguish writable layer, named volume, bind mount, and external storage; design backup ownership.
- Prerequisites and outline: 03.1; volume lifecycle, permissions, initialization, backup/restore boundaries.
- Syntax/API and example/output: `docker volume create`, `docker run --mount`; output plan verifies data survives container replacement.
- Exercise/homework and quiz: document a volume ownership policy; quiz on why deleting a container need not delete a volume.
- References/projects/duration/locales: Docker volumes docs; Project 02; 60 minutes; EN/MM planned.

#### 03.3 Bind Mounts, tmpfs, and Development Loops

- Difficulty and objectives: Intermediate; use bind mounts only with explicit scope; choose tmpfs for ephemeral sensitive data where appropriate.
- Prerequisites and outline: 03.2; host path trust, read-only mounts, file ownership, platform differences.
- Syntax/API and example/output: `--mount type=bind,readonly` and `type=tmpfs`; output plan records access and cleanup behavior.
- Exercise/homework and quiz: harden a development mount; quiz on host filesystem exposure.
- References/projects/duration/locales: Docker storage docs; Project 02; 55 minutes; EN/MM planned.

#### 03.4 Healthchecks, Restart Policy, and Startup Contracts

- Difficulty and objectives: Intermediate; distinguish process liveness, readiness, and health; choose bounded restart behavior.
- Prerequisites and outline: 03.1–03.3; `HEALTHCHECK`, exit code, retry interval, dependency readiness, backoff.
- Syntax/API and example/output: Dockerfile healthcheck and Compose `healthcheck`; output plan compares healthy/unhealthy evidence.
- Exercise/homework and quiz: define a health contract for a web service; quiz on restart policy versus readiness.
- References/projects/duration/locales: Docker container lifecycle docs; Projects 02–03; 60 minutes; EN/MM planned.

#### 03.5 Resource Constraints and Runtime Isolation

- Difficulty and objectives: Advanced; bound CPU, memory, PIDs, and file descriptors conceptually; explain noisy-neighbor risk.
- Prerequisites and outline: 03.4; resource limits, OOM behavior, cgroups, capability boundaries, observability.
- Syntax/API and example/output: `--memory`, `--cpus`, `--pids-limit`; output plan records limit configuration, not fabricated timings.
- Exercise/homework and quiz: write a resource budget; quiz on why limits are reliability and security controls.
- References/projects/duration/locales: Docker resource constraints/security docs; Project 04; 70 minutes; EN/MM planned.

#### 03.6 Logs, Exit Codes, and Graceful Shutdown

- Difficulty and objectives: Intermediate; make logs useful, preserve exit status, and handle SIGTERM/timeout behavior.
- Prerequisites and outline: 03.4–03.5; stdout/stderr, log drivers, signal forwarding, graceful shutdown, bounded retries.
- Syntax/API and example/output: `docker logs`, `docker wait`, `docker stop --time`; output plan captures an actual local shutdown trace in Phase 03.
- Exercise/homework and quiz: repair a service that ignores termination; quiz on why logs are not a database.
- References/projects/duration/locales: Docker logs/containers docs; Project 03; 60 minutes; EN/MM planned.

#### 03.7 Backup, Restore, and Data Migration

- Difficulty and objectives: Professional; define RPO/RTO, backup scope, restore verification, and migration rollback.
- Prerequisites and outline: 03.2–03.6; logical/physical backup, consistency, encryption, retention, restore drills.
- Syntax/API and example/output: plan volume/database backup commands with a disposable dataset; output is a verified restore record.
- Exercise/homework and quiz: create a recovery runbook; Project 04 backup drill; quiz on backup existence versus restore evidence.
- References/projects/duration/locales: Docker storage and backup guidance; Project 04; 75 minutes; EN/MM planned.

### Module 04 — Networking and Docker Compose

Level: Intermediate
Status: Planned, not authored
Competency: design explicit service networks and Compose applications with clear ports, dependencies, storage, and lifecycle.

#### 04.1 Container Networking Fundamentals

- Difficulty and objectives: Intermediate; explain network namespace, bridge, service discovery, published ports, and host reachability.
- Prerequisites and outline: Modules 1–3; internal versus published ports, bridge networks, DNS names, trust zones.
- Syntax/API and example/output: `docker network create`, `docker network inspect`; output plan verifies only intended paths.
- Exercise/homework and quiz: draw a two-service network boundary; quiz on container port versus host published port.
- References/projects/duration/locales: Docker networking docs; Project 02; 60 minutes; EN/MM planned.

#### 04.2 Custom Networks, DNS, and Service Discovery

- Difficulty and objectives: Intermediate; use named networks and service names instead of unstable container IPs.
- Prerequisites and outline: 04.1; aliases, network attachment, internal-only services, DNS failure diagnosis.
- Syntax/API and example/output: Compose service-to-service URL using service name; output plan records DNS and HTTP evidence.
- Exercise/homework and quiz: fix an IP-coupled application; quiz on why container IPs are not stable identifiers.
- References/projects/duration/locales: Docker network drivers and Compose docs; Project 02; 60 minutes; EN/MM planned.

#### 04.3 Port Publishing, Firewalls, and Exposure

- Difficulty and objectives: Advanced; distinguish `EXPOSE` from publishing; minimize host exposure and document firewall assumptions.
- Prerequisites and outline: 04.1–04.2; bind addresses, host firewall, reverse proxy boundary, public/private ports.
- Syntax/API and example/output: `-p 127.0.0.1:8080:80`; output plan confirms local-only binding.
- Exercise/homework and quiz: harden an overexposed Compose file; quiz on `EXPOSE` versus `ports`.
- References/projects/duration/locales: Docker port publishing/security docs; Project 03; 60 minutes; EN/MM planned.

#### 04.4 Compose File Structure and Profiles

- Difficulty and objectives: Intermediate; model services, networks, volumes, healthchecks, profiles, and project names in Compose.
- Prerequisites and outline: 04.1–04.3; YAML structure, interpolation, profiles, extension fields, override strategy.
- Syntax/API and example/output: `docker compose config`, `up`, `down`, `--profile`; output plan validates resolved configuration.
- Exercise/homework and quiz: create dev/test profiles; quiz on resolved configuration and project name isolation.
- References/projects/duration/locales: Docker Compose documentation; Projects 01–02; 60 minutes; EN/MM planned.

#### 04.5 Compose Dependencies and Readiness

- Difficulty and objectives: Intermediate; model startup order without treating dependency order as readiness; use healthchecks and retries.
- Prerequisites and outline: 04.4; `depends_on`, health conditions, migrations, idempotent initialization.
- Syntax/API and example/output: Compose `depends_on` plus healthcheck; output plan records one startup failure and recovery path.
- Exercise/homework and quiz: make an app tolerate a slow database; quiz on startup order versus readiness.
- References/projects/duration/locales: Docker Compose startup/dependency docs; Project 02; 65 minutes; EN/MM planned.

#### 04.6 Compose Secrets, Configs, and Environment Precedence

- Difficulty and objectives: Advanced; select secret/config mechanisms and reason about precedence without committing credentials.
- Prerequisites and outline: 03.1 and 04.4; `.env`, interpolation, secrets, configs, redaction, review boundaries.
- Syntax/API and example/output: Compose `secrets`, `configs`, `docker compose config`; output plan confirms no secret in rendered logs/artifacts.
- Exercise/homework and quiz: migrate a plaintext password; quiz on environment precedence and secret leakage.
- References/projects/duration/locales: Docker Compose environment/secrets docs; Project 03; 70 minutes; EN/MM planned.

#### 04.7 Compose for Testing and CI

- Difficulty and objectives: Professional; create isolated test services, deterministic fixtures, and teardown behavior.
- Prerequisites and outline: 04.4–04.6; test profile, ephemeral data, wait strategy, artifact collection, parallel jobs.
- Syntax/API and example/output: `docker compose run`, `up --abort-on-container-exit`, `down -v` in disposable CI only; output plan records test artifacts.
- Exercise/homework and quiz: design a CI Compose test environment; quiz on isolation and cleanup scope.
- References/projects/duration/locales: Docker Compose/CI docs; Project 03; 75 minutes; EN/MM planned.

#### 04.8 Compose Deployment Boundaries

- Difficulty and objectives: Advanced; identify what Compose solves and what requires orchestrator/cloud controls; document operational limits.
- Prerequisites and outline: 04.1–04.7; single-host assumptions, secrets, scaling, availability, backup, monitoring, migration.
- Syntax/API and example/output: plan a deployment decision record, not a live production deployment; output is an architecture review artifact.
- Exercise/homework and quiz: choose Compose versus orchestrator for three scenarios; quiz on single-host failure boundaries.
- References/projects/duration/locales: Docker Compose production guidance; Project 04; 70 minutes; EN/MM planned.

### Module 05 — Containerizing Real Applications

Level: Intermediate
Status: Planned, not authored
Competency: containerize common application stacks with safe build/runtime boundaries and testable local workflows.

#### 05.1 Python Application Images

- Difficulty and objectives: Intermediate; design a Python image with dependency pinning, non-root runtime, buffering, and health behavior.
- Prerequisites and outline: Modules 2–4; `pyproject.toml`/lockfile, virtualenv boundary, WSGI/ASGI process, static configuration.
- Syntax/API and example/output: multi-stage Python Dockerfile and Compose service; output plan verifies import, health, and graceful stop locally.
- Exercise/homework and quiz: containerize a small Python API; quiz on dependency and runtime stages; Project 02.
- References/projects/duration/locales: Docker build best practices; Project 02; 75 minutes; EN/MM planned.

#### 05.2 Django Application Images

- Difficulty and objectives: Intermediate; separate Django build, settings, static/media, database, and migration concerns.
- Prerequisites and outline: 05.1; WSGI/ASGI, `collectstatic`, migrations, trusted hosts, CSRF, PostgreSQL, secret settings.
- Syntax/API and example/output: Compose Django + PostgreSQL + reverse proxy plan; output must be a locally verified health/migration record.
- Exercise/homework and quiz: write a production settings checklist; quiz on migrations versus image build.
- References/projects/duration/locales: [Django official documentation](https://docs.djangoproject.com/en/stable/) and Docker Compose docs; Project 04; 80 minutes; EN/MM planned.

#### 05.3 Node.js and React Applications

- Difficulty and objectives: Intermediate; build frontend assets separately from the runtime server; control environment injection and static delivery.
- Prerequisites and outline: 05.1; package lock, build stage, static server, API URL boundary, source-map and secret risks.
- Syntax/API and example/output: multi-stage Node build with static server; output plan verifies asset route and no secret in bundle.
- Exercise/homework and quiz: fix a frontend image that leaks build-time credentials; quiz on build-time versus runtime configuration.
- References/projects/duration/locales: Docker multi-stage/build docs; Project 01; 70 minutes; EN/MM planned.

#### 05.4 PHP and Laravel Applications

- Difficulty and objectives: Intermediate; containerize PHP dependencies, web server/runtime, queues, storage, and database migrations.
- Prerequisites and outline: 05.1 and 03.2; Composer dependencies, PHP-FPM, queue worker, writable paths, secrets.
- Syntax/API and example/output: Compose web/worker/database plan; output plan verifies route, queue health, and cleanup.
- Exercise/homework and quiz: create a service boundary diagram; quiz on worker versus web process.
- References/projects/duration/locales: Docker Compose and language runtime docs; Project 02; 80 minutes; EN/MM planned.

#### 05.5 Database and Migration Workflows

- Difficulty and objectives: Intermediate; keep schema changes explicit, repeatable, and separate from image construction.
- Prerequisites and outline: 03.7, 04.5, 05.1–05.4; migration job, readiness, rollback, seed data, backup before destructive changes.
- Syntax/API and example/output: plan a one-off Compose migration service; output plan records migration status and rollback evidence.
- Exercise/homework and quiz: write a migration runbook; quiz on why database state is not baked into an image.
- References/projects/duration/locales: Docker Compose and database vendor docs; Projects 02–04; 75 minutes; EN/MM planned.

#### 05.6 Reverse Proxy, TLS, and Static Assets

- Difficulty and objectives: Advanced; place a reverse proxy at the boundary, route static assets, and document TLS termination.
- Prerequisites and outline: 04.3 and 05.1–05.5; proxy headers, HTTPS, certificates, trusted origins, cache headers.
- Syntax/API and example/output: Compose proxy/app topology; output plan checks redirect, health route, and redacted headers locally.
- Exercise/homework and quiz: review a proxy configuration for exposure and header mistakes; Project 04.
- References/projects/duration/locales: Docker networking/security docs; Project 04; 80 minutes; EN/MM planned.

#### 05.7 Background Jobs and Schedulers

- Difficulty and objectives: Advanced; separate worker responsibilities, idempotency, retries, scheduling, and observability.
- Prerequisites and outline: 05.1–05.6; queue, broker, worker, dead letter, retry budget, graceful shutdown.
- Syntax/API and example/output: Compose web/worker/broker topology; output plan observes a bounded job lifecycle.
- Exercise/homework and quiz: design an idempotent job; quiz on retrying non-idempotent work.
- References/projects/duration/locales: Docker Compose lifecycle docs; Project 04; 75 minutes; EN/MM planned.

#### 05.8 Application Image Review

- Difficulty and objectives: Professional; review image size, user, dependencies, ports, health, logs, data, and rollback evidence.
- Prerequisites and outline: Module 5; image review rubric, threat model, SBOM/provenance, test evidence, runbook.
- Syntax/API and example/output: `docker image inspect` and planned scan evidence; no unverified scan claim.
- Exercise/homework and quiz: conduct a peer review of one application image; quiz on release blockers; Project 03 gate.
- References/projects/duration/locales: Docker build/security docs; Projects 03–04; 75 minutes; EN/MM planned.

### Module 06 — Registries, Releases, and Supply Chain

Level: Advanced
Status: Planned, not authored
Competency: publish and consume images with identity, provenance, access control, and rollback discipline.

#### 06.1 Registry Concepts and Authentication

- Difficulty and objectives: Advanced; distinguish registry, repository, namespace, credential, and pull identity.
- Prerequisites and outline: 02.1 and 05.8; login boundaries, credential helpers, private repositories, least privilege.
- Syntax/API and example/output: `docker login`, `docker pull`, `docker push` only in a learner-owned registry; output plan redacts tokens.
- Exercise/homework and quiz: draft a registry access matrix; quiz on why credentials must not be in Dockerfiles.
- References/projects/duration/locales: Docker registry/security docs; Project 03; 60 minutes; EN/MM planned.

#### 06.2 Versioning, Promotion, and Rollback

- Difficulty and objectives: Advanced; define release tags, immutable references, promotion gates, and rollback criteria.
- Prerequisites and outline: 02.1, 02.7, 06.1; semantic intent, digests, environments, approval, rollback evidence.
- Syntax/API and example/output: release manifest with tag and digest; output plan is a reviewable promotion record.
- Exercise/homework and quiz: write a rollback plan for a failed image; Project 04 release milestone.
- References/projects/duration/locales: Docker image/release docs; Project 04; 65 minutes; EN/MM planned.

#### 06.3 Vulnerability Scanning and Triage

- Difficulty and objectives: Advanced; interpret scan findings, prioritize by exploitability/context, and avoid claiming that a scan proves safety.
- Prerequisites and outline: 02.6 and 06.2; CVE evidence, false positives, base image updates, exception ownership.
- Syntax/API and example/output: scan command selected during Phase 03 after provider approval; output must be captured, dated, and attributable.
- Exercise/homework and quiz: triage a sample report; quiz on vulnerability severity versus exploitability.
- References/projects/duration/locales: Docker build/security docs; Project 03; 70 minutes; EN/MM planned.

#### 06.4 SBOM, Attestations, and Provenance Gates

- Difficulty and objectives: Professional; connect build inputs, SBOM, provenance, signatures/attestations, and deployment policy.
- Prerequisites and outline: 02.6 and 06.3; artifact evidence, policy gate, retention, reviewability.
- Syntax/API and example/output: plan BuildKit provenance/SBOM evidence; no fabricated attestation identifiers.
- Exercise/homework and quiz: design a release evidence checklist; Project 04 CI gate; quiz on provenance claims.
- References/projects/duration/locales: Docker build attestations; Projects 03–04; 70 minutes; EN/MM planned.

#### 06.5 Base Image Selection and Update Policy

- Difficulty and objectives: Advanced; select supported minimal bases, monitor updates, and balance compatibility with attack surface.
- Prerequisites and outline: 02.4 and 06.3; OS packages, libc choice, patch cadence, vendor support, reproducibility.
- Syntax/API and example/output: compare two base image decision records; output plan states evidence rather than a universal “best” image.
- Exercise/homework and quiz: write a base-image exception request; quiz on minimal image trade-offs.
- References/projects/duration/locales: Docker build best practices; Project 03; 60 minutes; EN/MM planned.

#### 06.6 Supply-Chain Incident Response

- Difficulty and objectives: Professional; revoke/rotate credentials, quarantine an image, identify consumers, and recover safely.
- Prerequisites and outline: 06.1–06.5; blast radius, evidence preservation, replacement image, notification, post-incident review.
- Syntax/API and example/output: incident runbook with registry/API placeholders; output is a tabletop timeline, not a live incident claim.
- Exercise/homework and quiz: conduct a tabletop compromised-base-image response; Project 04 operations milestone.
- References/projects/duration/locales: Docker security docs; Project 04; 75 minutes; EN/MM planned.

### Module 07 — Docker Security and Hardening

Level: Advanced → Professional
Status: Planned, not authored
Competency: reduce build/runtime/daemon risk using least privilege, isolation, secret hygiene, and evidence-based controls.

#### 07.1 Docker Threat Model and Trust Boundaries

- Difficulty and objectives: Advanced; identify assets, actors, daemon boundary, image trust, host impact, and recovery assumptions.
- Prerequisites and outline: Modules 1–6; threat model, abuse cases, control mapping, residual risk.
- Syntax/API and example/output: architecture diagram and risk register; no exploit execution.
- Exercise/homework and quiz: threat-model a Compose education platform; quiz on Docker socket risk.
- References/projects/duration/locales: Docker Engine security; Project 04; 60 minutes; EN/MM planned.

#### 07.2 Non-Root Users, Capabilities, and Read-Only Filesystems

- Difficulty and objectives: Advanced; run as non-root, remove capabilities, and choose writable paths deliberately.
- Prerequisites and outline: 02.3, 03.2, 07.1; `USER`, capabilities, `--read-only`, tmpfs, file ownership.
- Syntax/API and example/output: runtime hardening checklist; output plan verifies effective user and writable paths locally.
- Exercise/homework and quiz: harden a service that assumes root; quiz on least privilege.
- References/projects/duration/locales: Docker security/rootless docs; Project 03; 70 minutes; EN/MM planned.

#### 07.3 Secrets and Credential Handling

- Difficulty and objectives: Advanced; keep secrets out of source, image layers, environment dumps, and logs.
- Prerequisites and outline: 03.1, 04.6, 06.1; secret injection, rotation, redaction, access scope, audit.
- Syntax/API and example/output: Compose secret design and BuildKit secret mount; output plan searches image history/logs for absence of secret values.
- Exercise/homework and quiz: replace a plaintext token flow; Project 03 security gate.
- References/projects/duration/locales: Docker build/Compose secrets docs; Project 03; 65 minutes; EN/MM planned.

#### 07.4 Rootless Docker and User Namespaces

- Difficulty and objectives: Advanced; explain rootless mode/user namespaces, compatibility constraints, and operational trade-offs.
- Prerequisites and outline: 07.2; daemon privileges, UID/GID mapping, volume permissions, network limitations.
- Syntax/API and example/output: plan a rootless verification checklist; output only after a learner-owned local environment is tested.
- Exercise/homework and quiz: assess rootless suitability for three workloads; quiz on host privilege reduction.
- References/projects/duration/locales: Docker rootless/user namespace docs; Project 04; 70 minutes; EN/MM planned.

#### 07.5 Daemon Socket and Remote Access Protection

- Difficulty and objectives: Professional; protect the Docker socket, avoid unsafe remote daemon exposure, and document admin boundaries.
- Prerequisites and outline: 07.1–07.4; socket authority, TLS, contexts, network exposure, operator roles.
- Syntax/API and example/output: inspect contexts and configuration without connecting to production; output is a threat-model review.
- Exercise/homework and quiz: review a CI runner that mounts `/var/run/docker.sock`; quiz on equivalent host control.
- References/projects/duration/locales: Docker security/daemon docs; Project 04; 65 minutes; EN/MM planned.

#### 07.6 Seccomp, AppArmor, and Isolation Profiles

- Difficulty and objectives: Professional; describe syscall and profile controls, defaults, exceptions, and testing evidence.
- Prerequisites and outline: 07.1–07.5; seccomp, AppArmor, namespaces, capabilities, compatibility and denial diagnosis.
- Syntax/API and example/output: profile review plan; output records a bounded denial and recovery process only when locally tested.
- Exercise/homework and quiz: map an application capability to a control; quiz on defense in depth.
- References/projects/duration/locales: Docker Engine security docs; Project 04; 75 minutes; EN/MM planned.

#### 07.7 Image and Runtime Policy Review

- Difficulty and objectives: Professional; turn security requirements into enforceable build/release/runtime checks.
- Prerequisites and outline: 06.3–07.6; policy-as-code concepts, exceptions, review ownership, evidence retention.
- Syntax/API and example/output: policy checklist for user, base, secrets, ports, capabilities, and provenance.
- Exercise/homework and quiz: reject or approve sample images with reasons; Project 04 security milestone.
- References/projects/duration/locales: Docker security/build docs; Project 04; 75 minutes; EN/MM planned.

#### 07.8 Security Incident Tabletop

- Difficulty and objectives: Professional; contain, investigate, rotate, rebuild, communicate, and verify after a container incident.
- Prerequisites and outline: 07.1–07.7; evidence, containment, recovery, lessons learned, residual risk.
- Syntax/API and example/output: tabletop timeline and evidence checklist; no live attack or credential use.
- Exercise/homework and quiz: produce an incident report with one control improvement; quiz on recovery verification.
- References/projects/duration/locales: Docker Engine security; Project 04; 75 minutes; EN/MM planned.

### Module 08 — Observability, Resources, Performance, and Recovery

Level: Advanced
Status: Planned, not authored
Competency: operate Docker workloads with measurable health, bounded resources, actionable logs, and tested recovery.

#### 08.1 Container Logs and Structured Events

- Difficulty and objectives: Advanced; design structured logs, correlation fields, redaction, retention, and failure evidence.
- Prerequisites and outline: 03.6, 07.1; stdout/stderr, driver choice, event stream, sensitive data.
- Syntax/API and example/output: `docker logs`, `docker events`; output plan captures a redacted local trace.
- Exercise/homework and quiz: turn free-form logs into an incident-friendly schema; Project 03.
- References/projects/duration/locales: Docker logs/events docs; Project 03; 60 minutes; EN/MM planned.

#### 08.2 Metrics, Health, and Runtime Signals

- Difficulty and objectives: Advanced; select service, container, host, and dependency signals; distinguish symptom from cause.
- Prerequisites and outline: 03.4–03.6; health, latency, saturation, errors, restart rate, dependency signals.
- Syntax/API and example/output: `docker stats` plus application health endpoint plan; output is a signal catalogue.
- Exercise/homework and quiz: define alert thresholds with rationale; quiz on healthcheck limitations.
- References/projects/duration/locales: Docker runtime metrics docs; Project 04; 60 minutes; EN/MM planned.

#### 08.3 CPU, Memory, PID, and IO Constraints

- Difficulty and objectives: Advanced; diagnose resource pressure and set limits without hiding application defects.
- Prerequisites and outline: 03.5 and 08.2; OOM, throttling, PID exhaustion, IO pressure, load profile.
- Syntax/API and example/output: bounded resource configuration; output plan compares baseline and constrained behavior after safe testing.
- Exercise/homework and quiz: create a resource incident runbook; Project 04.
- References/projects/duration/locales: Docker resource constraints; Project 04; 70 minutes; EN/MM planned.

#### 08.4 Performance Optimization and Build Cache

- Difficulty and objectives: Advanced; separate build performance, startup performance, request performance, and resource efficiency.
- Prerequisites and outline: 02.2, 02.4, 08.3; cache, layers, startup, dependency loading, measurement discipline.
- Syntax/API and example/output: plan repeatable build/run measurements; output must include environment and method.
- Exercise/homework and quiz: optimize a Dockerfile and explain the evidence; quiz on measurement versus guess.
- References/projects/duration/locales: Docker build best practices; Project 03; 70 minutes; EN/MM planned.

#### 08.5 Debugging Containers and Images

- Difficulty and objectives: Advanced; isolate build, startup, network, permission, dependency, and runtime failures.
- Prerequisites and outline: Modules 1–8; inspect, logs, shell access policy, minimal reproducer, rollback.
- Syntax/API and example/output: `docker inspect`, `docker logs`, `docker diff` where safe; output plan records first failing evidence.
- Exercise/homework and quiz: troubleshoot a deliberately broken service; Project 03.
- References/projects/duration/locales: Docker troubleshooting docs; Project 03; 75 minutes; EN/MM planned.

#### 08.6 Backup and Restore Drills

- Difficulty and objectives: Professional; test restore time, data integrity, permissions, and application consistency.
- Prerequisites and outline: 03.7, 04.7, 08.2; RPO/RTO, snapshot, logical backup, restore verification, audit trail.
- Syntax/API and example/output: disposable volume/database restore workflow; output is a timed evidence record only after actual testing.
- Exercise/homework and quiz: run a restore tabletop and identify an untested assumption; Project 04.
- References/projects/duration/locales: Docker storage/Compose docs; Project 04; 80 minutes; EN/MM planned.

#### 08.7 Upgrade, Rollback, and Compatibility

- Difficulty and objectives: Professional; plan image/base/Compose upgrades with compatibility checks and rollback triggers.
- Prerequisites and outline: 06.2, 06.5, 08.6; migration ordering, canary, backup, health, rollback.
- Syntax/API and example/output: release checklist with old/new image digests; output is a review artifact.
- Exercise/homework and quiz: write an upgrade plan for the Student Record System; quiz on rollback prerequisites.
- References/projects/duration/locales: Docker release/build docs; Project 04; 75 minutes; EN/MM planned.

#### 08.8 Operations Review

- Difficulty and objectives: Professional; conduct a complete operational review covering logs, metrics, limits, backups, security, and ownership.
- Prerequisites and outline: Module 8; SLO-style signals, runbook, on-call handoff, evidence and open risks.
- Syntax/API and example/output: no live command required; deliver an operations review packet.
- Exercise/homework and quiz: peer-review the packet; Project 04 gate; quiz on evidence quality.
- References/projects/duration/locales: Docker Engine docs; Project 04; 75 minutes; EN/MM planned.

### Module 09 — Production Architecture and Deployment

Level: Professional
Status: Planned, not authored
Competency: design a production-ready container platform with explicit availability, security, data, deployment, and ownership boundaries.

#### 09.1 Production Settings and Environment Separation

- Difficulty and objectives: Professional; separate development, test, staging, and production configuration and approvals.
- Prerequisites and outline: Modules 3–8; config contract, secret source, feature flags, environment drift.
- Syntax/API and example/output: environment matrix and Compose override policy; output is a reviewable configuration diff.
- Exercise/homework and quiz: identify environment leakage; Project 04.
- References/projects/duration/locales: Docker Compose environment docs; Project 04; 65 minutes; EN/MM planned.

#### 09.2 Reverse Proxy, TLS, and Certificate Lifecycle

- Difficulty and objectives: Professional; design TLS termination, renewal, headers, trust proxy settings, and failure behavior.
- Prerequisites and outline: 05.6 and 09.1; certificate ownership, renewal, HTTPS redirect, internal service boundaries.
- Syntax/API and example/output: proxy topology and certificate runbook; output is a local test plan, not a live certificate claim.
- Exercise/homework and quiz: review TLS boundary decisions; Project 04.
- References/projects/duration/locales: Docker networking/security docs; Project 04; 75 minutes; EN/MM planned.

#### 09.3 PostgreSQL and Durable Service Design

- Difficulty and objectives: Professional; connect database durability, backup, migrations, connection limits, and failure recovery.
- Prerequisites and outline: 03.2, 03.7, 05.5; connection pooling, readiness, migration ownership, backup encryption.
- Syntax/API and example/output: Compose database service and recovery runbook; output requires local disposable verification in Phase 03.
- Exercise/homework and quiz: design a database failure drill; Project 02 and 04.
- References/projects/duration/locales: Docker storage/Compose docs; Project 04; 80 minutes; EN/MM planned.

#### 09.4 WSGI/ASGI and Process Boundaries

- Difficulty and objectives: Professional; choose process model and graceful lifecycle for Python/Django services.
- Prerequisites and outline: 05.1–05.2; worker processes, health, timeouts, static assets, reverse proxy, graceful shutdown.
- Syntax/API and example/output: process command contract and healthcheck plan; output is a locally verified startup/stop record in Phase 03.
- Exercise/homework and quiz: compare development server and production process; Django project connection.
- References/projects/duration/locales: [Django deployment documentation](https://docs.djangoproject.com/en/stable/howto/deployment/) and Docker docs; Project 04; 75 minutes; EN/MM planned.

#### 09.5 Static and Media Storage

- Difficulty and objectives: Professional; distinguish immutable static assets, user media, shared volumes, and object storage.
- Prerequisites and outline: 03.2, 05.2, 05.6; collect/build, uploads, retention, backup, cache, access control.
- Syntax/API and example/output: storage architecture diagram; output is a file-lifecycle and restore test plan.
- Exercise/homework and quiz: choose storage for three asset types; Project 04.
- References/projects/duration/locales: Docker storage and Django deployment docs; Project 04; 70 minutes; EN/MM planned.

#### 09.6 Availability, Scaling, and Failure Domains

- Difficulty and objectives: Professional; distinguish replica count from availability, identify single-host failure, and plan recovery.
- Prerequisites and outline: Modules 4, 8, 9.1–9.5; stateless app, data layer, health, load balancing, failure domains.
- Syntax/API and example/output: architecture decision record; no fabricated uptime or scale claim.
- Exercise/homework and quiz: critique a single-host architecture; Project 04.
- References/projects/duration/locales: Docker Compose/orchestration boundary docs; Project 04; 80 minutes; EN/MM planned.

#### 09.7 Deployment Approvals and Change Management

- Difficulty and objectives: Professional; define review, evidence, approval, rollback, and post-deployment verification.
- Prerequisites and outline: 06.2, 06.4, 08.7, 09.1; release checklist, audit trail, change window, incident handoff.
- Syntax/API and example/output: deployment workflow specification; output is an approval packet, not a live deployment.
- Exercise/homework and quiz: build a change record; Project 04 gate.
- References/projects/duration/locales: Docker build/Compose docs; Project 04; 65 minutes; EN/MM planned.

#### 09.8 Production Readiness Review

- Difficulty and objectives: Professional; defend the platform against a readiness rubric and list unresolved risks.
- Prerequisites and outline: Module 9; security, data, monitoring, cost, ownership, recovery, documentation.
- Syntax/API and example/output: readiness checklist and architecture presentation; no certification claim.
- Exercise/homework and quiz: peer review with approve/conditional/reject decision; Project 04.
- References/projects/duration/locales: Docker Engine/Compose/security docs; Project 04; 80 minutes; EN/MM planned.

### Module 10 — CI/CD, Cloud Deployment, and Automation

Level: Professional
Status: Planned, not authored
Competency: build a safe delivery pipeline that tests, scans, attests, promotes, deploys, verifies, and rolls back.

#### 10.1 CI Pipeline Stages and Artifacts

- Difficulty and objectives: Professional; define source, lint, test, build, scan, package, and artifact stages with clear outputs.
- Prerequisites and outline: 02.6, 06.4, 09.7; pipeline graph, caching, artifact retention, permissions.
- Syntax/API and example/output: provider-neutral YAML plan; output is a simulated evidence table until a provider is approved.
- Exercise/homework and quiz: repair missing pipeline dependencies; Project 03.
- References/projects/duration/locales: Docker build/CI docs; Project 03; 70 minutes; EN/MM planned.

#### 10.2 Docker Build in CI

- Difficulty and objectives: Professional; use BuildKit/buildx, cache safely, pin inputs, and isolate builders.
- Prerequisites and outline: 02.2, 02.5, 02.7; builder driver, cache scope, multi-platform, secret mount.
- Syntax/API and example/output: `docker buildx build` workflow plan; output includes expected artifact metadata fields, not fabricated IDs.
- Exercise/homework and quiz: design a cache policy that cannot expose credentials; Project 03.
- References/projects/duration/locales: Docker build/CI docs; Project 03; 75 minutes; EN/MM planned.

#### 10.3 Test, Scan, and Policy Gates

- Difficulty and objectives: Professional; fail a build for meaningful defects and document exceptions without bypassing controls.
- Prerequisites and outline: 06.3–06.4, 07.7, 10.1; unit/integration tests, scan, policy, approval, evidence.
- Syntax/API and example/output: provider-neutral gate matrix; output is a sample pass/fail fixture, not a real result.
- Exercise/homework and quiz: create a gate decision table; Project 03.
- References/projects/duration/locales: Docker security/build docs; Project 03; 70 minutes; EN/MM planned.

#### 10.4 Registry Promotion and Deployment

- Difficulty and objectives: Professional; promote one immutable artifact across environments and verify deployment identity.
- Prerequisites and outline: 06.1–06.2, 09.7; registry auth, environment approval, deployment record, rollback.
- Syntax/API and example/output: release manifest and deployment checklist; no auto-deploy.
- Exercise/homework and quiz: trace an artifact from commit to environment; Project 04.
- References/projects/duration/locales: Docker registry/build docs; Project 04; 70 minutes; EN/MM planned.

#### 10.5 Cloud Container Deployment Decision

- Difficulty and objectives: Professional; compare managed container service, VM/Compose, and Kubernetes using workload constraints.
- Prerequisites and outline: 09.6, 10.1–10.4; state, network, identity, storage, cost, operations, vendor lock-in.
- Syntax/API and example/output: decision matrix; no cloud account or live deployment required.
- Exercise/homework and quiz: select a platform for the SaaS capstone; Project 04.
- References/projects/duration/locales: Docker deployment docs and selected provider docs in Phase 03; 75 minutes; EN/MM planned.

#### 10.6 OIDC, Short-Lived Credentials, and Secret Rotation

- Difficulty and objectives: Professional; avoid long-lived CI secrets, scope identities, and rotate credentials after incidents.
- Prerequisites and outline: 07.3, 10.3–10.4; federation, trust policy, secret store, audit, revocation.
- Syntax/API and example/output: provider-neutral identity flow; output is a threat-model and rotation runbook.
- Exercise/homework and quiz: identify privilege escalation in a CI identity; Project 04.
- References/projects/duration/locales: Docker security/registry docs; 70 minutes; EN/MM planned.

#### 10.7 Delivery Failure and Rollback Simulation

- Difficulty and objectives: Professional; stop a bad release, preserve evidence, rollback, verify health, and communicate status.
- Prerequisites and outline: 08.7, 09.7, 10.4–10.6; failure signals, rollback boundary, data compatibility, incident handoff.
- Syntax/API and example/output: tabletop pipeline timeline; output is a completed simulation record.
- Exercise/homework and quiz: run a no-deploy tabletop; Project 04 final operations gate.
- References/projects/duration/locales: Docker build/Compose docs; 75 minutes; EN/MM planned.

### Module 11 — Kubernetes Bridge and Troubleshooting

Level: Professional
Status: Planned, not authored
Competency: understand when Docker concepts map to Kubernetes and troubleshoot without overclaiming equivalence.

#### 11.1 Docker-to-Kubernetes Concept Map

- Difficulty and objectives: Professional; map image, container, network, volume, service, deployment, and secret concepts.
- Prerequisites and outline: Modules 4, 7, 9; orchestration, desired state, controllers, scheduling, service discovery.
- Syntax/API and example/output: conceptual mapping table; output is a boundary diagram.
- Exercise/homework and quiz: identify a false one-to-one mapping; Project 04 migration note.
- References/projects/duration/locales: [Kubernetes documentation](https://kubernetes.io/docs/) and Docker docs; 60 minutes; EN/MM planned.

#### 11.2 Images, Registries, and Workload Identity

- Difficulty and objectives: Professional; prepare image identity, pull policy, service account, and secret boundaries for orchestration.
- Prerequisites and outline: 06.1–06.4, 11.1; registry auth, immutable image, workload identity, policy.
- Syntax/API and example/output: provider-neutral deployment manifest outline; output is a review checklist.
- Exercise/homework and quiz: review image pull and identity assumptions; Project 04.
- References/projects/duration/locales: Docker registry/security and Kubernetes docs; 65 minutes; EN/MM planned.

#### 11.3 Networking and Storage Migration Risks

- Difficulty and objectives: Professional; identify port, DNS, ingress, volume, and data-migration differences before migration.
- Prerequisites and outline: 03.2, 04.1–04.3, 09.3; stateful workloads, storage classes, ingress, service discovery.
- Syntax/API and example/output: migration risk register; no live cluster required.
- Exercise/homework and quiz: choose a migration test; Project 04.
- References/projects/duration/locales: Docker/Kubernetes networking/storage docs; 70 minutes; EN/MM planned.

#### 11.4 Health, Probes, and Rollouts

- Difficulty and objectives: Professional; distinguish startup/readiness/liveness and connect them to safe rollout/rollback.
- Prerequisites and outline: 03.4, 08.2, 09.6; probe semantics, rollout, replica availability, failure signals.
- Syntax/API and example/output: rollout decision record; output is a simulated failure path.
- Exercise/homework and quiz: design probes for the SaaS API; Project 04.
- References/projects/duration/locales: Docker healthchecks and Kubernetes docs; 70 minutes; EN/MM planned.

#### 11.5 Logs, Events, and Incident Evidence

- Difficulty and objectives: Professional; correlate application logs, container/runtime events, and rollout state.
- Prerequisites and outline: 08.1–08.2, 11.4; correlation IDs, retention, redaction, time windows.
- Syntax/API and example/output: incident evidence template; output is a log/event correlation exercise.
- Exercise/homework and quiz: find the first causal signal in a sample timeline; Project 04.
- References/projects/duration/locales: Docker logs/events and Kubernetes docs; 65 minutes; EN/MM planned.

#### 11.6 Troubleshooting Playbook

- Difficulty and objectives: Professional; use a bounded hypothesis loop for image, config, network, storage, resource, and permission failures.
- Prerequisites and outline: Modules 1–11; reproduce, inspect, change one variable, verify, document, clean up.
- Syntax/API and example/output: provider-neutral troubleshooting tree; no unsafe host commands.
- Exercise/homework and quiz: complete three failure scenarios; Project 03 and 04.
- References/projects/duration/locales: Docker troubleshooting docs; 80 minutes; EN/MM planned.

#### 11.7 Migration Readiness Review

- Difficulty and objectives: Professional; decide whether a Compose workload is ready for orchestration and list blockers.
- Prerequisites and outline: 11.1–11.6; ownership, state, observability, security, cost, recovery, team capability.
- Syntax/API and example/output: migration readiness scorecard; output is a conditional approval/reject decision.
- Exercise/homework and quiz: peer-review the capstone migration boundary; Project 04.
- References/projects/duration/locales: Docker/Kubernetes official docs; 75 minutes; EN/MM planned.

### Module 12 — Professional Architecture, Projects, and Capstone

Level: Professional
Status: Planned, not authored
Competency: produce and defend a complete, secure, observable, testable, recoverable container platform design.

#### 12.1 SaaS Container Architecture

- Difficulty and objectives: Professional; decompose the Education SaaS into web, worker, database, cache, proxy, observability, and delivery boundaries.
- Prerequisites and outline: Modules 4–11; domain boundaries, trust zones, data flows, ownership, failure domains.
- Syntax/API and example/output: architecture diagram and ADR; output is a reviewed design artifact.
- Exercise/homework and quiz: identify one hidden coupling; Project 04.
- References/projects/duration/locales: Docker Engine/Compose/security docs; 80 minutes; EN/MM planned.

#### 12.2 Organization, Membership, and Tenant Isolation

- Difficulty and objectives: Professional; model organization membership and tenant isolation without claiming Docker alone provides authorization.
- Prerequisites and outline: 12.1; application authorization, database boundaries, request context, audit, tests.
- Syntax/API and example/output: service/data-flow design; output is a threat-model and test matrix.
- Exercise/homework and quiz: review a cross-tenant access failure; Project 04.
- References/projects/duration/locales: Docker security plus framework docs; 80 minutes; EN/MM planned.

#### 12.3 Student, Course, and Enrollment Services

- Difficulty and objectives: Professional; connect domain services, migrations, jobs, storage, and container boundaries.
- Prerequisites and outline: 05.2, 05.5, 07.3; service ownership, APIs, data lifecycle, idempotency.
- Syntax/API and example/output: Compose service map and API contract outline; output is a domain-to-runtime matrix.
- Exercise/homework and quiz: trace enrollment from request to durable data; Project 04.
- References/projects/duration/locales: Docker Compose and Django official docs; 80 minutes; EN/MM planned.

#### 12.4 Secure REST API Deployment

- Difficulty and objectives: Professional; deploy authenticated API services with validation, rate limits, logs, and secure configuration.
- Prerequisites and outline: 05.1–05.2, 07.3, 09.2; API boundary, auth, CSRF where applicable, CORS, secrets, observability.
- Syntax/API and example/output: API service deployment contract; output is a test and security evidence plan.
- Exercise/homework and quiz: review an API container release; Project 03 and 04.
- References/projects/duration/locales: Docker security and Django/REST official docs; 80 minutes; EN/MM planned.

#### 12.5 Testing Isolation and Security

- Difficulty and objectives: Professional; test image, runtime, API, migration, network, permissions, and recovery properties.
- Prerequisites and outline: Modules 6–11; test pyramid, disposable fixtures, policy checks, negative cases, evidence.
- Syntax/API and example/output: CI test matrix; output is a reproducible test report generated in Phase 03, not fabricated here.
- Exercise/homework and quiz: create a release-blocking test list; Project 04.
- References/projects/duration/locales: Docker build/Compose/security docs; 75 minutes; EN/MM planned.

#### 12.6 Deployment Architecture and Cost Boundaries

- Difficulty and objectives: Professional; explain runtime placement, network/data costs, retention, scaling, and operational ownership.
- Prerequisites and outline: 09.6, 10.5, 11.7; cost drivers, quotas, availability, support boundaries.
- Syntax/API and example/output: architecture/cost decision record; no provider pricing or live capacity claim in the plan.
- Exercise/homework and quiz: compare two deployment options; Project 04.
- References/projects/duration/locales: Docker deployment docs; 75 minutes; EN/MM planned.

#### 12.7 Final Capstone Review

- Difficulty and objectives: Professional; present architecture, implementation evidence, security controls, tests, observability, recovery, and known gaps.
- Prerequisites and outline: 12.1–12.6; review rubric, demo boundary, evidence index, rollback and next steps.
- Syntax/API and example/output: capstone review packet; output is a human-reviewed presentation and repository snapshot.
- Exercise/homework and quiz: defend one trade-off and respond to one failure scenario; Project 04 final.
- References/projects/duration/locales: all approved official references; 90 minutes; EN/MM planned.

#### 12.8 Final Assessment and Further Learning

- Difficulty and objectives: Professional; demonstrate independent judgment and define a safe next learning path.
- Prerequisites and outline: all modules; scenario assessment, architecture critique, troubleshooting, security, recovery, reflection.
- Syntax/API and example/output: no unbounded command execution; answer/evidence rubric is prepared before the assessment.
- Exercise/homework and quiz: final practical assessment plus improvement plan; no result is fabricated by this plan.
- References/projects/duration/locales: Docker official documentation and selected framework references; 90 minutes; EN/MM planned.

## 7. Source-topic crosswalk and deduplication

The source `PLANNED_MODULES` names are all covered, but overlapping topics already taught in Module 1 are not duplicated as new modules. The mapping is:

| Source planning topic | Covered by |
|---|---|
| Containers vs Virtual Machines; Docker Installation & Setup; Docker Architecture; Docker CLI Fundamentals; Container Lifecycle | Existing Module 01 lessons 1.2–1.6 |
| Docker Images; Dockerfile Fundamentals; Advanced Dockerfile; Docker Build & BuildKit; Multi-Stage Builds | Modules 01.7–01.8 and Module 02 |
| Docker Networking Fundamentals; Advanced Container Networking | Module 04 |
| Docker Volumes; Bind Mounts & Storage; Environment Variables & Configuration | Module 03 |
| Docker Compose Fundamentals; Advanced Docker Compose | Module 04 |
| Dockerizing Python Applications; Dockerizing Django Applications; Dockerizing Node.js & React; Dockerizing Laravel & PHP | Module 05 |
| Docker Hub & Registries; Image Versioning & Publishing | Module 06 |
| Docker Security Fundamentals; Image Scanning & Supply Chain; Secrets & Runtime Security; Rootless Docker & Hardening | Module 06 and Module 07 |
| Container Logs & Monitoring; Container Resource Management; Docker Performance Optimization; Backup & Recovery | Module 03 and Module 08 |
| Docker in Production; Professional Docker Architecture | Module 09 and Module 12 |
| Docker CI/CD Pipelines; Cloud Container Deployment | Module 10 |
| Docker & Kubernetes Fundamentals; Docker Troubleshooting | Module 11 |
| Real-World Docker Projects; Final Docker Capstone & Assessment | Module 12 and the project roadmap |

## 8. Project roadmap

Projects reuse the existing Admin Projects system. This phase defines mappings only; it does not create fake project records or mark any project published.

### Project 01 — Beginner Docker Website

- Objective: build a small static website image and run it safely in a disposable local context.
- Requirements: Dockerfile, `.dockerignore`, static pages, non-root runtime, bounded port, health/readiness note, README, cleanup.
- Architecture: browser → published local port → static web container; no database and no production daemon.
- Required lessons: 01.1–01.8, 02.1–02.4, 04.1–04.4, 05.3.
- Development phases: identify boundary; write Dockerfile; build/run; inspect; add health and security checks; document cleanup.
- Testing: build reproducibility, route response, non-root check, image history review, port exposure review.
- Evaluation rubric: 20% correctness, 20% reproducibility, 20% security, 20% evidence/README, 20% troubleshooting and cleanup.

### Project 02 — Student Record System

- Objective: containerize a CRUD application with forms/API, PostgreSQL, validation, search, pagination, and durable data.
- Requirements: web service, database service, migrations, healthchecks, named volume, safe configuration, backup/restore note.
- Architecture: reverse proxy → app → database; optional worker; internal network; no database port exposed by default.
- Required lessons: Modules 02–05, 08.6, 09.3, and 12.3.
- Development phases: schema and migration contract; application image; Compose; validation; data backup; failure drill.
- Testing: model/API tests, migration replay, validation errors, health/readiness, database restart, restore verification.
- Evaluation rubric: 20% feature behavior, 20% data correctness, 20% container design, 20% testing/recovery, 20% security/documentation.

### Project 03 — Education REST API Delivery Pipeline

- Objective: deliver an authenticated REST API through build, test, scan, provenance, and controlled registry promotion.
- Requirements: API image, Compose test profile, authentication/permissions, validation, API documentation, CI policy, redacted logs.
- Architecture: API + database + test dependencies; CI builder; registry; approval gate; deployment artifact.
- Required lessons: Modules 02, 04–07, 08.1–08.5, and 10.1–10.3.
- Development phases: API contract; containerize; test profile; security gates; SBOM/provenance; release evidence.
- Testing: unit/integration/API/security tests, dependency scan, image policy, secret absence, rollback fixture.
- Evaluation rubric: 20% API behavior, 20% tests, 20% supply-chain evidence, 20% security, 20% release documentation.

### Project 04 — Professional Education SaaS

- Objective: design a secure, observable, recoverable, multi-tenant education platform deployment.
- Requirements: organizations, membership, tenant isolation, student management, course enrollments, RBAC, monitoring, Docker deployment, CI/CD, backup/recovery.
- Architecture: proxy, web/API, worker, PostgreSQL, cache/queue, observability, registry, CI/CD, and a documented Kubernetes migration boundary.
- Required lessons: Modules 03–12, especially 07.1–07.8, 08.6–08.8, 09, 10, 11, and 12.
- Development phases: threat model; domain/data boundaries; local Compose; security hardening; observability; CI/CD; recovery; readiness review.
- Testing: tenant isolation, authorization, migration, backup/restore, failure injection in a disposable environment, image/runtime policy, deployment rollback tabletop.
- Evaluation rubric: 15% architecture, 15% security, 15% data/recovery, 15% tests, 15% observability, 15% delivery, 10% explanation/evidence.

## 9. Assessment planning

Every module receives the following assessment mix. Phase 03 must persist new assessment records only as drafts and must not alter existing quiz attempts.

| Assessment | Purpose | Difficulty progression | Evidence |
|---|---|---|---|
| Guided exercise | Practice one bounded command/concept with a cleanup step | Beginner → intermediate | Learner checklist and captured local output |
| Independent exercise | Transfer the concept to a new service or failure case | Intermediate → advanced | Repository change, explanation, and test evidence |
| Knowledge check | Verify vocabulary, boundaries, and safe decisions | All levels | 3–5 questions with answer explanations |
| Module quiz | Check prerequisite and competency coverage | Module level | Question blueprint, no fabricated results |
| Homework | Build an evidence/runbook/ADR artifact | Intermediate → professional | Submitted document or repository link |
| Practical assignment | Integrate multiple lessons | Advanced → professional | Rubric-scored project milestone |
| Mini project | Produce a small usable container artifact | Relevant modules | Dockerfile/Compose, tests, security, cleanup |

Suggested grading policy for future implementation: knowledge checks 10%, guided/independent exercises 25%, module quiz 20%, practical assignment 25%, documentation/safety/recovery evidence 20%. This is a proposal, not a published grading rule.

Required quiz quality: every question must have a correct answer, explanation, difficulty, mapped lesson objective, and locale-specific prose. Technical identifiers and commands remain unchanged between locales; explanations must not silently fall back to English in a Burmese lesson.

## 10. EN/MM translation plan

Locale codes remain `en` and `my`.

### Existing Module 1

- EN: persisted and published, but Phase 01 strict section audit found missing structural sections; classify as **existing / review required**, not complete.
- MM: persisted for all 8 lessons, but classify as **partial / review required** until each heading, explanation, exercise, quiz explanation, and safety note is fully translated.
- Required review: compare English and Burmese section-by-section; preserve code, commands, flags, function names, image tags, API names, and file paths exactly where executable.

### Planned Modules 2–12

- EN: **planned / not authored**. Phase 03 must author the English lesson body first, then review technical terminology.
- MM: **planned / not authored**. Do not copy English paragraphs or mark the translation complete because a Burmese heading exists.
- Module titles, lesson titles, objectives, theory, examples, output explanations, exercises, quizzes, answer explanations, homework, project instructions, and summaries all require separate locale content.
- Technical identifiers remain stable: Docker CLI flags, YAML keys, Dockerfile instructions, URLs, package names, image names, API routes, database identifiers, and code comments where code execution depends on them.
- Publication rule: EN and MM readiness are evaluated separately; a lesson cannot be reported as fully translated when one locale is missing, fallback-only, or structurally incomplete.

## 11. Admin Curriculum Builder mapping

This plan maps to the existing Admin > Courses > Curriculum Builder without rebuilding it:

- Expandable module rows: display the 12 planned module groups as a review outline; only Module 1 currently exists in the database.
- Lesson rows: existing Module 1 rows remain editable; clicking a row opens the existing inline editor directly below it.
- Future Phase 03 actions: Add Lesson, Duplicate, Reorder, Archive, View, Edit, and Translation Editing must operate through existing RBAC-protected APIs and preserve IDs/progress.
- Plan storage: no dedicated curriculum-plan table was found. This versioned repository document is therefore the Phase 02 source of truth.
- No empty records: this document must not be interpreted as permission to bulk-create placeholder lessons or modules.
- Publication: save draft, review, validate, authorize, and publish remain separate actions. Phase 02 performs none of them.

## 12. Coverage matrix

| Module | Level | Existing/planned | Core competency | Project mapping | Assessment mapping | EN readiness | MM readiness |
|---|---|---|---|---|---|---|---|
| 01 Introduction | Beginner | 8 existing published lessons | Engine, CLI, lifecycle, first image | P01 | Guided labs + Module 1 quiz | Existing; review required | Existing; partial/review required |
| 02 Images/builds | Beginner–Intermediate | Planned | Layers, Dockerfiles, BuildKit, reproducibility | P01–P03 | Dockerfile labs + build quiz | Planned | Planned |
| 03 Runtime/data | Intermediate | Planned | Config, storage, health, recovery | P02–P04 | Storage lab + recovery homework | Planned | Planned |
| 04 Networking/Compose | Intermediate | Planned | Networks, ports, service discovery, Compose | P01–P03 | Compose lab + topology quiz | Planned | Planned |
| 05 Applications | Intermediate | Planned | Python, Django, Node, Laravel, migrations | P01–P04 | App image assignment | Planned | Planned |
| 06 Supply chain | Advanced | Planned | Registry, releases, scans, provenance | P03–P04 | Evidence gate + triage exercise | Planned | Planned |
| 07 Security | Advanced–Professional | Planned | Least privilege, secrets, rootless, profiles | P03–P04 | Threat model + tabletop | Planned | Planned |
| 08 Operations | Advanced | Planned | Logs, metrics, limits, performance, restore | P03–P04 | Runbook + restore drill | Planned | Planned |
| 09 Production | Professional | Planned | Deployment, TLS, DB, availability, readiness | P02–P04 | Production readiness review | Planned | Planned |
| 10 CI/CD/cloud | Professional | Planned | Build/test/scan/promote/deploy/rollback | P03–P04 | Pipeline design + failure simulation | Planned | Planned |
| 11 Kubernetes bridge | Professional | Planned | Migration boundaries and troubleshooting | P04 | Migration scorecard | Planned | Planned |
| 12 Architecture/capstone | Professional | Planned | Secure SaaS architecture and final defense | P04 | Capstone rubric + final assessment | Planned | Planned |

## 13. Technical accuracy and source policy

The plan uses official primary references and defers version pinning to Phase 03 verification:

- [Docker Engine documentation](https://docs.docker.com/engine/) for installation, storage, networking, containers, CLI, daemon, logs, and security.
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/) for image layers, multi-stage builds, cache, secrets, and reproducibility.
- [Docker Compose documentation](https://docs.docker.com/compose/) for multi-container configuration, profiles, dependencies, environment variables, secrets, networking, and lifecycle.
- [Docker Engine security](https://docs.docker.com/engine/security/) for rootless mode, user namespaces, seccomp, daemon/socket protection, and attack-surface review.
- [Django official documentation](https://docs.djangoproject.com/en/stable/) only for the Django application-integration lessons; Django is not treated as Docker core.
- [Kubernetes documentation](https://kubernetes.io/docs/) only for the Module 11 migration bridge; Kubernetes is not presented as a Docker feature.

Phase 03 must verify the selected stable versions and compatibility matrix before writing examples. It must not copy documentation passages, use deprecated APIs without context, or claim that a provider-specific command is portable.

## 14. Quality review checklist

- [x] Phase 01 verified Docker as the first incomplete course.
- [x] Canonical course ID and slug were read from the live database.
- [x] Existing Module 1 and lesson IDs were inspected and preserved in this plan.
- [x] Four levels are represented: Beginner, Intermediate, Advanced, Professional.
- [x] Prerequisites progress from terminal/image basics to architecture and recovery.
- [x] Overlapping source topics are mapped instead of duplicated.
- [x] Project milestones and assessments map to modules.
- [x] EN/MM status is separated and planned content is not called complete.
- [x] No empty lesson record, lesson body, quiz result, project result, or publication was created.
- [ ] Phase 03 must verify all examples in a safe local environment.
- [ ] Phase 03 must author and review Module 1 repairs before adding later modules.
- [ ] Phase 03 must obtain human/content review before any publish action.

## 15. Phase 02 acceptance and next phase

This document satisfies the Phase 02 planning boundary for one verified incomplete course: it identifies the actual course, preserves existing records, defines a complete ordered Beginner-to-Professional architecture, specifies every planned lesson, maps projects and assessments, separates EN/MM readiness, and leaves all new content unpublished.

Phase 03 scope is **Module 01 complete lesson-content implementation** only. It must begin with a review of the existing eight published lessons, create no duplicate lessons, persist any new version as draft, add real exercises/assessment links through existing APIs, verify EN/MM independently, and stop for review before expanding to Module 02.
