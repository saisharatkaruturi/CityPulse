import type { Category } from '../../api';
import { useI18n } from '../../i18n';

/**
 * <option>s grouped by issue family. With `families`, each group starts with "All <family>" (the parent
 * id: the server matches its sub-categories too). Categories without a parent go under "Other".
 */
export function CategoryOptions({ categories, families = false, exclude }: {
  categories: Category[]; families?: boolean; exclude?: string | null;
}) {
  const { t } = useI18n();
  const active = categories.filter((c) => c.is_active);
  const parentIds = new Set(active.map((c) => c.parent_id).filter(Boolean) as string[]);
  const parents = active.filter((c) => parentIds.has(c.id)).sort((a, b) => a.code.localeCompare(b.code));
  const loose = active.filter((c) => !c.parent_id && !parentIds.has(c.id)).sort((a, b) => Number(a.is_triage) - Number(b.is_triage) || a.code.localeCompare(b.code));
  return (
    <>
      {parents.map((p) => {
        const kids = active.filter((c) => c.parent_id === p.id && c.id !== exclude).sort((a, b) => a.code.localeCompare(b.code));
        return (
          <optgroup key={p.id} label={p.label}>
            {families && <option value={p.id}>{t('staff.allOf', { family: p.label })}</option>}
            {kids.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
          </optgroup>
        );
      })}
      {loose.length > 0 && (
        <optgroup label={t('family.other')}>
          {loose.filter((c) => c.id !== exclude).map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
        </optgroup>
      )}
    </>
  );
}
