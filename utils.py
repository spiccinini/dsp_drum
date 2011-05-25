import json

def test_algorithm(input_audio, ground_truth_events, algorithm, algorithm_kwargs=None,
                   compare_kwargs=None):
    if algorithm_kwargs is None:
        algorithm_kwargs = {}
    if compare_kwargs is None:
        compare_kwargs = {}

    guess_events = algorithm(input_audio, **algorithm_kwargs)

    result = compare_events(ground_truth_events, guess_events, **compare_kwargs)
    return result

def discover(path):
    audio_files = glob.glob(os.path.join(path, "*.wav"))
    ground_truth_audio_tuples = []

    for audio_file in audio_files:
        event_file = audio_file[:-4] + "_events.json"
        if os.path.exists(event_file):
            ground_truth_audio_tuples.append((audio_file, event_file)

    return ground_truth_audio_tuples


