// Monthly-equivalent totals for the Templates view. Pure functions.
//
// Templates carry different periodicities, so summing default_amount as-is would mix
// a monthly cost with an annual one. We normalize every amount to a MONTHLY
// EQUIVALENT (annual / 12, quarterly / 3, ...) so the totals are comparable. This is
// a planning view over template defaults — NOT a cash-basis report of real movements,
// where amounts are never prorated.

import type { CategoryAmount, Template } from "./api";

/** Months per period. ONE_TIME is intentionally absent: a one-off is excluded. */
const MONTHLY_DIVISOR: Record<string, number> = {
  MONTHLY: 1,
  BIMONTHLY: 2,
  QUARTERLY: 3,
  SEMIANNUAL: 6,
  ANNUAL: 12,
};

/**
 * Monthly-equivalent contribution of one template.
 *  - ONE_TIME -> 0 (not a recurring monthly cost).
 *  - a known period -> amount / divisor.
 *  - an unknown period (should not happen) -> amount / 1, so the amount is not lost.
 */
export function monthlyEquivalent(tpl: Template): number {
  if (tpl.frequency === "ONE_TIME") return 0;
  const divisor = MONTHLY_DIVISOR[tpl.frequency] ?? 1;
  return Number(tpl.default_amount) / divisor;
}

export interface CategoryGroup {
  categoryCode: string;
  templates: Template[];
  subtotalMonthly: number;
}

/**
 * Walk an already-sorted list (grouped by category via templateSort) and cut it into
 * category groups, accumulating each group's monthly-equivalent subtotal. Preserves
 * the input order.
 */
export function groupWithSubtotals(rows: Template[]): CategoryGroup[] {
  const groups: CategoryGroup[] = [];
  for (const tpl of rows) {
    let group = groups[groups.length - 1];
    if (!group || group.categoryCode !== tpl.category_code) {
      group = { categoryCode: tpl.category_code, templates: [], subtotalMonthly: 0 };
      groups.push(group);
    }
    group.templates.push(tpl);
    group.subtotalMonthly += monthlyEquivalent(tpl);
  }
  return groups;
}

/**
 * Monthly-equivalent total per category, as CategoryAmount[] sorted by amount
 * descending — the shape the bar chart wants (it paints in the given order).
 * Categories whose monthly total is 0 (only ONE_TIME templates) are dropped, so
 * the chart shows no empty bar for them.
 */
export function categoryAmountsMonthly(rows: Template[]): CategoryAmount[] {
  return groupWithSubtotals(rows)
    .filter((g) => g.subtotalMonthly > 0)
    .map((g) => ({
      category_code: g.categoryCode,
      amount: String(g.subtotalMonthly),
    }))
    .sort((a, b) => Number(b.amount) - Number(a.amount));
}

export interface SectionSummary {
  essentialMonthly: number;
  nonEssentialMonthly: number;
  totalMonthly: number;
}

/**
 * Monthly-equivalent totals for a section, split by essential. For income the
 * essential split is meaningless (is_essential is null there); only totalMonthly is
 * used, and non-essential absorbs the income amounts — so totalMonthly stays correct.
 */
export function sectionSummary(rows: Template[]): SectionSummary {
  let essentialMonthly = 0;
  let nonEssentialMonthly = 0;
  for (const tpl of rows) {
    const m = monthlyEquivalent(tpl);
    if (tpl.is_essential) essentialMonthly += m;
    else nonEssentialMonthly += m;
  }
  return {
    essentialMonthly,
    nonEssentialMonthly,
    totalMonthly: essentialMonthly + nonEssentialMonthly,
  };
}
