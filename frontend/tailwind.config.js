/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0b0f19',
        panel: 'rgba(255, 255, 255, 0.03)',
        border: 'rgba(255, 255, 255, 0.08)',
        primary: '#6366f1',
        primaryHover: '#4f46e5',
        success: '#10b981',
        textMain: '#f3f4f6',
        textMuted: '#9ca3af'
      }
    },
  },
  plugins: [],
}
