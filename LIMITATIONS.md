# ChainNetra Limitations

While ChainNetra represents a state-of-the-art approach to blockchain tracing, it is important to recognize the following technical limitations:

1. **Privacy Coins (Zero-Knowledge Proofs):**
   ChainNetra relies on the public ledger's transparency (UTXOs and Account-based models). It cannot currently trace transactions that utilize zero-knowledge proofs (e.g., Zcash shielded transactions) or ring signatures (e.g., Monero).

2. **Off-Chain Transactions:**
   Transactions conducted entirely within centralized exchanges (off-chain) or over Layer-2 networks (e.g., Lightning Network) that are not settled on the main chain will appear as a single hop to an exchange wallet, hiding the internal flow of funds.

3. **API Rate Limiting:**
   Free tiers of Etherscan, TronGrid, and Esplora heavily throttle rapid graph traversals. For a production deployment, commercial API keys or running your own archive nodes are strictly required.

4. **False Positives in Heuristics:**
   Heuristics like Deposit Address Reuse (DAR) can occasionally misidentify a payment processor or a smart contract aggregation wallet as an exchange deposit wallet. We use ML to calculate a confidence score, but human verification remains necessary.
