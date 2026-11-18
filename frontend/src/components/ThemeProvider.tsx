'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import type { ReactNode } from 'react';

export function ThemeProvider({ children, nonce }: { children: ReactNode; nonce?: string }) {
  return <NextThemesProvider nonce={nonce} attribute="class" defaultTheme="light" enableSystem={false} storageKey="forma-theme">{children}</NextThemesProvider>;
}

