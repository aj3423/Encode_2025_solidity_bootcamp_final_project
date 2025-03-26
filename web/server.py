import os
import time
import threading

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pages import Environment, Home, Register, Lv0, Lv1

from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account


############### config begin ################
# forge create --rpc-url $SEPOLIA --private-key $PRIV_0 src/CTF.sol:CTF --broadcast
CTFContract = "0x7d2E153C13373B43146eEb692CBc2aea36f23895"

AesKey = b"12345rstxyzabcde"
# the CTF will end after 7 days, the server will automatically publish the AesKey to the contract.
DueDay = 7

EncodePassword = "q"  # Encode registration password

AllPages = [
    Home(),
    Register(),
    Lv0("0x28d85075C94cE8ea69ed3d393cAA4211cC0ea94e"),
    Lv1("0xe9C7290895594E762e28760FE68ee4761ECb04f3"),
]

ChallengeMessage = "challenge message"
############### config end ################


env = Environment(
    encode_password=EncodePassword,
    ctf=CTFContract,
    # or use "https://eth-sepolia.public.blastapi.io/"
    rpc=os.getenv("SEPOLIA"),
    # admin wallet private key, 64 bytes hex string without leading '0x'
    wallet_priv_key=os.getenv("PRIV_0"),
    aes_key=AesKey,
)


###### schedule to commit AesKey after 7 days
def commit_aes_key():
    global env
    contract_abi = [
        {
            "name": "setEncpyptionKey",
            "type": "function",
            "inputs": [
                {"name": "key", "type": "bytes16"},
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

    txn = contract.functions.setEncpyptionKey(AesKey).build_transaction(
        {
            "from": admin.address,
            "nonce": w3.eth.get_transaction_count(admin.address),
        }
    )
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=env.wallet_priv_key)

    w3.eth.send_raw_transaction(signed_txn.raw_transaction)


now = time.time()
seconds_to_wait = DueDay * 24 * 60 * 60  # n days in seconds
# seconds_to_wait = 5

timer = threading.Timer(seconds_to_wait, commit_aes_key)
timer.start()
###### end of schedule


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

template = Jinja2Templates(directory="./")


def verify_wallet(wallet, signed):
    global ChallengeMessage
    signature = signed

    # Expected wallet address
    expected_wallet_address = Web3.to_checksum_address(wallet)

    # Encode the message in the same way as it was signed (Ethereum's personal_sign)
    message = encode_defunct(text=ChallengeMessage)

    # Recover the address from the signature
    recovered_address = Account.recover_message(message, signature=signature)
    recovered_address = Web3.to_checksum_address(recovered_address)

    if recovered_address == expected_wallet_address:
        pass
    else:
        raise RuntimeError("Signature is invalid.")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page: str = Query(...)):
    global ChallengeMessage, CTFContract

    pg = next(
        (p for p in AllPages if p.__class__.__name__.lower() == page.lower()), None
    )

    pages = [p.__class__.__name__ for p in AllPages]

    context = {
        "request": request,
        "pages": pages,
        "currPage": pg.__class__.__name__,
        "ctfContract": CTFContract,
        "msgToSign": ChallengeMessage.encode().hex(),
        "body": pg.body(),
        "fields": pg.submit_fields(),
        "levelCount": len(AllPages) - 2,
    }
    return template.TemplateResponse("index.html", context)


@app.post("/submit")
async def submit(request: Request, page: str = Query(...)):
    global env

    pg = next(
        (p for p in AllPages if p.__class__.__name__.lower() == page.lower()), None
    )

    j = await request.json()
    wallet = j.get("wallet")
    signed = j.get("signed")
    verify_wallet(wallet, signed)

    try:
        return pg.handle_submit(env, j)
    except Exception as e:
        return str(e)
