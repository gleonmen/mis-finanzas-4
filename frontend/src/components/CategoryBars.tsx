import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CategoryAmount } from "../lib/api";
import { categoryColor, chartInk, OTHER_CODE } from "../lib/colors";
import { formatCompact, formatCurrency } from "../lib/format";
import { categoryNames, es } from "../i18n/es";

/**
 * Composition of spending. A horizontal bar sorted desc — NOT a donut: donuts are
 * an anti-pattern for comparing close values and past ~6 segments, and the Spanish
 * category names are long, which horizontal bars handle. Identity is carried by the
 * axis label, so it never depends on color alone (which also satisfies the
 * contrast "relief" rule for the sub-3:1 slots).
 */
export function CategoryBars({
  chartData,
  fullData,
}: {
  chartData: CategoryAmount[];
  fullData: CategoryAmount[];
}) {
  const t = es.reports;

  if (fullData.length === 0) {
    return (
      <section className="card">
        <h2>{t.byCategoryTitle}</h2>
        <p className="muted">{t.byCategoryEmpty}</p>
      </section>
    );
  }

  const label = (code: string) =>
    code === OTHER_CODE ? t.otherCategory : (categoryNames[code] ?? code);

  const rows = chartData.map((c) => ({
    code: c.category_code,
    name: label(c.category_code),
    value: Number(c.amount),
  }));

  const total = fullData.reduce((sum, c) => sum + Number(c.amount), 0);
  // Height grows with the bar count so the x-axis band is never clipped.
  const height = rows.length * 38 + 40;

  return (
    <section className="card">
      <h2>{t.byCategoryTitle}</h2>
      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
            barCategoryGap={2}
          >
            <CartesianGrid
              horizontal={false}
              stroke={chartInk.grid}
              strokeWidth={1}
            />
            <XAxis
              type="number"
              tickFormatter={formatCompact}
              stroke={chartInk.axis}
              tick={{ fill: chartInk.muted, fontSize: 11 }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={150}
              stroke={chartInk.axis}
              tick={{ fill: chartInk.textSecondary, fontSize: 12 }}
              tickLine={false}
            />
            <Tooltip
              cursor={{ fill: "rgba(11,11,11,0.04)" }}
              formatter={(value: number) => [formatCurrency(value), t.tableAmount]}
              contentStyle={{
                borderRadius: 8,
                border: `1px solid ${chartInk.grid}`,
                fontSize: 12,
              }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
              {rows.map((r) => (
                <Cell key={r.code} fill={categoryColor(r.code)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Table twin: the source of truth, and the relief for sub-3:1 slots. */}
      <table className="grid report-table">
        <thead>
          <tr>
            <th>{t.tableCategory}</th>
            <th className="num">{t.tableAmount}</th>
            <th className="num">{t.tableShare}</th>
          </tr>
        </thead>
        <tbody>
          {fullData.map((c) => {
            const amount = Number(c.amount);
            const share = total > 0 ? Math.round((amount / total) * 100) : 0;
            return (
              <tr key={c.category_code}>
                <td>
                  <span
                    className="cat-dot"
                    style={{ backgroundColor: categoryColor(c.category_code) }}
                  />
                  {label(c.category_code)}
                </td>
                <td className="num">{formatCurrency(amount)}</td>
                <td className="num">{share}%</td>
              </tr>
            );
          })}
          <tr className="total-row">
            <td>{t.tableTotal}</td>
            <td className="num">{formatCurrency(total)}</td>
            <td className="num">100%</td>
          </tr>
        </tbody>
      </table>
    </section>
  );
}
