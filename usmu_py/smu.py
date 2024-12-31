import serial
import time

class USMUSerialError(Exception):
    """Custom exception for uSMU serial communication errors."""
    pass

class USMU:
    """
    Python interface for the USB SMU device over a virtual COM port (VCP).
    """

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0, command_delay: float = 0.05):
        """
        Initialize the SMU interface.

        :param port: The COM port name (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux).
        :param baudrate: The baud rate used by the SMU. Default: 9600.
        :param timeout: Read timeout in seconds. Default: 1.0.
        :param command_delay: Delay (in seconds) after sending each command/query to allow
                              the SMU to process. Default: 0.05 (i.e., 50 ms).
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.command_delay = command_delay

        # Open a serial connection
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
        except serial.SerialException as e:
            raise USMUSerialError(f"Error opening serial port {self.port}: {str(e)}")

        # Flush buffers
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
    def _sanitize_response(self, text: str) -> str:
        # Remove all null bytes and strip leading/trailing whitespace
        return text.replace('\x00', '').strip()


    def close(self):
        """Close the serial connection."""
        if self.ser.is_open:
            self.ser.close()

    def _write(self, command: str):
        """
        Write a command to the SMU followed by a newline, then wait.
        """
        cmd_str = command.strip() + "\n"
        self.ser.write(cmd_str.encode("utf-8"))
        # Wait for the device to process the command
        time.sleep(self.command_delay)

    def _readline(self) -> str:
        """
        Read a line of response from the SMU (until newline).
        """
        line = self.ser.readline().decode("utf-8").strip()
        return line

    def _query(self, command: str) -> str:
        """
        Send a command, then read back a response line.
        """
        self._write(command)
        response = self._readline()
        return response

    #
    # Basic SMU commands
    #
    def enable_output(self):
        """Enable SMU output."""
        self._write("CH1:ENA")

    def disable_output(self):
        """Disable SMU output (high impedance)."""
        self._write("CH1:DIS")

    def set_current_limit(self, current_mA: float):
        """
        Set the sink/source current limit in mA.
        Example: set_current_limit(100.0) for 100 mA.
        """
        self._write(f"CH1:CUR {current_mA}")

    def set_voltage(self, voltage_V: float):
        """
        Set the SMU voltage in volts.
        Example: set_voltage(5.0) sets the device to 5 V.
        """
        self._write(f"CH1:VOL {voltage_V}")

    def set_voltage_and_measure(self, voltage_V: float):
        response = self._query(f"CH1:MEA:VOL {voltage_V}")

        # Sanitize
        response = response.replace('\x00', '').strip()

        try:
            vol_str, cur_str = response.split(",")
            measured_voltage = float(vol_str)
            measured_current = float(cur_str)
            return measured_voltage, measured_current
        except ValueError:
            raise USMUSerialError(f"Unexpected response: {response}")



    def set_oversample_rate(self, oversample: int):
        """
        Set the oversample rate (number of samples averaged per measurement).
        Default is 25.
        """
        self._write(f"CH1:OSR {oversample}")

    def set_dac(self, value: int):
        """
        Set the voltage DAC to this level. 16-bit integer.
        """
        self._write(f"DAC {value}")

    def read_adc(self, adc_channel: int):
        """
        Perform a differential conversion between adjacent ADC channels
        (0 = 0+1, 2=2+3). Returns a signed int16 value.
        """
        response = self._query(f"ADC {adc_channel}")
        try:
            return int(response)
        except ValueError:
            raise USMUSerialError(f"Unexpected response: {response}")

    def set_current_limit_dac(self, value: int):
        """
        Set the current limit DAC to this level. 12-bit integer.
        """
        self._write(f"ILIM {value}")

    def enable_voltage_calibration_mode(self):
        """Enable voltage calibration mode."""
        self._write("CH1:VCAL")

    def lock_current_range(self, range_val: int):
        """
        Lock current range and temporarily clear current calibration data.
        Range must be between 1 and 4.
        """
        if range_val not in [1, 2, 3, 4]:
            raise ValueError("Current range must be 1, 2, 3, or 4.")
        self._write(f"CH1:RANGE {range_val}")

    def read_idn(self):
        """Read the SMU identification string (*IDN?)."""
        return self._query("*IDN?")

    #
    # Utility methods for scripted measurements
    #
    def measure_iv_point(self, voltage_V: float):
        """
        Helper method to set a voltage and read back (voltage, current).
        """
        return self.set_voltage_and_measure(voltage_V)

    #
    # Cleanup
    #
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
