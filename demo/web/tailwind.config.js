/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        ocean: {
          50: '#f0f7ff',
          100: '#e0efff',
          200: '#b9dfff',
          300: '#7cc5ff',
          400: '#36a8ff',
          500: '#0c8cef',
          600: '#006fc9',
          700: '#0059a5',
          800: '#054c87',
          900: '#0A1628',
          950: '#060e1a',
        },
        gold: {
          50: '#fef9ec',
          100: '#fcefc9',
          200: '#f9dc8e',
          300: '#f5c44e',
          400: '#f2b028',
          500: '#D4A853',
          600: '#c28a1a',
          700: '#a26816',
          800: '#85521a',
          900: '#6d4419',
        },
        jade: {
          50: '#edfff8',
          100: '#d5ffed',
          200: '#aeffdb',
          300: '#70ffc2',
          400: '#2bfda1',
          500: '#00C9A7',
          600: '#00a287',
          700: '#00806c',
          800: '#066557',
          900: '#085347',
        },
        yiwu: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#D4272C',
          600: '#b91c1c',
          700: '#991b1b',
          800: '#7f1d1d',
          900: '#651a1a',
        },
      },
      fontFamily: {
        display: ['ZCOOL QingKe HuangYou', 'Noto Sans SC', 'sans-serif'],
        body: ['Noto Sans SC', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
