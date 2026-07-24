import { useMemo, useState } from "react";
import {
  ApiError,
  createTransaction,
  updateTransaction,
  type Category,
  type Transaction,
  type TransactionCreated,
  type TransactionType,
} from "../lib/api";
import { formatThousands, parseAmount } from "../lib/format";
import { categoryNames, es } from "../i18n/es";
import { Modal } from "./Modal";

interface TransactionFormModalProps {
  transaction: Transaction | null; // null => create
  categories: Category[];
  /** Prefills the date when creating, so a new movement lands in the month being viewed. */
  defaultDate: string;
  onClose: () => void;
  onSaved: (mode: "create" | "update", created?: TransactionCreated) => void;
}

export function TransactionFormModal({
  transaction,
  categories,
  defaultDate,
  onClose,
  onSaved,
}: TransactionFormModalProps) {
  const t = es.movements;
  const isEdit = transaction !== null;

  const initialCategoryId = useMemo<number | null>(() => {
    if (!transaction) return null;
    const match = categories.find(
      (c) =>
        c.code === transaction.category_code &&
        c.transaction_type === transaction.transaction_type,
    );
    return match ? match.id : null;
  }, [transaction, categories]);

  const [type, setType] = useState<TransactionType>(
    transaction?.transaction_type ?? "EXPENSE",
  );
  const [categoryId, setCategoryId] = useState<number | null>(initialCategoryId);
  const [name, setName] = useState(transaction?.name ?? "");
  const [isEssential, setIsEssential] = useState<boolean>(
    transaction?.is_essential ?? false,
  );
  const [amount, setAmount] = useState<number>(
    transaction ? Math.round(Number(transaction.amount)) : 0,
  );
  const [occurredOn, setOccurredOn] = useState<string>(
    transaction?.occurred_on ?? defaultDate,
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filteredCategories = categories.filter(
    (c) => c.transaction_type === type,
  );

  function handleTypeChange(newType: TransactionType) {
    // Only reachable when creating: the type is fixed once the movement exists.
    setType(newType);
    setCategoryId(null);
  }

  const nameValid = name.trim().length > 0;
  const amountValid = amount > 0;
  const categoryValid = categoryId !== null;
  const dateValid = occurredOn !== "";
  const canSave =
    nameValid && amountValid && categoryValid && dateValid && !submitting;

  async function handleSave() {
    if (!canSave || categoryId === null) return;
    setSubmitting(true);
    setError(null);
    const payload = {
      transaction_type: type,
      category_id: categoryId,
      name: name.trim(),
      is_essential: type === "EXPENSE" ? isEssential : null,
      amount,
      occurred_on: occurredOn,
    };
    try {
      if (isEdit) {
        await updateTransaction(transaction!.id, payload);
        onSaved("update");
      } else {
        const created = await createTransaction(payload);
        onSaved("create", created);
      }
    } catch (err) {
      setError(
        err instanceof ApiError && err.message ? err.message : t.genericError,
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal title={isEdit ? t.formEditTitle : t.formNewTitle} onClose={onClose}>
      <div className="form">
        <label className="form-field">
          <span>{t.fieldType}</span>
          <div className="radio-row">
            <label>
              <input
                type="radio"
                name="tx-type"
                checked={type === "INCOME"}
                disabled={isEdit}
                onChange={() => handleTypeChange("INCOME")}
              />
              {t.fieldTypeIncome}
            </label>
            <label>
              <input
                type="radio"
                name="tx-type"
                checked={type === "EXPENSE"}
                disabled={isEdit}
                onChange={() => handleTypeChange("EXPENSE")}
              />
              {t.fieldTypeExpense}
            </label>
          </div>
          {isEdit && <small className="field-hint">{t.fieldTypeLocked}</small>}
        </label>

        <label className="form-field">
          <span>{t.fieldCategory}</span>
          <select
            value={categoryId ?? ""}
            onChange={(e) =>
              setCategoryId(e.target.value === "" ? null : Number(e.target.value))
            }
          >
            <option value="">{t.fieldCategoryPlaceholder}</option>
            {filteredCategories.map((c) => (
              <option key={c.id} value={c.id}>
                {categoryNames[c.code] ?? c.code}
              </option>
            ))}
          </select>
          {!categoryValid && <small className="field-error">{t.errCategory}</small>}
        </label>

        <label className="form-field">
          <span>{t.fieldName}</span>
          <input
            type="text"
            value={name}
            placeholder={t.fieldNamePlaceholder}
            onChange={(e) => setName(e.target.value)}
          />
          {!nameValid && <small className="field-error">{t.errName}</small>}
        </label>

        {type === "EXPENSE" && (
          <label className="form-field checkbox-field">
            <input
              type="checkbox"
              checked={isEssential}
              onChange={(e) => setIsEssential(e.target.checked)}
            />
            <span>{t.fieldEssential}</span>
          </label>
        )}

        <label className="form-field">
          <span>{t.fieldAmount}</span>
          <input
            type="text"
            inputMode="numeric"
            className={amountValid ? "" : "invalid"}
            value={formatThousands(amount)}
            onChange={(e) => setAmount(parseAmount(e.target.value))}
          />
          {!amountValid && <small className="field-error">{t.errAmount}</small>}
        </label>

        <label className="form-field">
          <span>{t.fieldDate}</span>
          {/* No min/max: the date is free and may fall outside the month being viewed. */}
          <input
            type="date"
            className={dateValid ? "" : "invalid"}
            value={occurredOn}
            onChange={(e) => setOccurredOn(e.target.value)}
          />
          {!dateValid && <small className="field-error">{t.errDate}</small>}
        </label>

        {error && <div className="banner banner-error">{error}</div>}

        <div className="form-actions">
          <button type="button" className="secondary" onClick={onClose}>
            {t.cancel}
          </button>
          <button
            type="button"
            className="confirm"
            onClick={handleSave}
            disabled={!canSave}
          >
            {submitting ? t.saving : t.save}
          </button>
        </div>
      </div>
    </Modal>
  );
}
