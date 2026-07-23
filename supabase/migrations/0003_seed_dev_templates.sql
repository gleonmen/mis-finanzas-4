-- 0003_seed_dev_templates.sql
-- Example/starter templates so the monthly-load flow has data to copy.
-- These are dev seed data (single-user MVP): editable later, and wiped by
-- `docker compose down -v`. Names use sub-items from the user's category list.
-- Amounts are illustrative COP values.

INSERT INTO templates (name, transaction_type, category_id, is_essential, default_amount, frequency)
SELECT t.name, t.transaction_type, c.id, t.is_essential, t.default_amount, t.frequency
FROM (
    VALUES
        -- Income (is_essential must be NULL)
        ('Sueldo mensual',        'INCOME'::transaction_type, 'salaries',          NULL,        3500000, 'MONTHLY'::frequency),
        ('Honorarios freelance',  'INCOME'::transaction_type, 'freelance',         NULL,         800000, 'MONTHLY'::frequency),
        ('Arriendo apartamento',  'INCOME'::transaction_type, 'rentals',           NULL,        1200000, 'MONTHLY'::frequency),

        -- Expense (is_essential required)
        ('Arriendo',              'EXPENSE'::transaction_type, 'housing_utilities', true,       1300000, 'MONTHLY'::frequency),
        ('Energia electrica',     'EXPENSE'::transaction_type, 'housing_utilities', true,        120000, 'MONTHLY'::frequency),
        ('Internet y celular',    'EXPENSE'::transaction_type, 'housing_utilities', true,        130000, 'MONTHLY'::frequency),
        ('Mercado',               'EXPENSE'::transaction_type, 'food_household',    true,        800000, 'MONTHLY'::frequency),
        ('Gasolina',              'EXPENSE'::transaction_type, 'transport',         true,        250000, 'MONTHLY'::frequency),
        ('SOAT',                  'EXPENSE'::transaction_type, 'transport',         true,        900000, 'ANNUAL'::frequency),
        ('Medicina prepagada',    'EXPENSE'::transaction_type, 'health',            true,        200000, 'MONTHLY'::frequency),
        ('Netflix',               'EXPENSE'::transaction_type, 'lifestyle',         false,        44900, 'MONTHLY'::frequency),
        ('Spotify',               'EXPENSE'::transaction_type, 'lifestyle',         false,        16900, 'MONTHLY'::frequency),
        ('Restaurantes',          'EXPENSE'::transaction_type, 'lifestyle',         false,       300000, 'MONTHLY'::frequency),
        ('Tarjeta de credito',    'EXPENSE'::transaction_type, 'debt_finance',      true,        500000, 'MONTHLY'::frequency),
        ('Fondo de emergencia',   'EXPENSE'::transaction_type, 'savings_investment',false,       300000, 'MONTHLY'::frequency)
) AS t(name, transaction_type, category_code, is_essential, default_amount, frequency)
JOIN categories c
  ON c.code = t.category_code
 AND c.transaction_type = t.transaction_type;
