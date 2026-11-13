# Interactive lab architecture

PostgreSQL stores lab versions, workspace metadata, files, snapshots, runs, and evidence. Redis may queue future isolated-runner work, but durable state remains PostgreSQL. The application API only validates ownership and creates bounded jobs. Code, SQL, and API execution belong to separate configured services.
