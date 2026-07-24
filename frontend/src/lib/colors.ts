// Fixed chart palette, VALIDATED with the dataviz skill's validator against this
// app's real chart surface (#ffffff): ALL CHECKS PASS — worst adjacent CVD
// ΔE 9.1 (target >= 8), worst adjacent normal-vision ΔE 19.6 (floor 15).
//
// The previous placebo palette FAILED: #6A8EAD vs #4E79A7 measured ΔE 7.2 in
// normal vision (below the 15 floor — indistinguishable even with full color
// vision), #B07AA1 vs #6A8EAD measured 2.8 under protanopia, and 5 slots fell
// below the chroma floor (they read as gray). Do not hand-pick hues here: change
// them only by re-running scripts/validate_palette.js.
//
// Contrast WARN: aqua, yellow and magenta sit below 3:1 on white, so any chart
// using them MUST carry visible labels and a table view (the "relief" rule).
//
// Rules that must not be broken:
//  - Color follows the category `code`, in fixed order. NEVER reassign by rank.
//  - Never generate a 9th hue. The tail folds into "Otros" (neutral gray).
//  - Income (6) and expense (8) are SEPARATE scales: they never share a chart,
//    so the 8-slot ceiling is never exceeded.

/** The validated 8-slot categorical order (light mode). */
const SLOTS_LIGHT = [
  "#2a78d6", // 1 blue
  "#eb6834", // 2 orange
  "#1baf7a", // 3 aqua
  "#eda100", // 4 yellow
  "#e87ba4", // 5 magenta
  "#008300", // 6 green
  "#4a3aa7", // 7 violet
  "#e34948", // 8 red
];

/** Same eight hues stepped for a dark surface (#1a1a19), for when dark mode lands. */
const SLOTS_DARK = [
  "#3987e5",
  "#d95926",
  "#199e70",
  "#c98500",
  "#d55181",
  "#008300",
  "#9085e9",
  "#e66767",
];

/** Expense categories, in fixed slot order (8 categories -> 8 slots). */
const EXPENSE_ORDER = [
  "housing_utilities",
  "food_household",
  "transport",
  "health",
  "education",
  "lifestyle",
  "debt_finance",
  "savings_investment",
];

/** Income categories, in fixed slot order (6 categories -> slots 1-6). */
const INCOME_ORDER = [
  "salaries",
  "freelance",
  "rentals",
  "investment_income",
  "business",
  "other_income",
];

function buildScale(codes: string[]): Record<string, string> {
  return Object.fromEntries(codes.map((code, i) => [code, SLOTS_LIGHT[i]]));
}

export const expenseColors = buildScale(EXPENSE_ORDER);
export const incomeColors = buildScale(INCOME_ORDER);

/** The folded tail. Neutral gray, never a categorical hue. */
export const OTHER_CODE = "OTHER";
export const OTHER_COLOR = "#898781";

export const categoryColors: Record<string, string> = {
  ...incomeColors,
  ...expenseColors,
};

export function categoryColor(code: string): string {
  if (code === OTHER_CODE) return OTHER_COLOR;
  return categoryColors[code] ?? OTHER_COLOR;
}

/** Chart chrome & ink (light mode), from the validated reference instance. */
export const chartInk = {
  surface: "#ffffff",
  grid: "#e1e0d9",
  axis: "#c3c2b7",
  muted: "#898781",
  textPrimary: "#0b0b0b",
  textSecondary: "#52514e",
};

/**
 * Diverging pair for the net (above/below zero). Blue <-> red are warm/cool
 * opposites with a neutral gray midpoint. Deliberately NOT green/red, which is
 * the classic colorblind trap.
 */
export const divergingPositive = "#2a78d6";
export const divergingNegative = "#e34948";

/** Status tokens for the net sign in stat tiles (always paired with a label). */
export const netPositiveInk = "#006300";
export const netNegativeInk = "#d03b3b";

/** Series colors for the income/expense trend lines (slots 1 and 2). */
export const incomeSeries = SLOTS_LIGHT[0];
export const expenseSeries = SLOTS_LIGHT[1];

export { SLOTS_LIGHT, SLOTS_DARK };
