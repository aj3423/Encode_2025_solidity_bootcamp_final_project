from abc import ABC, abstractmethod
from Crypto.Cipher import AES
from Crypto.Util import Counter
from web3 import Web3


class Environment:
    def __init__(
        self,
        encode_password: str,
        ctf: str,
        rpc: str,
        wallet_priv_key: str,
        aes_key: bytes,
    ):
        self.encode_password = encode_password
        self.ctf = ctf
        self.rpc = rpc
        self.wallet_priv_key = wallet_priv_key
        self.aes_key = aes_key


def aes_enc(data: bytes, aes_key: bytes):
    nonce = b"00000000"
    ctr = Counter.new(64, prefix=nonce, initial_value=0)
    cipher = AES.new(aes_key, AES.MODE_CTR, counter=ctr)
    cipher_bytes = cipher.encrypt(data)
    return cipher_bytes


def encpypt_wallet(wallet: str, aes_key: bytes) -> bytes:
    enc_wallet = aes_enc(bytes.fromhex(wallet[2:]), aes_key)
    return enc_wallet


class Page(ABC):
    # Conver markdown to html: https://codebeautify.org/markdown-to-html
    @abstractmethod
    def body(self):
        pass

    @abstractmethod
    def submit_fields(self):
        pass

    @abstractmethod
    def handle_submit(self, env: Environment, j: dict):
        pass


class Home(Page):
    def body(self):
        return """
Quick Start:<br>
Install Metamask<br>
Get some Sepolia test ETH from the faucet<br>
Register your Ethereum address and a given `password`<br>
Click on a level to start. Level 0 is a tutorial.<br>
<br>
Levels:<br>
You get 1 point for submitting a solution and up to the maximum for correct solutions.<br>
<br>
#	Level Name	Max Score	<br>
0	Tutorial	2<br>
1	Array Sorting	5<br>
"""

    def submit_fields(self):
        return []

    def handle_submit(self, env: Environment, j: dict):
        pass


class Register(Page):
    def body(self):
        return """
Before you get started you need to register your Ethereum address. This will link your Ethereum address to the name you used to register with Encode and add you to the whitelist.<br>
<br>
Use the password provided by Encode & Extropy to register<br>
Once registered you will be able to submit levels solutions<br>
You should use the same Ethereum address for all levels
    """

    def submit_fields(self):
        return [
            {"hint": "Full Name", "id": "full_name"},
            {"hint": "Password", "id": "password"},
        ]

    def handle_submit(self, env: Environment, j: dict):
        password = j.get("password")
        if password != env.encode_password:
            return "wrong password"

        contract_abi = [
            {
                "inputs": [
                    {"name": "user", "type": "bytes20"},
                    {"name": "name", "type": "string"},
                ],
                "name": "register",
                "outputs": [],
                "payable": False,
                "type": "function",
            }
        ]
        w3 = Web3(Web3.HTTPProvider(env.rpc))

        if not w3.is_connected():
            raise Exception("Could not connect to the Ethereum node.")
        # Instantiate contract
        contract = w3.eth.contract(address=env.ctf, abi=contract_abi)

        # Define your function parameters
        useraddr = encpypt_wallet(j.get("wallet"), env.aes_key)
        username = j.get("full_name")[:32]

        admin = w3.eth.account.from_key(env.wallet_priv_key)

        # Call the contract function
        txn = contract.functions.register(useraddr, username).build_transaction(
            {
                "from": admin.address,
                "nonce": w3.eth.get_transaction_count(admin.address),
            }
        )
        signed_txn = w3.eth.account.sign_transaction(
            txn, private_key=env.wallet_priv_key
        )

        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        return "tx: " + w3.to_hex(txn_receipt["transactionHash"])


