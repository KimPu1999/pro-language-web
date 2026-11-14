# Marketplace architecture

The marketplace has three boundaries: existing published courses, owned
community resources, and moderator-controlled publication. PostgreSQL is the
source of truth. Redis is not required for correctness. Public pages never
query draft or private content.

There is no commercial transaction path. Every resource and course is free.
