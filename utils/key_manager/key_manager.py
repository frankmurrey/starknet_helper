import hashlib

from utlis.key_manager.seed_phrase_helper.crypto import (HDPrivateKey,
                                                         HDKey)
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair

from starknet_py.hash.address import compute_address


def get_key_pair_from_pk(private_key):
    return KeyPair.from_private_key(private_key)


def get_argent_key_from_phrase(mnemonic):
    master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)

    root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
    acc_private_key = root_keys[-1]

    keys = HDKey.from_path(acc_private_key, '0/0')
    eth_key = keys[-1]._key.to_hex()

    master_key = HDPrivateKey.master_key_from_seed(eth_key)

    root_keys = HDKey.from_path(master_key, "m/44'/9004'/0'/0/0")

    private_key = grid_key(root_keys[-1]._key.to_hex())

    return private_key


def get_braavos_key_from_phrase(mnemonic):
    master_key = HDPrivateKey.master_key_from_mnemonic(mnemonic)

    root_keys = HDKey.from_path(master_key, "m/44'/9004'/0'/0/0")

    private_key = eip2645_hashing(root_keys[-1]._key.to_hex())

    return private_key


def get_braavos_addr_from_private_key(
        private_key: hex,
        cairo_version: int = 0
) -> hex:
    # TODO replace class has for cairo 1 when it will be available
    if cairo_version == 0:
        class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
    elif cairo_version == 1:
        class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e
    else:
        raise ValueError(f'Invalid cairo version: {cairo_version}')

    key_pair = KeyPair.from_private_key(private_key)
    salt = key_pair.public_key
    account_initialize_call_data = [key_pair.public_key]
    call_data = [
        0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
        0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
        len(account_initialize_call_data),
        *account_initialize_call_data
    ]
    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=call_data,
        deployer_address=0,
    )
    return address


def get_argent_addr_from_private_key(
        private_key: hex,
        cairo_version: int = 1
) -> hex:
    if cairo_version == 0:
        class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
    elif cairo_version == 1:
        class_hash = 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003
    else:
        raise ValueError(f'Invalid cairo version: {cairo_version}')

    key_pair = KeyPair.from_private_key(private_key)
    salt = key_pair.public_key

    account_initialize_call_data = [key_pair.public_key, 0]

    if cairo_version == 0:
        call_data = [
            0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2,
            0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463,
            len(account_initialize_call_data),
            *account_initialize_call_data
        ]
    else:
        call_data = account_initialize_call_data

    address = compute_address(
        salt=salt,
        class_hash=class_hash,
        constructor_calldata=call_data,
        deployer_address=0,
    )

    return address


def eip2645_hashing(key0):
    N = 2**256

    starkCurveOrder = 0x800000000000010FFFFFFFFFFFFFFFFB781126DCAE7B2321E66A241ADC64D2F

    N_minus_n = N - (N % starkCurveOrder)

    i = 0
    while True:
        x = concat(arrayify(key0), arrayify(i))

        key = int(get_payload_hash(x), 16)

        if key < N_minus_n:
            return hex(key % starkCurveOrder)


def grid_key(key_seed):
    keyValueLimit = 0x800000000000010ffffffffffffffffb781126dcae7b2321e66a241adc64d2f
    sha256EcMaxDigest = 0x10000000000000000000000000000000000000000000000000000000000000000

    maxAllowedVal = sha256EcMaxDigest - (sha256EcMaxDigest % keyValueLimit)

    i = 0

    while True:
        key = hash_key_with_index(key_seed, i)
        i += 1
        if key <= maxAllowedVal:
            break

    res = hex(abs(key % keyValueLimit))
    return res


def hash_key_with_index(key, index):
    payload = concat(arrayify(key), arrayify(index))

    payload_hash = get_payload_hash(payload)
    return int(payload_hash, 16)


def concat(a, b):
    return a + b


def arrayify(hex_string_or_big_number_or_arrayish):
    try:
        value = int(hex_string_or_big_number_or_arrayish)

    except ValueError:
        value = int(hex_string_or_big_number_or_arrayish, 16)
    if value == 0:
        return [0]

    hex_v = hex(value)[2::]

    if len(hex_v) % 2 != 0:
        hex_v = "0" + hex_v

    result = []

    for i in range(int(len(hex_v) / 2)):
        offset = i * 2
        result.append(int(hex_v[offset:offset + 2], 16))

    return result


def get_payload_hash(payload):
    m = hashlib.sha256()

    for value in payload:
        hex_value = hex(value)[2::]
        if len(hex_value) == 1:
            hex_value = "0" + hex_value
        m.update(bytes.fromhex(hex_value))

    return m.hexdigest()
