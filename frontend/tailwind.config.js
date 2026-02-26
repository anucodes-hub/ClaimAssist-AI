/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        dark: "#050505",
        surface: "#111112",
        border: "#222224",
        accent: "#3b82f6",
        success: "#10b981",
        warning: "#f59e0b",
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      }




      
    },
  },
  plugins: [],
}


