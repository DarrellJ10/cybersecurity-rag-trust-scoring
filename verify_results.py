"""Verify the archived RAG study and print recorded results without model inference."""
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

BACKUP_NAME = "trust_detector_backup_20261027T030637Z.zip"
BACKUP_SHA256 = "599dc41687907dade3a6e0a62ba4c044be3d51697bf5411a8f9b80cfbe145664"
METHOD_SHA256 = "5348a7aa4e4eec8e441968e6cb7b1c8db3e5b5e1b012ab5aac796ed8bbe73144"
PLAN_SHA256 = "71cb213b0f603e7791b8ac81002746fe015d9f6ba60954dc95030af9fc054b33"
CORPUS_SHA256 = "3d79912c5233d7c273a19576416e910627bf640a7759c937140d07f8c2e09dd0"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root=None):
    """Read only; reject missing/tampered files and return the original summaries."""
    root = Path(root) if root is not None else Path(__file__).resolve().parent
    archive_path = root / BACKUP_NAME
    require(sha256(archive_path.read_bytes()) == BACKUP_SHA256, "Final backup hash mismatch")
    with zipfile.ZipFile(archive_path) as archive:
        require(archive.testzip() is None, "ZIP integrity check failed")
        manifest = json.loads(archive.read("backup_manifest.json"))
        workspace = manifest["workspace_folder"]
        records = manifest["files"]
        require(manifest["file_count"] == len(records) == 430, "Unexpected backup file count")
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP member names")
        for record in records:
            relative = PurePosixPath(record["path"])
            require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe archive path")
            data = archive.read(workspace + "/" + record["path"])
            require(len(data) == record["bytes"], "File size mismatch: " + record["path"])
            require(sha256(data) == record["sha256"], "File hash mismatch: " + record["path"])

        def read_suffix(suffix):
            matches = [name for name in names if name.endswith(suffix)]
            require(len(matches) == 1, "Missing or ambiguous archive suffix: " + suffix)
            return archive.read(matches[0])

        prefix = "/results/heldout_evaluation_v1/"
        method_bytes = read_suffix(prefix + "method_settings_v1.json")
        plan_bytes = read_suffix(prefix + "test_run_plan_v1.json")
        require(sha256(method_bytes) == METHOD_SHA256, "Frozen method settings mismatch")
        require(sha256(plan_bytes) == PLAN_SHA256, "Frozen test plan mismatch")
        package = "/evaluation_package_v1_20261021T1616878004Z/"
        corpus_bytes = read_suffix(package + "corpus/corpus.json")
        require(sha256(corpus_bytes) == CORPUS_SHA256, "Frozen corpus mismatch")
        for file_name in ["method_settings_v1.json", "test_run_plan_v1.json"]:
            require((root / file_name).read_bytes() == read_suffix(prefix + file_name),
                    "Browsable settings differ from archive: " + file_name)
        for file_name in ["claims.json", "development_questions.json", "test_questions.json",
                          "grading_rules.json", "evidence_evaluation_rules.json"]:
            require((root / file_name).read_bytes() == read_suffix(package + file_name),
                    "Browsable data differ from frozen archive: " + file_name)
        require((root / "corpus.json").read_bytes() == corpus_bytes, "Browsable corpus mismatch")

        workload_bytes = read_suffix(prefix + "generation_workload_v1.json")
        workload = json.loads(workload_bytes)
        cache = json.loads(read_suffix("/cache/qwen_answer_cache_v1.json"))
        groups = workload["prompt_groups"]
        require(len(groups) == 56, "Expected 56 unique held-out prompts")
        require(workload["method_condition_question_uses"] == 128, "Expected 128 answer uses")
        require(len(workload["policy_abstentions"]) == 5, "Expected five policy abstention uses")
        require(sum(len(group["uses"]) for group in groups) == 123,
                "Expected 123 generated-answer uses")
        group_by_key = {group["prompt_key"]: group for group in groups}
        require(len(group_by_key) == 56, "Duplicate held-out prompt keys")
        for group in groups:
            key = group["prompt_key"]
            require(key in cache, "Missing completed answer: " + key)
            record = cache[key]
            require(record["messages"] == group["messages"], "Cached prompt mismatch")
            require(sha256(record["answer"].encode()) == record["answer_sha256"],
                    "Cached answer checksum mismatch")

        contexts = json.loads(read_suffix(prefix + "method_context_results_v1.json"))
        require(contexts["test_run_plan_sha256"] == PLAN_SHA256, "Context plan mismatch")
        require(len(contexts["summary"]) == 27, "Expected 27 held-out conditions")

    with zipfile.ZipFile(root / "heldout_review_results.zip") as review_zip:
        review_bytes = review_zip.read("heldout_ai_review_results_v1.json")
        require((root / "heldout_ai_review_results_v1.json").read_bytes() == review_bytes,
                "Browsable answer review differs from packaged review")
    review = json.loads(review_bytes)
    require(review["source_backup_sha256"] == BACKUP_SHA256, "Review backup mismatch")
    require(review["test_run_plan_sha256"] == PLAN_SHA256, "Review plan mismatch")
    require(review["source_generation_workload_sha256"] == sha256(workload_bytes),
            "Review generation workload mismatch")
    require(review["counts"]["unique_generations"] == 56, "Review generation count mismatch")
    require(review["counts"]["total_answer_uses"] == 128, "Review answer-use count mismatch")
    require(len(review["generated_answer_reviews"]) == 56, "Review record count mismatch")
    require({r["prompt_key"] for r in review["generated_answer_reviews"]} == set(group_by_key),
            "Reviewed prompts do not match the held-out workload")
    for record in review["generated_answer_reviews"]:
        require(record["answer"] == cache[record["prompt_key"]]["answer"],
                "Reviewed answer differs from saved generation")
        require(sha256(record["answer"].encode()) == record["answer_sha256"],
                "Review answer checksum mismatch")
    require(len(review["summary"]) == 8, "Expected eight condition/method summary rows")

    snapshot_manifest = root / "artifact_manifest.json"
    if snapshot_manifest.exists():
        for record in json.loads(snapshot_manifest.read_text())["files"]:
            data = (root / record["path"]).read_bytes()
            require(sha256(data) == record["sha256"], "Repository file checksum mismatch: " + record["path"])

    return {"verified_backup_files": len(records), "unique_generations": len(groups),
            "policy_abstention_uses": 5, "total_answer_uses": 128,
            "review_status": review["status"], "context_summary": contexts["summary"],
            "answer_summary": review["summary"]}


