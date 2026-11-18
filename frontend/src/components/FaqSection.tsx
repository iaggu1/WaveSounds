'use client';
import { useState } from 'react';
import { Minus, Plus } from 'lucide-react';
const faqs = [
  ['Vocês comprimem os arquivos de áudio enviados?', 'Mantemos o arquivo recebido (WAV, MP3 ou FLAC) intacto para download e não aplicamos compressão destrutiva adicional ao áudio durante o streaming.'],
  ['Meus clientes precisam criar uma conta para ouvir e comentar?', 'Não. Quem recebe o link acessa o player instantaneamente no navegador do computador ou celular, podendo ouvir e deixar comentários no timecode informando apenas o nome.'],
  ['Posso proteger meus lançamentos inéditos contra vazamentos?', 'Sim. Você pode desativar o botão de download, exigir senha de acesso, definir data de expiração do link e acompanhar o registro de acessos.'],
];
export default function FaqSection() {
  const [open, setOpen] = useState<number | null>(0);
  return <section className="bg-white px-5 py-20 sm:py-24"><div className="mx-auto max-w-2xl"><p className="text-center text-sm font-medium text-indigo-600">Dúvidas comuns</p><h2 className="mt-3 text-center text-3xl font-semibold tracking-[-.04em]">Perguntas frequentes</h2><div className="mt-10 divide-y divide-gray-200/80">{faqs.map(([question, answer], index) => <article key={question} className="py-5"><h3><button aria-expanded={open === index} aria-controls={`faq-${index}`} onClick={() => setOpen(open === index ? null : index)} className="flex w-full items-center justify-between gap-4 text-left text-sm font-semibold"><span>{question}</span>{open === index ? <Minus size={17} className="shrink-0 text-gray-500" /> : <Plus size={17} className="shrink-0 text-gray-500" />}</button></h3><div id={`faq-${index}`} hidden={open !== index} className="max-w-xl pr-8 pt-3 text-sm leading-6 text-gray-600">{answer}</div></article>)}</div></div></section>;
}
