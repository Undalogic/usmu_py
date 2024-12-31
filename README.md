# μSMU Python Library
A lightweight Python library for controlling a the [μSMU source-measure unit](https://github.com/joeltroughton/uSMU) device over a Virtual COM Port (VCP). This library provides a simple Python interface to send commands and read measurements from the μSMU, making it easy to automate I–V sweeps, data logging, and more.

## Features
- Communicate with a USB SMU via a serial (VCP) interface using PySerial.
- Set output voltage, current limit, oversampling rate, DAC values, and other SMU settings.
- Measure voltage and current (I–V) in a single command.
- Perform scripted sweeps (e.g., from a negative voltage to a positive voltage).
- Automatically insert a configurable delay (e.g., 50 ms) between commands.
- Installation

You can install this package directly from PyPI (once published):
```bash
pip install usmu_py
```
If you're developing locally or have cloned this repo, install it in editable mode:

```bash
cd path/to/your/usmu_py
pip install -e .
```
Ensure PySerial and other dependencies are installed.
If plotting is desired, also install Matplotlib and NumPy.

```bash
pip install pyserial numpy matplotlib
```

## Basic Usage Example
Below is a minimal script demonstrating how to initialize the SMU, set voltage, measure it, and then close the session.

```python
from usmu_py.smu import USMU

def main():
    # Open SMU on the specified port (e.g., 'COM3' or '/dev/ttyUSB0')
    smu = USMU(port="COM3", baudrate=9600, command_delay=0.05)
    try:
        # Identify the SMU
        idn = smu.read_idn()
        print("IDN:", idn)

        # Enable output and configure current limit
        smu.enable_output()
        smu.set_current_limit(20.0)  # 20 mA current limit

        # Set voltage and measure
        voltage, current = smu.set_voltage_and_measure(1.0)
        print(f"Set voltage: 1.0 V | Measured Voltage: {voltage:.3f} V, Current: {current:.6f} A")

        # Disable output after testing
        smu.disable_output()
    finally:
        smu.close()

if __name__ == "__main__":
    main()
```
## Example I–V Sweep
Below is a snippet showing how to perform a simple I–V sweep, measuring voltage and current at each step, and then plotting the results:

```python
import numpy as np
import matplotlib.pyplot as plt
from usmu_py.smu import USMU

def iv_sweep_example():
    port = "COM3"
    start_voltage = -1.0
    end_voltage = +1.0
    points = 10

    voltages = np.linspace(start_voltage, end_voltage, points)
    measurements = []

    with USMU(port=port, baudrate=9600, command_delay=0.05) as smu:
        print("IDN:", smu.read_idn())
        smu.enable_output()
        smu.set_current_limit(20.0)
        smu.set_oversample_rate(25)

        for v in voltages:
            voltage, current = smu.measure_iv_point(v)
            measurements.append((voltage, current))
            print(f"{voltage:.3f} V, {current:.6e} A")

        smu.disable_output()

    # Plot the resulting I–V curve
    vs = [m[0] for m in measurements]
    is_ = [m[1] for m in measurements]
    plt.figure()
    plt.plot(vs, is_, 'o-')
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.title("I–V Sweep")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    iv_sweep_example()
	```

