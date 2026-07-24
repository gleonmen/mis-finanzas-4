// API client. All calls to the backend go through here.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type TransactionType = "INCOME" | "EXPENSE";

export interface Template {
  id: number;
  name: string;
  transaction_type: TransactionType;
  category_code: string;
  is_essential: boolean | null;
  default_amount: string; // decimal as string
  frequency: string;
}

export interface Category {
  id: number;
  code: string;
  transaction_type: TransactionType;
}

export interface TemplateWrite {
  transaction_type: TransactionType;
  category_id: number;
  name: string;
  is_essential: boolean | null;
  default_amount: number;
  frequency: string;
}

export interface MonthStatus {
  year: number;
  month: number;
  already_loaded: boolean;
  templates: Template[];
}

export interface DraftLineIn {
  template_id: number;
  amount: number;
  occurred_on: string; // YYYY-MM-DD
}

export interface MonthLoadResult {
  created: number;
}

// --- Reports ---------------------------------------------------------------

/** Amounts arrive as decimal strings; convert with Number() at the edge. */
export interface Totals {
  income: string;
  expense: string;
  net: string;
}

export interface CategoryAmount {
  category_code: string; // "OTHER" for the folded tail
  amount: string;
}

export interface EssentialSplit {
  essential: string;
  non_essential: string;
}

export interface MonthPoint {
  month: number;
  income: string;
  expense: string;
  net: string;
}

export interface MonthlyReport {
  year: number;
  month: number;
  totals: Totals;
  by_category: CategoryAmount[];
  by_category_chart: CategoryAmount[];
  essential: EssentialSplit;
}

export interface AnnualReport {
  year: number;
  totals: Totals;
  by_category: CategoryAmount[];
  by_category_chart: CategoryAmount[];
  essential: EssentialSplit;
  monthly_series: MonthPoint[];
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

async function readDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
  } catch {
    // ignore
  }
  return "";
}

export async function getTemplates(): Promise<Template[]> {
  const res = await fetch(`${BASE_URL}/templates`);
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function getCategories(): Promise<Category[]> {
  const res = await fetch(`${BASE_URL}/categories`);
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function createTemplate(payload: TemplateWrite): Promise<Template> {
  const res = await fetch(`${BASE_URL}/templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function updateTemplate(
  id: number,
  payload: TemplateWrite,
): Promise<Template> {
  const res = await fetch(`${BASE_URL}/templates/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function deleteTemplate(id: number): Promise<void> {
  const res = await fetch(`${BASE_URL}/templates/${id}`, { method: "DELETE" });
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
}

export async function getMonthlyReport(
  year: number,
  month: number,
): Promise<MonthlyReport> {
  const res = await fetch(`${BASE_URL}/reports/monthly/${year}/${month}`);
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function getAnnualReport(year: number): Promise<AnnualReport> {
  const res = await fetch(`${BASE_URL}/reports/annual/${year}`);
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  return res.json();
}

export async function getMonthStatus(
  year: number,
  month: number,
): Promise<MonthStatus> {
  const res = await fetch(`${BASE_URL}/months/${year}/${month}/status`);
  if (!res.ok) {
    throw new ApiError(res.status, await readDetail(res));
  }
  return res.json();
}

export async function loadMonth(
  year: number,
  month: number,
  lines: DraftLineIn[],
): Promise<MonthLoadResult> {
  const res = await fetch(`${BASE_URL}/months/${year}/${month}/load`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lines }),
  });
  if (!res.ok) {
    throw new ApiError(res.status, await readDetail(res));
  }
  return res.json();
}
