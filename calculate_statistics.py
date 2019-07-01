import matplotlib.pyplot as plt
import json

CONCEPT_LEARNING_FILES = [
    "data/concept_learning1a.json",
    "data/concept_learning2a.json",
    "data/concept_learning1b.json",
    "data/concept_learning2b.json"
]

COMPOSITION_LEARNING_FILES = [
    "data/composition_learning0.json",
    "data/composition_learning1.json",
    "data/composition_learning2.json",
    "data/composition_learning3.json"
]


def print_statistics():
    TOTAL_DIALOGUE_COUNT = 0
    TOTAL_CORRECTED_ANNOTATIONS = 0

    print("CONCEPT LEARNING")
    for file in CONCEPT_LEARNING_FILES:
        dialog_count, corrected_annotations = print_concept_learning_statistics(file)

        TOTAL_DIALOGUE_COUNT += dialog_count
        TOTAL_CORRECTED_ANNOTATIONS += corrected_annotations

    print("COMPOSITION LEARNING")
    for file in COMPOSITION_LEARNING_FILES:
        dialog_count, corrected_annotations = print_composition_learning_statistics(file)

        TOTAL_DIALOGUE_COUNT += dialog_count
        TOTAL_CORRECTED_ANNOTATIONS += corrected_annotations

    print(f"GLOBAL TOTAL DIALOGUE COUNT: {TOTAL_DIALOGUE_COUNT}")
    print(f"GLOBAL MANUALLY CORRECTED DIALOGUE ANNOTATIONS: {TOTAL_CORRECTED_ANNOTATIONS}")

    print()
    print("COMPOSITION LEARNING PROGRESS")
    plot_composition_progress_graph(COMPOSITION_LEARNING_FILES[1:])


def print_concept_learning_statistics(file):
    with open(file) as f:
        dialogs = json.load(f)

    corrected_annotations = 0
    dialog_count = 0
    turn_count = 0
    successful_dialog_count = 0
    dialogs_with_payout = 0

    for dialog in dialogs:
        dialog_count += 1
        turn_count += get_turn_count(dialog)

        if was_task_payed_out(dialog):
            dialogs_with_payout += 1

        if dialog["ManualAnnotation"] != "valid":
            corrected_annotations += 1

        if dialog["SuccessCode"] == 1:
            successful_dialog_count += 1

    print(f"\t\t Statistics for: {file}")
    print(f"\t\t\t total dialogue count {dialog_count}")
    print(f"\t\t\t total turn count {turn_count}")
    print(f"\t\t\t avg turn count {turn_count / dialog_count:.2f}")
    print(f"\t\t\t success rate {successful_dialog_count / dialog_count:.2f}")
    print(f"\t\t\t dialogues with payout {dialogs_with_payout}")

    print("\n")

    return dialog_count, corrected_annotations


