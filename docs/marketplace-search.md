# Marketplace search

Search uses bounded SQL filters, stable pagination, and server-side published
visibility. Keyword search currently uses indexed relational filters and is
safe for local operation. A PostgreSQL full-text or external index can be added
later without changing publication rules.
