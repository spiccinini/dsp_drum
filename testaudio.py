import json
from collections import defaultdict, namedtuple

"""

The detected onset times will be compared with the ground-truth ones.
For a given ground-truth onset time, if there is a detection in a tolerance
time-window around it, it is considered as a correct detection (CD).
If not, there is a false negative (FN). The detections outside all the tolerance
windows are counted as false positives (FP). Doubled onsets (two detections for
one ground-truth onset) and merged onsets (one detection for two ground-truth onsets)
will be taken into account in the evaluation. Doubled onsets are a subset of the
FP onsets, and merged onsets a subset of FN onsets.

We define:

* Precision: P = Ocd / (Ocd +Ofp)
* Recall:  R = Ocd / (Ocd + Ofn)
* F-measure: F = 2*P*R/(P+R)

with these notations:

* Ocd: number of correctly detected onsets (CD)
* Ofn: number of missed onsets (FN)
* Om:  number of merged onsets
* Ofp: number of false positive onsets (FP)
* Od:  number of double onsets

Other indicative measurements:

* FP rate: FP = 100. * (Ofp) / (Ocd+Ofp)
* Doubled Onset rate in FP: D = 100 * Od / Ofp
* Merged Onset rate in FN: M = 100 * Om / Ofn

http://www.music-ir.org/mirex/wiki/2007:Audio_Onset_Detection
"""

class EVENT_TYPES:
    NOTE_ON = "NoteOn"


class Event(object):
    """Event object.

    >>> e = Event(EVENT_TYPES.NOTE_ON, time=25446, data={"velocity":0.57})
    >>> e.to_json()
    '{"data": {"velocity": 0.57}, "type": "NoteOn", "time": 25446}'
    >>> e2 = Event.from_json('{"data": {"velocity": 0.57}, "type": "NoteOn", "time": 25446}')
    >>> e2.data.get("velocity")
    0.57
    """

    def __init__(self, type, time, data=None):
        """
        Create an Event of type type. time is the time elapsed from the begining
        measured in seconds (float).
        """
        self.type = type
        self.time = time
        self.data = data

    @classmethod
    def to_json(cls, event, *args, **kwargs):
        return json.dumps(event.to_dict(), *args, **kwargs)

    def to_dict(self):
        return {"type": self.type, "time":self.time, "data":self.data}

    @classmethod
    def from_json(cls, s):
        d = json.loads(s)
        type, time, data = d.get("type"), d.get("time"), d.get("data")
        return Event(type, time, data)

    def __repr__(self):
        return "< Event: %s, %f, %s >" % (self.type, self.time, self.data)

class TestFile(object):
    def __init__(self, filename, events):
        self.filename = filename
        self.events = events

    def to_json(self, *args, **kwargs):
        events = [event.to_dict() for event in self.events]
        return json.dumps({"filename": self.filename, "events": events},
                           *args, **kwargs)
    @classmethod
    def from_json(cls, s):
        d = json.loads(s)
        events = [Event(**event) for event in d.get("events")]
        return TestFile(d.get("filename"), events)

    def __repr__(self):
        return "< Test: %s >" % self.filename

    @classmethod
    def load(cls, fp):
        return TestFile(**json.load(fp))

    def dump(self, fp):
        fp.write(self.to_json(indent=True))

Result = namedtuple('Result', ['cd', 'fp', 'fn'])

def precision(result):
    """
    Precision: P = Ocd / (Ocd +Ofp)
    """
    return result.cd / float( result.cd + result.fp)

def recall(result):
    """
    Recall:  R = Ocd / (Ocd + Ofn)
    """
    return result.cd / float( result.cd + result.fn)

def f_measure(result):
    """
    F-measure: F = 2*P*R/(P+R)
    """
    P, R = precision(result), recall(result)
    return 2*P*R/float(P+R)

def compare_events(ground_truth, guess, time_precision=0.05):
    """
    Compare a guess event list with a ground truth one. Returns a Result namedtuple.

    Note: time_precision must be less than the distance between two ground truth
    events. Only one truth event a (precision window) time.
    """

    results = defaultdict(int)
    paired_events = defaultdict(list) # key:ground_truth, value: [guess1, guess2]
    seen_events = set()

    for gt_event in ground_truth:
        detected = False
        for guess_event in guess:
            if (guess_event.time + time_precision/2. >= gt_event.time) and \
               (guess_event.time - time_precision/2. <= gt_event.time) and \
               guess_event.type == gt_event.type:

                if detected:
                    results["false_positive"] += 1
                else:
                    detected = True
                    results["correct"] += 1

                paired_events[gt_event].append(guess_event)
                seen_events.add(guess_event)

        if not detected:
            results["false_negative"] += 1

    for guess_event in guess:
        if guess_event not in seen_events:
            results["false_positive"] += 1

    return Result(results["correct"], results["false_positive"], results["false_negative"])



if __name__ == "__main__":
    import doctest
    doctest.testmod()

