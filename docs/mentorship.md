# Mentorship

Mentors apply as regular authenticated users. Only administrators can approve, reject, or suspend a mentor profile. Public directory results contain approved profiles only. Availability is stored in UTC and has a uniqueness constraint; booking changes the slot state inside a transaction and conflicts return `409`.
