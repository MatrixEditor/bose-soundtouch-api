# MIT License
#
# Copyright (c) 2023 MatrixEditor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import re
import urllib3

from xml.etree.ElementTree import fromstring

from boseapi.model import InfoNetworkConfig
from boseapi.common.nodes import list_uris

RE_IPV4_ADDRESS = r"\d{1,3}([.]\d{1,3}){3}"

class BoseDeviceComponent:
    """ A small wrapper class to store component related data.

    Attributes:
      category: str
        A simple string used to identify the component object.
      software_version: str
        If present, this attribute contains the current version the software
        is running with.
      serial_number: str
        As the name already states, this string contains a serial number if
        present.
    """

    def __init__(self, category: str = None, software_version: str = None,
                 serial_number: str = None) -> None:
        self.category = category
        self.software_version = software_version
        self.serial_number = serial_number

    def __str__(self) -> str:
        return f'<Component category="{self.category}">'


class BoseDevice:
    """The most important object when working with the boseapi.

    This class contains device-related information, such as: host ip address,
    device name/type/id, a list of the device's components, a list of supported
    URLs and the current network configuration.

    The supported URLs are used by the SoundTouchClient to verify the requested
    URL is supported by the device. They are queried when invoking the new_device()
    method.

    Attributes:
        host: str
            An Ipv4 address of the target host.
        device_name: str
            The current device's name. The name is updated when using the name()-method
            in the SoundTouchClient.
        device_type: str
            The device's type.
        components: list[BoseDeviceComponent]
            A small list containing various information about the device's components.
        network_info: list[NetworkConfig]
            A list storing the current network configuration
        supportedURLs: list[SoundTouchUri]
            A list of usable URIs. These can be invoked using the SoundTouchClient.
    """

    def __init__(self, host: str, device_name: str = None,
                 device_type: str = None, device_id: str = None,
                 components: list = None, # _type: list[BoseDeviceComponent]
                 network_info: list = None) -> None:
        self.host = host
        self.device_name = device_name
        self.device_type = device_type
        self.device_id = device_id
        self.components = components if components else []
        self.network_info = network_info if network_info else []
        self.supported_urls = []

    def get_upnp_url(self) -> str: # str | None
        """Returns the UPnP root URL.

        The document located at the returned URL contains additional information about
        methods and properties that can be used with UPnP.

        Returns: str
        An URL in the following format:
            http://host:8091/XD/BO5EBO5E-F00D-FEED-device_id.xml

        """
        return f'http://{self.host}:8091/XD/BO5EBO5E-F00D-FEED-{self.device_id}.xml'

    def get_logread_url(self) -> str: # str | None
        """Returns the URL to download a logread file.

        Returns: str
        A string-URL in the following format:
            http://host/logread.dat
        """
        return f'http://{self.host}/logread.dat'

    def get_pts_url(self) -> str: # str | None
        """Returns the URL to download a logread file.

        Returns: str
        A string-URL in the following format:
            http://host/logread.dat
        """
        return f'http://{self.host}/pts.dat'

    def get(self, component_category: str):
        """Iterates over all components that match the given category.

        :param component_category: the  component's category
        :type component_category: str
        :return: an iterator over the filtered components
        :yield: a device component
        :rtype: Generator[BoseDeviceComponent, None, None]
        """
        if not component_category:
            return None

        for component in filter(lambda x: x and x.category == component_category, self.components):
            yield component

    def __str__(self) -> str:
        return f'<BoseDevice at "{self.host}">'

    def __iter__(self):
        return iter(self.components)


def new_device(host: str, proxy: urllib3.ProxyManager = None) -> BoseDevice:
    """Tries to create a new BoseDevice with a complete data section.

    This method automatically reloads all components and device properties allocated
    at the given host. There will be a None result if the given host does not match
    the following pattern: r"\d{1,3}([.]\d{1,3}){3}".

    In order to load all properties and attributes of the BoseDevice object, some
    special URLs will be queried:
        - http://host:8090/info and http://host:8090/supportedURLs

    Arguments:
        host: str
            An IPv4 address og the target host.
        proxy: Optional[urllib3.ProxyManager]
            If a custom proxy should be used, it can be passed as a parameter.

    Returns: Optional[BoseDevice]
        If the host does not match the IPv4 pattern, None will be returned as
        a result.

    Raises:
        InterruptedError: An error occurred while fetching information from the
                        target host.
    """
    if not host or not re.match(RE_IPV4_ADDRESS, host):
        raise ValueError(f'Invalid host argument: "{host}"')

    manager = proxy if proxy else urllib3.PoolManager(headers={'User-Agent': 'BoseApi/0.1.2'})
    try:
        response = manager.request('GET', f'http://{host}:8090/info')
        if response.status == 200:
            root = fromstring(response.data)
            dev = BoseDevice(host, device_id=root.get('deviceID', None))
            for e_name in ['name', 'type']:
                element = root.find(e_name)
                if element.text:
                    setattr(dev, 'device_' + e_name, element.text)

        for component in root.find('components'):
            dev.components.append(BoseDeviceComponent(
                category=component.find('componentCategory').text,
                serial_number=component.find('serialNumber').text,
                software_version=component.find('softwareVersion').text
            ))

        for info in root.find('network_info'):
            dev.network_info.append(InfoNetworkConfig(info))

        response.close()
        response = manager.request('GET', f'http://{host}:8090/supportedURLs')
        if response.status == 200:
            uris = list_uris()
            for url_element in fromstring(response.data).findall('URL'):
                name = url_element.get('location', default='/')[1:]
                if name and name in uris:
                    dev.supported_urls.append(uris[name])
        return dev
    except Exception as err:
        # log that
        raise InterruptedError from err
