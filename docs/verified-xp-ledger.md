# Verified XP Ledger

`GamificationXPLedger` is append-only at the application boundary and has a
unique evidence reference. Quest completion creates one posted transaction and
updates the existing XP balance. A reversal must be represented as a separate
negative ledger transaction; historical rewards are not overwritten.
