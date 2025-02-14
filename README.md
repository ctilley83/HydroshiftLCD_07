# Lian Li HydroshiftLCD Fan Control

This software runs as a systemd service written in Python. This is a work in progress.

### Dependencies



```bash
pip install hidapi
pip install psutil
```



### Setup

We work directly with the HID USB interface. To list the HID Interfaces use the following script. The product vendor and product id should be 0x416 and 0x7399. If not note the ones that correspond with the HydroshiftLCD



```python
import hid

# Enumerate all devices and print relevant info
devices = hid.enumerate()
for device in devices:
    print(f"Vendor: {hex(device['vendor_id'])}, Product: {hex(device['product_id'])}, Path: {device['path']}, Interface: {device.get('interface_number', 'N/A')}, Product: {device['product_string']}")

```



Next we need to create the appropriate udev rules so our user has access to the system. Create and add your user to the plugdev group if necessary. You may have to change the vendor and product ids.

```

sudo vim /etc/udev/rules.d/99-hydroshift.rules
```

Add This line

```bash
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="7399", MODE="0666", GROUP="plugdev"
```

Reload the udev rules

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Copy the python script to the following location and alter its permissions.

```bash
sudo cp hydroshift_fan_control.py /usr/local/bin/hydroshift_fan_control.py
sudo chmod +x /usr/local/bin/hydroshift_fan_control.py

```

Create the systemd service.

```bash
sudo nano /etc/systemd/system/hydroshift_fan.service
```

And place the following code

```bash
[Unit]
Description=HydroShift AIO Fan Control Service
After=network.target

[Service]
ExecStart=/usr/bin/python /usr/local/bin/hydroshift_fan_control.py
Restart=always
User=root
WorkingDirectory=/usr/local/bin
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target

```

Enable and start the service.

```bash
sudo systemctl daemon-reload
sudo systemctl enable hydroshift_fan.service
sudo systemctl start hydroshift_fan.service
```

Verify it started.

```
systemctl status hydroshift_fan.service
```

You can test with stress-ng with the following command.

```bash
stress-ng --cpu 0 --cpu-method matrixprod --timeout 120s
```

