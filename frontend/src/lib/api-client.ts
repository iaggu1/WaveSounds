type LeadPayload = { email: string; plan_interest: 'starter' | 'pro'; company_website: string };
const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '');

export async function createLead(payload: LeadPayload): Promise<void> {
  if (!apiUrl) throw new Error('Serviço indisponível no momento. Tente novamente mais tarde.');
  let response: Response;
  try {
    response = await fetch(`${apiUrl}/api/v1/leads`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), cache: 'no-store' });
  } catch {
    throw new Error('Falha de conexão. Verifique sua internet e tente novamente.');
  }
  if (response.ok) return;
  if (response.status === 429) throw new Error('Muitas tentativas. Aguarde um minuto e tente novamente.');
  if (response.status === 422) throw new Error('Confira o endereço de e-mail informado.');
  throw new Error('Não foi possível enviar agora. Tente novamente em instantes.');
}
