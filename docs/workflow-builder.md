# Workflow builder

The organization builder creates a workflow and a validated draft graph. The current UI presents a compact structured node editor for trigger, notification action, and end nodes without adding a new dependency. The API is ready for a maintained node-editor library when the product requires richer drag-and-drop editing.

Publishing requires a valid graph and stores a graph hash. Published versions are never edited in place; create a new draft version for changes.
