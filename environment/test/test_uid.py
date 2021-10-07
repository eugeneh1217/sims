import unittest
import weakref

from environment import uid

class TestUidSystem(unittest.TestCase):
    # pylint: disable=too-few-public-methods
    class TestSystem():
        uid_system = uid.UidSystem()
        def __init__(self, name=None):
            self.uid_system.create(self)
            self.name = name

    def setUp(self):
        self.test_systems = [self.TestSystem(i) for i in range(5)]

    def tearDown(self):
        self.TestSystem.uid_system.reset()

    def test_uid_unique_uidsystem_uid(self):
        other_system_keys = list(
            self.TestSystem.uid_system.get_uids())
        self.assertListEqual(other_system_keys, [0, 1, 2, 3, 4])

    def test_init_unique_object_uid(self):
        test_system_uids = [
            system.uid for system in self.test_systems]
        self.assertListEqual(test_system_uids, test_system_uids)

    def test_get_by_uid(self):
        self.assertEqual(self.test_systems[4].uid, 4)
        self.assertEqual( # confirms accuracy of next assertion
            len(weakref.getweakrefs(self.test_systems[0])), 1)
        self.assertTrue(
            self.TestSystem.uid_system.get_by_uid(0)
            is weakref.getweakrefs(self.test_systems[0])[0])

if __name__ == '__main__':
    unittest.main()
