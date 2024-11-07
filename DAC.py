import time
import board
import busio
import adafruit_mcp4728
from datetime import datetime

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize MCP4728 DAC
mcp4728 = adafruit_mcp4728.MCP4728(i2c)

def set_dac_values(control_signals):
    """
    Set the DAC values for the control valves using the control signals.
    Expects a dictionary with 'CV_1' and 'CV_2' values (0-1 scale).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    CV_1 = control_signals.get('CV_1', 0)  # default to 0 if not provided
    CV_2 = control_signals.get('CV_2', 0)

    # Scale the control valve openness to a DAC value (0-65535)
    mcp4728.channel_a.value = int(CV_1 * 65535)
    mcp4728.channel_b.value = int(CV_2 * 65535)

    return {'timestamp': timestamp, 'CV_1_set': CV_1, 'CV_2_set': CV_2}

if __name__ == "__main__":
    control_signals = {'CV_1': 0.5, 'CV_2': 0.7}
    set_dac_values(control_signals)
    print("DAC values set successfully.")
