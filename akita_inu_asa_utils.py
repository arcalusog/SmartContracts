import base64
from algosdk.v2client import algod
from algosdk.future import transaction
from joblib import dump, load
import json
import os


def check_build_dir():
    if not os.path.exists('build'):
        os.mkdir('build')


def compile_program(client, source_code, file_path=None):
    compile_response = client.compile(source_code)
    if file_path == None:
        return base64.b64decode(compile_response['result'])
    else:
        check_build_dir()
        dump(base64.b64decode(compile_response['result']), 'build/' + file_path)


def dump_teal_assembly(file_path, program_fn_pointer):
    check_build_dir()
    with open('build/' + file_path, 'w') as f:
        compiled = program_fn_pointer()
        f.write(compiled)


def load_compiled(file_path):
    try:
        compiled = load('build/' + file_path)
    except:
        print("Error reading source file...exiting")
        exit(-1)
    return compiled


def load_developer_config(file_path='DeveloperConfig.json'):
    fp = open(file_path)
    return json.load(fp)


def get_algod_client(token, address):
    return algod.AlgodClient(token, address)


def write_schema(file_path, num_ints, num_bytes):
    schema = transaction.StateSchema(num_ints, num_bytes)
    dump(schema, 'build/' + file_path)


def load_schema(file_path):
    load('build/' + file_path)


def wait_for_txn_confirmation(client, transaction_id, timeout):
    """
    Wait until the transaction is confirmed or rejected, or until 'timeout'
    number of rounds have passed.
    Args:
        transaction_id (str): the transaction to wait for
        timeout (int): maximum number of rounds to wait
    Returns:
        dict: pending transaction information, or throws an error if the transaction
            is not confirmed or rejected in the next timeout rounds
    """
    start_round = client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(
                'pool error: {}'.format(pending_txn["pool-error"]))
        client.status_after_block(current_round)
        current_round += 1
    raise Exception(
        'pending tx not found in timeout rounds, timeout value = : {}'.format(timeout))

def sign_txn(unsigned_txn, private_key):
    """
        signs the provided unsigned transaction
            Args:
                unsigned_txn (???): transaction to be signed
                private_key (str): private key of sender
            Returns:
                ???: signed transaction
    """
    signed_tx = unsigned_txn.sign(private_key)
    return signed_tx

def create_app_signed_txn(private_key,
                          public_key,
                          params,
                          on_complete,
                          approval_program,
                          clear_program,
                          global_schema,
                          local_schema):
    """
        Creates an signed "create app" transaction to an application
            Args:
                private_key (str): private key of sender
                public_key (str): public key of sender
                params (???): parameters obtained from algod
                on_complete (???):
                approval_program (???): compiled approval program
                clear_program (???): compiled clear program
                global_schema (???): global schema variables
                local_schema (???): local schema variables
            Returns:
                tuple: Tuple containing the signed transaction and signed transaction id
    """
    unsigned_txn = transaction.ApplicationCreateTxn(public_key,
                                           params,
                                           on_complete,
                                           approval_program,
                                           clear_program,
                                           global_schema,
                                           local_schema)

    signed_txn = sign_txn(unsigned_txn, private_key)
    return signed_txn, signed_txn.transaction.get_txid()


def create_app_unsigned_txn(
                       public_key,
                       params,
                       on_complete,
                       approval_program,
                       clear_program,
                       global_schema,
                       local_schema):
    """
        Creates an unsigned "create app" transaction to an application
            Args:
                public_key (str): public key of sender
                params (???): parameters obtained from algod
                on_complete (???):
                approval_program (???): compiled approval program
                clear_program (???): compiled clear program
                global_schema (???): global schema variables
                local_schema (???): local schema variables
            Returns:
                ApplicationOptInTxn: unsigned transaction
    """
    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(public_key,
                                           params,
                                           on_complete,
                                           approval_program,
                                           clear_program,
                                           global_schema,
                                           local_schema)
    return txn


def opt_in_app_signed_txn(private_key,
                          public_key,
                          params,
                          app_id):
    """
    Creates and signs an "opt in" transaction to an application
        Args:
            private_key (str): private key of sender
            public_key (str): public key of sender
            params (???): parameters obtained from algod
            app_id (int): id of application
        Returns:
            tuple: Tuple containing the signed transaction and signed transaction id
    """
    txn = transaction.ApplicationOptInTxn(public_key,
                                          params,
                                          app_id)
    signed_txn = sign_txn(txn, private_key)
    return signed_txn, signed_txn.transaction.get_txid()


def opt_in_app_unsigned_txn(public_key,
                          params,
                          app_id):
    """
    Creates an unsigned "opt in" transaction to an application
        Args:
            public_key (str): public key of sender
            params (???): parameters obtained from algod
            app_id (int): id of application
        Returns:
            ApplicationOptInTxn: unsigned transaction
    """
    unsigned_txn = transaction.ApplicationOptInTxn(public_key,
                                                   params,
                                                   app_id)
    return unsigned_txn
