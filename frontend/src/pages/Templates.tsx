import { useEffect, useMemo, useState } from "react";
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

  function renderSection(title: string, rows: Template[], emptyText: string) {
    return (
      <section className="template-section">
        <h2>{title}</h2>
        {rows.length === 0 ? (
          <div className="banner banner-warning">{emptyText}</div>
        ) : (
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
              {rows.map((tpl) => (
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
              ))}
            </tbody>
          </table>
        )}
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
          {renderSection(t.sectionIncome, income, t.emptyIncome)}
          {renderSection(t.sectionExpense, expense, t.emptyExpense)}
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
