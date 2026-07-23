import { useMemo, useState } from "react";
import {
  ApiError,
  createTemplate,
  updateTemplate,
  type Category,
  type Template,
  type TransactionType,
} from "../lib/api";
import { formatThousands, parseAmount } from "../lib/format";
import { categoryNames, es, frequencyNames } from "../i18n/es";
import { Modal } from "./Modal";

const FREQUENCIES = Object.keys(frequencyNames);

interface TemplateFormModalProps {
  template: Template | null; // null => create
  categories: Category[];
  onClose: () => void;
  onSaved: (saved: Template, mode: "create" | "update") => void;
}

export function TemplateFormModal({
  template,
  categories,
  onClose,
  onSaved,
}: TemplateFormModalProps) {
  const t = es.templates;
  const isEdit = template !== null;

  const initialCategoryId = useMemo<number | null>(() => {
    if (!template) return null;
    const match = categories.find(
      (c) =>
        c.code === template.category_code &&
        c.transaction_type === template.transaction_type,
    );
    return match ? match.id : null;
  }, [template, categories]);

  const [type, setType] = useState<TransactionType>(
    template?.transaction_type ?? "EXPENSE",
  );
  const [categoryId, setCategoryId] = useState<number | null>(initialCategoryId);
  const [name, setName] = useState(template?.name ?? "");
  const [isEssential, setIsEssential] = useState<boolean>(
    template?.is_essential ?? false,
  );
  const [amount, setAmount] = useState<number>(
    template ? Math.round(Number(template.default_amount)) : 0,
  );
  const [frequency, setFrequency] = useState<string>(
    template?.frequency ?? "MONTHLY",
  );
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filteredCategories = categories.filter(
    (c) => c.transaction_type === type,
  );

  function handleTypeChange(newType: TransactionType) {
    setType(newType);
    setCategoryId(null); // categories differ by type; force a re-pick
  }

  const nameValid = name.trim().length > 0;
  const amountValid = amount > 0;
  const categoryValid = categoryId !== null;
  const canSave = nameValid && amountValid && categoryValid && !submitting;

  async function handleSave() {
    if (!canSave || categoryId === null) return;
    setSubmitting(true);
    setError(null);
    const payload = {
      transaction_type: type,
      category_id: categoryId,
      name: name.trim(),
      is_essential: type === "EXPENSE" ? isEssential : null,
      default_amount: amount,
      frequency,
    };
    try {
      const saved = isEdit
        ? await updateTemplate(template!.id, payload)
        : await createTemplate(payload);
      onSaved(saved, isEdit ? "update" : "create");
    } catch (err) {
      setError(err instanceof ApiError && err.message ? err.message : t.genericError);
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
                name="type"
                checked={type === "INCOME"}
                onChange={() => handleTypeChange("INCOME")}
              />
              {t.fieldTypeIncome}
            </label>
            <label>
              <input
                type="radio"
                name="type"
                checked={type === "EXPENSE"}
                onChange={() => handleTypeChange("EXPENSE")}
              />
              {t.fieldTypeExpense}
            </label>
          </div>
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
          <span>{t.fieldFrequency}</span>
          <select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
            {FREQUENCIES.map((f) => (
              <option key={f} value={f}>
                {frequencyNames[f]}
              </option>
            ))}
          </select>
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
