import type { Metadata } from 'next';
import { headers } from 'next/headers';
import { Inter, Plus_Jakarta_Sans } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/ThemeProvider';

const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-jakarta', display: 'swap' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' });

export const metadata: Metadata = {
  title: 'forma. — Espaço minimalista para áudio lossless e revisão criativa',
  description: 'Organize versões, compartilhe áudio lossless e receba feedback preciso no timecode. Seu estúdio na nuvem, sem ruído visual.',
  openGraph: { title: 'forma. — Seu estúdio na nuvem', description: 'Compartilhe masters e receba feedback preciso, sem perdas de qualidade.', type: 'website', locale: 'pt_BR', images: [{ url: '/og-image.svg', width: 1200, height: 630, alt: 'forma. — espaço de trabalho para áudio e criação' }] },
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const nonce = (await headers()).get('x-nonce') ?? undefined;

  return <html lang="pt-BR" suppressHydrationWarning><body className={`${jakarta.variable} ${inter.variable}`}><ThemeProvider nonce={nonce}>{children}</ThemeProvider></body></html>;
}

