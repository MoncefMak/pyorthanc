import httpx
import pytest

from pyorthanc import Orthanc, RemoteModality
from .setup_server import ORTHANC_1, ORTHANC_2, clear_data, setup_data, add_modality

MODALITY = 'Orthanc2'
PAYLOAD = {'Level': 'Study', 'Query': {'PatientID': 'MP*'}}
PATIENT_INFORMATION = {
    'ID': '50610f37-9df85809-faaec921-9c829c41-e5261ca2',
    'IsStable': False,
    'LastUpdate': 'THIS_ALWAYS_VARY',
    'MainDicomTags': {
        'PatientBirthDate': '',
        'PatientID': 'MP15-067',
        'PatientName': 'DVH_Phantom',
        'PatientSex': 'O'
    },
    'Studies': ['1e21052b-c7b6ea5c-e1c7e4ec-672ca250-0c54d47e'],
    'Type': 'Patient'
}


@pytest.fixture
def client():
    yield Orthanc(ORTHANC_1.url, ORTHANC_1.username, ORTHANC_1.password)
    clear_data(ORTHANC_1)
    clear_data(ORTHANC_2)


@pytest.fixture
def modality(client):
    if ORTHANC_2.AeT not in client.get_modalities():
        add_modality(ORTHANC_1, ORTHANC_2.AeT, 'orthanc2', 4242)
        add_modality(ORTHANC_2, ORTHANC_1.AeT, 'orthanc1', 4242)

    return RemoteModality(client, ORTHANC_2.AeT)


def test_echo(modality):
    result = modality.echo()

    assert result


def test_query(modality):
    setup_data(ORTHANC_2)
    expected_query_answer = {
        '0008,0005': {'Name': 'SpecificCharacterSet', 'Type': 'String', 'Value': 'ISO_IR 100'},
        '0008,0050': {'Name': 'AccessionNumber', 'Type': 'String', 'Value': '20090926001'},
        '0008,0052': {'Name': 'QueryRetrieveLevel', 'Type': 'String', 'Value': 'STUDY'},
        '0008,0054': {'Name': 'RetrieveAETitle', 'Type': 'String', 'Value': 'ORTHANC'},
        '0010,0020': {'Name': 'PatientID', 'Type': 'String', 'Value': 'MP15-067'},
        '0020,000d': {'Name': 'StudyInstanceUID', 'Type': 'String', 'Value': '1.3.6.1.4.1.22213.2.6291.2.1'}
    }

    result = modality.query(PAYLOAD)

    assert 'ID' in result.keys()
    assert 'Path' in result.keys()

    queries_answers = modality.get_query_answers()[result['ID']]

    assert expected_query_answer == queries_answers


def test_failed_query(modality):
    BAD_PAYLOAD = {'Level': 'Study', 'Query': {'BadTag': 'MP*'}}

    with pytest.raises(httpx.HTTPError):
        modality.query(BAD_PAYLOAD)


def test_move(modality):
    cmove_data = {'TargetAet': ORTHANC_1.AeT}
    expected_move_answer = {
        'Description': 'REST API',
        'LocalAet': ORTHANC_1.AeT,
        'RemoteAet': ORTHANC_2.AeT,
        'Query': [{
            '0008,0050': '20090926001',
            '0008,0052': 'STUDY',
            '0010,0020': 'MP15-067',
            '0020,000d': '1.3.6.1.4.1.22213.2.6291.2.1'
        }],
    }
    setup_data(ORTHANC_2)

    query_result = modality.query(PAYLOAD)
    result = modality.move(query_result['ID'], cmove_data)

    assert result == expected_move_answer

    resulting_patient_information = modality.client.get_patients_id(
        modality.client.get_patients()[0]
    )

    assert {k: v for k, v in PATIENT_INFORMATION.items() if k not in ['LastUpdate']} == \
           {k: v for k, v in resulting_patient_information.items() if k not in ['LastUpdate']}


def test_store(modality):
    setup_data(ORTHANC_1)
    an_instance_identifier = modality.client.get_instances()[0]

    result = modality.store(an_instance_identifier)

    assert {k: v for k, v in result.items() if k != 'ParentResources'} == \
           {
               'Description': 'REST API',
               'FailedInstancesCount': 0,
               'InstancesCount': 1,
               'LocalAet': ORTHANC_1.AeT,
               'RemoteAet': ORTHANC_2.AeT
           }
