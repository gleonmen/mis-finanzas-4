import type { EssentialSplit } from "../lib/api";
import { formatCurrency } from "../lib/format";
import { SLOTS_LIGHT } from "../lib/colors";
import { es } from "../i18n/es";

const ESSENTIAL_COLOR = SLOTS_LIGHT[0]; // blue
const NON_ESSENTIAL_COLOR = SLOTS_LIGHT[1]; // orange

/**
 * A single ratio against a total -> a meter, NOT a 2-slice pie (explicit
 * anti-pattern). Both amounts and the percentage are labeled, so the value is
 * never gated behind color or a tooltip.
 */
export function EssentialMeter({
  split,
  title = es.reports.essentialTitle,
  emptyText = es.reports.noExpense,
  leftLabel = es.reports.essential,
  rightLabel = es.reports.nonEssential,
}: {
  split: EssentialSplit;
  title?: string;
  emptyText?: string;
  /** Labels for the two parts (left = split.essential, right = split.non_essential). */
  leftLabel?: string;
  rightLabel?: string;
}) {
  const essential = Number(split.essential);
  const nonEssential = Number(split.non_essential);
  const total = essential + nonEssential;

  if (total <= 0) {
    return (
      <section className="card">
        <h2>{title}</h2>
        <p className="muted">{emptyText}</p>
      </section>
    );
  }

  const pct = Math.round((essential / total) * 100);

  return (
    <section className="card">
      <h2>{title}</h2>
      <p className="meter-headline">
        <strong>{pct}%</strong> {leftLabel.toLowerCase()}
      </p>
      <div
        className="meter"
        role="img"
        aria-label={`${pct}% ${leftLabel}, ${100 - pct}% ${rightLabel}`}
      >
        <span
          className="meter-fill"
          style={{ width: `${pct}%`, backgroundColor: ESSENTIAL_COLOR }}
        />
        <span
          className="meter-fill"
          style={{ width: `${100 - pct}%`, backgroundColor: NON_ESSENTIAL_COLOR }}
        />
      </div>
      <ul className="meter-legend">
        <li>
          <span className="cat-dot" style={{ backgroundColor: ESSENTIAL_COLOR }} />
          {leftLabel}: <strong>{formatCurrency(essential)}</strong>
        </li>
        <li>
          <span
            className="cat-dot"
            style={{ backgroundColor: NON_ESSENTIAL_COLOR }}
          />
          {rightLabel}: <strong>{formatCurrency(nonEssential)}</strong>
        </li>
      </ul>
    </section>
  );
}
