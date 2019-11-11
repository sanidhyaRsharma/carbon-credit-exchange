# Carbon Credit Exchange

An application for trading of carbon credits(CERs) on a blockchain.

## Running instructions

After cloning the repository and after every pull run the following command to install python modules

`python -m pip install -r dependencies.txt`

To run the project run the following command in the root folder

`python webapp.py`

After installing any new module run the following command to update `dependencies.txt`:

`python -m pip freeze > dependencies.txt`

Please update .gitignore in case you or your IDE creates some unwanted folders/configurations.

## Pending tasks

- [ ] Blockchain backend
  - [ ] broadcast_transaction in chain.py
  - [ ] broadcast_block in chain.py
  - [ ] resolve_conflicts in chain.py
  - [ ] Sharing Blockchain's transaction_pool
  - [ ] Delete those transactions which have been added to a pool once the block is verified and added to the chain
  - [ ] Make proof of stake run using kernel hash logic (using old transactions and granular timestamp instead of PoW style)
- [ ] Buy credits page
- [ ] Create credits page
- [ ] Authentication
- [ ] Download certificate page
- [ ] Verify digital signature page