class Challenge(Page):
    def submit_fields(self):
        return [
            {"hint": "Solution Address", "id": "solution"},
            {"hint": "Solution Source Code", "id": "source_code", "type": "textarea"},
        ]

    def handle_submit(self, env: Environment, j: dict):
        useraddr = encpypt_wallet(j.get("wallet"), env.aes_key)
        enc_source_code = aes_enc(j.get("source_code").encode(), env.aes_key)
        solution = Web3.to_checksum_address(j.get("solution"))

        contract_abi = [
            {
                "name": "verify",
                "type": "function",
                "inputs": [
                    {"name": "studentContract", "type": "address"},
                ],
                "outputs": [
                    {"name": "score", "type": "uint8"},
                    {"name": "gasCost", "type": "uint256"},
                ],
                "payable": True,
            }
        ]
        w3 = Web3(Web3.HTTPProvider(env.rpc))
        contract = w3.eth.contract(address=self.lvl_contract, abi=contract_abi)
        score, gas_cost = contract.functions.verify(solution).call()

        return self.commit_result(
            env=env,
            ctf_contract=env.ctf,
            useraddr=useraddr,
            level=self.level,
            source_code=enc_source_code,
            score=score,
            gas_cost=gas_cost,
        )

    def commit_result(
        self,
        env: Environment,
        ctf_contract: str,
        useraddr: bytes,
        level: int,
        source_code: bytes,
        score: int,
        gas_cost: int,
    ):
        gas_cost = gas_cost - 1
        contract_abi = [
            {
                "name": "confirmSolution",
                "type": "function",
                "inputs": [
                    {"name": "user", "type": "bytes20"},
                    {"name": "level", "type": "uint8"},
                    {"name": "score", "type": "uint8"},
                    {"name": "gasCost", "type": "uint256"},
                    {"name": "sourceCode", "type": "bytes"},
                ],
                "outputs": [],
                "payable": False,
            }
        ]
        w3 = Web3(Web3.HTTPProvider(env.rpc))

        if not w3.is_connected():
            raise Exception("Could not connect to the Ethereum node.")
        contract = w3.eth.contract(address=env.ctf, abi=contract_abi)

        admin = w3.eth.account.from_key(env.wallet_priv_key)

        txn = contract.functions.confirmSolution(
            useraddr, level, score, gas_cost, source_code
        ).build_transaction(
            {
                "from": admin.address,
                "nonce": w3.eth.get_transaction_count(admin.address),
            }
        )
        signed_txn = w3.eth.account.sign_transaction(
            txn, private_key=env.wallet_priv_key
        )

        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        return (
            "tx: "
            + w3.to_hex(txn_receipt["transactionHash"])
            + "\n"
            + f"score: {score}, gasCost: {gas_cost}"
        )


class Lv0(Challenge):
    def __init__(self, lvl_contract: str):
        self.level = 0
        self.lvl_contract = lvl_contract

    def body(self):
        return """
<h1 id="level-0---return-42-tutorial">Level 0 - Return 42 (tutorial)</h1>
<p>This level is really simple. Use the interface below to write a smart contract. Your contract should contain a function called solution that returns a uint8. In this case the function body logic is very simply as the answer is always 42.</p>
<pre><code class="language-solidity">Interface:
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.17;

interface Isolution {
    function solution() external pure returns (uint8);
}
</code></pre>
        """


class Lv1(Challenge):
    def __init__(self, lvl_contract: str):
        self.level = 1
        self.lvl_contract = lvl_contract

    def body(self):
        return """
<h1 id="level-1---matrix-addition">Level 1 - Matrix Addition</h1>
<p>Write a function that adds two matrices returns the result. To keep things simple the array sizes will be fixed sizes of 2x3 (uint256[2][3]). Take a look at Wikipedia if you need help understanding matrix addition. Your solution should implement the following interface:</p>
<pre><code class="language-solidity">interface Isolution1 {
    function solution(
        uint256[2][3] calldata x, 
        uint256[2][3] calldata y
    ) external pure returns (
        uint256[2][3] memory
    );
}
</code></pre>

    """
