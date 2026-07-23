import { useState } from "react";
import {
  ApiError,
  getMonthStatus,
  loadMonth,
  type DraftLineIn,
} from "../lib/api";
import { formatMonthYear } from "../lib/format";
import {
  currentYearMonth,
  isDateInMonth,
  monthBounds,
  parseMonthInput,
  toMonthInput,
} from "../lib/month";
import { es } from "../i18n/es";
import { DraftGrid, type DraftRow } from "../components/DraftGrid";

type GridState = "idle" | "ready" | "already_loaded" | "no_templates";

interface Feedback {
  type: "success" | "error";
  text: string;
}

export function MonthLoad() {
  const t = es.monthLoad;
  const initial = currentYearMonth();

  const [monthInput, setMonthInput] = useState(
    toMonthInput(initial.year, initial.month),
  );
  const [loaded, setLoaded] = useState<{ year: number; month: number } | null>(null);
  const [gridState, setGridState] = useState<GridState>("idle");
  const [rows, setRows] = useState<DraftRow[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  async function handleLoad() {
    const ym = parseMonthInput(monthInput);
    if (!ym) return;
    setFeedback(null);
    setRows([]);
    setLoadingStatus(true);
    try {
      const status = await getMonthStatus(ym.year, ym.month);
      setLoaded({ year: ym.year, month: ym.month });
      if (status.already_loaded) {
        setGridState("already_loaded");
      } else if (status.templates.length === 0) {
        setGridState("no_templates");
      } else {
        const { first } = monthBounds(ym.year, ym.month);
        setRows(
          status.templates.map((tpl) => ({
            key: tpl.id,
            template: tpl,
            amount: Math.round(Number(tpl.default_amount)),
            occurredOn: first,
          })),
        );
        setGridState("ready");
      }
    } catch {
      setFeedback({ type: "error", text: t.loadError });
      setGridState("idle");
    } finally {
      setLoadingStatus(false);
    }
  }

  function updateRow(key: number, patch: Partial<DraftRow>) {
    setRows((prev) => prev.map((r) => (r.key === key ? { ...r, ...patch } : r)));
  }

  function discardRow(key: number) {
    setRows((prev) => prev.filter((r) => r.key !== key));
  }

  function rowIsValid(row: DraftRow, year: number, month: number): boolean {
    return row.amount > 0 && isDateInMonth(row.occurredOn, year, month);
  }

  const allValid =
    loaded !== null && rows.every((r) => rowIsValid(r, loaded.year, loaded.month));
  const canConfirm =
    gridState === "ready" && rows.length > 0 && allValid && !submitting;

  async function handleConfirm() {
    if (!loaded || !canConfirm) return;
    setSubmitting(true);
    setFeedback(null);
    const lines: DraftLineIn[] = rows.map((r) => ({
      template_id: r.template.id,
      amount: r.amount,
      occurred_on: r.occurredOn,
    }));
    try {
      const result = await loadMonth(loaded.year, loaded.month, lines);
      const monthYear = formatMonthYear(loaded.year, loaded.month);
      setFeedback({
        type: "success",
        text: t.successMessage(result.created, monthYear),
      });
      setRows([]);
      setGridState("already_loaded");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) setGridState("already_loaded");
        setFeedback({ type: "error", text: err.message || t.genericError });
      } else {
        setFeedback({ type: "error", text: t.genericError });
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="month-load">
      <h1>{t.title}</h1>
      <p className="intro">{t.intro}</p>

      <div className="controls">
        <label htmlFor="month">{t.monthLabel}</label>
        <input
          id="month"
          type="month"
          value={monthInput}
          onChange={(e) => setMonthInput(e.target.value)}
        />
        <button type="button" onClick={handleLoad} disabled={loadingStatus}>
          {t.loadButton}
        </button>
      </div>

      {feedback && (
        <div className={`banner banner-${feedback.type}`}>{feedback.text}</div>
      )}

      {gridState === "already_loaded" && !feedback && (
        <div className="banner banner-warning">{t.alreadyLoaded}</div>
      )}
      {gridState === "no_templates" && (
        <div className="banner banner-warning">{t.noTemplates}</div>
      )}

      {gridState === "ready" && loaded && (
        <>
          {rows.length === 0 ? (
            <div className="banner banner-warning">{t.emptyDraft}</div>
          ) : (
            <>
              <DraftGrid
                rows={rows}
                year={loaded.year}
                month={loaded.month}
                disabled={submitting}
                onAmountChange={(key, amount) => updateRow(key, { amount })}
                onDateChange={(key, occurredOn) => updateRow(key, { occurredOn })}
                onDiscard={discardRow}
              />
              <div className="footer">
                <span className="summary">{t.rowsSummary(rows.length)}</span>
                <button
                  type="button"
                  className="confirm"
                  onClick={handleConfirm}
                  disabled={!canConfirm}
                >
                  {submitting ? t.confirming : t.confirm}
                </button>
              </div>
            </>
          )}
        </>
      )}
    </section>
  );
}
