# Scope
 
## MVP (Must Build)
 
1. Analyze the code using **Slither**.
2. Detect vulnerabilities such as:
   - Reentrancy
   - Access control flaws
   - Unchecked external calls
3. Send the findings to an LLM.
4. The LLM explains:
   - **What** the vulnerability is.
   - **Why** it's dangerous.
   - **How** it could be exploited.
   - **How** to fix it.
5. The user receives a clear report and suggested code changes.
Instead of a developer seeing a technical message like:
 
> "Potential reentrancy in `withdraw()` due to external call before state update."
 
They would see something like:
 
**High Risk: Reentrancy**
 
Your `withdraw()` function sends Ether before updating the user's balance. An attacker could repeatedly call this function before the balance changes, allowing them to withdraw more funds than they own.
 
**Recommended fix:** Update the balance before making the external call, or use a reentrancy guard.
 
## Future Scope
 
ContractShield can evolve into a comprehensive AI-powered smart contract security platform. Future enhancements include support for multiple blockchain networks and smart contract languages, integration with GitHub and CI/CD pipelines for automated security checks, and a VS Code extension for real-time vulnerability detection during development.
