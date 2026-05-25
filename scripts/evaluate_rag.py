import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import load_manual, retrieve


CASES = [
    {
        "name": "chest_pain",
        "payload": {"chief_concern": "chest pain sweating low oxygen left arm pain", "top_k": 4},
        "expected": {"Emergency Department Chest Pain Intake"},
    },
    {
        "name": "sepsis",
        "payload": {"chief_concern": "suspected infection fever low blood pressure sepsis fluids", "top_k": 4},
        "expected": {"Sepsis Screening And Escalation"},
    },
    {
        "name": "stroke",
        "payload": {"chief_concern": "facial droop arm weakness speech difficulty last known well", "top_k": 4},
        "expected": {"Stroke Alert Workflow"},
    },
    {
        "name": "handoff",
        "payload": {"question": "What should a nurse handoff include for an unstable patient?", "top_k": 4},
        "expected": {"Nurse Handoff Standard"},
    },
]


def main():
    documents = load_manual()
    passed = 0
    for case in CASES:
        titles = {document["title"] for document in retrieve(case["payload"], documents)}
        matched = bool(case["expected"] & titles)
        passed += int(matched)
        status = "PASS" if matched else "FAIL"
        print(f"{status} {case['name']}: retrieved={sorted(titles)} expected={sorted(case['expected'])}")

    score = passed / len(CASES)
    print(f"RAG retrieval score: {score:.2%}")
    if score < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
