## Requirements

```sh
$ uv --version
uv 0.4.30 (61ed2a236 2024-11-04)

$ cmake --version # Required for building dlib
cmake version 3.28.3
```

## Running in production

```sh
$ uv run scripts/run.py
```

## Running in development

To run the application in development mode with dummy communication between apps,
you can use the following command to start each app independently.

```sh
$ uv run scripts/run_local_dev.py

$ uv run scripts/run_processing_dev.py

$ uv run scripts/run_web_dev.py
```
