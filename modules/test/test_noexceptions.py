import unittest
from modules.test.command_test import CommandTest

class TestNoexceptions(CommandTest, unittest.TestCase):
    modules = ['noexceptions']

    def test_noexceptions(self):
        self.check_response('there are some exceptions here',
                            nick='Testuser',
                            expected='NO EXCEPTIONS, Testuser!')

    def test_harglebarglep(self):
        self.check_response('.hargle', nick='test',
                            expected='HARGLE BARGLE, test!')

    def test_bargle(self):
        self.check_response('hargle', expected='bargle!')

    def test_hargle(self):
        self.check_response('bargle', expected='HARGLE BARGLE!')

    def test_udmurt(self):
        self.check_response('udmurt', expected=r'\o/ \o/ \o/ U D M U R T \o/ \o/ \o/')

    def test_particles(self):
        self.check_response('I call this a particle', nick='Testuser',
                            expected='Testuser: this is my particles face :(((((')

    def test_nightnight(self):
        message = {'nn, Testuser!', 'night, Testuser!', 'жашкы жат, Testuser!', 'later, Testuser!', 'sweet dreams, Testuser!', 'o/, Testuser!'}
        out = self.message_response('nn', nick='Testuser')
        self.assertIn(out, message)

    def test_uderp(self):
        message = {r'\o/ UD \o/, Testuser!', '（。々°） #u_dep, Testuser!', 'ᕕ(ᐛ)ᕗ #u_dep, Testuser!', 'universal derpendencies!, Testuser!', 'treegrams ftw!, Testuser!'}
        out = self.message_response('#u_dep', nick='Testuser')
        self.assertIn(out, message)
