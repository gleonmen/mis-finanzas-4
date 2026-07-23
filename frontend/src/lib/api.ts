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
