import { useEffect, useState } from "react";
import {
  getAnnualReport,
  getMonthlyReport,
  type AnnualReport,
  type MonthlyReport,
} from "../lib/api";
import { currentYearMonth } from "../lib/month";
import { formatMonthYear } from "../lib/format";
import { es } from "../i18n/es";
import { StatTiles } from "../components/StatTiles";
import { CategoryBars } from "../components/CategoryBars";
import { EssentialMeter } from "../components/EssentialMeter";
import { AnnualTrend } from "../components/AnnualTrend";

type View = "monthly" | "annual";

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);

export function Reports() {
  const t = es.reports;
  const initial = currentYearMonth();

  const [view, setView] = useState<View>("monthly");
  const [year, setYear] = useState(initial.year);
  const [month, setMonth] = useState(initial.month);

  const [monthly, setMonthly] = useState<MonthlyReport | null>(null);
  const [annual, setAnnual] = useState<AnnualReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      if (view === "monthly") {
        setMonthly(await getMonthlyReport(year, month));
      } else {
        setAnnual(await getAnnualReport(year));
      }
    } catch {
      setError(t.loadError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, year, month]);

  const report = view === "monthly" ? monthly : annual;
  const totals = report?.totals;
  const isEmpty =
    totals !== undefined &&
    Number(totals.income) === 0 &&
    Number(totals.expense) === 0;

  const periodLabel =
    view === "monthly" ? formatMonthYear(year, month) : String(year);

  return (
    <section className="reports">
      <h1>{t.title}</h1>
      <p className="intro">{t.intro}</p>

      {/* One filter row above everything it scopes — never inside a chart card. */}
      <div className="controls filter-row">
        <div className="segmented">
          <button
            type="button"
            className={view === "monthly" ? "seg active" : "seg"}
            onClick={() => setView("monthly")}
          >
            {t.viewMonthly}
          </button>
          <button
            type="button"
            className={view === "annual" ? "seg active" : "seg"}
            onClick={() => setView("annual")}
          >
            {t.viewAnnual}
          </button>
        </div>

        {view === "monthly" && (
          <label className="inline-field">
            <span>{t.monthLabel}</span>
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
            >
              {MONTHS.map((m) => (
                <option key={m} value={m}>
                  {formatMonthYear(year, m).split(" de ")[0]}
                </option>
              ))}
            </select>
          </label>
        )}

        <label className="inline-field">
          <span>{t.yearLabel}</span>
          <input
            type="number"
            min={1970}
            max={9999}
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
          />
        </label>
      </div>

      {error && (
        <div className="banner banner-error">
          {error}{" "}
          <button type="button" className="link-btn" onClick={load}>
            {t.retry}
          </button>
        </div>
      )}

      {/* Hold the previous render at reduced opacity on refetch — no skeleton flash. */}
      {!error && report && (
        <div style={{ opacity: loading ? 0.5 : 1, transition: "opacity 120ms" }}>
          <h2 className="period-label">{periodLabel}</h2>

          {isEmpty ? (
            <div className="banner banner-warning">{t.empty}</div>
          ) : (
            <>
              <StatTiles totals={report.totals} />

              {view === "annual" && annual && (
                <AnnualTrend series={annual.monthly_series} />
              )}

              {/* Money in: where the income comes from. */}
              <CategoryBars
                chartData={report.income_by_category}
                fullData={report.income_by_category}
                title={t.byIncomeTitle}
                shareLabel={t.tableShareIncome}
                emptyText={t.byIncomeEmpty}
              />

              {/* Money out: expense composition (top 7 + "Otros"). */}
              <CategoryBars
                chartData={report.by_category_chart}
                fullData={report.by_category}
              />

              <EssentialMeter split={report.essential} />

              {/* Payment meters: monthly only. */}
              {view === "monthly" && monthly && (
                <>
                  <EssentialMeter
                    split={{
                      essential: monthly.expense_payment.paid,
                      non_essential: monthly.expense_payment.pending,
                    }}
                    title={t.expensePaymentTitle}
                    emptyText={t.noExpense}
                    leftLabel={t.paid}
                    rightLabel={t.pendingToPay}
                  />
                  <EssentialMeter
                    split={{
                      essential: monthly.income_payment.paid,
                      non_essential: monthly.income_payment.pending,
                    }}
                    title={t.incomePaymentTitle}
                    emptyText={t.noIncomeMeter}
                    leftLabel={t.received}
                    rightLabel={t.pendingToCollect}
                  />
                </>
              )}
            </>
          )}
        </div>
      )}
    </section>
  );
}
