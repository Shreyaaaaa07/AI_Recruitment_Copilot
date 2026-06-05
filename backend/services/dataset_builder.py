import json

from backend.schemas.training_example import (
    TrainingExample
)

class DatasetBuilder:

    def __init__(
        self,
        output_file
    ):

        self.output_file = output_file

    def add_example(
        self,
        example: TrainingExample
    ):

        with open(
            self.output_file,
            "a"
        ) as f:

            f.write(
                json.dumps(
                    example.model_dump()
                )
            )

            f.write("\n")