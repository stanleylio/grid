import unittest,sys
sys.path.append('/home/stanley')


class T2(unittest.TestCase):

    def test_get_list_of_devices(self):
        from grid.config.config_support import get_list_of_devices
        self.assertTrue(len(get_list_of_devices()) > 0)

    def test_get_list_of_variables(self):
        from grid.config.config_support import get_list_of_variables
        self.assertTrue('FREQ' in get_list_of_variables('grid-gw-3'))

    def test_config_as_dict(self):
        from grid.config.config_support import config_as_dict
        print(config_as_dict())


if '__main__' == __name__:
    unittest.main()
