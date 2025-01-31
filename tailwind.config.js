/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // ✅ รองรับ Dark Mode
  content: [
    "./templates/**/*.html", 
    "./static/**/*.js",       
    "./src/**/*.{js,jsx,ts,tsx,vue}", 
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0288d1", // ✅ สีหลัก (น้ำเงิน)
        secondary: "#01579b", // ✅ สีรอง (น้ำเงินเข้ม)
        accent: "#ffc107", // ✅ สีเน้น (เหลือง)
        success: "#4caf50", // ✅ สีเขียว
        warning: "#ff9800", // ✅ สีส้ม
        danger: "#f44336", // ✅ สีแดง
        dark: "#121212", // ✅ โหมดมืด
        light: "#f5f5f5", // ✅ โหมดสว่าง
        muted: "#9e9e9e", // ✅ สีเทาอ่อน
        info: "#00bcd4", // ✅ สีฟ้าอ่อน
        neutral: "#e0e0e0", // ✅ สีเทากลาง สำหรับ UI ที่อ่านง่ายขึ้น
      },
      fontFamily: {
        sans: ['Inter', 'Arial', 'sans-serif'], // ✅ ฟอนต์อ่านง่าย
        display: ['Poppins', 'sans-serif'], // ✅ ฟอนต์สวยงาม
        mono: ['Fira Code', 'monospace'], // ✅ ฟอนต์สำหรับโค้ด
      },
      boxShadow: {
        soft: "0px 4px 6px rgba(0, 0, 0, 0.1)",
        strong: "0px 6px 10px rgba(0, 0, 0, 0.15)",
        intense: "0px 10px 20px rgba(0, 0, 0, 0.25)", // ✅ เงาเข้ม
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem",
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
        26: "6.5rem",
        30: "7.5rem",
      },
      container: {
        center: true,
        padding: {
          DEFAULT: "1rem",
          sm: "2rem",
          lg: "4rem",
          xl: "5rem",
          "2xl": "6rem",
        },
      },
      transitionProperty: {
        height: "height",
        spacing: "margin, padding",
        opacity: "opacity",
        transform: "transform",
      },
      transitionTimingFunction: {
        inOut: "ease-in-out",
      },
      animation: {
        fade: "fadeIn 0.5s ease-in-out",
        slideIn: "slideIn 0.5s ease-in-out",
        zoom: "zoomIn 0.5s ease-in-out",
        rotate: "rotate 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(0)" },
        },
        zoomIn: {
          "0%": { transform: "scale(0.5)" },
          "100%": { transform: "scale(1)" },
        },
        rotate: {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // ✅ ปรับแต่งฟอร์มให้ดูดีขึ้น
    require('@tailwindcss/typography'), // ✅ ปรับแต่งข้อความ
    require('@tailwindcss/aspect-ratio'), // ✅ รองรับอัตราส่วนภาพ
    require('@tailwindcss/line-clamp'), // ✅ ตัดข้อความที่ยาวเกินไป
    require('tailwind-scrollbar')({ nocompatible: true }), // ✅ ปรับแต่ง Scrollbar
  ],
};
