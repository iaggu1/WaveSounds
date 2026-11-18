'use client';
import { motion, MotionConfig } from 'framer-motion';
import WaitlistForm from '@/components/WaitlistForm';
import InteractiveAudioPlayer from '@/components/InteractiveAudioPlayer';

export default function HeroSection() {
  return <section id="top" className="overflow-hidden bg-[#F9FAFB] px-5 pb-20 pt-16 sm:pb-24 sm:pt-20"><MotionConfig reducedMotion="user"><motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }} className="mx-auto max-w-7xl text-center"><div className="mb-6 inline-flex items-center gap-2 rounded-full border border-gray-200/80 bg-white px-3.5 py-2 text-xs font-medium text-gray-700 shadow-xs"><span className="h-1.5 w-1.5 rounded-full bg-indigo-600" /> Streaming lossless 24-bit / 192kHz sem compressão</div><h1 className="mx-auto max-w-3xl text-4xl font-semibold leading-[1.12] tracking-[-0.045em] text-[#111827] sm:text-6xl">O espaço silencioso para suas obras em progresso.</h1><p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-gray-600 sm:text-lg">Organize catálogos, compare mixagens em tempo real e compartilhe links privados com clientes — sem perdas de qualidade, sem ruído visual.</p><div id="waitlist" className="mx-auto mt-8 max-w-xl scroll-mt-24"><WaitlistForm /></div><p className="mt-3 text-xs text-gray-500">5 GB gratuitos para sempre <span className="px-1">•</span> Sem cartão de crédito</p><div className="mx-auto mt-14 max-w-4xl text-left"><InteractiveAudioPlayer /></div></motion.div></MotionConfig></section>;
}
