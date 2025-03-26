A slightly improved version of the Encode 2025 solidity CTF.

# Improvements:
1. Provide a way to view other people's solution.
2. Result is updated instantly after committing a solution.
3. Competitors won't be able to see other people's wallet during the CTF. 

# How it works:
- It allows committing the source code along with the solution, the source code will be encrypted using an AES_KEY and stored in the CTF contract.
- After it ends, the backend will publish the AES_KEY to the contract. The client will use it to decrypt the encrypted source code.

# How to test:
0. set the environment variables:
  - $SEPOLIA, it's the RPC url for sepolia testnet.
  - $PRIV_0, it's the admin private key, the CTF contract should be deployed by this wallet.
1. go to dir `web`
2. `uvicorn server:app --reload`
3. open "http://127.0.0.1:8000/?page=home"

# Screenshot:
![image](https://github.com/user-attachments/assets/71168208-f111-4510-8be6-2d9385b69fa7)
