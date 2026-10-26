import unittest
from modules.test.command_test import CommandTest

class TestQueue(CommandTest, unittest.TestCase):
    modules = ['item_queue']

    def test_display_not_found(self):
        self.check_response(
            '.queue display todo', nick='tester',
            expected='tester: No queues found.')

    def test_create_empty(self):
        self.check_response(
            '.queue new todo', nick='tester',
            expected='tester: Empty queue tester:todo created.')

    def test_create_with_items(self):
        self.check_response(
            '.queue new todo lorem, ipsum', nick='tester',
            expected='tester: Queue tester:todo with items lorem, ipsum created.')

    def test_display_empty(self):
        self.check_conversation([
            ('tester', '.queue new todo', 'tester: Empty queue tester:todo created.'),
            ('tester', '.queue display todo', '[tester:todo] - <empty>'),
        ])

    def test_display_with_items(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue display todo',
             '[tester:todo] - lorem, ipsum'),
        ])

    def test_add_items(self):
        self.check_response(
            '.queue new todo', nick='tester',
            expected='tester: Empty queue tester:todo created.')
        self.check_response(
            '.queue todo add dolor, sit, amet', nick='tester',
            expected='[tester:todo] - dolor, sit, amet')

    def test_swap_items(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue todo swap lorem, ipsum',
             '[tester:todo] - ipsum, lorem'),
        ])

    def test_move_items(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue todo move dolor, amet',
             '[tester:todo] - sit, amet, dolor'),
        ])

    def test_swap_indices(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue todo swap 0, 1',
             '[tester:todo] - ipsum, lorem'),
        ])

    def test_move_indices(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue todo move 2, 1',
             '[tester:todo] - dolor, amet, sit'),
        ])

    def test_replace_items(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue todo replace amet meta',
             '[tester:todo] - dolor, sit, meta'),
        ])

    def test_replace_index(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue todo replace 1, dolor',
             '[tester:todo] - lorem, dolor'),
        ])

    def test_remove_item(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue todo remove sit',
             '[tester:todo] - dolor, amet'),
        ])

    def test_pop_item(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue todo pop',
             '[tester:todo] - ipsum'),
        ])

    def test_random_item(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
        ])
        out = self.message_response('.queue todo random', nick='tester')
        messages = ("tester: '%s' is the lucky one." % x for x in ['dolor', 'sit', 'amet'])
        self.assertIn(out, messages)

    def test_reassign_queue(self):
        self.check_conversation([
            ('tester', '.queue new todo lorem, ipsum',
             'tester: Queue tester:todo with items lorem, ipsum created.'),
            ('tester', '.queue todo reassign devil',
             '[devil:todo] - lorem, ipsum'),
        ])

    def test_rename_queue(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue todo rename nope',
             '[tester:nope] - dolor, sit, amet'),
        ])

    def test_delete_queue(self):
        self.check_conversation([
            ('tester', '.queue new todo dolor, sit, amet',
             'tester: Queue tester:todo with items dolor, sit, amet created.'),
            ('tester', '.queue delete todo',
             'tester: Queue tester:todo deleted.'),
            ('tester', '.queue display todo', 'tester: No queues found.'),
        ])
