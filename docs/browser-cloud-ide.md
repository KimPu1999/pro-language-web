# Browser Cloud IDE

The Phase 26 workspace uses the existing Monaco editor and authenticated file
endpoints. Files are ownership-checked, CSRF-protected, path-validated, and
bounded by a 5 MB workspace quota. Autosave is represented by explicit save
requests; no host filesystem is mounted into the browser or API process.
