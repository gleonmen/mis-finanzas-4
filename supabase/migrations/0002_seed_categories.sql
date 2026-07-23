-- 0002_seed_categories.sql
-- Fixed category catalog (the "groups"), not user-editable.
-- Spanish display names live in frontend/src/i18n/es.ts, keyed by `code`.
-- Sub-items from the user's list (Arriendo, Netflix, Combustible...) are NOT
-- categories: they belong in a template's `name`.

INSERT INTO categories (code, transaction_type) VALUES
    -- Income (6)
    ('salaries',           'INCOME'),   -- Sueldos y Salarios
    ('freelance',          'INCOME'),   -- Trabajos Independientes / Freelance
    ('rentals',            'INCOME'),   -- Rentas y Alquileres
    ('investment_income',  'INCOME'),   -- Rendimientos e Inversiones
    ('business',           'INCOME'),   -- Negocios / Emprendimientos
    ('other_income',       'INCOME'),   -- Otros Ingresos
    -- Expense (8)
    ('housing_utilities',  'EXPENSE'),  -- Vivienda y Servicios Públicos
    ('food_household',     'EXPENSE'),  -- Alimentación y Hogar
    ('transport',          'EXPENSE'),  -- Transporte y Vehículos
    ('health',             'EXPENSE'),  -- Salud y Bienestar
    ('education',          'EXPENSE'),  -- Educación y Desarrollo
    ('lifestyle',          'EXPENSE'),  -- Entretenimiento y Estilo de Vida
    ('debt_finance',       'EXPENSE'),  -- Deudas y Finanzas
    ('savings_investment', 'EXPENSE');  -- Ahorro e Inversión
