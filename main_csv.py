import time
from simple_pid import PID
import ADC
import DAC
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv

# Global flag for legend activation
legend_activated = False

# Stagnant tank setpoints
t1_sp = 35
t2_sp = 35 

# PID controller gains
p = 0.08
i = 0.005
d = 0.0005

# PID Controller parameters for Tank 1 and Tank 2
pid_tank_1 = PID(p, i, d, setpoint=t1_sp)
pid_tank_2 = PID(p, i, d, setpoint=t2_sp)

# Set PID output limits for valve control
pid_tank_1.output_limits = (0, 1)  
pid_tank_2.output_limits = (0, 1)  

# Initialize time array and other data arrays
t_array = np.array([])
tank_1_sp = np.zeros(len(t_array))
tank_1_meas = np.zeros(len(t_array))
tank_2_sp = np.zeros(len(t_array))
tank_2_meas = np.zeros(len(t_array))
cv_1_sp = np.zeros(len(t_array))
cv_1_meas = np.zeros(len(t_array))
cv_2_sp = np.zeros(len(t_array))
cv_2_meas = np.zeros(len(t_array))

# Create a GridSpec layout for multiple subplots
fig = plt.figure(figsize=(10, 8))
gs = plt.GridSpec(3, 2, figure=fig)

# Plot 1: Tank 1 Level
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_title('Tank 1 Level')
ax1.set_ylabel('% Full')

# Plot 2: Tank 2 Level
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_title('Tank 2 Level')
ax2.set_ylabel('% Full')

# Plot 3: Control Valve 1
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_title('Control Valve 1 Openness')
ax3.set_ylabel('Openness')

# Plot 4: Control Valve 2
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_title('Control Valve 2 Openness')
ax4.set_ylabel('Openness')

plt.tight_layout()

# List to store all simulation data
simulation_data = []

def update_plot():
    """ Updates the plots with the current data. """
    ax1.plot(t_array, tank_1_sp, 'r', label='Tank 1 Setpoint')
    ax1.plot(t_array, tank_1_meas, 'b', label='Tank 1 Measurement')

    ax2.plot(t_array, tank_2_sp, 'r', label='Tank 2 Setpoint')
    ax2.plot(t_array, tank_2_meas, 'b', label='Tank 2 Measurement')

    ax3.plot(t_array, cv_1_sp, 'r', label='CV 1 Openness')
    ax3.plot(t_array, cv_1_meas, 'b', label='CV 1 Measurement')
    
    ax4.plot(t_array, cv_2_sp, 'r', label='CV 2 Openness')
    ax4.plot(t_array, cv_2_meas, 'b', label='CV 2 Measurement')
    
    plt.pause(0.05)

def write_data_to_csv():
    """ Writes the collected data to a CSV file. """
    filename = f"simulation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Tank 1 Setpoint", "Tank 1 Measurement", "Tank 2 Setpoint", 
                         "Tank 2 Measurement", "CV 1 Setpoint", "CV 1 Measurement", 
                         "CV 2 Setpoint", "CV 2 Measurement"])
        writer.writerows(simulation_data)
    print(f"\nData successfully written to {filename}")

def control_loop():
    start_time =  datetime.now()
    global t_array, tank_1_sp, tank_1_meas, tank_2_sp, tank_2_meas, cv_1_sp, cv_1_meas, cv_2_sp, cv_2_meas, legend_activated, simulation_data, t1_sp, t2_sp

    plt.ion()  # Turn on interactive plotting

    try:
        while True:
            curr_time = datetime.now() - start_time 
            t_diff_sec = curr_time.total_seconds()
            t_array = np.append(t_array, t_diff_sec)
            
            # add SP step on tank 2
            if t_diff_sec >= 200: 
                #t2_sp = 51
                t2_sp = 35 + 5 * np.sin(2 * np.pi * 0.005 * (t_diff_sec - 200))
                pid_tank_2.setpoint = t2_sp 

            # Get ADC data (tank levels and current valve positions)
            adc_data = ADC.read_adc_values()
            tank_1_level = adc_data['tank_1']
            tank_2_level = adc_data['tank_2']
            
            # Compute control signal using PID
            control_signal_tank_1 = pid_tank_1(tank_1_level)
            control_signal_tank_2 = pid_tank_2(tank_2_level)
            
            # Send control signal to DAC
            control_signals = {
                'CV_1': control_signal_tank_1,
                'CV_2': control_signal_tank_2
            }
            DAC.set_dac_values(control_signals)

            # Update the data arrays
            tank_1_sp = np.append(tank_1_sp, t1_sp)
            tank_1_meas = np.append(tank_1_meas, tank_1_level)
            tank_2_sp = np.append(tank_2_sp, t2_sp)
            tank_2_meas = np.append(tank_2_meas, tank_2_level)
            cv_1_sp = np.append(cv_1_sp, control_signal_tank_1)
            cv_1_meas = np.append(cv_1_meas, adc_data['CV_1'])
            cv_2_sp = np.append(cv_2_sp, control_signal_tank_2)
            cv_2_meas = np.append(cv_2_meas, adc_data['CV_2'])

            # Store the current data for CSV export
            simulation_data.append([curr_time, t1_sp, tank_1_level, t2_sp, tank_2_level, 
                                    control_signal_tank_1, adc_data['CV_1'], 
                                    control_signal_tank_2, adc_data['CV_2']])

            # Update the plots
            update_plot()

            if not legend_activated:
                ax1.legend(loc='upper left')
                ax2.legend(loc='upper left')
                ax3.legend(loc='upper left')
                ax4.legend(loc='upper left')
                legend_activated = True

            # Sleep for a control period
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nControl loop stopped.")
        print("\nSending signal to open CVs.")
        control_signals = {'CV_1': 1, 'CV_2': 1}
        DAC.set_dac_values(control_signals)

        # Write the collected data to a CSV file
        write_data_to_csv()

        plt.ioff()  # Turn off interactive mode
        plt.show()

if __name__ == "__main__":
    legend_activated = False 
    control_loop()
