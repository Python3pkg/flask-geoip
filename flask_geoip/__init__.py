import pygeoip
from .metadata import __version_info__, __version__

CACHE_MAP = {
    'STANDARD': pygeoip.STANDARD,
    'MEMORY_CACHE': pygeoip.MEMORY_CACHE,
    'MMAP_CACHE': pygeoip.MMAP_CACHE,
}

PYGEOIP_METHODS = (
    # 'last_netmask',
    'country_code_by_addr',
    'country_code_by_name',
    'country_name_by_addr',
    'country_name_by_name',
    'org_by_addr',
    'org_by_name',
    'record_by_addr',
    'record_by_name',
    'region_by_addr',
    'region_by_name',
    'time_zone_by_addr',
    'time_zone_by_name',
)


class GeoIP(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('GEOIP_CACHE', pygeoip.STANDARD)
        cache_setting = app.config['GEOIP_CACHE']
        invalid_cache_setting_msg = ('{0} is not a valid GEOIP_CACHE setting! '
                                     'The following are available: {1}')

        if cache_setting not in CACHE_MAP.values():
            error_args = (cache_setting, ', '.join(CACHE_MAP.keys()))
            raise Exception(invalid_cache_setting_msg.format(*error_args))

        if 'GEOIP_FILEPATH' not in app.config:
            raise Exception('You must specify GEOIP_FILEPATH.')

        self._instance = pygeoip.GeoIP(app.config['GEOIP_FILEPATH'],
                                       app.config['GEOIP_CACHE'])


        # Set pygeoip's public methods on the class
        for method in PYGEOIP_METHODS:
            setattr(self, method, getattr(self._instance, method))

        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, exception):
        pass