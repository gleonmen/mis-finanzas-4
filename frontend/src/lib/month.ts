// Helpers for working with a calendar month (year + month, 1-based).

export interface YearMonth {
  year: number;
  month: number; // 1-12
}

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

/** First and last day of the month as YYYY-MM-DD (for <input type="date"> bounds). */
export function monthBounds(year: number, month: number): { first: string; last: string } {
  return {
    first: `${year}-${pad2(month)}-01`,
    last: `${year}-${pad2(month)}-${pad2(daysInMonth(year, month))}`,
  };
}

/** True if a YYYY-MM-DD date string falls within the given month. */
export function isDateInMonth(dateStr: string, year: number, month: number): boolean {
  const { first, last } = monthBounds(year, month);
  return dateStr >= first && dateStr <= last;
}

export function currentYearMonth(): YearMonth {
  const now = new Date();
  return { year: now.getFullYear(), month: now.getMonth() + 1 };
}

/** "2026-07" -> { year: 2026, month: 7 } (null if malformed). */
export function parseMonthInput(value: string): YearMonth | null {
  const match = /^(\d{4})-(\d{2})$/.exec(value);
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  if (month < 1 || month > 12) return null;
  return { year, month };
}

/** { year: 2026, month: 7 } -> "2026-07" (for <input type="month">). */
export function toMonthInput(year: number, month: number): string {
  return `${year}-${pad2(month)}`;
}
