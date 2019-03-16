# PyOrthanc
Python library that wrap the Orthanc REST API and facilitate the manipulation of Orthanc data.

## Installation
If you have `git`:
```sh
pip install git+https://github.com/gacou54/pyorthanc.git
```

If not, clone the repository, unzip and pip install the directory:
```sh
pip install -e pyorthanc-master
```

## Usage
Be sure that Orthanc is running. The default URL (if running localy) is `http://localhost:8042`.

### Example of usage:

#### With Orthanc server:
```python
from orthanc import Orthanc


orthanc = Orthanc('http://localhost:8042')
orthanc.setup_credentials('username', 'password')  # If needed

# To get patients identifier and main information
patients_identifiers = orthanc.get_patients().json()

for patient_identifier in patients_identifiers:
    patient_information = orthanc.get_patient_information(patient_identifier).json()


# To get patient's studies identifier and main information
a_patient_identifier = patients_identifiers[0]
studies_identifiers = orthanc.get_studies(a_patient_identifier)

for study_identifier in studies_identifiers:
    study_information = orthanc.get_study_information(study_identifier).json()
```

#### Getting list of remote modalities
```python
from orthanc import Orthanc


orthanc = Orthanc('http://localhost:8042')
orthanc.setup_credentials('username', 'password')  # If needed

orthanc.get_modalities().json()
```

#### Query (C-Find) and Retrieve (C-Move) from remote modality:
```python
from orthanc import RemoteModality


remote_modality = RemoteModality('http://localhost:8042', 'modality')
remote_modality.setup_credentials('username', 'password')  # If needed

# Query (C-Find) on modality
data = {'Level': 'Study', 'Query': {'PatientID': '*'}}
query_response = remote_modality.query(data=data)

# Retrieve (C-Move) results of query on a target modality (AET)
remote_modality.retrieve(query_response.json()['ID'], 'target_modality')
```
