<h1 align="center">
  <br>
  <img src="https://cash.place/images/full_logo.svg" alt="cash.place logo" width="256">
  <br>
</h1>

<h4 align="center">🦾 Backend of the cash.place platform, based on python3 and asyncio.</h4>

<p align="center">
    <a href="https://lgtm.com/projects/g/cashplace/server/context:python">
        <img alt="Language grade: Python" src="https://img.shields.io/lgtm/grade/python/g/cashplace/server.svg?logo=lgtm"/>
    </a>
</p>

## What is cash.place for?

cash.place is a platform for secure bitcoin transactions: if you are a customer you are sure that the seller will give you what you paid for and if you are a seller you are sure that you will receive your payment. Unlike traditional middlemen, cash.place is automatic and therefore very fast: if there is no dispute requiring human intervention, a transaction will only take a few minutes. No matter what happens, you will only pay a one percent fee for this service.

## Server features

### Requests
> These actions will be performed when requested by a client
- create a ticket
- check if a ticket exists
- set a temp password for both btc spender and receiver
- confirm receipt of items (using btc spender password) # this will send the BTC to the receiver
- report an issue (from both sides) and connect participants with a moderator
- download the transaction logs (signed by the server)
- ask for deletion (both sides must ask for immediate deletion)

### Tasks
> These actions will be performed automatically
- delete tickets without funds after 24h of inactify
- create and store a btc address for every ticket
- confirm the receipt of funds and tell to the btc receiver to send the counterpart
- automatically open an issue if the buyer didn't confirm the receipt after a configured delay (e.g. 72h)

## Donate
- ETH (ENS): ``thomas.ethers.xyz``
- ETH (legacy address): ``0x54c5a92c57A07f33500Ec9977797219D70D506C9``
- BTC: ``bc1qm9g2k3fznl2a9vghnpnwem87p03txl4y5lahyu``