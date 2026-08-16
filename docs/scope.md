Scope
MVP (Must Build)
Analyze the code using Slither.
Detect vulnerabilities such as:
Reentrancy
Access control flaws
Unchecked external calls
Send the findings to an LLM.
The LLM explains:
What the vulnerability is.
Why it's dangerous.
How it could be exploited.
How to fix it.
The user receives a clear report and suggested code changes.

Instead of a developer seeing a technical message like:

"Potential reentrancy in withdraw() due to external call before state update."

They would see something like:

High Risk: Reentrancy

Your withdraw() function sends Ether before updating the user's balance. An attacker could repeatedly call this function before the balance changes, allowing them to withdraw more funds than they own.

Recommended fix: Update the balance before making the external call, or use a reentrancy guard.

Future Scope

ContractShield can evolve into a comprehensive AI-powered smart contract security platform. Future enhancements include support for multiple blockchain networks and smart contract languages, integration with GitHub and CI/CD pipelines for automated security checks, and a VS Code extension for real-time vulnerability detection during development.

A key planned addition is the RAG (retrieval-augmented generation) layer originally scoped for this project — retrieving similar historical exploits (such as The DAO hack) to give the LLM richer real-world context when assessing risk. This was deliberately left out of the current build to keep the core Slither + LLM pipeline reliable within the hackathon timeframe, and remains the clearest next step on the roadmap.

The platform can also incorporate additional security analysis tools and generate professional audit reports. In the long term, ContractShield can be offered as a SaaS solution for developers, startups, and enterprises, providing continuous security monitoring and automated auditing throughout the smart contract development lifecycle.
}
