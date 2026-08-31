# Rutafy Backend

Production-oriented API foundation for the Rutafy travel-itinerary marketplace beta.

## Beta scope

- Supabase email/password authentication, verification, login, and recovery.
- Creator application and administrator-only verification.
- Verified-creator itinerary drafting, admin approval, public discovery.
- Independent creator/itinerary follows and private saved collections.
- EUR itinerary pricing for market validation only.

The beta has no checkout, payments, orders, refunds, taxes, platform fees, creator payouts, subscriptions, or bundles.

## Local setup

1. Copy `.env.example` to `.env` and supply values for a non-production Supabase project.
2. Create/use an isolated local PostgreSQL or local Supabase environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the API: `uvicorn app.main:app --reload`.
5. Check health at `GET /health`.

Do not place a production database URL or Supabase service-role key in `.env` for local development.

## Database migrations

Alembic migration files are under `alembic/versions/`. Apply them only to an isolated development or staging database during setup. Production migrations must run through the reviewed GitHub Actions release workflow after staging validation.

## Security boundaries

- Supabase Auth owns credentials and verification emails.
- The Rutafy API validates Supabase bearer JWTs.
- Creator identity documents are private Storage objects and are never returned by public APIs.
- Only users with the `admin` role can approve creator applications or itinerary submissions.
- Follow and Save are separate data models and API concerns.

## Product decisions pending

The exact itinerary content format, creator-application resubmission behavior, public profile handle rules, rejection-reason visibility, notification triggers, and saved-collection behavior remain product decisions. See the approved architecture discussion before implementing those extensions.
