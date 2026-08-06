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
  taxes: "Impuestos",
};

export const transactionTypeNames: Record<string, string> = {
  INCOME: "Ingreso",
  EXPENSE: "Gasto",
};

// Payment-status labels depend on the movement type: expenses read as
// paid/pending-to-pay, income as received/pending-to-collect.
export const paymentStatusNames: Record<string, Record<string, string>> = {
  EXPENSE: { PAID: "Pagado", PENDING: "Pendiente de pago" },
  INCOME: { PAID: "Recibido", PENDING: "Pendiente de cobro" },
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
  tabs: {
    templates: "Plantillas",
    monthLoad: "Carga mensual",
    movements: "Movimientos",
    reports: "Reportes",
  },
  movements: {
    title: "Movimientos",
    intro:
      "Revisá y corregí los movimientos de cada mes. También podés registrar " +
      "un gasto o ingreso suelto que no venga de una plantilla.",
    monthLabel: "Mes",
    newButton: "Nuevo movimiento",
    edit: "Editar",
    delete: "Borrar",
    emptyState: "No hay movimientos en este mes. Podés crear uno o cargarlo desde tus plantillas.",
    loadError: "No se pudieron cargar los movimientos.",
    // columns
    colType: "Tipo",
    colCategory: "Categoría",
    colName: "Concepto",
    colEssential: "Esencial",
    colAmount: "Valor",
    colDate: "Fecha",
    colStatus: "Estado",
    colActions: "",
    essentialYes: "Sí",
    essentialNo: "No",
    essentialNA: "—",
    // bulk delete
    deleteAll: "Borrar todos",
    confirmDeleteAllTitle: "Borrar todos los movimientos del mes",
    confirmDeleteAllBody: (count: number, monthYear: string) =>
      `¿Seguro que querés borrar los ${count} movimiento(s) de ${monthYear}? ` +
      `Esta acción no se puede deshacer. El mes quedará libre para volver a cargarlo.`,
    deletedAll: (count: number) => `Se borraron ${count} movimiento(s).`,
    deleteAllError: "No se pudieron borrar los movimientos. Intentá de nuevo.",
    // payment meters (by month)
    paymentExpenseTitle: "Gastos: pagado vs pendiente",
    paymentIncomeTitle: "Ingresos: recibido vs pendiente",
    paid: "Pagado",
    pendingToPay: "Pendiente de pago",
    received: "Recibido",
    pendingToCollect: "Pendiente de cobro",
    noExpenseMeter: "No hay gastos en este mes.",
    noIncomeMeter: "No hay ingresos en este mes.",
    // form
    fieldStatus: "Estado",
    formNewTitle: "Nuevo movimiento",
    formEditTitle: "Editar movimiento",
    fieldType: "Tipo",
    fieldTypeIncome: "Ingreso",
    fieldTypeExpense: "Gasto",
    fieldTypeLocked: "El tipo no se puede cambiar. Si está mal, borrá el movimiento y creá uno nuevo.",
    fieldCategory: "Categoría",
    fieldCategoryPlaceholder: "Elegí una categoría",
    fieldName: "Concepto",
    fieldNamePlaceholder: "Ej: Taxi, Reintegro, Multa…",
    fieldEssential: "Es un gasto esencial",
    fieldAmount: "Valor",
    fieldDate: "Fecha",
    save: "Guardar",
    saving: "Guardando…",
    cancel: "Cancelar",
    errName: "El concepto es obligatorio.",
    errAmount: "El valor debe ser mayor a cero.",
    errCategory: "Elegí una categoría.",
    errDate: "La fecha es obligatoria.",
    genericError: "No se pudo guardar el movimiento. Intentá de nuevo.",
    // feedback
    created: "Movimiento creado.",
    updated: "Movimiento actualizado.",
    deleted: "Movimiento borrado.",
    savedInOtherMonth: (monthYear: string) =>
      `El movimiento quedó registrado en ${monthYear}, por eso no aparece en esta lista.`,
    blocksMonthlyLoad: (monthYear: string) =>
      `Ojo: ${monthYear} ya tiene movimientos, así que la carga mensual quedará bloqueada para ese mes.`,
    // delete confirm
    confirmTitle: "Borrar movimiento",
    confirmBody: (name: string) =>
      `¿Seguro que querés borrar "${name}"? Esta acción no se puede deshacer.`,
    confirmDelete: "Borrar",
    deleteError: "No se pudo borrar el movimiento. Intentá de nuevo.",
  },
  reports: {
    title: "Reportes",
    intro:
      "Mirá en qué se te va la plata, cuánto entra contra cuánto sale, y cómo " +
      "evolucionás a lo largo del año.",
    viewMonthly: "Mensual",
    viewAnnual: "Anual",
    monthLabel: "Mes",
    yearLabel: "Año",
    // KPI tiles
    totalIncome: "Ingresos",
    totalExpense: "Gastos",
    net: "Neto",
    netPositive: "Te sobró",
    netNegative: "Te faltó",
    // charts
    byCategoryTitle: "Gasto por categoría",
    byCategoryEmpty: "No hay gastos en este período.",
    byIncomeTitle: "Ingreso por categoría",
    byIncomeEmpty: "No hay ingresos en este período.",
    tableShareIncome: "% del ingreso",
    topConceptsTitle: "Top conceptos de gasto",
    topConceptsEmpty: "No hay gastos en este período.",
    colConcept: "Concepto",
    otherCategory: "Otros",
    essentialTitle: "Cuánto de tu gasto es esencial",
    essential: "Esencial",
    nonEssential: "No esencial",
    trendTitle: "Evolución mes a mes",
    netByMonthTitle: "Neto por mes",
    // tables
    tableCategory: "Categoría",
    tableAmount: "Monto",
    tableShare: "% del gasto",
    tableMonth: "Mes",
    tableTotal: "Total",
    // states
    empty: "No hay movimientos en este período.",
    noIncome: "No hay ingresos en este período.",
    noExpense: "No hay gastos en este período.",
    loadError: "No se pudo cargar el reporte.",
    retry: "Reintentar",
  },
  templates: {
    title: "Plantillas",
    intro:
      "Administrá tus plantillas de ingresos y gastos. Se usan como base para " +
      "precargar los movimientos de cada mes.",
    newButton: "Nueva plantilla",
    edit: "Editar",
    delete: "Borrar",
    sectionIncome: "Ingresos",
    sectionExpense: "Egresos",
    emptyIncome: "No tenés plantillas de ingreso todavía.",
    emptyExpense: "No tenés plantillas de gasto todavía.",
    // totals (monthly equivalent)
    subtotalLabel: "Subtotal",
    perMonth: "/mes",
    summaryEssential: "Esencial",
    summaryNonEssential: "No esencial",
    summaryTotal: "Total",
    monthlyEquivNote:
      "Equivalente mensual: los valores anuales, trimestrales, etc. se llevan a " +
      "mensual; las plantillas de periodicidad Único no se cuentan.",
    chartIncomeByCategory: "Ingreso por categoría (mensual)",
    chartExpenseByCategory: "Gasto por categoría (mensual)",
    chartEssentialTitle: "Esencial vs no esencial (mensual)",
    chartEmpty: "Sin datos para graficar.",
    colType: "Tipo",
    // (emptyState removed: each section now has its own empty state)
    colCategory: "Categoría",
    colName: "Concepto",
    colEssential: "Esencial",
    colAmount: "Valor por defecto",
    colFrequency: "Periodicidad",
    colActions: "",
    essentialYes: "Sí",
    essentialNo: "No",
    essentialNA: "—",
    loadError: "No se pudieron cargar las plantillas.",
    deleted: "Plantilla borrada.",
    created: "Plantilla creada.",
    updated: "Plantilla actualizada.",
    // form
    formNewTitle: "Nueva plantilla",
    formEditTitle: "Editar plantilla",
    fieldType: "Tipo",
    fieldTypeIncome: "Ingreso",
    fieldTypeExpense: "Gasto",
    fieldCategory: "Categoría",
    fieldCategoryPlaceholder: "Elegí una categoría",
    fieldName: "Concepto",
    fieldNamePlaceholder: "Ej: Arriendo, Netflix, Sueldo…",
    fieldEssential: "Es un gasto esencial",
    fieldAmount: "Valor por defecto",
    fieldFrequency: "Periodicidad",
    save: "Guardar",
    saving: "Guardando…",
    cancel: "Cancelar",
    errName: "El nombre es obligatorio.",
    errAmount: "El valor debe ser mayor a cero.",
    errCategory: "Elegí una categoría.",
    genericError: "No se pudo guardar la plantilla. Intentá de nuevo.",
    // delete confirm
    confirmTitle: "Borrar plantilla",
    confirmBody: (name: string) =>
      `¿Seguro que querés borrar la plantilla "${name}"? Esta acción no se puede deshacer. ` +
      `Los movimientos ya registrados no se ven afectados.`,
    confirmDelete: "Borrar",
    deleteError: "No se pudo borrar la plantilla. Intentá de nuevo.",
  },
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
