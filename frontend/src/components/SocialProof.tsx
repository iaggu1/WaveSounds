const names = ['KINETIC AUDIO', 'MONOGRAPH RECORDS', 'ESTÚDIO SÍNTESE', 'AETHER SOUND', 'SOLARIS LAB'];
export default function SocialProof() {
  return <section aria-label="Comunidade forma" className="border-y border-gray-200/80 bg-white px-5 py-9"><div className="mx-auto max-w-6xl"><p className="text-center text-[10px] font-semibold tracking-[.16em] text-gray-400">UTILIZADO POR PRODUTORES, ENGENHEIROS DE MASTERIZAÇÃO E SELOS INDEPENDENTES</p><div className="mt-6 flex flex-wrap items-center justify-center gap-x-12 gap-y-5 text-xs font-semibold tracking-[.1em] text-gray-400 sm:text-sm">{names.map((name) => <span key={name}>{name}</span>)}</div></div></section>;
}
