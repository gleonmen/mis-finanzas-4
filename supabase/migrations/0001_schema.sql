-- 0001_schema.sql
-- Core schema for the personal finance MVP (single-user, no auth).
-- Design notes:
--  * transaction_type distinguishes INCOME vs EXPENSE.
--  * Categories are fixed (seeded in 0002), one level only (the "groups").
--  * A composite UNIQUE (id, transaction_type) on categories backs a composite FK
--    from templates, so the DB guarantees a category matches its transaction type.
--  * Transactions store a SNAPSHOT of the template fields (type/category_code/name/
--    is_essential/frequency) so editing or deleting a template/category does NOT
--    change historical reports.
--  * is_essential is required for EXPENSE, NULL for INCOME (enforced by CHECK).

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------
CREATE TYPE transaction_type AS ENUM ('INCOME', 'EXPENSE');

CREATE TYPE frequency AS ENUM ('MONTHLY', 'BIMONTHLY', 'QUARTERLY', 'SEMIANNUAL', 'ANNUAL', 'ONE_TIME');

-- ---------------------------------------------------------------------------
-- categories  (fixed catalog, seeded in 0002, not user-editable)
-- ---------------------------------------------------------------------------
CREATE TABLE categories (
    id               SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code             TEXT NOT NULL UNIQUE,          -- stable english identifier (e.g. 'transport')
    transaction_type transaction_type NOT NULL,
    -- Composite unique key that the templates FK references, so a template's
    -- category is guaranteed to belong to the same transaction_type.
    UNIQUE (id, transaction_type)
);

-- ---------------------------------------------------------------------------
-- templates  (the configurable "types": preload amount + frequency on entry)
-- ---------------------------------------------------------------------------
CREATE TABLE templates (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name             TEXT NOT NULL,
    transaction_type transaction_type NOT NULL,
    category_id      SMALLINT NOT NULL,
    is_essential     BOOLEAN,                        -- required for EXPENSE, NULL for INCOME
    default_amount   NUMERIC(14, 2) NOT NULL,
    frequency        frequency NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Composite FK: category must exist AND match this template's transaction_type.
    FOREIGN KEY (category_id, transaction_type)
        REFERENCES categories (id, transaction_type),

    CONSTRAINT templates_default_amount_positive CHECK (default_amount > 0),

    -- is_essential is mandatory on EXPENSE, must be NULL on INCOME.
    CONSTRAINT templates_is_essential_by_type CHECK (
        (transaction_type = 'EXPENSE' AND is_essential IS NOT NULL)
        OR (transaction_type = 'INCOME' AND is_essential IS NULL)
    )
);

CREATE INDEX idx_templates_type ON templates (transaction_type);

-- ---------------------------------------------------------------------------
-- transactions  (real movements; SNAPSHOT of template fields at creation time)
-- ---------------------------------------------------------------------------
CREATE TABLE transactions (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- Snapshot columns (frozen copy; NOT a live FK to templates/categories) --
    transaction_type transaction_type NOT NULL,
    category_code    TEXT NOT NULL,                  -- stable copy, survives catalog changes
    name             TEXT NOT NULL,
    is_essential     BOOLEAN,
    frequency        frequency NOT NULL,
    -- Actual movement data --
    amount           NUMERIC(14, 2) NOT NULL,
    occurred_on      DATE NOT NULL,
    -- Optional soft link to originating template (nullable, kept for traceability;
    -- reports never depend on it). ON DELETE SET NULL so deleting a template does
    -- not touch the historical snapshot.
    template_id      INTEGER REFERENCES templates (id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT transactions_amount_positive CHECK (amount > 0),

    CONSTRAINT transactions_is_essential_by_type CHECK (
        (transaction_type = 'EXPENSE' AND is_essential IS NOT NULL)
        OR (transaction_type = 'INCOME' AND is_essential IS NULL)
    )
);

-- Index for the "month already loaded" presence guard and future cash reports.
CREATE INDEX idx_transactions_occurred_on ON transactions (occurred_on);
