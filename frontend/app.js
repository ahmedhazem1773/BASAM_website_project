let moisture_val = null;
let temp_val = null;
let humidity_val = null;
const BACKEND_URL = "BACKEND_URL"
const API_WEATHER_KEY  = "API_WEATHER_KEY"
const WS_URL = BACKEND_URL.replace("http", "ws"); 
// ================= WebSocket Connection =================
const userData = JSON.parse(localStorage.getItem("userData"));
if (userData && userData.id) {
    const userId = userData.id;
    const ws = new WebSocket(`${WS_URL}/ws/realtimedata/${userId}`);
    ws.onmessage = (event) => {
        const readings = JSON.parse(event.data);
        console.log("البيانات المستلمة:", readings);
        if (document.getElementById('circle1')) {
            if (Array.isArray(readings) && readings.length > 0) {
                const firstBlock = readings[0];
                
                moistureVal(firstBlock.moisture);
                tempVal(firstBlock.temp);
                HumidityVal(firstBlock.humidity);


                setCircle('circle1', firstBlock.moisture, '%');
                setCircle('circle2', firstBlock.temp, '°C');
                setCircle('circle3', firstBlock.humidity, '%');
            }
        } else {
            console.log("إحنا مش في صفحة الـ Dashboard، كود الدوائر مش هيشتغل.");
        }
    };
}else {
    console.error("المستخدم لم يسجل الدخول بعد، لا يمكن فتح الـ WebSocket");
}
// ================= Circles (live update) =================
function setCircle(id, percent, unit){
    const circle = document.getElementById(id);
    const bg = circle.querySelector('.circle-bg');
    const val = document.getElementById('val'+id.slice(-1));
    const deg = percent * 3.6;
    bg.style.background = `conic-gradient( #4cc9f0 ${deg}deg, #1f2a40 ${deg}deg)`;
    val.textContent = percent + unit;
    const side = document.getElementById('sideVal'+id.slice(-1));
    if(side) side.textContent = percent + unit;
}
// ================= Charts data =================
let times=["00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00","08:00","09:00",
             "10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"]; 
//just any number to test only because it work on 24 hours
let moisture=[2,3,4,5,6,7,8,9,5,4,5,5,7,3,2,5,5,7,7,2,7,3];
let temp=[6,6,6,6,6];
let gas=[7,8,5,8,0];
let reades = [];

function collectDailyReadings() {

    //  CLEAR ARRAYS WITHOUT BREAKING CHART REFERENCES
    moisture.length = 0;// reset moisture data
    temp.length = 0;// reset temperature data
    gas.length = 0;// reset gas data
    reades.length = 0;  // reset collected readings
    //  FORCE CHARTS TO REDRAW WITH EMPTY DATA
    chart1.update();
    chart2.update();
    chart3.update();
    console.log("make chart zeros");
}

// ================= Charts =================
const ctx1=document.getElementById('lineChart1').getContext('2d');
const chart1=new Chart(ctx1,{
    type:'line',
    data:{labels:times,datasets:[{label:'Moisture %',data:moisture,borderWidth:2}]},
    options:{responsive:true,plugins:{legend:{position:'bottom'},title:{display:true,text:'Soil Moisture Sensor'}}}
});


const ctx2=document.getElementById('lineChart2').getContext('2d');
const chart2=new Chart(ctx2,{
    type:'line',
    data:{labels:times,datasets:[{label:'Temperature °C',data:temp,borderWidth:2}]},
    options:{responsive:true,plugins:{legend:{position:'bottom'},title:{display:true,text:'Temperature Sensor (DHT22)'}}}
});


const ctx3=document.getElementById('lineChart3').getContext('2d');
const chart3=new Chart(ctx3,{
    type:'line',
    data:{labels:times,datasets:[{label:'Gas %',data:gas,borderWidth:2}]},
    options:{responsive:true,plugins:{legend:{position:'bottom'},title:{display:true,text:'Humidity Sensor (DHT22)'}}}
}); 

// Variables to save database current values
let newGas;
let newMoist;
let newTemp;

function moistureVal(value) {
    console.log("moisture is done and its is :" + value);
    newMoist = value;
    moisture.push(value);
    chart1.update();
    }

function tempVal(value) {
    console.log("temperature is done and its is :" + value);
    newTemp = value;
    temp.push(value);
    chart2.update();
}

function HumidityVal(value) {
    console.log("humidity is done and its is :" + value);
    newGas = value;
    gas.push(value);
    chart3.update();
}

