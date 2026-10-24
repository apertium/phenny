from bot import Phenny, COMMANDS, KEYWORDS, EVENTS
import tools
import pathlib

class TestBot(Phenny):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.write_queue = []

    def write(self, args, text=None):
        line = self.prepare_outgoing_message(args, text)
        self.write_queue.append(line.decode('utf-8'))

    def msg(self, *args, **kwargs):
        super().msg(*args, **kwargs)
        self.stack = [] # cancel the cooldown timer

class TestConfig:
    nick = 'begiak-test'
    host = 'somewhere.irc.net'
    channels = ['#Testsworth']
    ignore = []
    admins = ['admin']
    owner = 'owner'

class CommandTest:
    modules = []
    
    def add_config(self):
        pass
        
    def setUp(self):
        global COMMANDS, KEYWORDS, EVENTS
        COMMANDS.clear()
        KEYWORDS.clear()
        EVENTS.clear()
        self.config = TestConfig()
        self.config.enable = self.modules
        self.add_config()
        self.phenny = TestBot(self.config)

    def tearDown(self):
        for name in self.modules:
            db = tools.db_path(self.phenny, name)
            pathlib.Path(db).unlink(missing_ok=True)

    def run_event(self, line):
        self.phenny.handle_line(line.encode('utf-8'))
        ret = self.phenny.write_queue[:]
        self.phenny.write_queue = []
        return ret

    def run_message(self, message, nick='dangswan', channel='#apertium'):
        line = f':{nick}!someuser@somehost PRIVMSG {channel} :{message}'
        return self.run_event(line)

    def message_response(self, *args, **kwargs):
        ret = self.run_message(*args, **kwargs)
        self.assertEqual(len(ret), 1)
        self.assertTrue(ret[0].startswith('PRIVMSG'))
        self.assertIn(' :', ret[0])
        return ret[0].split(' :', 1)[1]

    def check_response(self, message, expected, **kwargs):
        out = self.message_response(message, **kwargs)
        if isinstance(expected, list):
            self.assertIn(out, expected)
        else:
            self.assertEqual(out, expected)

    def check_conversation(self, messages):
        for nick, command, response in messages:
            self.check_response(command, response, nick=nick)

    def get_module(self, name=None):
        n = name or self.modules[0]
        return self.phenny.modules[n]
