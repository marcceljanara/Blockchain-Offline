import os

from dotenv import load_dotenv

# pylint: disable=no-name-in-module
from iota_sdk import (ClientOptions, CoinType, StrongholdSecretManager, Wallet,
                      migrate_stronghold_snapshot_v2_to_v3)

load_dotenv()

v2_path = "../../../sdk/tests/wallet/fixtures/v2.stronghold"
v3_path = "./v3.stronghold"
node_url = os.environ.get('NODE_URL', 'https://api.testnet.shimmer.network')
client_options = ClientOptions(nodes=[node_url])
coin_type = CoinType.SHIMMER

try:
    secret_manager = StrongholdSecretManager(v2_path, "current_password")
    # This should fail with error, migration required.
    wallet = Wallet(
        os.environ['WALLET_DB_PATH'],
        client_options,
        coin_type,
        secret_manager)
except ValueError as e:
    print(e)

migrate_stronghold_snapshot_v2_to_v3(
    v2_path,
    "kucing_oyen",
    "wallet.rs",
    100,
    v3_path,
    "kucing_oyen")

secret_manager = StrongholdSecretManager(v3_path, "kucing_oyen")
# This shouldn't fail anymore as snapshot has been migrated.
wallet = Wallet(
    os.environ['WALLET_DB_PATH'],
    client_options,
    coin_type,
    secret_manager)

account = wallet.create_account(os.environ['ACCOUNT_NAME'])
print(account.get_metadata())