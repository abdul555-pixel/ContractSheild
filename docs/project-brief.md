# ContractShield — Project Brief

## What is a Smart Contract?

Smart contract is a self executing contract that enforces the rules when the certain conditions are met.

Smart contracts are generally used in blockchain transactions, it is very safe because it cannot be altered or changed.

## What is Solidity?

Solidity is an object oriented programming language that is specifically designed to make smart contracts. It requires a virtual environment (Ethereum Virtual Machine) to run the code. If you know basic concepts of C++ or Python, you can easily understand solidity code.

## What it does?

ContractShield is an AI-powered smart contract auditing platform that automatically scans Solidity contracts for security vulnerabilities before they are deployed.

A user uploads or pastes a Solidity smart contract, and the platform:

- Performs static analysis using Slither.
- Detects common security vulnerabilities (e.g., reentrancy, access control flaws, integer overflows, unchecked external calls).
- Uses an LLM to explain each vulnerability in simple, human-readable language.
- Assigns a severity level (Critical, High, Medium, Low).
- Suggests secure code fixes and generates code diffs.

The result is an interactive, easy-to-understand security report that helps developers fix issues before deployment.

> **Note:** The original design also called for a RAG (retrieval-augmented generation) layer, referencing historical blockchain exploits to add real-world context to each finding. This was scoped out of the current build to keep the core Slither + LLM pipeline reliable within the hackathon timeframe, and remains on the roadmap (see Future Scope).

## Who it's for?

ContractShield is designed for:

- Blockchain developers writing Solidity smart contracts.
- Web3 startups that cannot afford expensive professional security audits.
- Students and beginner blockchain developers who need understandable explanations of security issues.
- Security researchers and auditors who want a faster pre-audit analysis tool.
- Hackathon participants building decentralized applications (dApps) who need to verify their smart contracts before submission.

## What makes it different?

Unlike traditional static analysis tools, ContractShield doesn't stop at detecting vulnerabilities — it helps developers understand and resolve them.

Key differentiators include:

- AI-powered explanations that translate technical findings into plain English.
- Actionable remediation, including suggested secure code patches.
- Transparent, rule-based severity scoring that prioritizes the most critical issues first.
- Developer-friendly interface that makes smart contract security accessible to non-experts.
- Combination of deterministic static analysis and generative AI, reducing noise while improving usability.

## What "done" looks like for the hackathon?

A successful hackathon MVP should allow a user to:

- Upload or paste a Solidity smart contract.
- Automatically scan the contract using Slither.
- Display detected vulnerabilities with severity levels.
- Generate AI-powered explanations for each finding.
- Suggest secure code fixes for the most critical vulnerabilities.
- Show side-by-side code diffs between the original and suggested fix.
- Present all results in a clean, responsive web dashboard.
