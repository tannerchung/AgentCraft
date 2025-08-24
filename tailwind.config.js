
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        salesforce: {
          blue: '#0176d3',
          darkblue: '#005fb2',
          lightblue: '#e8f4fd',
          gray: '#f3f2f2',
          darkgray: '#706e6b',
        }
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
