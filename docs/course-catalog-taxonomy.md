# Course catalog taxonomy

The catalog uses the existing `programming_languages` and `course_categories` tables. Published cards are read from real records where `courses.published = true`; the application does not seed placeholder courses or fabricate lesson counts.

The requested taxonomy is the authoring backlog for the existing CMS:

- Frontend: HTML5, CSS3, JavaScript, TypeScript, React, Next.js, jQuery, Tailwind CSS, Bootstrap, Vue.js, Angular
- Programming: C, C++, Java, Advanced Java, Python, C#, Go, Rust, Kotlin, Dart, Swift
- Backend: Node.js, Express.js, PHP, Laravel, FastAPI, Django, Spring Boot, ASP.NET Core
- Database: SQL, MySQL, PostgreSQL, SQLite, MongoDB, Redis, Database Design
- Full-stack: MERN Stack, Next.js Full-Stack, Laravel + React, FastAPI + React
- DevOps: Linux, Git, GitHub, Docker, CI/CD, Nginx, AWS, Microsoft Azure
- Cybersecurity: Cybersecurity Fundamentals, Networking, Linux Security, Web Security, OWASP Top 10, Secure Coding, Ethical Hacking in Authorized Labs
- AI and data: Python for AI, Data Analysis, Machine Learning, Deep Learning, Generative AI
- Mobile: Flutter, React Native, Android Kotlin, Swift
- Computer science: Data Structures, Algorithms, Operating Systems, Computer Networks, Software Engineering

Each technology should be published only after its own curriculum and examples have passed the existing admin review and publish validation. The current C curriculum plan is documented in [c-programming-curriculum.md](./c-programming-curriculum.md); it records authored counts separately from planned targets.
