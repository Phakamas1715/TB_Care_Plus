import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

document.addEventListener("DOMContentLoaded", function () {
    const locations = [
        { subdistrict: "เมืองขอนแก่น", district: "เมืองขอนแก่น", province: "ขอนแก่น" },
        { subdistrict: "ศิลา", district: "เมืองขอนแก่น", province: "ขอนแก่น" },
        { subdistrict: "บ้านเป็ด", district: "เมืองขอนแก่น", province: "ขอนแก่น" },
        { subdistrict: "หนองเรือ", district: "หนองเรือ", province: "ขอนแก่น" },
        { subdistrict: "ยางคำ", district: "หนองเรือ", province: "ขอนแก่น" },
        { subdistrict: "บ้านไผ่", district: "บ้านไผ่", province: "ขอนแก่น" },
        { subdistrict: "หัวทะเล", district: "บ้านไผ่", province: "ขอนแก่น" },
        { subdistrict: "ชุมแพ", district: "ชุมแพ", province: "ขอนแก่น" },
        { subdistrict: "น้ำพอง", district: "น้ำพอง", province: "ขอนแก่น" }
    ];

    const subdistrictSelect = document.getElementById("registerSubdistrict");
    const districtSelect = document.getElementById("registerDistrict");

    locations.forEach(loc => {
        let option = new Option(loc.subdistrict, loc.subdistrict);
        subdistrictSelect.appendChild(option);
    });

    subdistrictSelect.addEventListener("change", function () {
        districtSelect.innerHTML = "<option value=''>เลือกอำเภอ</option>";
        const selectedSubdistrict = this.value;
        const matchedDistrict = locations.find(loc => loc.subdistrict === selectedSubdistrict)?.district;
        if (matchedDistrict) {
            let option = new Option(matchedDistrict, matchedDistrict);
            districtSelect.appendChild(option);
        }
    });
});

// Firebase Configuration
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID",
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

document.getElementById("enableNotifications").addEventListener("click", async () => {
    try {
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
            const token = await getToken(messaging, { vapidKey: "YOUR_VAPID_KEY" });
            console.log("🔹 Device Token:", token);
            await saveDeviceTokenToBackend(token);
            alert("✅ เปิดใช้งานแจ้งเตือนสำเร็จ!");
        } else {
            alert("❌ กรุณาอนุญาตการแจ้งเตือน!");
        }
    } catch (error) {
        console.error("❌ Error:", error);
    }
});

async function saveDeviceTokenToBackend(token) {
    try {
        const response = await fetch("/api/save-device-token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
        });
        const result = await response.json();
        console.log("✅ Token saved:", result);
    } catch (error) {
        console.error("❌ Error saving token:", error);
    }
}

onMessage(messaging, (payload) => {
    console.log("🔔 มีข้อความแจ้งเตือน:", payload);
    alert(`📢 ${payload.notification.title}: ${payload.notification.body}`);
});
