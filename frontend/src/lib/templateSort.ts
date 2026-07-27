// Grouping + fixed ordering for the Templates view. Pure functions.
//
// Expenses:  category (canonical order) -> essential first -> amount desc
// Income:    category (canonical order) -> amount desc
//
// The canonical category order comes from the categories list (the backend returns
// it ordered by transaction_type, id), so there is a single source of truth for it.

import type { Category, Template } from "./api";

/** Map category_code -> its position in the canonical catalog order. */
export function categoryRank(categories: Category[]): Record<string, number> {
  const rank: Record<string, number> = {};
  categories.forEach((c, i) => {
    rank[c.code] = i;
  });
  return rank;
}

function rankOf(code: string, rank: Record<string, number>): number {
  // An unknown code sorts last instead of breaking the order.
  return code in rank ? rank[code] : Number.MAX_SAFE_INTEGER;
}

function byCategoryThenAmount(
  a: Template,
  b: Template,
  rank: Record<string, number>,
): number {
  const byCat = rankOf(a.category_code, rank) - rankOf(b.category_code, rank);
  if (byCat !== 0) return byCat;
  return Number(b.default_amount) - Number(a.default_amount); // desc
}

/** Expenses: category -> essential first -> amount desc. */
function compareExpense(
  a: Template,
  b: Template,
  rank: Record<string, number>,
): number {
  const byCat = rankOf(a.category_code, rank) - rankOf(b.category_code, rank);
  if (byCat !== 0) return byCat;
  // essential (true) before non-essential (false)
  const essA = a.is_essential ? 0 : 1;
  const essB = b.is_essential ? 0 : 1;
  if (essA !== essB) return essA - essB;
  return Number(b.default_amount) - Number(a.default_amount); // desc
}

/**
 * Split templates into income/expense and sort each group. Array.sort is stable,
 * so ties keep their relative order (no row is lost or duplicated).
 */
export function groupByType(
  templates: Template[],
  rank: Record<string, number>,
): { income: Template[]; expense: Template[] } {
  const income = templates
    .filter((t) => t.transaction_type === "INCOME")
    .sort((a, b) => byCategoryThenAmount(a, b, rank));
  const expense = templates
    .filter((t) => t.transaction_type === "EXPENSE")
    .sort((a, b) => compareExpense(a, b, rank));
  return { income, expense };
}
