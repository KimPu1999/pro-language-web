# GitHub integration

Students submit repository URLs, branch or commit identifiers, optional demo URLs, and setup instructions. Repository validation accepts GitHub hosts only. Demo and profile URLs must be HTTP(S) and reject credentials, localhost, loopback, and private IP addresses.

The current implementation stores links and metadata without fetching or executing repositories. Private repository access should use a GitHub App installation flow in a future deployment; personal access tokens are never accepted in ordinary form fields.
