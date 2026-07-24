import type { Totals } from "../lib/api";
import { formatCurrency } from "../lib/format";
import { netNegativeInk, netPositiveInk } from "../lib/colors";
import { es } from "../i18n/es";

/**
 * Three headline numbers -> a KPI row of stat tiles, NOT a grouped bar chart.
 * The net sign is carried by an explicit label + arrow as well as color, so it
 * never depends on color alone.
 */
export function StatTiles({ totals }: { totals: Totals }) {
  const t = es.reports;
  const net = Number(totals.net);
  const positive = net >= 0;

  return (
    <div className="kpi-row">
      <div className="kpi">
        <span className="kpi-label">{t.totalIncome}</span>
        <span className="kpi-value">{formatCurrency(Number(totals.income))}</span>
      </div>
      <div className="kpi">
        <span className="kpi-label">{t.totalExpense}</span>
        <span className="kpi-value">{formatCurrency(Number(totals.expense))}</span>
      </div>
      <div className="kpi">
        <span className="kpi-label">{t.net}</span>
        <span
          className="kpi-value"
          style={{ color: positive ? netPositiveInk : netNegativeInk }}
        >
          {formatCurrency(net)}
        </span>
        <span
          className="kpi-note"
          style={{ color: positive ? netPositiveInk : netNegativeInk }}
        >
          {positive ? "▲" : "▼"} {positive ? t.netPositive : t.netNegative}
        </span>
      </div>
    </div>
  );
}
