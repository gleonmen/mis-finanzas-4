import { Fragment, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  deleteTemplate,
  getCategories,
  getTemplates,
  type Category,
  type Template,
} from "../lib/api";
import { formatCurrency } from "../lib/format";
import { categoryColor } from "../lib/colors";
import { categoryRank, groupByType } from "../lib/templateSort";
import {
  categoryAmountsMonthly,
  groupWithSubtotals,
  sectionSummary,
} from "../lib/templateTotals";
import { CategoryBars } from "../components/CategoryBars";
import { EssentialMeter } from "../components/EssentialMeter";
import {
  categoryNames,
  es,
  frequencyNames,
  transactionTypeNames,
} from "../i18n/es";
import { TemplateFormModal } from "../components/TemplateFormModal";
import { Modal } from "../components/Modal";

export function Templates() {
  const t = es.templates;
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Template | null>(null);

  const [deleting, setDeleting] = useState<Template | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function loadTemplates() {
    const list = await getTemplates();
    setTemplates(list);
  }

  useEffect(() => {
    (async () => {
      try {
        const [tpls, cats] = await Promise.all([getTemplates(), getCategories()]);
        setTemplates(tpls);
        setCategories(cats);
      } catch {
        setLoadError(t.loadError);
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function openNew() {
    setEditing(null);
    setFeedback(null);
    setFormOpen(true);
  }

  function openEdit(tpl: Template) {
    setEditing(tpl);
    setFeedback(null);
    setFormOpen(true);
  }

  async function handleSaved(_saved: Template, mode: "create" | "update") {
    setFormOpen(false);
    await loadTemplates();
    setFeedback(mode === "create" ? t.created : t.updated);
  }

  async function confirmDelete() {
    if (!deleting) return;
    setDeleteBusy(true);
    setDeleteError(null);
    try {
      await deleteTemplate(deleting.id);
      setDeleting(null);
      await loadTemplates();
      setFeedback(t.deleted);
    } catch (err) {
      setDeleteError(
        err instanceof ApiError && err.message ? err.message : t.deleteError,
      );
    } finally {
      setDeleteBusy(false);
    }
  }

  function essentialLabel(tpl: Template): string {
    if (tpl.transaction_type !== "EXPENSE") return t.essentialNA;
    return tpl.is_essential ? t.essentialYes : t.essentialNo;
  }

  // Split into income/expense and sort each group (fixed order). Recomputes when
  // templates or the category order change, so a new/edited template lands in place.
  const { income, expense } = useMemo(
    () => groupByType(templates, categoryRank(categories)),
    [templates, categories],
  );

  function renderTemplateRow(tpl: Template) {
    return (
      <tr key={tpl.id}>
        <td>
          <span className={`pill pill-${tpl.transaction_type.toLowerCase()}`}>
            {transactionTypeNames[tpl.transaction_type]}
          </span>
        </td>
        <td>
          <span
            className="cat-dot"
            style={{ backgroundColor: categoryColor(tpl.category_code) }}
          />
          {categoryNames[tpl.category_code] ?? tpl.category_code}
        </td>
        <td>{tpl.name}</td>
        <td>{essentialLabel(tpl)}</td>
        <td className="num">
          {formatCurrency(Math.round(Number(tpl.default_amount)))}
        </td>
        <td>{frequencyNames[tpl.frequency] ?? tpl.frequency}</td>
        <td className="row-actions">
          <button type="button" onClick={() => openEdit(tpl)}>
            {t.edit}
          </button>
          <button
            type="button"
            className="discard"
            onClick={() => {
              setDeleteError(null);
              setDeleting(tpl);
            }}
          >
            {t.delete}
          </button>
        </td>
      </tr>
    );
  }

  function renderSection(
    title: string,
    rows: Template[],
    emptyText: string,
    kind: "income" | "expense",
  ) {
    if (rows.length === 0) {
      return (
        <section className="template-section">
          <h2>{title}</h2>
          <div className="banner banner-warning">{emptyText}</div>
        </section>
      );
    }

    const groups = groupWithSubtotals(rows);
    const summary = sectionSummary(rows);
    const money = (n: number) => formatCurrency(Math.round(n));

    // Chart data: monthly-equivalent per category, sorted desc. Bar only — the
    // detail table with subtotals already lives below in this same section.
    const chartData = categoryAmountsMonthly(rows);
    const chartTitle =
      kind === "income" ? t.chartIncomeByCategory : t.chartExpenseByCategory;

    return (
      <section className="template-section">
        <h2>{title}</h2>

        <div className="section-summary">
          {kind === "expense" && (
            <>
              <span>
                {t.summaryEssential}: <strong>{money(summary.essentialMonthly)}</strong>
                {t.perMonth}
              </span>
              <span>
                {t.summaryNonEssential}:{" "}
                <strong>{money(summary.nonEssentialMonthly)}</strong>
                {t.perMonth}
              </span>
            </>
          )}
          <span>
            {t.summaryTotal}: <strong>{money(summary.totalMonthly)}</strong>
            {t.perMonth}
          </span>
        </div>
        <p className="summary-note">{t.monthlyEquivNote}</p>

        <CategoryBars
          chartData={chartData}
          fullData={chartData}
          title={chartTitle}
          emptyText={t.chartEmpty}
          showTable={false}
        />
        {kind === "expense" && (
          <EssentialMeter
            split={{
              essential: String(summary.essentialMonthly),
              non_essential: String(summary.nonEssentialMonthly),
            }}
            title={t.chartEssentialTitle}
          />
        )}

        <table className="grid">
          <thead>
            <tr>
              <th>{t.colType}</th>
              <th>{t.colCategory}</th>
              <th>{t.colName}</th>
              <th>{t.colEssential}</th>
              <th className="num">{t.colAmount}</th>
              <th>{t.colFrequency}</th>
              <th>{t.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((group) => (
              <Fragment key={group.categoryCode}>
                {group.templates.map(renderTemplateRow)}
                <tr className="subtotal-row" key={`subtotal-${group.categoryCode}`}>
                  <td />
                  <td colSpan={3}>
                    {t.subtotalLabel}{" "}
                    {categoryNames[group.categoryCode] ?? group.categoryCode}
                  </td>
                  <td className="num">
                    {money(group.subtotalMonthly)}
                    {t.perMonth}
                  </td>
                  <td colSpan={2} />
                </tr>
              </Fragment>
            ))}
          </tbody>
        </table>
      </section>
    );
  }

  return (
    <section className="templates">
      <h1>{t.title}</h1>
      <p className="intro">{t.intro}</p>

      <div className="controls">
        <button type="button" className="confirm" onClick={openNew}>
          {t.newButton}
        </button>
      </div>

      {feedback && <div className="banner banner-success">{feedback}</div>}
      {loadError && <div className="banner banner-error">{loadError}</div>}

      {!loading && !loadError && (
        <>
          {renderSection(t.sectionIncome, income, t.emptyIncome, "income")}
          {renderSection(t.sectionExpense, expense, t.emptyExpense, "expense")}
        </>
      )}

      {formOpen && (
        <TemplateFormModal
          template={editing}
          categories={categories}
          onClose={() => setFormOpen(false)}
          onSaved={handleSaved}
        />
      )}

      {deleting && (
        <Modal title={t.confirmTitle} onClose={() => setDeleting(null)}>
          <p>{t.confirmBody(deleting.name)}</p>
          {deleteError && <div className="banner banner-error">{deleteError}</div>}
          <div className="form-actions">
            <button
              type="button"
              className="secondary"
              onClick={() => setDeleting(null)}
              disabled={deleteBusy}
            >
              {t.cancel}
            </button>
            <button
              type="button"
              className="danger"
              onClick={confirmDelete}
              disabled={deleteBusy}
            >
              {t.confirmDelete}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
