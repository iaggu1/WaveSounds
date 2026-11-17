const steps = [
  ['01', 'Arraste seus arquivos WAV, AIFF ou FLAC', 'Upload paralelo de alta velocidade com preservação automática de metadados, BPM e tonalidade.'],
  ['02', 'Personalize a apresentação', 'Adicione capa, notas de versão e escolha se o link permite download ou apenas audição em streaming.'],
  ['03', 'Compartilhe um link único', 'Seus colaboradores ou clientes ouvem em qualquer dispositivo com player instantâneo e deixam feedback centralizado.'],
];
export default function HowItWorks() {
  return <section id="workflow" className="scroll-mt-16 bg-white px-5 py-20 sm:py-24"><div className="mx-auto max-w-6xl"><p className="text-sm font-medium text-indigo-600">Um fluxo mais simples</p><h2 className="mt-3 text-3xl font-semibold tracking-[-.04em] sm:text-4xl">Do exportar ao aprovado em minutos</h2><div className="mt-12 grid divide-y divide-gray-200/80 md:grid-cols-3 md:divide-x md:divide-y-0">{steps.map(([number, title, text]) => <article key={number} className="py-7 md:px-8 md:py-2 md:first:pl-0 md:last:pr-0"><span className="font-mono text-sm font-medium text-indigo-600">{number}</span><h3 className="mt-5 text-base font-semibold leading-6">{title}</h3><p className="mt-2 text-sm leading-6 text-gray-600">{text}</p></article>)}</div></div></section>;
}
