importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js");

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAufjcTKbLjo-GchgDKdEkOP-qFpnCPl0o",
    authDomain: "tb-care-plus.firebaseapp.com",
    projectId: "tb-care-plus",
    storageBucket: "tb-care-plus.firebasestorage.app",
    messagingSenderId: "615072952671",
    appId: "1:615072952671:web:20c6d4419c6f8edd4446ea",
    measurementId: "G-0PYBT6KWHG"
  };

const messaging = firebase.messaging();

// ✅ รับการแจ้งเตือนเมื่อเว็บปิดอยู่ (Background Notification)
messaging.onBackgroundMessage((payload) => {
  console.log("🔔 Background Notification:", payload);
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: "/icon.png",
  });
});