def print_report(report):
    print("Final checkpoint verified:", report["verified_backup_files"], "files")
    print("Frozen method settings, test plan, corpus, prompts, and answer hashes: verified")
    print("Unique held-out model generations:", report["unique_generations"])
    print("Policy abstention uses:", report["policy_abstention_uses"])
    print("Total answer uses:", report["total_answer_uses"])
    print("Review status:", report["review_status"])
    print("\nCOMBINED POISONED CONDITION: all8_copies2")
    for condition in report["context_summary"]:
        if condition["condition_id"] != "all8_copies2":
            continue
        for method, values in condition["methods"].items():
            print(f"{method}: poison removed {values['poison_occurrences_removed']}/{values['poison_occurrences_before']}; "
                  f"benign removed {values['benign_occurrences_removed']}/{values['benign_occurrences_before']}; "
                  f"reference coverage {values['sufficient_reference_after']}/{values['answerable_questions']}")
    print("\nANSWER REVIEW: eight answerable and eight unanswerable queries per row")
    for row in report["answer_summary"]:
        print(f"{row['condition_id']} | {row['method']} | answerable: {row['answerable_grade_counts']} | "
              f"unanswerable: {row['unanswerable_response_counts']}")
    print("\nVerification only: no model inference, regrading, or threshold changes.")


if __name__ == "__main__":
    print_report(verify())
