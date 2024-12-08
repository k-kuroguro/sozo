## Requirements

```sh
$ uv --version
uv 0.4.30 (61ed2a236 2024-11-04)

$ cmake --version # Required for building dlib
cmake version 3.28.3
```

## Setup

Download images required for the web app.
```sh
$ uv run scripts/download_images.py
```

## Running in production

If you want to run all the apps on the same computer,
```sh
$ uv run scripts/launch.py
```

If you want to run the processing app on a separate computer,
```sh
$ uv run scripts/launch.py --config config/launch_web_and_local.yaml # On the web and local computer

$ uv run scripts/launch.py --config config/launch_processing.yaml # On the processing computer
```
Make sure to update the IP addresses in the corresponding YAML configuration files (config/launch_web_and_local.yaml and config/launch_processing.yaml) to match the addresses of the target machines for communication.

## Running in development

To run the application in development mode with dummy communication between apps,
you can use the following command to start each app independently.

```sh
$ uv run scripts/run_web_dev.py

$ uv run scripts/run_processing_dev.py

$ uv run scripts/run_local_dev.py
```
