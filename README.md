# CASH.PLACE

## What is cash.place for?

cash.place is a platform for secure bitcoin transactions: if you are a customer you are sure that the seller will give you what you paid for and if you are a seller you are sure that you will receive your payment. Unlike traditional middlemen, cash.place is automatic and therefore very fast: if there is no dispute requiring human intervention, a transaction will only take a few minutes and you will only pay a one percent fee for this service.

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