# Contribution verification

The contribution API returns only records owned by the current user and marked `verified`. A contribution becomes eligible for verification only after a configured server-side GitHub sync matches the connected GitHub identity, repository, and external contribution state. User-submitted URLs alone cannot create verified evidence. Duplicate records are prevented by the connection, external ID, and contribution type constraint.
