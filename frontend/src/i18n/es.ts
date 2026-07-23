// UI strings in Spanish, keyed by the english `code`. Never hardcode user-facing
// text in components; add it here.

export const categoryNames: Record<string, string> = {
  // Income
  salaries: "Sueldos y Salarios",
  freelance: "Trabajos Independientes / Freelance",
  rentals: "Rentas y Alquileres",
  investment_income: "Rendimientos e Inversiones",
  business: "Negocios / Emprendimientos",
  other_income: "Otros Ingresos",
  // Expense
  housing_utilities: "Vivienda y Servicios Públicos",
  food_household: "Alimentación y Hogar",
  transport: "Transporte y Vehículos",
  health: "Salud y Bienestar",
  education: "Educación y Desarrollo",
  lifestyle: "Entretenimiento y Estilo de Vida",
  debt_finance: "Deudas y Finanzas",
  savings_investment: "Ahorro e Inversión",
};

export const transactionTypeNames: Record<string, string> = {
  INCOME: "Ingreso",
  EXPENSE: "Gasto",
};

export const frequencyNames: Record<string, string> = {
  MONTHLY: "Mensual",
  BIMONTHLY: "Bimestral",
  QUARTERLY: "Trimestral",
  SEMIANNUAL: "Semestral",
  ANNUAL: "Anual",
  ONE_TIME: "Único",
};

export const es = {
  appTitle: "Finanzas",
  monthLoad: {
    title: "Carga mensual de movimientos",
    intro:
      "Elegí un mes y cargá todos tus movimientos a partir de tus plantillas. " +
      "Ajustá el valor y la fecha de cada uno, descartá los que no apliquen y confirmá.",
    monthLabel: "Mes",
    loadButton: "Ver movimientos del mes",
    alreadyLoaded:
      "Este mes ya tiene movimientos cargados. No se puede volver a cargar.",
    noTemplates:
      "No hay plantillas configuradas. Primero creá tus plantillas de ingresos y gastos.",
    emptyDraft: "No hay movimientos para cargar. Ajustá o restaurá la grilla.",
    colType: "Tipo",
    colCategory: "Categoría",
    colName: "Concepto",
    colFrequency: "Periodicidad",
    colAmount: "Valor",
    colDate: "Fecha",
    colActions: "",
    discard: "Descartar",
    confirm: "Confirmar carga",
    confirming: "Cargando…",
    successMessage: (n: number, monthYear: string) =>
      `Se cargaron ${n} movimiento(s) en ${monthYear}.`,
    invalidAmount: "El valor debe ser mayor a cero.",
    invalidDate: "La fecha debe pertenecer al mes seleccionado.",
    rowsSummary: (count: number) => `${count} movimiento(s) en el borrador`,
    genericError: "Ocurrió un error al cargar los movimientos. Intentá de nuevo.",
    loadError: "No se pudieron obtener los datos del mes.",
  },
};
