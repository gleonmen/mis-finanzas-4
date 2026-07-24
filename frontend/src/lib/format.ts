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

const monthShortFmt = new Intl.DateTimeFormat("es-CO", { month: "short" });

/** "ene", "feb"… — for chart axis ticks. */
export function formatMonthShort(month: number): string {
  return monthShortFmt.format(new Date(2000, month - 1, 1)).replace(".", "");
}

/** Compact money for axis ticks: "1,3 M" / "450 k". */
export function formatCompact(value: number): string {
  const abs = Math.abs(value);
  if (abs >= 1_000_000) {
    return `${new Intl.NumberFormat("es-CO", { maximumFractionDigits: 1 }).format(value / 1_000_000)} M`;
  }
  if (abs >= 1_000) {
    return `${new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 }).format(value / 1_000)} k`;
  }
  return formatThousands(value);
}
