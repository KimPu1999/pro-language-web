# Enterprise SSO

Organizations expose SSO configuration status at `/api/v1/organizations/{slug}/security/sso`. Provider records can be staged only when the corresponding deployment configuration is enabled. Activation must follow a provider-specific validation and lockout-prevention process.
