from usmu_py.smu import USMU
import numpy as np
import matplotlib.pyplot as plt

def main():
    port = "COM39"   # uSMU's serial port (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux or macOS)
    
    start_voltage = -1.0 # Voltage to start the sweep from
    end_voltage = +1.0 # Voltage to end the sweep at
    number_of_points = 50 # Number of points to measure between the start and end voltages
    
    voltages = np.linspace(start_voltage, end_voltage, number_of_points)

    # Connect to the SMU
    with USMU(port=port, baudrate=9600) as smu:
        # Print identification
        print("IDN:", smu.read_idn())

        # Configure SMU
        smu.enable_output()
        smu.set_current_limit(20.0)     # 20 mA
        smu.set_oversample_rate(10)     # Default oversample rate (10)

        results = []

        print("Voltage (V),Current (A)")

        # Sweep the voltage and measure
        for v in voltages:
            voltage, current = smu.measure_iv_point(v)
            results.append((voltage, current))

            print(f"{voltage:.6f},{current:.6e}")

        smu.disable_output()

    # --- Save data to CSV ---
    with open("iv_data.csv", "w", newline="") as f:
        f.write("Voltage_V,Current_A\n")
        for (v, i) in results:
            f.write(f"{v},{i}\n")

    # --- Plot the IV curve ---
    volt_list = [r[0] for r in results]
    curr_list = [r[1] for r in results]

    plt.figure()
    plt.plot(volt_list, curr_list, marker='o')
    plt.title("I–V Curve")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()