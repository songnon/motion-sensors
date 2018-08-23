"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal

from pyhap.accessory import Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader

from MotionSensor import MotionSensor

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')
    temp_sensor = MotionSensor(driver, 'Motion Sendor 1')
    # temp_sensor2 = TemperatureSensor(driver, 'Sensor 1')
    bridge.add_accessory(temp_sensor)
    # bridge.add_accessory(temp_sensor2)

    return bridge


# def get_accessory(driver):
#     """Call this method to get a standalone Accessory."""
#     return TemperatureSensor(driver, 'MyTempSensor')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_bridge(driver))

# We want SIGTERM (kill) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()