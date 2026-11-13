# Session management

Session listing and revocation use the existing server-side `AuthSession` rows. Revocation updates the backend row; subsequent requests fail authentication. Password reset and password changes already revoke sessions globally for the user.
