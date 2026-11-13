# Accessibility audit

The UI uses semantic links/buttons and visible focus styles from the shared design system. The new quality page uses headings, `role=alert` for fetch failures, and responsive cards.

Automated axe and Lighthouse scans were **not run** because no axe/Lighthouse runner is configured in this repository. Before production, run them at 375px, 768px, 1280px, and 1440px; manually verify keyboard order, dialog focus, screen-reader labels, contrast, reduced motion, and error association. Resolve all critical and serious findings.
