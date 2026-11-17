'use client';

import { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const isDark = mounted && resolvedTheme === 'dark';
  const label = isDark ? 'Ativar modo claro' : 'Ativar modo noturno';

  return <button type="button" onClick={() => setTheme(isDark ? 'light' : 'dark')} aria-label={label} aria-pressed={isDark} title={label} className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-gray-200/80 bg-white text-gray-600 transition-colors hover:bg-gray-50 hover:text-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-600">
    {isDark ? <Sun size={17} aria-hidden="true" /> : <Moon size={17} aria-hidden="true" />}
  </button>;
}
