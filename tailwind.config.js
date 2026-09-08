/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: '#FAF9F5',
          card: '#FFFFFF',
          muted: '#F3F1EA',
          border: '#E3DFD5',
          dark: '#ECE8DC',
          hover: '#F7F5EE',
        },
        charcoal: {
          900: '#171816',
          800: '#282A26',
          700: '#3D403A',
          600: '#585A54',
          500: '#72746D',
          400: '#8C8E87',
          300: '#B2B0A8',
          200: '#D5D3CB',
          100: '#E8E7E1',
        },
        forest: {
          900: '#0E2218',
          800: '#153626',
          700: '#1C4633',
          DEFAULT: '#163626',
          600: '#265B42',
          500: '#347556',
          200: '#CBE0D4',
          100: '#E7F0EB',
          50: '#F2F7F4',
        },
        editorial: {
          amber: '#B45309',
          amberLight: '#FEF3C7',
          rust: '#9A3412',
          rustLight: '#FFEDD5',
          sage: '#2D6A4F',
          sageLight: '#EBF5EE',
          slate: '#334155',
        }
      },
      fontFamily: {
        serif: ['Newsreader', 'Lora', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)',
        'elevated': '0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        'modal': '0 10px 25px -3px rgba(0, 0, 0, 0.08), 0 4px 10px -4px rgba(0, 0, 0, 0.04)',
      },
      borderWidth: {
        hairline: '1px',
      },
    },
  },
  plugins: [],
}
