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
import type { ConceptAmount } from "../lib/api";
import { categoryColor, chartInk } from "../lib/colors";
import { formatCompact, formatCurrency } from "../lib/format";
import { categoryNames, es } from "../i18n/es";

/**
 * Top expense concepts of the period, ranked across all categories. A horizontal
 * bar labeled by CONCEPT and colored by the concept's category (Impuestos gray),
 * plus a table with concept / category / amount / % of total expense. Concepts have
 * no color of their own, so identity is the label; color reinforces the category.
 */
export function TopConcepts({
  concepts,
  totalExpense,
}: {
  concepts: ConceptAmount[];
  totalExpense: number;
}) {
  const t = es.reports;

  if (concepts.length === 0) {
    return (
      <section className="card">
        <h2>{t.topConceptsTitle}</h2>
        <p className="muted">{t.topConceptsEmpty}</p>
      </section>
    );
  }

  const rows = concepts.map((c) => ({
    name: c.name,
    code: c.category_code,
    value: Number(c.amount),
  }));
  const height = rows.length * 38 + 40;

  return (
    <section className="card">
      <h2>{t.topConceptsTitle}</h2>
      <div style={{ width: "100%", height }}>
        <ResponsiveContainer>
          <BarChart
            data={rows}
            layout="vertical"
            margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
            barCategoryGap={2}
          >
            <CartesianGrid horizontal={false} stroke={chartInk.grid} strokeWidth={1} />
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
              {rows.map((r, i) => (
                <Cell key={i} fill={categoryColor(r.code)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <table className="grid report-table">
        <thead>
          <tr>
            <th>{t.colConcept}</th>
            <th>{t.tableCategory}</th>
            <th className="num">{t.tableAmount}</th>
            <th className="num">{t.tableShare}</th>
          </tr>
        </thead>
        <tbody>
          {concepts.map((c, i) => {
            const amount = Number(c.amount);
            const share =
              totalExpense > 0 ? Math.round((amount / totalExpense) * 100) : 0;
            return (
              <tr key={i}>
                <td>{c.name}</td>
                <td>
                  <span
                    className="cat-dot"
                    style={{ backgroundColor: categoryColor(c.category_code) }}
                  />
                  {categoryNames[c.category_code] ?? c.category_code}
                </td>
                <td className="num">{formatCurrency(amount)}</td>
                <td className="num">{share}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