setInterval(() => {
    if (newMoist != null)
        setCircle('circle1', newMoist, '%');

    if (newTemp != null)
        setCircle('circle2', newTemp, '°C');

    if (newGas != null)
        setCircle('circle3', newGas, '%');
}, 1500);

// for testing my chart
// setInterval(() => {
//   HumidityVal(Math.floor(Math.random()*100));
//   moistureVal(Math.floor(Math.random()*100));
//   tempVal(Math.floor(Math.random()*40));
// }, 3000);


const d=new Date();
document.getElementById('dateCircle').textContent=String(d.getDate()).padStart(2,'0');
document.getElementById('dateText').textContent=d.toLocaleString('ar-EG',{month:'long',year:'numeric'});


document.getElementById('info1').textContent='رطوبة مناسبة للنبات';
document.getElementById('info2').textContent='درجة حرارة مستقرة';
document.getElementById('info3').textContent='نسبة الرطوبة ضمن الطبيعي';
//wheather
const weatherResult = document.getElementById("weatherResult");

async function loadWeather(cityName) {
    const url = 
    `https://api.openweathermap.org/data/2.5/weather?q=${cityName}&appid=${API_WEATHER_KEY}&units=metric&lang=ar`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.cod !== 200) {
            weatherResult.innerHTML = "<p> Faild to load weather .-. </p>";
            return;
        }

        weatherResult.innerHTML = `
            <h3>${data.name}</h3>
            <p>الحرارة: ${data.main.temp}°C</p>
            <p>الطقس: ${data.weather[0].description}</p>
            <p>الرطوبة: ${data.main.humidity}%</p>
            <p>الرياح: ${data.wind.speed} م/ث</p>
        `;
    } catch (error) {
        weatherResult.innerHTML = "<p> حدث خطأ أثناء جلب البيانات.</p>";}}

const storedData = localStorage.getItem('userData');
let city = 'Sohag'; // الافتراضي

if (storedData) {
    try {
        const userData = JSON.parse(storedData);
        city = userData.city || 'Sohag';
    } catch(e) {
        console.error("Error parsing user data");
    }
}
loadWeather(city);



// chatpot 
const text = document.getElementById('text');
document.getElementById('sendData').onclick = chat_bot;
text.onkeydown = e => { if (e.key === 'Enter') chat_bot(); };


async function chat_bot() {
    const textInput = text.value;

    fetch(`${BACKEND_URL}/chat_bot`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ text: textInput }),
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("chatResult").innerText = data.bot;
    })
}
//production_model
document.getElementById("press").onclick = crop_predication;
async function crop_predication() {
    const resultElement = document.getElementById("crop-result");
    resultElement.innerText = "جاري التحليل..."
    try {
        const response = await fetch(`${BACKEND_URL}/crop_predication`);
        const resData = await response.json();

        if (response.ok) {
            resultElement.innerText = resData.crop;
            console.log("النتيجة:", resData.crop, "بناءً على:", resData.used_data);
        } else {
            resultElement.innerText = "خطأ في البيانات";
            console.error("Error:", resData.detail);
        }
    } catch (error) {
        console.error("Connection Error:", error);
        resultElement.innerText = "فشل الاتصال";
    }

}

//sign_up
async function handleSignUp() {
    const registrationData = {
        personal_info: {
            first_name: document.getElementById("firstName").value,
            last_name: document.getElementById("lastName").value,
            email: document.getElementById("Email").value,
            password: document.getElementById("pwd").value,
            country: document.getElementById("country").value,
            city: document.getElementById("city").value
        },
        devices_info: [
            {
                serial_number: document.getElementById("Serial").value,
                block_order: 1 
            }
        ]
    };
    try {
        const response = await fetch(`${BACKEND_URL}/user_sign_up`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(registrationData)
        });

        const result = await response.json();
        if (response.status === 201) {
            alert("تم إنشاء الحساب بنجاح!");
            window.location.href = "sign in.html";
        } else {
            alert(result.detail);
        }
    } catch (error) {
        alert("السيرفر مش شغال");
    }
}
//login
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(`${BACKEND_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("isLoggedIn", "true");
            localStorage.setItem("userData", JSON.stringify(data)); 
            const userData = JSON.parse(localStorage.getItem("userData"));
            localStorage.setItem("username", userData.name );
            // window.location.href = "bage.html"; // التوجه للداشبورد
            window.location.href = "index.html";
        } else {
            //showing the error that coming from backend
            alert(data.detail); 
        }
    } catch (error) {
        alert("فشل الاتصال بالباك إند");
    }
}


