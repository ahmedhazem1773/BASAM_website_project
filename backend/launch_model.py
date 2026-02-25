import numpy as np
import keras
import joblib
def predict_crop(temp, humidity, soil_moisture):
    model = keras.models.load_model("backend\crop_recommendation_model.h5")
    le = joblib.load("backend\label_encoder.pkl")
    
    input_data = np.array([[temp, humidity, soil_moisture]])
    prediction = model.predict(input_data)
    confidence = np.max(prediction) * 100
    crop_idx = np.argmax(prediction)
    crop_name = le.inverse_transform([crop_idx])[0]
    
    if crop_name == "Not Suitable" or confidence < 60:
        return "Not Recommended", f"Confidence: {confidence:.1f}%", "Wait or improve conditions"
    else:
        return crop_name, f"Confidence: {confidence:.1f}%", "Good time to plant!"

if __name__ == "__main__":
    print(predict_crop(40, 50, 60))