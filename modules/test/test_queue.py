import unittest
from mock import MagicMock

from modules import queue
import tools

tools.debug = True

class TestQueue(unittest.TestCase):
    def setUp(self):
        self.phenny = MagicMock()

        self.input = MagicMock()
        self.input.sender = '#test'
        self.input.nick = 'tester'
        self.input.admin = False

        queue.setup(self.phenny)

    def set_input(self, *args):
        self.input.group = lambda x: ((None,) + args)[x]

    def expect_msg(self, message):
        self.phenny.msg.assert_called_once_with(self.input.sender, message)

    def expect_reply(self, message):
        self.phenny.reply.assert_called_once_with(message)

    def _test_mutating(self, output, revert=True):
        input = self.input.group

        self.set_input('todo', 'reassign', 'devil')
        queue.queue(self.phenny, self.input)

        self.phenny.msg.reset_mock()
        self.phenny.reply.reset_mock()

        self.input.group = input
        queue.queue(self.phenny, self.input)
        self.expect_reply('You aren\'t the owner of this queue!')

        self.input.admin = True

        if revert:
            self.set_input('todo', 'reassign', self.input.nick)
            queue.queue(self.phenny, self.input)
            self.phenny.msg.reset_mock()

        self.input.group = input
        queue.queue(self.phenny, self.input)
        self.expect_msg(output)

    def test_display_not_found(self):
        self.set_input('display', 'todo', None)
        queue.queue(self.phenny, self.input)
        self.expect_reply('No queues found.')

    def test_create_empty(self):
        self.set_input('new', 'todo', None)
        queue.queue(self.phenny, self.input)
        self.expect_reply('Empty queue tester:todo created.')

    def test_create_with_items(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)
        self.expect_reply('Queue tester:todo with items lorem, ipsum created.')

    def test_display_empty(self):
        self.set_input('new', 'todo', None)
        queue.queue(self.phenny, self.input)

        self.set_input('display', 'todo', None)
        queue.queue(self.phenny, self.input)
        self.expect_msg('[tester:todo] - <empty>')

    def test_display_with_items(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('display', 'todo', None)
        queue.queue(self.phenny, self.input)
        self.expect_msg('[tester:todo] - lorem, ipsum')

    def test_add_items(self):
        self.set_input('new', 'todo', None)
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'add', 'dolor, sit, amet')
        self._test_mutating('[tester:todo] - dolor, sit, amet')

    def test_swap_items(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'swap', 'lorem, ipsum')
        self._test_mutating('[tester:todo] - ipsum, lorem')

    def test_move_items(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'move', 'dolor, amet')
        self._test_mutating('[tester:todo] - sit, amet, dolor')

    def test_swap_indices(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'swap', '0, 1')
        self._test_mutating('[tester:todo] - ipsum, lorem')

    def test_move_indices(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'move', '2, 1')
        self._test_mutating('[tester:todo] - dolor, amet, sit')

    def test_replace_items(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'replace', 'amet, meta')
        self._test_mutating('[tester:todo] - dolor, sit, meta')

    def test_replace_index(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'replace', '1, dolor')
        self._test_mutating('[tester:todo] - lorem, dolor')

    def test_remove_item(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'remove', 'sit')
        self._test_mutating('[tester:todo] - dolor, amet')

    def test_pop_item(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'pop', None)
        self._test_mutating('[tester:todo] - ipsum')

    def test_random_item(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'random', None)
        queue.queue(self.phenny, self.input)
        messages = ("'%s' is the lucky one." % x for x in ['dolor', 'sit', 'amet'])
        self.assertIn(self.phenny.reply.call_args[0][0], messages)

    def test_reassign_queue(self):
        self.set_input('new', 'todo', 'lorem, ipsum')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'reassign', 'devil')
        self._test_mutating('[devil:todo] - lorem, ipsum')

    def test_rename_queue(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)

        self.set_input('todo', 'rename', 'nope')
        self._test_mutating('[devil:nope] - dolor, sit, amet', revert=False)

    def test_delete_queue(self):
        self.set_input('new', 'todo', 'dolor, sit, amet')
        queue.queue(self.phenny, self.input)
        self.set_input('delete', 'todo', None)
        queue.queue(self.phenny, self.input)

        self.phenny.reply.reset_mock()

        self.set_input('display', 'todo', None)
        queue.queue(self.phenny, self.input)
        self.expect_reply('No queues found.')
