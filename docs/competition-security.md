# Competition security

FastAPI does not execute untrusted code. Shared editing requires a separately deployed CRDT gateway. Hidden tests are never returned by competition routes. Team resources require membership checks, mutations require CSRF, and platform controls require platform roles.
