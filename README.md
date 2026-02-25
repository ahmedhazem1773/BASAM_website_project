# 🌿 BASAM (Basic Automated Soil & Agriculture Monitoring)

**BASAM** is a professional IoT ecosystem integrated with Advanced Artificial Intelligence, designed to transform traditional farming into Data-Driven Agriculture. It provides a centralized hub for real-time soil analytics, intelligent crop forecasting, and a cognitive AI assistant for precision farming.

---

## 🚀 Key Features

- **📡 Real-Time Telemetry & Monitoring**
    - **High-Precision Tracking:** Real-time monitoring of Soil Moisture, Ambient Temperature, and Atmospheric Humidity.
    - **Instant Data Sync:** Low-latency synchronization via **Firebase Realtime Database**.
    - **Live Dashboard:** Streaming using **FastAPI WebSockets** for zero-latency updates and visualization.

- **🤖 AI Intelligence Layer**
    - **Crop Prediction:** Integrated Machine Learning engine (Keras/TensorFlow) that identifies the most compatible crops based on live soil profile analysis.
    - **Agricultural Expert AI:** Powered by **Google Gemini 2.5 Flash** for specialized consultations, diagnosing soil deficiencies, and providing actionable irrigation advice.

- **📊 Industrial-Grade Architecture**
    - **Multi-User Security:** Secure authentication framework with **Bcrypt** cryptographic password hashing.
    - **Data Persistence:** Relational storage in **MySQL** for system metadata, user profiles, and historical telemetry auditing.
    - **Multi-Device Scalability:** Support for managing multiple agricultural blocks under a single user account.

---

## 🏗️ Evolution of BASAM

### **Phase 1: Concept & AI Prototype**
* **Backend:** Initial implementation focused on serving the **Prediction Model** and basic **Chatbot API**.
* **Data:** Direct bridge between the web interface and **Firebase**; lacked persistent relational storage.
* **Hardware:** Basic sensor connectivity (DHT22 and Resistive Soil Moisture) without dynamic provisioning.
* **User Experience:** Static environment with no user accounts or session management.

### **Phase 2: Full Scalable Infrastructure (Current)**
* **Advanced Backend:** Re-engineered **FastAPI** to handle complex business logic, relational integrity, and real-time **WebSockets** for high-frequency data streaming.
* **Relational Database:** Integration of **MySQL** to manage a hierarchical data structure (**User → Agricultural Blocks → IoT Devices**).
* **Smart Actuation:** Integrated an **Automated Water Pump** system controlled by **Programmatic Logic** to execute precision irrigation based on real-time sensor thresholds.
* **Dynamic Connectivity:** Integrated **WiFiManager** on ESP32 for seamless, on-field configuration without hardcoded credentials.
* **Energy Autonomy:** Transitioned to a sustainable **Solar-Powered System** featuring:
     Solar Panel, TP4056 charging circuit, and Lithium-Ion battery for 24/7 off-grid operation.
* **Intelligence Upgrade:** Transitioned to **Gemini 2.5 Flash** for superior agricultural reasoning.

---

## 🛠️ Technologies Used

### **Backend & Intelligence**
- **Python (FastAPI)** - Asynchronous API and WebSocket management.
- **SQLAlchemy (ORM)** - Advanced database abstraction and relational mapping.
- **Google GenAI (Gemini 2.5 Flash)** - State-of-the-art LLM for agricultural consultation.
- **TensorFlow / Keras** - Neural network execution for predictive analytics.

### **Cloud & Data Connectivity**
- **Firebase RTDB** - Real-time synchronization bridge for hardware-to-cloud data.
- **MySQL** - Secure relational storage for users, farm blocks, and time-series sensor history.

---

## 🌐 Data Structure & Hierarchy

The system employs a hybrid data architecture. **MySQL** handles the relational integrity of users and devices, while **Firebase** manages the real-time telemetry fleet.
###  Relational Architecture (MySQL)
* **`User`**: Manages encrypted credentials (Bcrypt) and secure personal profiles.
* **`Block`**: Handles relational mapping of specific agricultural sections or "fields" assigned to users.
* **`Device`**: Responsible for linking physical hardware (via unique Serial Numbers) to specific blocks.
* **`Soil_Readings`**: Provides persistent time-series logging for Moisture, Temperature, and Humidity for historical auditing.


### **Real-time Hierarchy (Firebase JSON)**
The following structure represents how telemetry is organized in the **Firebase Realtime Database** for instant synchronization:

```json
{
  "Data_Hierarchy": {
    "User": {
      "Relations": ["Blocks", "Devices"],
      "Agricultural_Blocks": {
        "Fields": ["Block_Metadata", "Location"],
        "Device_Fleet": [
          {
            "Hardware_ID": "Serial_Number",
            "Telemetry": ["Moisture", "Temp", "Humidity", "Timestamp"]
          }
        ]
      }
    }
  }
}
```
---

## 👥 Authors & Team Contributions

### **Phase 2 (Current Core Team)**
* [**Ahmed Hazem**](https://www.linkedin.com/in/ahmed-hazem-7730262b9/) - Team Leader & Lead Backend Architect (Full System Logic & Integration).
* [**Bassam El-Badry**](https://www.linkedin.com/in/bassam-albadry-414102360/) - Frontend Engineering Leader.
* [**Mohraiel Ayman**](https://www.linkedin.com/in/mohraeil-ayman-66450637b/) - Frontend Development & UI/UX Design.
* [**Ahmed M. Khalafallah**](https://www.linkedin.com/in/ahmed-m-khalafallah-335475350/) - Hardware Engineering Leader & Embedded Systems Code.
* [**Islam Fathy**](https://www.linkedin.com/in/islam-fathy-81a2b1358/) - Hardware Implementation & Field Deployment (Solar & Power Management).
* [**Ahmed El-Sayed**](https://www.linkedin.com/in/ahmed-elsayed-a628a1363/) - Hardware Systems Support & Pump Control Logic.
* [**Abdalluh Mahmoud**](https://www.linkedin.com/in/abdalluh-mahmoud-a59b9733b/) - Hardware Systems Support.
* [**Aymen Abdel-Hasib**](https://www.linkedin.com/in/ayman-abdel-hasib-bilal-9b1bb735b/) - Hardware Systems Support.
* [**Youssef Bahaa**](https://www.linkedin.com/in/youssef-mazen-818128361/) - Design & Fabrication Leader (Full implementation of the **BASAM Case** using **Autodesk Fusion 360**).

### **Phase 1 (Contributors)**
* [**Seif Ashraf**](https://www.linkedin.com/in/seif-a-mohamed/) - Responsible for the **Prediction Model** development.
* [**Ahmed Hatem**](https://www.linkedin.com/in/ahmed-hatem-882527318/) - Backend Support (**Chatbot Integration** development).
* [**Sama Mohamed**](https://www.linkedin.com/in/sama-mohammed-503915364/) - Website & Hardware Connectivity.
* [**Mohamed Ali**](https://www.linkedin.com/in/%D9%85%D8%AD%D9%85%D8%AF-%D8%B9%D9%84%D9%8A-%D9%82%D8%A7%D8%B9%D9%88%D8%AF-ab91893a7/) - Design & Fabrication Support.

---

**BASAM — Precision Agriculture for a Sustainable Future.**
