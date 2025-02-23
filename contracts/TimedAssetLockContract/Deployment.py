from algosdk.future import transaction
from algosdk import account, mnemonic, logic
from akita_inu_asa_utils import *


def deploy_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    public_key = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    signed_txn, tx_id = create_app_signed_txn(private_key,
                                                   public_key,
                                                   params,
                                                   on_complete,
                                                   approval_program,
                                                   clear_program,
                                                   global_schema,
                                                   local_schema)

    # send transaction
    client.send_transactions([signed_txn])

    wait_for_txn_confirmation(client, tx_id, 5)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Deployed new app-id:", app_id)

    return app_id


def deploy():
    developer_config = load_developer_config()

    algod_address = developer_config['algodAddress']
    algod_token = developer_config['algodToken']
    creator_mnemonic = developer_config['creatorMnemonic']

    private_key = mnemonic.to_private_key(creator_mnemonic)
    algod_client = get_algod_client(algod_token,
                                          algod_address)

    approval_program = load_compiled(file_path='assetTimedVault_Approval.compiled')
    clear_program = load_compiled(file_path='assetTimedVault_Clear.compiled')

    global_schema = load_schema(file_path='globalSchema')
    local_schema = load_schema(file_path='localSchema')

    deploy_app(algod_client, private_key, approval_program, clear_program, global_schema, local_schema)

