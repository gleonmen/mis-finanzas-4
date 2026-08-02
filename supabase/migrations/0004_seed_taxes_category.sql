-- 0004_seed_taxes_category.sql
-- Additive to the fixed catalog: a new EXPENSE category "Impuestos" (taxes).
-- No id given, so IDENTITY assigns the next value (15) on a fresh init, same as
-- 0002. ON CONFLICT makes it idempotent, so the exact same statement can also be
-- applied by hand to an already-initialized database (migrations only run on the
-- volume's first init).
INSERT INTO categories (code, transaction_type)
VALUES ('taxes', 'EXPENSE')
ON CONFLICT (code) DO NOTHING;
