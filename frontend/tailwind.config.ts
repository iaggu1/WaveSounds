import type { Config } from 'tailwindcss';
const config: Config = { content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'], theme: { extend: { colors: { ink: '#111827', canvas: '#F9FAFB', indigo: { 600: '#4F46E5' } }, boxShadow: { xs: '0 1px 2px rgb(17 24 39 / 0.04)' } } }, plugins: [] };
export default config;
