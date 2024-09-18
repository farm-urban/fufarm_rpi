#!/usr/bin/env python3

from dataclasses import dataclass, field
import json
import pprint
import logging
import socket
import sys

import time
from typing import Callable

import requests
import paho.mqtt.client as mqtt
import yaml


# https://api-docs.edenic.io/v1/telemetry/

# ORG_KEY = "9e9efe10-6e9f-11ef-9338-8dff4b34f2dc"
# API_KEY = "ed_jry99y9dgf8bomuw2j5xsm4qt4mezwu75rkwop2y2n8phub1rslktmbbo2zb4kz8"

#    ec_device_label: str = "4q3f"
#    ec_device_id: str = "08041fa0-6ea2-11ef-9d80-63543a698b74"

"""
curl --include https://api.edenic.io/api/v1/device/9e9efe10-6e9f-11ef-9338-8dff4b34f2dc \
  --header 'Authorization: ed_jry99y9dgf8bomuw2j5xsm4qt4mezwu75rkwop2y2n8phub1rslktmbbo2zb4kz8'
"""
PRO_CONTROLLER = "pro_controller"


@dataclass
class DeviceConfig:
    """Configures an individual device."""

    name: str
    type: str
    label: str
    id: str = None
    ec_state_topic: str = None
    ph_state_topic: str = None
    temp_state_topic: str = None

    def __repr__(self):
        x = "\n ".join(f"{k} : {repr(v)}" for (k, v) in self.__dict__.items())
        return f"<\n{x}\n>"


@dataclass
class AppConfig:
    """Configures the Application."""

    log_level: str = "INFO"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = "hamqtt"
    mqtt_password: str = "UbT4Rn3oY7!S9L"

    discovery_prefix: str = "homeassistant"

    org_key: str = "9e9efe10-6e9f-11ef-9338-8dff4b34f2dc"
    api_key: str = "ed_jry99y9dgf8bomuw2j5xsm4qt4mezwu75rkwop2y2n8phub1rslktmbbo2zb4kz8"

    # https://docs.python.org/3/library/dataclasses.html#mutable-default-values
    devices: list[DeviceConfig] = field(default_factory=list)

    def __repr__(self):
        x = "\n ".join(f"{k} : {repr(v)}" for (k, v) in self.__dict__.items())
        return f"<\n{x}\n>"


def get_devices(organisation_id, api_key):
    """Returns the devices for an organisation.

    E.g.:
    [{'id': '08041fa0-6ea2-11ef-9d80-63543a698b74',
    'name': '9e9efe10-6e9f-11ef-9338-8dff4b34f2dc__0013a20041cdb315',
    'label': '4q3f',
    'gateway': False,
    'sortOrder': 0,
    'deviceTypeId': 'f33da651-1851-4291-a184-56e0c16e418c',
    'organisationId': '9e9efe10-6e9f-11ef-9338-8dff4b34f2dc',
    'deleted': False,
    'additionalInfo': {'lastConnectedGateway': 'c10ed720-6ea1-11ef-9d80-63543a698b74'}}]
    """
    url = f"https://api.edenic.io/api/v1/device/{organisation_id}"
    headers = {"Authorization": api_key}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.RequestException(
            f"Failed to get devices: {response.text}"
        )
    return response.json()


# print(pprint.pp(get_devices(ORG_KEY, API_KEY)))


# def get_telemetry(device_id, api_key):
#     """Returns the telemetry for a device.

#     E.g.:
#     {'ph': [{'ts': 1726605615556, 'value': '5.8'}],
#      'temperature': [{'ts': 1726605615556, 'value': '27.0'}],
#       'electrical_conductivity': [{'ts': 1726605615556, 'value': '1.5'}]}
#     """
#     url = f"https://api.edenic.io/api/v1/telemetry/{device_id}"
#     headers = {"Authorization": api_key}
#     response = requests.get(url, headers=headers, timeout=10)
#     if response.status_code != 200:
#         raise requests.exceptions.RequestException(
#             f"Failed to get telmetry: {response.text}"
#         )
#     return response.json()


def get_telemetry(device_id, api_key):
    return {
        "ph": [{"ts": 1726605615556, "value": "5.8"}],
        "temperature": [{"ts": 1726605615556, "value": "27.0"}],
        "electrical_conductivity": [{"ts": 1726605615556, "value": "1.5"}],
    }


