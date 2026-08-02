import { useEffect, useState } from "react";
import {
  ApiError,
  deleteMonthTransactions,
  deleteTransaction,
  getCategories,
  getMonthTransactions,
  type Category,
  type MonthTransactions,
  type Transaction,
  type TransactionCreated,
} from "../lib/api";
import { formatCurrency, formatMonthYear } from "../lib/format";
import { currentYearMonth, monthBounds, parseMonthInput, toMonthInput } from "../lib/month";
import { categoryColor } from "../lib/colors";
import {
  categoryNames,
  es,
  paymentStatusNames,
  transactionTypeNames,
} from "../i18n/es";
import { StatTiles } from "../components/StatTiles";
import { TransactionFormModal } from "../components/TransactionFormModal";
import { Modal } from "../components/Modal";

interface Feedback {
  type: "success" | "warning" | "error";
  text: string;
}

export function Movements() {
  const t = es.movements;
  const initial = currentYearMonth();

  const [monthInput, setMonthInput] = useState(
    toMonthInput(initial.year, initial.month),
  );
  const [data, setData] = useState<MonthTransactions | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Feedback[]>([]);

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Transaction | null>(null);

  const [deleting, setDeleting] = useState<Transaction | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  const [confirmDeleteAll, setConfirmDeleteAll] = useState(false);
  const [deleteAllBusy, setDeleteAllBusy] = useState(false);

  const ym = parseMonthInput(monthInput) ?? initial;

  async function loadMonth() {
    setLoading(true);
    setLoadError(null);
    try {
      setData(await getMonthTransactions(ym.year, ym.month));
    } catch {
      setLoadError(t.loadError);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMonth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monthInput]);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  function openNew() {
    setEditing(null);
    setFeedback([]);
    setFormOpen(true);
  }

  function openEdit(tx: Transaction) {
    setEditing(tx);
    setFeedback([]);
    setFormOpen(true);
  }

  async function handleSaved(
    mode: "create" | "update",
    created?: TransactionCreated,
  ) {
    setFormOpen(false);
    const messages: Feedback[] = [
      { type: "success", text: mode === "create" ? t.created : t.updated },
    ];

    if (mode === "create" && created) {
      const date = created.transaction.occurred_on;
      const [y, m] = [Number(date.slice(0, 4)), Number(date.slice(5, 7))];
      const landedElsewhere = y !== ym.year || m !== ym.month;
      if (landedElsewhere) {
        messages.push({
          type: "warning",
          text: t.savedInOtherMonth(formatMonthYear(y, m)),
        });
      }
      if (created.blocks_monthly_load) {
        messages.push({
          type: "warning",
          text: t.blocksMonthlyLoad(formatMonthYear(y, m)),
        });
      }
    }

    await loadMonth();
    setFeedback(messages);
  }

  async function confirmDelete() {
    if (!deleting) return;
    setDeleteBusy(true);
    try {
      await deleteTransaction(deleting.id);
      setDeleting(null);
      await loadMonth();
      setFeedback([{ type: "success", text: t.deleted }]);
    } catch (err) {
      setFeedback([
        {
          type: "error",
          text:
            err instanceof ApiError && err.message ? err.message : t.deleteError,
        },
      ]);
      setDeleting(null);
    } finally {
      setDeleteBusy(false);
    }
  }

  async function handleDeleteAll() {
    setDeleteAllBusy(true);
    try {
      const { deleted } = await deleteMonthTransactions(ym.year, ym.month);
      setConfirmDeleteAll(false);
      await loadMonth();
      setFeedback([{ type: "success", text: t.deletedAll(deleted) }]);
    } catch (err) {
      setFeedback([
        {
          type: "error",
          text:
            err instanceof ApiError && err.message
              ? err.message
              : t.deleteAllError,
        },
      ]);
      setConfirmDeleteAll(false);
    } finally {
      setDeleteAllBusy(false);
    }
  }

  function essentialLabel(tx: Transaction): string {
    if (tx.transaction_type !== "EXPENSE") return t.essentialNA;
    return tx.is_essential ? t.essentialYes : t.essentialNo;
  }

  const items = data?.items ?? [];

  return (
    <section className="movements">
      <h1>{t.title}</h1>
      <p className="intro">{t.intro}</p>

      <div className="controls filter-row">
        <label className="inline-field">
          <span>{t.monthLabel}</span>
          <input
            type="month"
            value={monthInput}
            onChange={(e) => setMonthInput(e.target.value)}
          />
        </label>
        <button type="button" className="confirm" onClick={openNew}>
          {t.newButton}
        </button>
        {items.length > 0 && (
          <button
            type="button"
            className="danger"
            onClick={() => setConfirmDeleteAll(true)}
          >
            {t.deleteAll}
          </button>
        )}
      </div>

      {feedback.map((f, i) => (
        <div key={i} className={`banner banner-${f.type}`}>
          {f.text}
        </div>
      ))}
      {loadError && <div className="banner banner-error">{loadError}</div>}

      {data && !loadError && (
        <div style={{ opacity: loading ? 0.5 : 1, transition: "opacity 120ms" }}>
          <h2 className="period-label">{formatMonthYear(ym.year, ym.month)}</h2>
          <StatTiles totals={data.totals} />

          {items.length === 0 ? (
            <div className="banner banner-warning">{t.emptyState}</div>
          ) : (
            <table className="grid">
              <thead>
                <tr>
                  <th>{t.colType}</th>
                  <th>{t.colCategory}</th>
                  <th>{t.colName}</th>
                  <th>{t.colEssential}</th>
                  <th className="num">{t.colAmount}</th>
                  <th>{t.colDate}</th>
                  <th>{t.colStatus}</th>
                  <th>{t.colActions}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((tx) => (
                  <tr key={tx.id}>
                    <td>
                      <span
                        className={`pill pill-${tx.transaction_type.toLowerCase()}`}
                      >
                        {transactionTypeNames[tx.transaction_type]}
                      </span>
                    </td>
                    <td>
                      <span
                        className="cat-dot"
                        style={{ backgroundColor: categoryColor(tx.category_code) }}
                      />
                      {categoryNames[tx.category_code] ?? tx.category_code}
                    </td>
                    <td>{tx.name}</td>
                    <td>{essentialLabel(tx)}</td>
                    <td className="num">
                      {formatCurrency(Math.round(Number(tx.amount)))}
                    </td>
                    <td>{tx.occurred_on}</td>
                    <td>
                      <span
                        className={`pill pill-pay-${tx.payment_status.toLowerCase()}`}
                      >
                        {paymentStatusNames[tx.transaction_type][tx.payment_status]}
                      </span>
                    </td>
                    <td className="row-actions">
                      <button type="button" onClick={() => openEdit(tx)}>
                        {t.edit}
                      </button>
                      <button
                        type="button"
                        className="discard"
                        onClick={() => setDeleting(tx)}
                      >
                        {t.delete}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {formOpen && (
        <TransactionFormModal
          transaction={editing}
          categories={categories}
          defaultDate={monthBounds(ym.year, ym.month).first}
          onClose={() => setFormOpen(false)}
          onSaved={handleSaved}
        />
      )}

      {deleting && (
        <Modal title={t.confirmTitle} onClose={() => setDeleting(null)}>
          <p>{t.confirmBody(deleting.name)}</p>
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

      {confirmDeleteAll && (
        <Modal
          title={t.confirmDeleteAllTitle}
          onClose={() => setConfirmDeleteAll(false)}
        >
          <p>
            {t.confirmDeleteAllBody(
              items.length,
              formatMonthYear(ym.year, ym.month),
            )}
          </p>
          <div className="form-actions">
            <button
              type="button"
              className="secondary"
              onClick={() => setConfirmDeleteAll(false)}
              disabled={deleteAllBusy}
            >
              {t.cancel}
            </button>
            <button
              type="button"
              className="danger"
              onClick={handleDeleteAll}
              disabled={deleteAllBusy}
            >
              {t.deleteAll}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
