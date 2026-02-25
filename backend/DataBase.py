from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean , Column ,Integer ,String  , ForeignKey , DateTime , Float , func
import os
from dotenv import load_dotenv , find_dotenv
#find env file 
dataenv_path=find_dotenv()
if  dataenv_path :
    load_dotenv(dataenv_path)
else:
    print("not found")
#connect my sql database
url_database=os.getenv("url_database")
engine = create_engine(url_database) #connect between mysql & backend
sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)#creating class
Base = declarative_base()
#schema
class User(Base):
    __tablename__ ="users"
    id = Column(Integer , primary_key=True , index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    country = Column(String(50))
    city= Column(String(50))
    email = Column(String(50) , unique=True)
    password_hashed = Column(String(255))
    created_at = Column(DateTime(timezone=True) , server_default= func.now())

    blocks = relationship("Block" , back_populates="user")
    devices = relationship("Device" , back_populates="user")
class Block(Base) :
    __tablename__ ="blocks"
    id = Column(Integer , primary_key=True , index=True)
    block_name = Column(String(50))
    user_id = Column(Integer , ForeignKey('users.id'))

    user = relationship("User" , back_populates="blocks")
    devices = relationship("Device" , back_populates="block")
class Device(Base):
    __tablename__ ="devices"
    id = Column(Integer , primary_key=True , index=True)
    user_id = Column(Integer , ForeignKey('users.id'))
    network_id = Column(Integer , ForeignKey('blocks.id'))
    serial_number = Column(String(50),unique=True)
    added_at = Column(DateTime(timezone=True) , server_default=func.now())

    user = relationship("User" , back_populates="devices")
    block = relationship("Block" , back_populates="devices")
    readings = relationship("Soil_Readings" , back_populates="device")
class Soil_Readings(Base):
    __tablename__ ="soil_readings"
    id = Column(Integer , primary_key=True)
    device_id = Column(Integer , ForeignKey('devices.id'))
    created_at = Column(DateTime(timezone=True) , server_default=func.now())
    moisture = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)

    device = relationship("Device" , back_populates="readings")
