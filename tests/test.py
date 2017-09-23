import unittest,sys,logging,uuid,os,random
sys.path.append('..')
from os.path import exists
from config.config_support import Config


logging.basicConfig(level=logging.WARNING)
logging.getLogger('config.config_support').setLevel(logging.INFO)


def almost_equal(a,b):
    assert type(a) in [int,float]
    if a == b:
        return True
    if 0 != min(a,b):
        return abs(a - b)/abs(min(a,b)) < 1e-6
    else:
        # if one of them is 0, and a != b
        return False


class T1(unittest.TestCase):
    """should complain if the db does not exist and create_if_not_exists is False"""
    def test_config_create_if_not_exists1(self):
        name = str(uuid.uuid4())
        assert not exists(name)
        try:
            c = Config(name,create_if_not_exists=False)
        except RuntimeError:
            pass

    def test_config_create_if_not_exists2(self):
        """create if not exists"""
        name = str(uuid.uuid4())
        assert not exists(name)
        try:
            c = Config(name)
            self.assertTrue(exists(name))
        finally:
            os.remove(name)
            assert not exists(name)

    def test_non_existent_param(self):
        """should complain on attempt to read undefined parameter"""
        name = str(uuid.uuid4())
        assert not exists(name)
        check = False
        try:
            c = Config(name)
            assert exists(name)
            c.get('haha')
        except LookupError:
            check = True
        finally:
            os.remove(name)
            assert not exists(name)
        self.assertTrue(check)
        
    def test_create_param(self):
        """should create param if not exists"""
        name = str(uuid.uuid4())
        assert not exists(name)
        c = Config(name)
        assert exists(name)
        check = False
        try:
            c.get('haha')
        except LookupError:
            check = True
        self.assertTrue(check)

        try:
            v = random.random()
            c.set('haha',v)
            self.assertTrue(almost_equal(v,c.get('haha')))
        finally:
            os.remove(name)
            assert not exists(name)
        
    def test_update_param(self):
        """update existing parameter"""
        name = str(uuid.uuid4())
        assert not exists(name)
        try:
            c = Config(name)
            assert exists(name)
            
            for i in range(100):
                v = random.random()
                c.set('haha',v)
                self.assertTrue(almost_equal(v,c.get('haha')))

                v = random.random()
                c.set('haha',v)
                self.assertTrue(almost_equal(v,c.get('haha')))
        finally:
            os.remove(name)
            assert not exists(name)

    def test_same_as_present(self):
        name = str(uuid.uuid4())
        assert not exists(name)
        try:
            c = Config(name)

            for i in range(100):
                v = round(random.random(),6)
                self.assertTrue(c.set('haha',v))
                self.assertTrue(almost_equal(v,c.get('haha')))
                self.assertFalse(c.set('haha',v))
        finally:
            os.remove(name)
            assert not exists(name)


if __name__ == '__main__':
    unittest.main()
