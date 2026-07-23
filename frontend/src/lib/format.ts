// Centralized currency/locale formatting. Default COP, es-CO, thousands with dot.
// No number formatting should happen outside this module.

const currencyFmt = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const thousandsFmt = new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0,
});

/** "$ 1.300.000" */
export function formatCurrency(value: number): string {
  return currencyFmt.format(value);
}

/** "1.300.000" — for editable amount fields. */
export function formatThousands(value: number): string {
  return thousandsFmt.format(value);
}

/** Parse a user-typed amount ("1.300.000", "$ 44.900") back into a number. */
export function parseAmount(input: string): number {
  const digits = input.replace(/\D/g, "");
  return digits ? parseInt(digits, 10) : 0;
}

/** "julio de 2026" */
export function formatMonthYear(year: number, month: number): string {
  return new Intl.DateTimeFormat("es-CO", {
    month: "long",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
}
