import json

from backend.services.dataset_builder import DatasetBuilder
from backend.schemas.training_example import TrainingExample


def test_add_example(tmp_path):
    output_file = tmp_path / "training_data.jsonl"
    builder = DatasetBuilder(str(output_file))

    example = TrainingExample(
        resume="""
        Python AWS FastAPI
        """,
        job_description="""
        Backend Engineer
        Python AWS
        """,
        score=92,
        reason="Strong match"
    )

    builder.add_example(example)

    lines = output_file.read_text().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["score"] == 92
    assert data["reason"] == "Strong match"


