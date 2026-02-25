from fastapi import FastAPI , WebSocket , Depends , status , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel , EmailStr
import uvicorn
import base64
import os
from dotenv import load_dotenv , find_dotenv
from google import genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, db
from contextlib import asynccontextmanager
import asyncio
import json
from sqlalchemy.orm import Session 
from sqlalchemy import func
from typing import Annotated
from datetime import datetime, timedelta, timezone
import time
import bcrypt
import launch_model
import DataBase
class UserBase(BaseModel):
    first_name : str
    last_name : str
    email : EmailStr
    password : str
    country : str = None
    city : str = None
class DeviceBase(BaseModel) : 
    serial_number : str
    block_order : int
class EntryData(BaseModel):
    personal_info : UserBase
    devices_info : list[DeviceBase]
class LoginSchema(BaseModel):
    email: EmailStr
    password: str
#connect env variables
dataenv_path=find_dotenv()
if  dataenv_path :
    load_dotenv(dataenv_path)
else:
    print("not found")
#get gemini key
Gemini_key=os.getenv("apikey_Gemini")
#make firebase configuration
firebase_config = {
                'credential_path': os.getcwd()+"/backend/serviceAccountKey.json",
                'database_url': os.getenv("databaseURL_Firebase")
            }
#
origins_raw = os.getenv("ALLOWED_ORIGINS")
origins = origins_raw.split(",")
#make sure if tables we created in database is exist in mysql or will create it 
DataBase.Base.metadata.create_all(bind=DataBase.engine)
# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config["credential_path"])
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_config["database_url"]
    })
ref = db.reference("/")
#for passwords
def hashing_password(password : str) :
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password_bytes, salt)
    return password_hashed.decode('utf-8')
def verify_password(plain_password: str, hashed_password: str):
    password_byte_enc = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)
#get_database_for_fastapi
def get_db():
    db_BASAM_website = DataBase.sessionlocal()
    db_BASAM_website.commit()
    try :
        yield db_BASAM_website
    finally:
        db_BASAM_website.close()
db_dependency = Annotated[Session , Depends(get_db)]
last_cached_averages = []
def calcucate_readings_for_showing(user_id: int):
    global last_cached_averages
    with DataBase.sessionlocal() as db:
        latest_ids_subquery = db.query(
            func.max(DataBase.Soil_Readings.id).label('max_id')
        ).join(DataBase.Device).filter(DataBase.Device.user_id == user_id).group_by(DataBase.Soil_Readings.device_id).subquery()
        results = db.query(
            DataBase.Block.block_name,
            func.avg(DataBase.Soil_Readings.moisture).label('moisture'),
            func.avg(DataBase.Soil_Readings.humidity).label('humidity'),
            func.avg(DataBase.Soil_Readings.temperature).label('temp'))\
            .join(DataBase.Device, DataBase.Block.id == DataBase.Device.network_id) \
            .join(DataBase.Soil_Readings, DataBase.Device.id == DataBase.Soil_Readings.device_id) \
            .filter(DataBase.Device.user_id == user_id) \
            .filter(DataBase.Soil_Readings.id.in_(latest_ids_subquery.select())) \
            .group_by(DataBase.Block.block_name) \
            .all()
        if results :
            #average mean avg last reading of all device in single block
            averages_list = [
            {
                "block_name": row.block_name,
                "moisture": round(float(row.moisture), 2) if row.moisture else 0,
                "humidity": round(float(row.humidity), 2) if row.humidity else 0,
                "temp": round(float(row.temp), 2) if row.temp else 0
            } 
            for row in results
            ]
            last_cached_averages = averages_list
            return averages_list
        elif last_cached_averages:
            return last_cached_averages
        else:
            user_blocks = db.query(DataBase.Block).filter(DataBase.Block.user_id == user_id).all()
            if user_blocks:
                return [
                    {
                        "block_name": block.block_name,
                        "moisture": 0,
                        "humidity": 0,
                        "temp": 0
                    } for block in user_blocks
                ]
            else:
                return [{
                    "block_name": "No Data Available",
                    "moisture": 0,
                    "humidity": 0,
                    "temp": 0
                }]

