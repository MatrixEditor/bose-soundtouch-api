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
__doc__ = """
The `stu` module contains methods and classes related to the update process.
Classes defined here are made to store data.
"""

import xml.etree.ElementTree as xmltree

BOSE_ST_INDEX_URL = 'https://downloads.bose.com/updates/soundtouch'
"""
To fetch the BOSE SoundTouch index.xml file this URL has to be visited.
"""

class Release:
    """A release class by bose targets a specific firmware upgrade.

    The specific information can be loaded from an XML-Element (ElementTree.Element).
    There is a static method that implements the parsing process to save the values
    stored in the XML-Element.

    Attributes:
        revision: str
            The revision number of the current release.
        host: str
            The hostname of the update provider.
        uri: str
            The uri part of the full url linked to the downloadable update file.
        usb_uri: str
            Another uri which was not usable in any context.
        image: dict[str, str]
            The main property storing data related to the firmware image.
        notes_url: str
            If the update file contains some release notes, the url is given within this property.
        features: list[dict[str, str]]
            If there are some features within the release, they are added to this list as a dict.
    """
    def __init__(self, revision: str = None, host: str = None,
                 uri: str = None, usb_uri: str = None, image: dict = None,
                 notes_url: str = None, features: list = None) -> None:
        self.revision = revision
        self.host = host
        self.uri = uri
        self.usb_uri = usb_uri
        self.image = image if image else {}
        self.notes_url = notes_url
        self.features = features if features else []

    @staticmethod
    def loadxml(element: xmltree.Element) -> 'Release':
        """Reads the given XML-Element and loads information into an BoseRelease object.

        :param element: The root element with the tag "RELEASE"
        :type element: xmltree.Element
        :return: An object containing all relevant information about a software release.
        :rtype: Release
        """
        if not element:
            raise ValueError('Expected non null input')

        release = Release(
            element.get('REVISION', None),
            element.get('HTTPHOST', None),
            element.get('URLPATH', None),
            element.get('USBPATH', None)
        )
        image = element.find('IMAGE')
        if image is not None:
            release.image = image.attrib

        notes = element.find('NOTES')
        if notes:
            release.notes_url = notes.get('URL', None)

        for feature in element.findall('FEATURE'):
            release.features.append(feature.attrib)
        return release

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(revision={self.revision})"


class Firmware:
    """A class by bose that targets a specific firmware upgrade.

    The specific information can be loaded from an XML-Element (ElementTree.Element).
    There is a static method that implements the parsing process to save the values
    stored in the XML-Element.

    Attributes:
        device_id: str
            A bose-specific device id for this hardware object.
        product_name: str
            Specifying the product name for the linked firmware.
        revision: str
            The revision number of the current release.
        release: BoseRelease
            The linked firmware release.
        protocols: list[str]
            If there are specific platform targets, some protocols are added to the
        hardware object.
    """
    def __init__(self, device_id: int = 0, product_name: str = None,
                 revision: str = None, release: Release = None,
                 protocols: list = None) -> None:
        self.revision = revision
        self.release = release
        self.protocols = protocols if protocols else []
        self.device_id = device_id
        self.product_name = product_name

    @staticmethod
    def loadxml(element: xmltree.Element) -> 'Firmware':
        """Reads the given XML-Element and loads information into an Firmware object.

        This function can be called outside this class.

        :param element: The root element
        :type element: xmltree.Element
        :raises ValueError: if the element is null
        :return: the parsed firmware object
        :rtype: Firmware
        """
        if not element:
            raise ValueError('Invalid XML-Element')

        dev = Firmware(
            int(element.get('ID', default='0'), 16),
            element.get('PRODUCTNAME')
        )
        hardware_el = element.find('HARDWARE')
        if hardware_el:
            dev.revision = hardware_el.get('REVISION', None)
            dev.release = Release.loadxml(hardware_el.find('RELEASE'))

        return dev


class Product:
    """
    A class storing the product id and the linked URL where the firmware
    can be downloaded.

    Attributes:
        product_id: int
            The product id given by BOSE
        index_url:
            Specifies where the index.xml file is located. Use the XML-Document stored at
            this link as the parameter in load_index().
        device_class:
            Some products have a special device_class added to their entry. (Usage unknown)
    """
    def __init__(self, product_id: int = 0x00, index_url: str = None,
                 device_class: str = None) -> None:
        self.product_id = product_id
        self.index_url = index_url
        self.device_class = device_class


    def has_device_class(self) -> bool:
        """Returns whether this product stores a device class.

        :return: True, if the device_class attribute is not None
        :rtype: bool
        """
        return self.device_class is not None

    @staticmethod
    def loadxml(element: xmltree.Element) -> 'Product':
        """Reads the given XML-Element and loads information into an Product object.

        This function can be called outside this class.

        :param element: The root element.
        :type element: xmltree.Element
        :raises ValueError: if the given element is null
        :return: An object containing all relevant information about a software release.
        :rtype: Product
        """
        if not element:
            raise ValueError('Invalid XML-Element (nullptr)')

        return Product(
            int(element.get('PID', default='0'), 16),
            element.get('URL'),
            element.get('DEVICE_CLASS', None)
        )


def load_index(root: xmltree.Element) -> list:
    """Loads an XML-Element into a list of Firmware objects.

    This method can be called after fetching the index.xml file for a firmware
    release.

    :param root: The xml root-element for the index file.
    :type root: xmltree.Element
    :return:  A list of parsed firmware releases.
    :rtype: list
    """
    if not root:
        return []

    elements = []
    for dev in root.findall('DEVICE'):
        elements.append(Firmware.loadxml(dev))
    return elements


def load_lookupxml(root: xmltree.Element) -> list:
    """Loads a XML-Element into a list of BoseProducts.

    This method can be called after fetching the lookup.xml file.

    :param root: The xml root-element for the lookup file.
    :type root: xmltree.Element
    :return:  A list of parsed products.
    :rtype: list
    """
    if not root:
        return []

    data = []
    for prod in root.findall('PRODUCT'):
        data.append(Product.loadxml(prod))

    for prod in root.findall('PRA-PRODUCT'):
        data.append(Product.loadxml(prod))
    return data
