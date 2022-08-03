/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx,css,scss}"],
  theme: {
    extend: {
      colors: {
        oxfordBlue: "#000022",
        bittersweet: "#ff6f59",
        eggshell: "#f1e9da",
        cyberYellow: "#ffd400",
        oldLavender: "#6d6a75",
        gold: "#ffd700",
        silver: "#c0c0c0",
        bronze: "#CD7F32",
        neutral: "b7b7b7",
      },
      boxShadow: {
        slider: "0 0px 5px 1px rgba(255,255,255,0.5)",
        "slider-gauge": "0 0px 3px 1px rgba(255,255,255,0.3)",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
