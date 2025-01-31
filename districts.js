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
        { subdistrict: "โนนหัน", district: "ชุมแพ", province: "ขอนแก่น" },
        { subdistrict: "พล", district: "พล", province: "ขอนแก่น" },
        { subdistrict: "โนนข่า", district: "พล", province: "ขอนแก่น" },
        { subdistrict: "มัญจาคีรี", district: "มัญจาคีรี", province: "ขอนแก่น" },
        { subdistrict: "เขื่อนอุบลรัตน์", district: "อุบลรัตน์", province: "ขอนแก่น" },
        { subdistrict: "โนนสมบูรณ์", district: "อุบลรัตน์", province: "ขอนแก่น" },
        { subdistrict: "บ้านทุ่ม", district: "เมืองขอนแก่น", province: "ขอนแก่น" },
        { subdistrict: "น้ำพอง", district: "น้ำพอง", province: "ขอนแก่น" },
        { subdistrict: "บัวใหญ่", district: "น้ำพอง", province: "ขอนแก่น" },
        { subdistrict: "หนองสองห้อง", district: "หนองสองห้อง", province: "ขอนแก่น" },
        { subdistrict: "หนองบัว", district: "หนองสองห้อง", province: "ขอนแก่น" },
        { subdistrict: "โคกสี", district: "เมืองขอนแก่น", province: "ขอนแก่น" }
    ];

    const subdistrictSelect = document.getElementById("registerSubdistrict");
    const districtSelect = document.getElementById("registerDistrict");

    // ✅ เติมตำบลให้ dropdown
    locations.forEach(loc => {
        let option = new Option(loc.subdistrict, loc.subdistrict);
        subdistrictSelect.appendChild(option);
    });

    // ✅ เมื่อเลือกตำบล -> อัพเดทอำเภอให้อัตโนมัติ
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
