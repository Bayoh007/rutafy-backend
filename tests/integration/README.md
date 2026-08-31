# Integration tests

Run these tests only against an isolated local Supabase/PostgreSQL instance.
They must never receive production connection settings or production credentials.

Required coverage before production release:

- migrations upgrade an empty database;
- RLS prevents cross-user reads/writes;
- private creator documents cannot be read by a normal user;
- an admin may approve a pending creator application and itinerary;
- only approved itineraries are discoverable publicly.
