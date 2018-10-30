import unittest
from modules import reload
from mock import MagicMock
 
class TestReload(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()
        self.input = MagicMock()
 
    def test_f_reload(self):
        d = {True:'calc.py', False:'calc.py'}
        for val in d:
            self.input.admin.return_value = val
            self.input.group.return_value = d[val]
            reload.f_reload(self.phenny, self.input)
        self.input.group.return_value = 'no_module.py'
        reload.f_reload(self.phenny, self.input)
        self.input.group.return_value = 'bot.py'
        reload.f_reload(self.phenny, self.input)
