# Job Lib

A lightweight application to run arbitrary docker images on GCP infrastructure. 

### Local Development


1. Pre-requisite: Python 3.10 is available.
2. Install poetry (if necessary) and create virtualenv for project, with all requirements.
```
pip install poetry
poetry install
```

3. Install Terraform (v1.0.10) via [tfenv](https://github.com/tfutils/tfenv).
```
brew install tfenv
tfenv install 1.0.10
```

4. [Download and configure gcloud](https://cloud.google.com/sdk/docs/install) for using personal credentials for interacting with GCP from the CLI.