def getting_data_of_prediction_model():
    with DataBase.sessionlocal() as db:
        months_count = 3
        required_days = months_count * 30
        time_threshold = datetime.now(timezone.utc) - timedelta(days=required_days)
        #to know about date of my readings
        stats = db.query(
            DataBase.Block.block_name,
            func.min(DataBase.Soil_Readings.created_at).label('first_read'),
            func.max(DataBase.Soil_Readings.created_at).label('last_read'),
            func.count(DataBase.Soil_Readings.id).label('readings_count')
        ).join(DataBase.Device, DataBase.Block.id == DataBase.Device.network_id) \
         .join(DataBase.Soil_Readings) \
         .group_by(DataBase.Block.block_name).all()
        averages_list = []
        for s in stats:
            data_duration = (s.last_read - s.first_read).days
            if data_duration < required_days:
                averages_list.append({
                    "block_name": s.block_name,
                    "status": "incomplete",
                    "message": f"البيانات غير كافية. متاح فقط {data_duration} يوم، والمطلوب {required_days} يوم."
                })
                continue
            avg_row = db.query(
                func.avg(DataBase.Soil_Readings.moisture).label('moisture'),
                func.avg(DataBase.Soil_Readings.humidity).label('humidity'),
                func.avg(DataBase.Soil_Readings.temperature).label('temp'))\
             .join(DataBase.Device, DataBase.Block.id == DataBase.Device.network_id) \
             .filter(DataBase.Device.network_id == db.query(DataBase.Block.id).filter(DataBase.Block.block_name == s.block_name).scalar_subquery()) \
             .filter(DataBase.Soil_Readings.created_at >= time_threshold) \
             .first()

            averages_list.append({
                "block_name": s.block_name,
                "status": "ready",
                "moisture": round(float(avg_row.moisture), 2) if avg_row.moisture else 0,
                "humidity": round(float(avg_row.humidity), 2) if avg_row.humidity else 0,
                "temp": round(float(avg_row.temp), 2) if avg_row.temp else 0
            })
        return averages_list
#for_the_listner
last_call_time = 0
last_readings = []
def getting_data():
    global last_call_time , last_readings
    with DataBase.sessionlocal() as db:
        devices_readings=[]
        soil_reading_geted_of_devices=ref.child("devices").get()
        print(soil_reading_geted_of_devices)
        for soil_reading_geted in soil_reading_geted_of_devices.values():
            if not soil_reading_geted or "SERIAL_NUMBER" not in soil_reading_geted:
                devices_readings.append([None , "No data from Firebase", False ]) 
                continue
            serial_number=str(soil_reading_geted["SERIAL_NUMBER"])
            device = db.query(DataBase.Device).filter_by(serial_number=serial_number).first()
            if not device:
                devices_readings.append([None, "Device serial not found in DB", False ]) 
                continue
            try :
                reading = DataBase.Soil_Readings(device_id   = device.id,
                                                moisture = soil_reading_geted["moisture"] ,
                                                temperature = soil_reading_geted["temperature"] , 
                                                humidity = soil_reading_geted["humidity"])
                print(f"Test Readings before commit : {reading}")
                db.add(reading)
                db.commit()
                del soil_reading_geted["SERIAL_NUMBER"]
            except Exception as e:
                db.rollback()
                print(f"Error saving readings: {e}")
            owner_id = device.user_id
            print(f"id: {owner_id}")
            new_averages=calcucate_readings_for_showing(owner_id)
            print(f"Test  new_averages: {new_averages}")
        # if new_averages :
        #     last_readings = new_averages
            devices_readings.append([owner_id , new_averages , True ]) 
        return devices_readings
        # else:
        #     return owner_id,last_readings , True
connected_clients = set() #for multiple browsers connected 
def firebase_listener(event,main_loop):
    payload = {
        "type": event.event_type,
        "path": event.path,
        "data": event.data
    }
    find_data_for_user=False
    devices_readings= getting_data()
    print(devices_readings)
    for result in devices_readings:
        if isinstance(result, list) and result[2] is True:
            owner_user_id, updated_data , _ = result
            for ws in connected_clients:
                if hasattr(ws, 'owner_id') and ws.owner_id == owner_user_id:
                    print(updated_data)
                    find_data_for_user=True
                    asyncio.run_coroutine_threadsafe(
                        ws.send_json(updated_data),
                        main_loop
                )
    if not find_data_for_user:
            for ws in connected_clients:
                asyncio.run_coroutine_threadsafe(
                    ws.send_json("No data for this block from Firebase"),
                    main_loop
            )


#connect live stream of firebase to frontend using webstock
listener_ref = None 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use the running loop
    main_loop = asyncio.get_running_loop()
    # Start Firebase listener
    global listener_ref
    listener_ref = ref.listen(lambda event: firebase_listener(event, main_loop))
    print("Firebase listener started")
    try:
        yield
    finally:
        # Stop listener on shutdown
        if listener_ref:
            listener_ref.close()
        print("Firebase listener stopped")
