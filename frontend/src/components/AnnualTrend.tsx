import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MonthPoint } from "../lib/api";
import {
  chartInk,
  divergingNegative,
  divergingPositive,
  expenseSeries,
  incomeSeries,
} from "../lib/colors";
import { formatCompact, formatCurrency, formatMonthShort } from "../lib/format";
import { es } from "../i18n/es";

/**
 * Trend over the year. Split into TWO single-axis charts on purpose:
 *  - income vs expense as a 2-series line (legend required for >= 2 series)
 *  - net as a diverging bar around zero (blue positive / red negative — the
 *    documented diverging pair; deliberately NOT green/red, the classic CVD trap)
 * Putting all three on one plot would push toward a dual axis (the #1 chart
 * anti-pattern) or an unreadable zero crossing.
 */
export function AnnualTrend({ series }: { series: MonthPoint[] }) {
  const t = es.reports;

  const data = series.map((p) => ({
    month: formatMonthShort(p.month),
    income: Number(p.income),
    expense: Number(p.expense),
    net: Number(p.net),
  }));

  const tooltipStyle = {
    borderRadius: 8,
    border: `1px solid ${chartInk.grid}`,
    fontSize: 12,
  };

  return (
    <>
      <section className="card">
        <h2>{t.trendTitle}</h2>
        <div style={{ width: "100%", height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 8 }}>
              <CartesianGrid vertical={false} stroke={chartInk.grid} />
              <XAxis
                dataKey="month"
                stroke={chartInk.axis}
                tick={{ fill: chartInk.muted, fontSize: 11 }}
                tickLine={false}
              />
              <YAxis
                tickFormatter={formatCompact}
                stroke={chartInk.axis}
                tick={{ fill: chartInk.muted, fontSize: 11 }}
                tickLine={false}
              />
              <Tooltip
                formatter={(value: number, name: string) => [
                  formatCurrency(value),
                  name === "income" ? t.totalIncome : t.totalExpense,
                ]}
                contentStyle={tooltipStyle}
              />
              <Legend
                formatter={(value) =>
                  value === "income" ? t.totalIncome : t.totalExpense
                }
              />
              <Line
                type="linear"
                dataKey="income"
                stroke={incomeSeries}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="linear"
                dataKey="expense"
                stroke={expenseSeries}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="card">
        <h2>{t.netByMonthTitle}</h2>
        <div style={{ width: "100%", height: 220 }}>
          <ResponsiveContainer>
            <BarChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 8 }}>
              <CartesianGrid vertical={false} stroke={chartInk.grid} />
              <XAxis
                dataKey="month"
                stroke={chartInk.axis}
                tick={{ fill: chartInk.muted, fontSize: 11 }}
                tickLine={false}
              />
              <YAxis
                tickFormatter={formatCompact}
                stroke={chartInk.axis}
                tick={{ fill: chartInk.muted, fontSize: 11 }}
                tickLine={false}
              />
              <ReferenceLine y={0} stroke={chartInk.axis} />
              <Tooltip
                cursor={{ fill: "rgba(11,11,11,0.04)" }}
                formatter={(value: number) => [formatCurrency(value), t.net]}
                contentStyle={tooltipStyle}
              />
              {/* Radius goes on each Cell, not on the Bar: this series crosses
                  zero, so the rounded end must sit on the outer end of each bar
                  (top when positive, bottom when negative) and stay square
                  against the zero baseline. */}
              <Bar dataKey="net" maxBarSize={26} isAnimationActive={false}>
                {data.map((d) => (
                  <Cell
                    key={d.month}
                    fill={d.net >= 0 ? divergingPositive : divergingNegative}
                    // Recharts types Cell's `radius` as a single number, but the
                    // underlying Rectangle accepts a per-corner tuple.
                    radius={
                      (d.net >= 0
                        ? [4, 4, 0, 0]
                        : [0, 0, 4, 4]) as unknown as number
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Table twin for the whole series. */}
      <section className="card">
        <table className="grid report-table">
          <thead>
            <tr>
              <th>{t.tableMonth}</th>
              <th className="num">{t.totalIncome}</th>
              <th className="num">{t.totalExpense}</th>
              <th className="num">{t.net}</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.month}>
                <td>{d.month}</td>
                <td className="num">{formatCurrency(d.income)}</td>
                <td className="num">{formatCurrency(d.expense)}</td>
                <td className="num">{formatCurrency(d.net)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
