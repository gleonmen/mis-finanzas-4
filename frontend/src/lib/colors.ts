// Fixed chart palette: color follows the category `code`, in a stable order.
// Do not reassign by ranking. (Placeholder palette — to be validated with the
// dataviz skill when charts are built.)

export const categoryColors: Record<string, string> = {
  // Income
  salaries: "#2E7D6B",
  freelance: "#3E8E7E",
  rentals: "#5BA98F",
  investment_income: "#6FBF9F",
  business: "#83C5A8",
  other_income: "#A7D7C5",
  // Expense
  housing_utilities: "#C0504D",
  food_household: "#D9713B",
  transport: "#E0A458",
  health: "#4E79A7",
  education: "#6A8EAD",
  lifestyle: "#B07AA1",
  debt_finance: "#9C6B4F",
  savings_investment: "#7B8794",
};

export function categoryColor(code: string): string {
  return categoryColors[code] ?? "#9AA0A6";
}
