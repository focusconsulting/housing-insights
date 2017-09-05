from housinginsights.sources.base import BaseApiConn
from housinginsights.tools.logger import HILogger

logger = HILogger(name=__file__, logfile="sources.log", level=10)

class GoogleMapsApiConn(BaseApiConn):
    """
    API Interface to google maps.
    Use public methods to retrieve data.
    """

    # Note - this is not the only base url for google maps
    # if we expand further should consider adding additional params to the
    # init call to dictate which base url to use or make base url = 'http://'
    BASEURL = 'http://maps.google.com'

    def __init__(self,baseurl=None,proxies=None,database_choice=None):
        super().__init__(baseurl=GoogleMapsApiConn.BASEURL)

    def check_street_view(self, latitude, longitude, radius=50):
        """
        Returns the result from checking whether street view panorama is
        available or not. We're using the url endpoint based on the
        information from this link:
        https://andresmartinezsoto.wordpress.com/2012/05/19/php-some-google-maps-v3-streetview-tricks/

        :param latitude: latitude for location of interest
        :param longitude: longitude for location of interest
        :param radius: the distance in meters of range for finding a valid
        panorama
        :return: json object with the following keys: 'Data', 'Links',
        'Location', 'Projection'. Location is the data we're interested in.
        """

        url = '/cbk?output=json&hl=en&ll={},' \
              '{}&radius={}&cb_client=maps_sv&v=4'.format(latitude, longitude,
                                                          radius)

        result = self.get(url)

        if result.status_code != 200:
            err = "An error occurred during request: status {0}"
            logger.exception(err.format(result.status_code))
            raise

        return result.json()

    def get_street_view_url(self, latitude, longitude, pano_id=None):
        """
        Returns a url string for launching a viewer to display Google maps
        Street View images as interactive panoramas. This is based on info
        from Google Maps API end point from this link:
        https://developers.google.com/maps/documentation/urls/guide#street-view-action

        :param latitude: the latitude coordinate for a given location
        :param longitude: the longitude coordinate for a given location
        :param pano_id: the specific panorama ID of the image to be
        displayed. This is optional but works much better if provided because
        for some reason lat/lon when used in Google Maps returns inconsistent
        results.
        :return: string representing the street view url end point
        """
        endpoint_url = 'https://www.google.com/maps/@?api=1&map_action=pano'

        if pano_id is not None:
            endpoint_url += '&pano={}'.format(pano_id)

        endpoint_url += '&viewpoint={},{}'.format(latitude, longitude)

        return endpoint_url