def print_composition_learning_statistics(file):
    with open(file) as f:
        dialogs = json.load(f)

    corrected_annotations = 0
    dialog_count = 0
    total_turn_count = 0
    dialogs_with_payout = 0

    teaching_dialog_count = 0
    teaching_turn_count = 0
    teaching_success_count = 0
    teaching_payout_count = 0

    retrieving_dialog_count = 0
    retrieving_turn_count = 0
    retrieving_success_count = 0
    retrieving_payout_count = 0

    for dialog in dialogs:
        dialog_count += 1

        turn_count = get_turn_count(dialog)
        has_payout = was_task_payed_out(dialog)
        total_turn_count += turn_count

        success_code = dialog["SuccessCode"]

        if has_payout:
            dialogs_with_payout += 1

        if dialog["ManualAnnotation"] != "valid":
            corrected_annotations += 1

        if is_teaching_task(dialog):
            teaching_dialog_count += 1
            teaching_turn_count += turn_count

            if success_code > 0:
                teaching_success_count += 1

            if has_payout:
                teaching_payout_count += 1
        else:
            retrieving_dialog_count += 1
            retrieving_turn_count += turn_count

            if success_code > 0:
                retrieving_success_count += 1

            if has_payout:
                retrieving_payout_count += 1

    print(f"\t\t Statistics for: {file}")
    print(f"\t\t\t total dialogue count {dialog_count}")
    print(f"\t\t\t total turn count {total_turn_count}")
    print(f"\t\t\t avg turn count {total_turn_count / dialog_count:.2f}")
    print(f"\t\t\t dialogues with payout {dialogs_with_payout}")
    print(f"\t\t\t teaching dialogue count {teaching_dialog_count}")
    print(f"\t\t\t teaching turn count {teaching_turn_count}")
    print(f"\t\t\t teaching avg turn count {teaching_turn_count / max(1, teaching_dialog_count):.2f}")
    print(f"\t\t\t teaching success rate {teaching_success_count / max(1, teaching_dialog_count):.2f}")
    print(f"\t\t\t teaching with payout {teaching_payout_count}")
    print(f"\t\t\t retrieving dialogue count {retrieving_dialog_count}")
    print(f"\t\t\t retrieving turn count {retrieving_turn_count}")
    print(f"\t\t\t retrieving avg turn count {retrieving_turn_count / max(1, retrieving_dialog_count):.2f}")
    print(f"\t\t\t retrieving success rate {retrieving_success_count / max(1, retrieving_dialog_count):.2f}")
    print(f"\t\t\t retrieving with payout {retrieving_payout_count}")

    print("\n")

    return dialog_count, corrected_annotations


def plot_composition_progress_graph(files):
    print("\tPlotting composition learning progress")
    progresses = []
    for file in files:
        progress = get_progress(file)
        print(f"\t\t\t progress (len: {len(progress)}) {file}")
        print(f"\t\t\t\t {progress}")
        progresses.append(progress)

    averaged_progress = []
    for i in range(min(len(p) for p in progresses)):
        success_sum = sum(p[i] for p in progresses)
        averaged_progress.append(success_sum / len(progresses))

    print(f"\t\t\t averaged progress (len: {len(averaged_progress)})")
    print(f"\t\t\t\t {averaged_progress}")

    # show the plot
    prefix_length = 10
    prefix = [0] * prefix_length
    x = list(range(-prefix_length, len(averaged_progress)))

    plt.title("Cumulative Success Count", fontsize=24)
    plt.xlabel("Retrieval attempts", fontsize=18)
    plt.ylabel("Retrieval successes", fontsize=18)

    for i, progress in enumerate(progresses):
        plt.plot(x, prefix + progress[0:len(averaged_progress)], label="run " + str(i + 1), color='lightgray',
                 linestyle='dashed')

    plt.plot(x, prefix + averaged_progress, label="averaged success count")
    plt.axvline(x=0.0, color='gray', linestyle='dotted')

    plt.legend(loc='upper center')
    plt.show()


def get_progress(file):
    with open(file) as f:
        dialogs = json.load(f)

    acc = 0
    progress = []
    for dialog in dialogs:
        if is_retrieval_task(dialog):
            continue

        if dialog["SuccessCode"] > 0:
            acc += 1

        progress.append(acc)

    return progress


def is_end_of_turn(event):
    return event["Type"] == "T_utterance"


def get_events(dialog):
    return dialog["DialogEvents"]


def get_turn_count(dialog):
    turn_count = 0
    for event in get_events(dialog):
        if is_end_of_turn(event):
            turn_count += 1

    return turn_count


def was_task_payed_out(dialog):
    for event in get_events(dialog):
        if is_payout_event(event):
            return True

    return False


def is_payout_event(event):
    return event["Type"] == "T_completition"


def is_teaching_task(dialog):
    return dialog["Task"] == "Provide restaurant info."


def is_retrieval_task(dialog):
    return dialog["Task"] != "Find a restaurant."


print_statistics()
