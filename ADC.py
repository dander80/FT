import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1015(i2c)

# Create single-ended input on channels
chan1 = AnalogIn(ads, ADS.P0)
chan2 = AnalogIn(ads, ADS.P1)
chan3 = AnalogIn(ads, ADS.P2)
chan4 = AnalogIn(ads, ADS.P3)

# Define the range for scaling
tank_min = 0.4020122684408
tank_max = 1.992060792870876
tank_range = tank_max - tank_min 

cv_min = 0.001
cv_max = 2.96
cv_range = cv_max - cv_min 

def read_adc_values():
    """
    Reads the levels of tank_1, tank_2, CV_1, and CV_2.
    Returns a dictionary with the values and timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tank_1 = (100 * (chan1.voltage - tank_min) / tank_range)
    tank_2 = (100 * (chan2.voltage - tank_min) / tank_range)
    CV_1   = (chan3.voltage - cv_min) / cv_range
    CV_2   = (chan4.voltage - cv_min) / cv_range

    adc_data = {
        'timestamp': timestamp,
        'tank_1': round(tank_1, 2),
        'tank_2': round(tank_2, 2),
        'CV_1': round(CV_1, 3),
        'CV_2': round(CV_2, 3)
    }
    
    return adc_data

if __name__ == "__main__":
    while True:
        data = read_adc_values()
        print(data)
        time.sleep(0.1)
