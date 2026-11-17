'use client';

import { useEffect, useRef, useState } from 'react';
import { AudioLines, Check, ChevronDown, Download, Headphones, MessageCircle, MoreHorizontal, Pause, Play, Plus, Share2, Volume2 } from 'lucide-react';

const tracks = [
  { name: 'v1_rough_mix.wav', meta: 'WAV · 24-bit / 48kHz', duration: 184, color: 'from-indigo-500 to-violet-400' },
  { name: 'v2_master_24bit.wav', meta: 'WAV · 24-bit / 192kHz', duration: 211, color: 'from-indigo-600 to-sky-400' },
  { name: 'v3_alt_mix.wav', meta: 'FLAC · 24-bit / 96kHz', duration: 196, color: 'from-cyan-500 to-indigo-400' },
];
const comments = [
  { time: 42, label: '00:42', text: 'Aumentar +1.5dB no subgrave aqui', who: 'Marina' },
  { time: 118, label: '01:58', text: 'Voz ficou ótima nessa parte ✨', who: 'Rafael' },
];
const bars = Array.from({ length: 104 }, (_, index) =>
  Math.min(100, 12 + Math.abs((Math.sin(index * 12.9898) * 43758.5453) % 1) * 38 + Math.abs(Math.sin(index * 0.27) * 28)),
);
const stamp = (seconds: number) => `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;

export default function InteractiveAudioPlayer() {
  const [selected, setSelected] = useState(1);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [comment, setComment] = useState(0);
  const audio = useRef<AudioContext | null>(null);
  const oscillator = useRef<OscillatorNode | null>(null);
  const startAt = useRef(0);
  const elapsed = useRef(0);
  const track = tracks[selected];
  const current = Math.round(progress * track.duration);

  useEffect(() => () => {
    oscillator.current?.stop();
    void audio.current?.close();
  }, []);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      const seconds = Math.min(track.duration, elapsed.current + (audio.current?.currentTime ?? startAt.current) - startAt.current);
      setProgress(seconds / track.duration);
      if (seconds >= track.duration) {
        elapsed.current = track.duration;
        oscillator.current?.stop();
        oscillator.current = null;
        setPlaying(false);
      }
    }, 150);
    return () => window.clearInterval(timer);
  }, [playing, track.duration]);

  function togglePlayback() {
    if (playing) {
      elapsed.current = Math.min(track.duration, elapsed.current + (audio.current?.currentTime ?? startAt.current) - startAt.current);
      setProgress(elapsed.current / track.duration);
      oscillator.current?.stop();
      oscillator.current = null;
      setPlaying(false);
      return;
    }

    if (elapsed.current >= track.duration) {
      elapsed.current = 0;
      setProgress(0);
    }
    const context = audio.current ?? new AudioContext();
    audio.current = context;
    if (context.state === 'suspended') void context.resume();
    const oscillatorNode = context.createOscillator();
    const gain = context.createGain();
    oscillatorNode.type = 'sine';
    oscillatorNode.frequency.value = [110, 130.81, 146.83][selected];
    gain.gain.value = 0.025;
    oscillatorNode.connect(gain);
    gain.connect(context.destination);
    oscillatorNode.start();
    oscillator.current = oscillatorNode;
    startAt.current = context.currentTime;
    setPlaying(true);
  }

  function seek(seconds: number) {
    elapsed.current = seconds;
    startAt.current = audio.current?.currentTime ?? 0;
    setProgress(seconds / track.duration);
  }

  function selectTrack(index: number) {
    oscillator.current?.stop();
    oscillator.current = null;
    setPlaying(false);
    elapsed.current = 0;
    setProgress(0);
    setSelected(index);
  }

  return (
    <section aria-label="Prévia interativa do workspace" className="overflow-hidden rounded-2xl border border-gray-200/80 bg-white shadow-[0_18px_70px_-38px_rgba(17,24,39,.25)]">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 px-5 py-4 sm:px-7">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-50 text-indigo-600"><AudioLines size={20} /></div>
          <div><p className="text-sm font-semibold">EP — Horizonte Noturno</p><p className="mt-0.5 text-xs text-gray-500">Master_Final · 3 faixas</p></div>
        </div>
        <div className="flex items-center gap-2">
          <button aria-label="Compartilhar projeto" className="rounded-lg p-2 text-gray-500 hover:bg-gray-50"><Share2 size={16} /></button>
          <button aria-label="Mais opções" className="rounded-lg p-2 text-gray-500 hover:bg-gray-50"><MoreHorizontal size={18} /></button>
          <button className="hidden items-center gap-2 rounded-lg bg-[#111827] px-3.5 py-2 text-xs font-medium text-white sm:flex"><Share2 size={14} /> Compartilhar</button>
        </div>
      </div>

      <div className="grid md:grid-cols-[235px_1fr]">
        <aside className="border-b border-gray-100 p-4 md:border-b-0 md:border-r md:p-5">
          <div className="mb-3 flex items-center justify-between"><span className="text-[11px] font-semibold uppercase tracking-[.12em] text-gray-400">Versões</span><button aria-label="Adicionar faixa" className="rounded-md p-1 text-gray-400 hover:bg-gray-100"><Plus size={15} /></button></div>
          <div className="space-y-1">
            {tracks.map((item, index) => <button key={item.name} onClick={() => selectTrack(index)} className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition-colors ${selected === index ? 'bg-gray-50 ring-1 ring-gray-200' : 'hover:bg-gray-50/70'}`}>
              <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br text-white ${item.color}`}>{selected === index && playing ? <Volume2 size={16} /> : <Headphones size={16} />}</span>
              <span className="min-w-0 flex-1"><span className="block truncate text-xs font-medium text-gray-800">{item.name}</span><span className="mt-1 block text-[10px] text-gray-400">{item.meta}</span></span>
              {selected === index && <Check size={14} className="text-indigo-600" />}
            </button>)}
          </div>
          <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-gray-200 py-2.5 text-xs font-medium text-gray-500 hover:border-gray-300"><Plus size={14} /> Adicionar versão</button>
        </aside>

        <div className="min-w-0 p-5 sm:p-7">
          <div className="flex items-start justify-between">
            <div><div className="flex items-center gap-2"><h3 className="text-sm font-semibold">{track.name}</h3><span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-emerald-700">Lossless</span></div><p className="mt-1 text-xs text-gray-400">{track.meta} · Stereo</p></div>
            <button aria-label="Baixar faixa" className="rounded-lg p-2 text-gray-400 hover:bg-gray-50"><Download size={16} /></button>
          </div>

          <div className="relative mt-7">
            <div className="flex h-[76px] items-center gap-[2px]" aria-hidden="true">
              {bars.map((height, index) => <span key={index} className="wave-bar flex-1 rounded-full" style={{ height: `${height}%`, backgroundColor: index / bars.length < progress ? '#6366f1' : '#e5e7eb' }} />)}
            </div>
            <input aria-label="Posição na faixa" type="range" min={0} max={track.duration} value={current} onChange={(event) => seek(Number(event.target.value))} className="absolute inset-0 z-0 h-full w-full cursor-pointer opacity-0 focus-visible:opacity-20 focus-visible:accent-indigo-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-500" />
            {comments.map((item, index) => <button key={item.time} aria-label={`Comentário ${item.label}: ${item.text}`} onClick={() => { seek(item.time); setComment(index); }} className="absolute top-0 z-10 -translate-x-1/2" style={{ left: `${(item.time / track.duration) * 100}%` }}><span className="block h-2 w-2 rounded-full border-2 border-white bg-indigo-600 ring-2 ring-indigo-100" /></button>)}
            <div className="flex justify-between text-[10px] tabular-nums text-gray-400"><span>{stamp(current)}</span><span>{stamp(track.duration)}</span></div>
          </div>

          <div className="mt-5 flex items-center justify-between">
            <div className="flex items-center gap-3"><button onClick={togglePlayback} aria-label={playing ? 'Pausar áudio' : 'Reproduzir áudio'} className="grid h-11 w-11 place-items-center rounded-full bg-[#111827] text-white transition-transform hover:scale-105">{playing ? <Pause size={18} fill="currentColor" /> : <Play size={18} fill="currentColor" className="ml-0.5" />}</button><span className="text-xs text-gray-500">{playing ? 'Reproduzindo prévia' : 'Ouvir prévia'}</span></div>
            <div className="hidden items-center gap-2 text-xs text-gray-400 sm:flex"><Volume2 size={15} /><span>Original · sem compressão</span></div>
          </div>

          <div className="mt-6 rounded-xl border border-gray-100 bg-gray-50/70 p-3.5 sm:p-4">
            <div className="mb-2 flex items-center justify-between"><span className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-600"><MessageCircle size={13} /> Comentários</span><span className="text-[10px] text-gray-400">2 notas</span></div>
            <div className="flex items-start gap-3"><span className="rounded-md border border-indigo-100 bg-white px-1.5 py-1 font-mono text-[10px] font-medium text-indigo-700">{comments[comment].label}</span><div className="min-w-0"><p className="text-xs text-gray-700">“{comments[comment].text}”</p><p className="mt-1 text-[10px] text-gray-400">{comments[comment].who} · agora</p></div><button aria-label="Próximo comentário" onClick={() => setComment((comment + 1) % comments.length)} className="ml-auto rounded-md p-1 text-gray-400 hover:bg-white"><ChevronDown size={14} /></button></div>
          </div>
        </div>
      </div>
    </section>
  );
}
