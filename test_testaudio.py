import json
import unittest

from testaudio import Event, compare_events, EVENT_TYPES, Result

class TestCompareEvents(unittest.TestCase):

    def test_simple_events(self):
        e1 = Event(EVENT_TYPES.NOTE_ON, time=1.5)
        e2 = Event(EVENT_TYPES.NOTE_ON, time=1.5)

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=0.001)
        self.assertEqual(r, Result(cd=1, fp=0, fn=0))

        r = compare_events(ground_truth=[e1], guess=[], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=0, fn=1))

        r = compare_events(ground_truth=[e2], guess=[], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=0, fn=1))

        r = compare_events(ground_truth=[], guess=[e1], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=1, fn=0))

        r = compare_events(ground_truth=[], guess=[e1, e2], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=2, fn=0))

    def test_window(self):
        e1 = Event(EVENT_TYPES.NOTE_ON, time=1)
        e2 = Event(EVENT_TYPES.NOTE_ON, time=1.5)

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=1, fn=1))

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=0.9)
        self.assertEqual(r, Result(cd=0, fp=1, fn=1))

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=1)
        self.assertEqual(r, Result(cd=1, fp=0, fn=0))

        e1 = Event(EVENT_TYPES.NOTE_ON, time=1)
        e2 = Event(EVENT_TYPES.NOTE_ON, time=1.05)

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=0.05)
        self.assertEqual(r, Result(cd=0, fp=1, fn=1))

        r = compare_events(ground_truth=[e1], guess=[e2], time_precision=0.1)
        self.assertEqual(r, Result(cd=1, fp=0, fn=0))

    def test_multiple_events(self):
        e1 = Event(EVENT_TYPES.NOTE_ON, time=1)
        e2 = Event(EVENT_TYPES.NOTE_ON, time=1.1)
        e3 = Event(EVENT_TYPES.NOTE_ON, time=1.5)
        e4 = Event(EVENT_TYPES.NOTE_ON, time=2)
        e5 = Event(EVENT_TYPES.NOTE_ON, time=2.1)

        r = compare_events(ground_truth=[e1,e2,e3,e4,e5], guess=[e1,e2,e3,e4,e5], time_precision=0.001)
        self.assertEqual(r, Result(cd=5, fp=0, fn=0))

        r = compare_events(ground_truth=[e1,e2,e3,e4], guess=[e1,e2,e3,e4,e5], time_precision=0.001)
        self.assertEqual(r, Result(cd=4, fp=1, fn=0))

        r = compare_events(ground_truth=[e1,e2,e3], guess=[e1,e2,e3,e4,e5], time_precision=0.001)
        self.assertEqual(r, Result(cd=3, fp=2, fn=0))

        r = compare_events(ground_truth=[e2], guess=[e2, e5], time_precision=0.001)
        self.assertEqual(r, Result(cd=1, fp=1, fn=0))


    def test_multiple_hard(self):
        gt1 = Event(EVENT_TYPES.NOTE_ON, time=1)
        gt2 = Event(EVENT_TYPES.NOTE_ON, time=2)
        gt3 = Event(EVENT_TYPES.NOTE_ON, time=3)

        g1 = Event(EVENT_TYPES.NOTE_ON, time=1.1)
        g2 = Event(EVENT_TYPES.NOTE_ON, time=2.1)
        g3 = Event(EVENT_TYPES.NOTE_ON, time=2.01)

        r = compare_events(ground_truth=[gt1, gt2], guess=[g1, g2, g3], time_precision=0.001)
        self.assertEqual(r, Result(cd=0, fp=3, fn=2))

        r = compare_events(ground_truth=[gt1, gt2], guess=[g1, g2, g3], time_precision=0.2)
        self.assertEqual(r, Result(cd=2, fp=1, fn=0))

        r = compare_events(ground_truth=[gt1, gt2, gt3], guess=[g1, g2, g3], time_precision=0.2)
        self.assertEqual(r, Result(cd=2, fp=1, fn=1))

