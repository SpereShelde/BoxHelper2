from xml.dom.minidom import Document


class Feed(object):
    """Represents an RSS feed."""

    def __init__(self, title, url):
        """Initialize the feed."""
        self._document = Document()
        rss_element = self._document.createElement('rss')
        rss_element.setAttribute('version', '2.0')
        self._document.appendChild(rss_element)
        self._channel = self._document.createElement('channel')
        rss_element.appendChild(self._channel)
        self._channel.appendChild(self._create_text_element('title', title))
        self._channel.appendChild(self._create_text_element('link', url))

    def _create_text_element(self, type, text):
        """Create an element with a text node."""
        element = self._document.createElement(type)
        element.appendChild(self._document.createTextNode(text))
        return element

    def append_item(self, title, link=None, enclosure=None):
        """Append an item to the feed."""
        item = self._document.createElement('item')
        item.appendChild(self._create_text_element('title', title))
        if link:
            item.appendChild(self._create_text_element('link', link))
        if enclosure:
            en = self._document.createElement('enclosure')
            en.setAttribute('url', enclosure)
            en.setAttribute('type', 'application/x-bittorrent')
            item.appendChild(en)
        self._channel.appendChild(item)

    def get_xml(self):
        """Return the XML for the feed."""
        return self._document.toxml()
