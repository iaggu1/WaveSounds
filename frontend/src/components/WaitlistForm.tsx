'use client';
import { FormEvent, useId, useState } from 'react';
import { Check, Loader2, ArrowRight } from 'lucide-react';
import { createLead } from '@/lib/api-client';

type FormState = 'idle' | 'loading' | 'success' | 'error';
export default function WaitlistForm({ plan = 'starter' }: { plan?: 'starter' | 'pro' }) {
  const [email, setEmail] = useState('');
  const [website, setWebsite] = useState('');
  const [state, setState] = useState<FormState>('idle');
  const [message, setMessage] = useState('');
  const [invalid, setInvalid] = useState(false);
  const formId = useId();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
    setInvalid(!valid);
    if (!valid) { setMessage('Confira o formato do seu e-mail.'); return; }
    setState('loading'); setMessage('');
    try {
      await createLead({ email: email.trim(), plan_interest: plan, company_website: website });
      setState('success');
    } catch (error) {
      setState('error'); setMessage(error instanceof Error ? error.message : 'Não foi possível enviar agora. Tente novamente em instantes.');
    }
  }

  if (state === 'success') return <div role="status" className="flex min-h-[60px] items-center justify-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800"><Check size={18} className="text-emerald-600" /> Acesso liberado. Verifique sua caixa de entrada.</div>;
  return <form onSubmit={submit} noValidate><div className="flex flex-col gap-2 rounded-xl border border-gray-200 bg-white p-1.5 shadow-sm sm:flex-row"><label htmlFor={`email-${formId}`} className="sr-only">Seu e-mail</label><input id={`email-${formId}`} type="email" autoComplete="email" maxLength={255} required disabled={state === 'loading'} value={email} onChange={(e) => { setEmail(e.target.value); setInvalid(false); }} placeholder="voce@estudio.com" className={`min-w-0 flex-1 rounded-lg bg-transparent px-4 py-3 text-sm outline-none placeholder:text-gray-400 disabled:opacity-60 ${invalid ? 'border border-red-300' : ''}`} /><button disabled={state === 'loading'} className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#111827] px-5 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-wait disabled:opacity-70">{state === 'loading' ? <><Loader2 size={16} className="animate-spin" /> Enviando</> : <>{plan === 'pro' ? 'Testar 14 dias grátis' : 'Começar gratuitamente'} <ArrowRight size={16} /></>}</button></div><div className="sr-only" aria-hidden="true"><label htmlFor={`website-${formId}`}>Não preencha este campo</label><input id={`website-${formId}`} name="company_website" type="text" tabIndex={-1} autoComplete="off" value={website} onChange={(e) => setWebsite(e.target.value)} /></div><p aria-live="polite" className={`min-h-[20px] pt-1 text-left text-xs ${invalid || state === 'error' ? 'text-red-600' : 'text-gray-500'}`}>{message || 'Ao continuar, você concorda com nossa política de privacidade.'}</p></form>;
}
