## Smart Contract Execution Policy

ContractShield never executes, deploys, or interacts with uploaded
Solidity contracts.

Uploaded contracts are treated as untrusted source code.

ContractShield only performs static analysis using Slither.
The contract is never compiled and executed as part of the scanning flow.