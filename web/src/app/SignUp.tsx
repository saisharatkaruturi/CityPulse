import '../styles/app.css';
import '../styles/auth.css';

import { useEffect, useId, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api, ApiError } from '../api';
import { useAuth } from '../auth';
import { Icon } from '../components/Icon';
import { useI18n } from '../i18n';
import { afterSignIn, looksLikeEmail } from '../landing/helpers';
import { errorKey, fieldErrors } from '../lib';
import { experienceOf } from '../roles';
import { AuthFrame, FieldError, PasswordField } from './SignIn';

type Fields = 'display_name' | 'email' | 'password';

export default function SignUp() {
  const { signIn } = useAuth();
  const { t, locale } = useI18n();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const id = useId();
  const [f, setF] = useState<Record<Fields, string>>({ display_name: '', email: '', password: '' });
  const [errors, setErrors] = useState<Partial<Record<Fields, string>>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);

  useEffect(() => { document.title = `${t('auth.signUp.title')} · ${t('app.name')}`; }, [t]);

  const set = (k: Fields) => (v: string) => setF((x) => ({ ...x, [k]: v }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (pending.current) return;
    const errs: Partial<Record<Fields, string>> = {};
    if (!f.display_name.trim()) errs.display_name = t('auth.err.nameRequired');
    if (!f.email.trim()) errs.email = t('auth.err.emailRequired');
    else if (!looksLikeEmail(f.email)) errs.email = t('auth.err.emailFormat');
    if (f.password.length < 10) errs.password = f.password ? t('auth.err.passwordShort') : t('auth.err.passwordRequired');
    setErrors(errs);
    setFormError(null);
    const first = (['display_name', 'email', 'password'] as Fields[]).find((k) => errs[k]);
    if (first) {
      document.getElementById(`${id}-${first}`)?.focus();
      return;
    }
    pending.current = true;
    setBusy(true);
    try {
      await api('/auth/register', { body: { ...f, display_name: f.display_name.trim(), email: f.email.trim(), preferred_language: locale } });
      const me = await signIn(f.email.trim(), f.password);
      // Residents land on the report form unless they came here from a specific page.
      nav(params.get('next') ? afterSignIn(params.get('next'), experienceOf(me.roles)) : '/app/report', { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.code === 'registration_disabled') setFormError(t('auth.signUp.disabled'));
      else if (err instanceof ApiError && err.status === 409) setFormError(t('auth.signUp.taken'));
      else {
        const fe = fieldErrors(err) as Partial<Record<Fields, string>>;
        if (Object.keys(fe).length) setErrors(fe);
        const k = errorKey(err);
        setFormError(t(k.key, k.vars));
      }
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return (
    <AuthFrame>
      <div className="auth-card glass">
        <h1 className="auth-title">{t('auth.signUp.title')}</h1>
        <p className="auth-lead">{t('auth.signUp.lead')}</p>
        <form className="stack auth-form" onSubmit={submit} noValidate aria-describedby={formError ? `${id}-form-err` : undefined}>
          <div className="field">
            <label htmlFor={`${id}-display_name`}>{t('auth.field.name')}</label>
            <input id={`${id}-display_name`} className="input" autoComplete="name" value={f.display_name} maxLength={120}
              onChange={(e) => set('display_name')(e.target.value)} aria-invalid={Boolean(errors.display_name)}
              aria-describedby={`${id}-name-hint${errors.display_name ? ` ${id}-name-err` : ''}`} />
            <span id={`${id}-name-hint`} className="hint">{t('auth.field.nameHint')}</span>
            <FieldError id={`${id}-name-err`} text={errors.display_name} />
          </div>
          <div className="field">
            <label htmlFor={`${id}-email`}>{t('auth.field.email')}</label>
            <input id={`${id}-email`} className="input" type="email" inputMode="email" autoComplete="email" value={f.email}
              onChange={(e) => set('email')(e.target.value)} aria-invalid={Boolean(errors.email)}
              aria-describedby={errors.email ? `${id}-email-err` : undefined} spellCheck={false} autoCapitalize="none" />
            <FieldError id={`${id}-email-err`} text={errors.email} />
          </div>
          <div className="field">
            <label htmlFor={`${id}-password`}>{t('auth.field.password')}</label>
            <PasswordField id={`${id}-password`} value={f.password} onChange={set('password')} error={errors.password}
              autoComplete="new-password" describedBy={`${id}-pw-hint`} />
            <span id={`${id}-pw-hint`} className="hint">{t('auth.field.passwordHint')}</span>
            <FieldError id={`${id}-password-err`} text={errors.password} />
          </div>
          {formError && <p id={`${id}-form-err`} className="notice notice-bad auth-error" role="alert"><Icon.alert size={16} />{formError}</p>}
          <button className="btn btn-primary btn-block" type="submit" disabled={busy} aria-busy={busy}>
            {busy ? t('auth.signUp.busy') : t('auth.signUp.submit')}
          </button>
        </form>
        <p className="auth-alt">{t('auth.signUp.haveAccount')} <Link to="/signin">{t('nav.signIn')}</Link></p>
        <p className="auth-alt"><Link to="/"><Icon.chevronLeft size={16} /> {t('auth.backHome')}</Link></p>
      </div>
    </AuthFrame>
  );
}
