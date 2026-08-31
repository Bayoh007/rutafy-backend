"""Rutafy beta marketplace schema and Supabase security boundary."""

from alembic import op

revision = "20260830_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    create schema if not exists private;
    create type public.creator_status as enum ('none','pending','verified','premium');
    create type public.itinerary_status as enum ('draft','pending_review','approved','rejected');
    create type private.creator_application_status as enum ('pending','approved','rejected');
    create table public.profiles (
      id uuid primary key references auth.users(id) on delete cascade,
      display_name varchar(120), avatar_path varchar(500),
      created_at timestamptz not null default now(), updated_at timestamptz not null default now()
    );
    create table public.roles (id smallserial primary key, name varchar(32) unique not null);
    insert into public.roles(name) values ('user'), ('admin');
    create table public.user_roles (
      user_id uuid references public.profiles(id) on delete cascade,
      role_id smallint references public.roles(id) on delete cascade,
      primary key(user_id, role_id)
    );
    create table public.creator_profiles (
      user_id uuid primary key references public.profiles(id) on delete cascade,
      status public.creator_status not null default 'none', bio text, public_photo_path varchar(500),
      verified_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
    );
    create table public.itineraries (
      id uuid primary key default gen_random_uuid(),
      creator_id uuid not null references public.creator_profiles(user_id),
      title varchar(180) not null, slug varchar(220) unique,
      status public.itinerary_status not null default 'draft',
      price_amount integer, currency char(3) not null default 'EUR', is_free boolean not null default true,
      approved_version_id uuid, created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
      constraint itinerary_beta_price check ((is_free and coalesce(price_amount, 0) = 0) or (not is_free and price_amount > 0)),
      constraint itinerary_beta_currency check (currency = 'EUR')
    );
    create table public.itinerary_versions (
      id uuid primary key default gen_random_uuid(), itinerary_id uuid not null references public.itineraries(id) on delete cascade,
      version_number integer not null, summary text, content jsonb not null default '{}'::jsonb,
      created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
      unique(itinerary_id, version_number)
    );
    alter table public.itineraries add constraint itinerary_approved_version_fk foreign key(approved_version_id) references public.itinerary_versions(id);
    create table public.itinerary_days (id uuid primary key default gen_random_uuid(), version_id uuid not null references public.itinerary_versions(id) on delete cascade, day_number integer not null, title varchar(180), description text, unique(version_id, day_number));
    create table public.itinerary_items (id uuid primary key default gen_random_uuid(), day_id uuid not null references public.itinerary_days(id) on delete cascade, position integer not null, title varchar(180) not null, details text, location_data jsonb not null default '{}'::jsonb, unique(day_id, position));
    create table public.itinerary_media (id uuid primary key default gen_random_uuid(), itinerary_id uuid not null references public.itineraries(id) on delete cascade, storage_path varchar(500) unique not null, alt_text varchar(250), created_at timestamptz not null default now());
    create table public.itinerary_reviews (id uuid primary key default gen_random_uuid(), itinerary_id uuid not null references public.itineraries(id) on delete cascade, version_id uuid not null references public.itinerary_versions(id), admin_id uuid not null references public.profiles(id), decision public.itinerary_status not null, note text, created_at timestamptz not null default now(), constraint review_decision check(decision in ('approved','rejected')));
    create table public.creator_follows (follower_id uuid references public.profiles(id) on delete cascade, creator_id uuid references public.creator_profiles(user_id) on delete cascade, created_at timestamptz not null default now(), primary key(follower_id, creator_id));
    create table public.itinerary_follows (follower_id uuid references public.profiles(id) on delete cascade, itinerary_id uuid references public.itineraries(id) on delete cascade, created_at timestamptz not null default now(), primary key(follower_id, itinerary_id));
    create table public.collections (id uuid primary key default gen_random_uuid(), owner_id uuid not null references public.profiles(id) on delete cascade, name varchar(100) not null, created_at timestamptz not null default now(), updated_at timestamptz not null default now());
    create table public.collection_itineraries (collection_id uuid references public.collections(id) on delete cascade, itinerary_id uuid references public.itineraries(id) on delete cascade, created_at timestamptz not null default now(), primary key(collection_id, itinerary_id));
    create table public.notifications (id uuid primary key default gen_random_uuid(), recipient_id uuid not null references public.profiles(id) on delete cascade, event_type varchar(80) not null, payload jsonb not null default '{}'::jsonb, read_at timestamptz, created_at timestamptz not null default now());
    create table public.notification_preferences (user_id uuid primary key references public.profiles(id) on delete cascade, in_app_enabled boolean not null default true, email_enabled boolean not null default true, updated_at timestamptz not null default now());
    create table private.creator_applications (id uuid primary key default gen_random_uuid(), applicant_id uuid not null references public.profiles(id) on delete cascade, status private.creator_application_status not null default 'pending', full_name varchar(160) not null, phone_number varchar(50) not null, social_profile_url varchar(500) not null, travel_experience text not null, portfolio text not null, sample_itinerary text not null, application_letter text not null, profile_photo_path varchar(500) not null, reviewed_by uuid references public.profiles(id), reviewed_at timestamptz, review_note text, created_at timestamptz not null default now(), updated_at timestamptz not null default now());
    create table private.creator_application_documents (id uuid primary key default gen_random_uuid(), application_id uuid not null references private.creator_applications(id) on delete cascade, storage_path varchar(500) unique not null, document_type varchar(32) not null, created_at timestamptz not null default now());
    create table public.audit_logs (id uuid primary key default gen_random_uuid(), actor_id uuid references public.profiles(id), action varchar(120) not null, target_type varchar(80) not null, target_id uuid, metadata jsonb not null default '{}'::jsonb, created_at timestamptz not null default now());
    create index itineraries_discovery_idx on public.itineraries(status, created_at desc);
    create index notifications_recipient_idx on public.notifications(recipient_id, created_at desc);
    create index creator_applications_pending_idx on private.creator_applications(status, created_at);

    create or replace function private.is_admin() returns boolean language sql stable security definer set search_path = public, private as $$
      select exists (select 1 from public.user_roles ur join public.roles r on r.id = ur.role_id where ur.user_id = auth.uid() and r.name = 'admin');
    $$;
    revoke all on schema private from public, anon, authenticated;
    grant usage on schema public to anon, authenticated;
    alter table public.profiles enable row level security;
    alter table public.creator_profiles enable row level security;
    alter table public.itineraries enable row level security;
    alter table public.itinerary_versions enable row level security;
    alter table public.itinerary_days enable row level security;
    alter table public.itinerary_items enable row level security;
    alter table public.itinerary_media enable row level security;
    alter table public.creator_follows enable row level security;
    alter table public.itinerary_follows enable row level security;
    alter table public.collections enable row level security;
    alter table public.collection_itineraries enable row level security;
    alter table public.notifications enable row level security;
    alter table public.notification_preferences enable row level security;
    create policy "public reads approved itineraries" on public.itineraries for select using (status = 'approved' or creator_id = auth.uid() or private.is_admin());
    create policy "creator manages own itineraries" on public.itineraries for all to authenticated using (creator_id = auth.uid() or private.is_admin()) with check (creator_id = auth.uid() or private.is_admin());
    create policy "profile public read" on public.profiles for select using (true);
    create policy "profile self update" on public.profiles for update to authenticated using (id = auth.uid()) with check (id = auth.uid());
    create policy "collections owner only" on public.collections for all to authenticated using (owner_id = auth.uid()) with check (owner_id = auth.uid());
    create policy "notifications recipient only" on public.notifications for select to authenticated using (recipient_id = auth.uid());
    create policy "creator follows own" on public.creator_follows for all to authenticated using (follower_id = auth.uid()) with check (follower_id = auth.uid());
    create policy "itinerary follows own" on public.itinerary_follows for all to authenticated using (follower_id = auth.uid()) with check (follower_id = auth.uid());
    create policy "private collections items" on public.collection_itineraries for all to authenticated using (exists(select 1 from public.collections c where c.id = collection_id and c.owner_id = auth.uid())) with check (exists(select 1 from public.collections c where c.id = collection_id and c.owner_id = auth.uid()));
    insert into storage.buckets (id, name, public) values ('creator-verification', 'creator-verification', false), ('itinerary-media', 'itinerary-media', false) on conflict (id) do nothing;
    create policy "admins access verification documents" on storage.objects for all to authenticated using (bucket_id = 'creator-verification' and private.is_admin()) with check (bucket_id = 'creator-verification' and private.is_admin());
    create policy "approved public itinerary media" on storage.objects for select using (bucket_id = 'itinerary-media');
    """)


def downgrade() -> None:
    op.execute("drop schema if exists private cascade; drop schema if exists public cascade;")
