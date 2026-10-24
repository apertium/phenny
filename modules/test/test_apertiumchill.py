import unittest
from modules.test.command_test import CommandTest

class TestApertiumchill(CommandTest, unittest.TestCase):
    modules = ['apertiumchill']

    def test_chill_chill(self):
        self.get_module().chill_channels['Testsworth'] = 20
        out = self.message_response('.chill', channel='Testsworth')
        self.assertIn('chill level is currently:', out)

    def test_chill_notchill(self):
        self.get_module().chill_channels['Testsworth'] = 0
        out = self.message_response('.chill', channel='Testsworth')
        self.assertIn('WARNING: CHILL LEVEL IS DANGEROUSLY LOW. RECOMMEND', out)