def create_on_connect(app_config: AppConfig) -> Callable:
    """Create a callback to handle connection to MQTT broker.

    https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery
    https://developers.home-assistant.io/docs/core/entity/sensor/
    """

    def on_mqtt_connect(client: mqtt.Client, _userdata, _flags, _reason_code):
        """Subscribe to topics on connect."""

        for d in app_config.devices:
            if d.type == PRO_CONTROLLER:
                base_url = f"{app_config.discovery_prefix}/sensor"
                for stype in ["pH", "Temp", "EC"]:
                    sname = f"{stype.lower()}_{d.label}"
                    config_topic = f"{base_url}/{sname}/config"
                    state_topic = f"{base_url}/{sname}/state"
                    if stype == "pH":
                        d.ph_state_topic = state_topic
                    elif stype == "Temp":
                        d.temp_state_topic = state_topic
                    elif stype == "EC":
                        d.ec_state_topic = state_topic
                    munit = {"pH": "pH", "Temp": "°C", "EC": "EC"}.get(stype)
                    payload = {
                        "name": f"Bluelab {stype} {d.label}",
                        "device_class": None,
                        "state_topic": state_topic,
                        "unique_id": sname,
                        "unit_of_measurement": munit,
                        # "expire_after": 600,
                    }
                    client.publish(config_topic, json.dumps(payload).encode("utf8"))
                    _LOG.debug(
                        "Added Bluelab %s sensor to Home Assistant: %s", sname, payload
                    )
            else:
                raise ValueError(f"Unknown device type: {d.type}")

    return on_mqtt_connect


def setup_mqtt(app_config: AppConfig, create_on_connect: Callable) -> mqtt.Client:
    """Setup the MQTT client and subscribe to topics."""
    # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client = mqtt.Client()
    host = app_config.mqtt_host
    port = app_config.mqtt_port
    username = app_config.mqtt_username
    password = app_config.mqtt_password
    client.username_pw_set(username, password)
    try:
        client.connect(host, port=port)
    except (ConnectionRefusedError, socket.gaierror) as e:
        _LOG.error("Could not connect to MQTT broker: %s", e)
        raise e
    client.on_connect = create_on_connect(app_config)

    return client


def process_config(file_path: str) -> AppConfig:
    """Process the configuration file."""
    with open(file_path, "r", encoding="utf-8") as f:
        yamls = yaml.safe_load(f)
        _app_config = AppConfig(**yamls["app"])

        if not "devices" in yamls:
            raise ValueError("No devices in config file")

        for d in yamls["devices"]:
            device = DeviceConfig(**d)
            if device.type != PRO_CONTROLLER:
                raise ValueError(
                    f"Only {PRO_CONTROLLER} devices are currently supported."
                )
            _app_config.devices.append(device)

    if not hasattr(logging, _app_config.log_level):
        raise AttributeError(f"Unknown log_level: {_app_config.APP.log_level}")

    return _app_config


app_config = process_config("bluelab.yml")

logging.basicConfig(
    level=app_config.log_level,
    format="%(asctime)s rpi: %(message)s",
)
_LOG = logging.getLogger(__name__)

_LOG.info("Starting Bluelab MQTT")

# print(pprint.pp(app_config))
# sys.exit()
# print(pprint.pp(get_telemetry(app_config.ec_device_id, app_config.api_key)))

### NEED TO GET DEVICE ID FROM API HERE

mqtt_client = setup_mqtt(app_config, create_on_connect)

mqtt_client.loop_start()
state = 0
while True:
    while not mqtt_client.is_connected():
        _LOG.warning("mqtt_client not connected")
        mqtt_client.reconnect()
        time.sleep(2)

    _LOG.info("RUNNING")

    for d in app_config.devices:
        telemetry = get_telemetry(d.id, app_config.api_key)
        for stype in ["ph", "temp", "ec"]:
            if stype == "ph":
                state_topic = d.ph_state_topic
                value = telemetry["ph"][0]["value"]
            elif stype == "temp":
                state_topic = d.temp_state_topic
                value = telemetry["temperature"][0]["value"]
            elif stype == "ec":
                state_topic = d.ec_state_topic
                value = telemetry["electrical_conductivity"][0]["value"]
            _LOG.info("GOT VALUE: %s %s %s", value, type(value), state_topic)
            mqtt_client.publish(state_topic, value.encode("utf8"))
            _LOG.info("Published %s to %s", value, state_topic)

        # "ph": [{"ts": 1726605615556, "value": "5.8"}],
        # "temperature": [{"ts": 1726605615556, "value": "27.0"}],
        # "electrical_conductivity": [{"ts": 1726605615556, "value": "1.5"}],

    # base_url = f"{app_config.discovery_prefix}/sensor/ec_{app_config.ec_device_label}"
    # state_topic = f"{base_url}/state"
    # if state > 0:
    #     state = 0
    # else:
    #     state = 1
    # mqtt_client.publish(state_topic, f"{state}".encode("utf8"))
    time.sleep(2)
