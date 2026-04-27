from django.test import LiveServerTestCase
import urllib.request


class LiveSiteTest(LiveServerTestCase):
    def test_home_page_loads(self):
        # check home page is actually running
        response = urllib.request.urlopen(self.live_server_url + '/')
        self.assertEqual(response.getcode(), 200)

    def test_flight_search_loads(self):
        response = urllib.request.urlopen(self.live_server_url + '/flights/search/')
        self.assertEqual(response.getcode(), 200)
