from threading import Thread

import time
from time import time as unixtime
import requests
requests.packages.urllib3.disable_warnings()
import xml.etree.ElementTree as ET

from collections import OrderedDict

from requests.adapters import HTTPAdapter, Retry
from typing import Optional

from device_name_mapping import HOSTNAME_TO_IP

def parse_allnet_json(j_decoded):
    # j_decoded = json.loads(j, encoding='ISO-8859-1')
    d = OrderedDict({'Wechselspannung': None,
                     'Wechselstrom': None,
                     'Leistung': None,
                     'Leistungsfaktor': None,
                     'Frequenz': None,
                     'Kontakt Eingang': None,
                     'Intern': None,
                     'Schaltrelais': None,
                     'Geräte LED': None,
                     'Geräte LED 3': None
                     })
    # for sub_dict in j_decoded:
    #    key = sub_dict['name']
    #    messwert = float(sub_dict['value'])
    #    d[key] = messwert
    sensors = ET.fromstring(j_decoded)
    for sensor in sensors:
        measurement_id = sensor[1].text
        measurement = sensor[2].text
        mapped_id = mapSensorIDToDict(measurement_id)
        if measurement == 'error' and mapped_id is not None:
            d = None
            return d
        else:
            d[mapped_id] = measurement
    return d


def mapSensorIDToDict(measurement_id: str) -> Optional[str]:
    """
    Maps ordered xml sensor objects to the dict names defined in OrderedDict
    @rtype: str
    """
    sensor_map_dict = {'AC Voltage': 'Wechselspannung',
                       'AC Current': 'Wechselstrom',
                       'Power': 'Leistung',
                       'Power factor': 'Leistungsfaktor',
                       'Frequency': 'Frequenz',
                       'Contact input': 'Kontakt Eingang',
                       'Internal': 'Intern'}
    if measurement_id in sensor_map_dict:
        return sensor_map_dict[measurement_id]
    else:
        return None


class AllnetPoll(Thread):
    TIMEOUT = 20  # max response-time with one powerplug recorded = 11.14s

    def __init__(self, name, output_queue, auth=None):
        super(AllnetPoll, self).__init__()
        self.name = str(name)
        self.daemon = True
        self.ip = HOSTNAME_TO_IP[name]
        if auth is None:
            self.url = "https://%s/xml/?mode=sensor" % self.ip
        else:
            self.url = f'https://{auth["username"]}:{auth["password"]}@{self.ip}/xml/?mode=sensor'
        self.output_queue = output_queue
        retry_counter = 0
        while retry_counter < 2:
            try:
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                response = session.get(self.url, timeout=AllnetPoll.TIMEOUT, verify=False)
                assert response.status_code == 200, ('HTTP-Statuscode', response.status_code, response.content)
                print(f'{self.url} is ok!')
                retry_counter = 2
            except requests.exceptions.Timeout as e:
                print("%s %s is unreachable" % (self.name, self.ip))
                raise e
            except requests.exceptions.ConnectionError:
                print(f'waiting for {self.ip} to reconnect')
                time.sleep(10)
                retry_counter += 1

    def run(self):
        with requests.Session() as session:
            while True:
                try:
                    t_request = unixtime()
                    response = session.get(self.url, timeout=AllnetPoll.TIMEOUT, verify=False)
                    assert response.status_code == 200, ('HTTP-Statuscode', response.status_code, response.content)
                    t_reply = unixtime()

                    allnet_dict = parse_allnet_json(response.content.decode('utf-8'))
                    if allnet_dict:  # allnet_dict is None if the parser encounters an error
                        allnet_dict['Unixtime Request'] = t_request
                        allnet_dict['Unixtime Reply'] = t_reply
                        allnet_dict['DeviceName'] = self.name

                        self.output_queue.put(allnet_dict)
                except requests.exceptions.Timeout as e:
                    print("%s %s Timeout " % (self.name, self.ip), e)
                except requests.exceptions.ConnectionError as e:
                    # ConnectionError occurs if plug is unreachable, eg during and after a powerloss
                    print("%s %s No Connection to Host " % (self.name, self.ip), e)
                    time.sleep(3)
                except requests.exceptions.RequestException as e:
                    print("------ Unknown Exception ------ ", e)
                    time.sleep(3)
