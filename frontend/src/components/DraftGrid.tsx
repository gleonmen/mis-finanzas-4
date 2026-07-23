import type { Template } from "../lib/api";
import { formatThousands, parseAmount } from "../lib/format";
import { isDateInMonth, monthBounds } from "../lib/month";
import { categoryColor } from "../lib/colors";
import {
  categoryNames,
  es,
  frequencyNames,
  transactionTypeNames,
} from "../i18n/es";

export interface DraftRow {
  key: number;
  template: Template;
  amount: number;
  occurredOn: string; // YYYY-MM-DD
}

interface DraftGridProps {
  rows: DraftRow[];
  year: number;
  month: number;
  disabled: boolean;
  onAmountChange: (key: number, amount: number) => void;
  onDateChange: (key: number, date: string) => void;
  onDiscard: (key: number) => void;
}

export function DraftGrid({
  rows,
  year,
  month,
  disabled,
  onAmountChange,
  onDateChange,
  onDiscard,
}: DraftGridProps) {
  const { first, last } = monthBounds(year, month);
  const t = es.monthLoad;

  return (
    <table className="grid">
      <thead>
        <tr>
          <th>{t.colType}</th>
          <th>{t.colCategory}</th>
          <th>{t.colName}</th>
          <th>{t.colFrequency}</th>
          <th className="num">{t.colAmount}</th>
          <th>{t.colDate}</th>
          <th>{t.colActions}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => {
          const amountInvalid = row.amount <= 0;
          const dateInvalid = !isDateInMonth(row.occurredOn, year, month);
          const type = row.template.transaction_type;
          return (
            <tr key={row.key} className={type === "INCOME" ? "row-income" : "row-expense"}>
              <td>
                <span className={`pill pill-${type.toLowerCase()}`}>
                  {transactionTypeNames[type]}
                </span>
              </td>
              <td>
                <span
                  className="cat-dot"
                  style={{ backgroundColor: categoryColor(row.template.category_code) }}
                />
                {categoryNames[row.template.category_code] ?? row.template.category_code}
              </td>
              <td>{row.template.name}</td>
              <td>{frequencyNames[row.template.frequency] ?? row.template.frequency}</td>
              <td className="num">
                <input
                  className={`amount-input${amountInvalid ? " invalid" : ""}`}
                  type="text"
                  inputMode="numeric"
                  disabled={disabled}
                  value={formatThousands(row.amount)}
                  onChange={(e) => onAmountChange(row.key, parseAmount(e.target.value))}
                  aria-label={t.colAmount}
                />
                {amountInvalid && <div className="field-error">{t.invalidAmount}</div>}
              </td>
              <td>
                <input
                  className={`date-input${dateInvalid ? " invalid" : ""}`}
                  type="date"
                  min={first}
                  max={last}
                  disabled={disabled}
                  value={row.occurredOn}
                  onChange={(e) => onDateChange(row.key, e.target.value)}
                  aria-label={t.colDate}
                />
                {dateInvalid && <div className="field-error">{t.invalidDate}</div>}
              </td>
              <td>
                <button
                  type="button"
                  className="discard"
                  disabled={disabled}
                  onClick={() => onDiscard(row.key)}
                >
                  {t.discard}
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
