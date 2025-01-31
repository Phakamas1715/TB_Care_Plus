module.exports = {
  plugins: {
    "postcss-import": {}, // รองรับ @import ใน CSS
    "tailwindcss": {},  // ใช้งาน Tailwind CSS
    "autoprefixer": {}, // เติม vendor prefixes ให้ CSS รองรับเบราว์เซอร์เก่า
    "postcss-nested": {}, // รองรับการเขียน CSS แบบ Nested (เหมือน SCSS)
    "cssnano": process.env.NODE_ENV === "production" ? {} : false, // ลดขนาด CSS เมื่อ build production
  },
};