data_sensors = ref.child("data").get()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.websocket(path="/ws/realtimedata/{user_id}")
async def realtimedata(ws : WebSocket , user_id: int)  :
    origin = ws.headers.get("origin")
    if origin not in origins:
        await ws.close()
        return
    await ws.accept() #for first handshack
    ws.owner_id = user_id
    print("Client connected to WebSocket")
    connected_clients.add(ws)
    try:
        initial_data = calcucate_readings_for_showing(user_id)
        if initial_data:
            await ws.send_json(initial_data)
        while True:
            await asyncio.sleep(4)  # keep alive connection
    except Exception as e:
      print(f"WebSocket Error: {e}")
    finally:
        connected_clients.discard(ws)
#endpoint of sign & login
@app.post("/user_sign_up",status_code=status.HTTP_201_CREATED)
def user_sign_up(input_user : EntryData , db : db_dependency)  :
    checking_user = db.query(DataBase.User).filter_by(email = input_user.personal_info.email).first()
    if checking_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="this email is existing use another one")
    hashed_pw_user=hashing_password(input_user.personal_info.password)
    user = DataBase.User(first_name=input_user.personal_info.first_name , 
                         last_name=input_user.personal_info.last_name ,
                         email =input_user.personal_info.email , 
                         password_hashed = hashed_pw_user ,
                         country = input_user.personal_info.country ,
                         city= input_user.personal_info.city )
    db.add(user)
    db.flush()
    default_block = DataBase.Block(
        block_name="Main Block",
        user_id=user.id
    )
    db.add(default_block)
    db.flush() 
    db.refresh(default_block)
    for item in input_user.devices_info:
        checking_serial = db.query(DataBase.Device).filter_by(serial_number = item.serial_number).first()
        if checking_serial is not None:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE , detail=f"this device  is already used")
        device = DataBase.Device(serial_number = item.serial_number ,
                                 user_id=user.id,
                                 network_id=default_block.id)
        db.add(device)
    db.commit()
    return "done"
@app.post("/login", status_code=status.HTTP_200_OK)
def user_login(input_user:LoginSchema , db: db_dependency):
    user = db.query(DataBase.User).filter_by(email=input_user.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الايميل غير موجود")
    #if i want do anyquery ic can use methode called excute and write in it the command in string without using ;
    if not verify_password(input_user.password, user.password_hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="كلمة السر خطأ")
    return {"id": user.id , "name": user.first_name +" "+ user.last_name, "city": user.city}
#endpoint crop_predication model
class request_crop(BaseModel):
    details : list
@app.get(path="/crop_predication")
def crop_predication() -> dict :
    averages = getting_data_of_prediction_model()
    if not averages:
        raise HTTPException(status_code=404, detail="لا توجد بيانات كافية في قاعدة البيانات")
    block_data = averages[0]
    if block_data.get("status") == "incomplete":
        raise HTTPException(status_code=400, detail=block_data.get("message"))
    t=block_data["moisture"]
    h=block_data["humidity"]
    s=block_data["temp"]
    crop, conf, msg=launch_model.predict_crop(t, h, s) 
    return {"crop": crop , "conf":conf,"msg" :msg , "used_data": {"temp": s, "humidity": h, "moisture": t}} 
#endpoint of chat_bot
class request_bot(BaseModel):
    text :str
@app.post(path="/chat_bot")
def chat_bot(input_user : request_bot): #reurn should be a dic 
    return {"bot": generate_conversation(input_user.text)}
#func of chat_bot
def generate_conversation(input_user : str):
    client = genai.Client(
        api_key=Gemini_key
    )
    
    model = "gemini-2.5-flash"

    tools = [
        types.Tool(
            googleSearch=types.GoogleSearch()
        )
    ]
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1
        ),
        tools=tools,
        system_instruction=types.Content(
            role="system",
            parts=[
                types.Part.from_text(
                    text = os.getenv("Gemini_prompt")
                )
            ],
        ),
    )
    history_conversation=[]
    chat = client.chats.create(
        model=model,
        config=generate_content_config,
        history=history_conversation)
    # Add user message
    response = chat.send_message(f"\nYou:{input_user}")
    model_response=response.text
    history_conversation.append( 
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=input_user)],
        )
    )
    
    history_conversation.append(types.Content(
        role="assistant",
        parts=[types.Part.from_text(text=model_response)]
    ))
    if  model_response is  None :
        return "نأسف ان هذه الخدمة متوقفة لأن نحن نستخدم نسخة مجانية فا صعب تكون متاحة للكل بسبب الضغط علي السيرفر"
    else :
        return model_response
if __name__=="__main__":
    uvicorn.run(app="backend:app",port=8000,reload=True)#app = folder.folder.file:app fastapi , host=domain(0.0.0.0=local host), reload for add changes 