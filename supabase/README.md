# Supabase operating rules

- Use a distinct development, staging, and production project.
- Apply Alembic migrations through CI only after review.
- Never use the dashboard to make untracked production schema changes.
- `creator-verification` is private. Only administrators access documents through audited, short-lived signed URLs.
- Marketplace data is accessed through the Rutafy API, not directly from client applications.
