-- 0005_add_payment_status.sql
-- Per-movement payment status (PAID/PENDING). NOT a template snapshot: it is
-- mutable state on the transaction.
--
-- Idempotent so the same file runs on a fresh init AND can be applied by hand to
-- an already-initialized database (migrations only run on the volume's first init).
--
-- The ADD COLUMN default 'PAID' backfills existing rows to PAID (historical
-- movements are treated as already settled). The default is then switched to
-- 'PENDING' so new movements are born pending.

DO $$ BEGIN
  CREATE TYPE payment_status AS ENUM ('PAID', 'PENDING');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE transactions
  ADD COLUMN IF NOT EXISTS payment_status payment_status NOT NULL DEFAULT 'PAID';

ALTER TABLE transactions
  ALTER COLUMN payment_status SET DEFAULT 'PENDING';
