/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3366FF',
        success: '#52C41A',
        warning: '#FAAD14',
        error: '#F5222D',
        'text-primary': '#000000',
        'text-secondary': '#8C8C8C',
        'border': '#D9D9D9',
        'bg-light': '#F5F5F5',
      },
    },
  },
  plugins: [],
}
