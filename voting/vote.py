from flask import request, redirect, flash
from blockchain.blockchain import add_vote_to_chain
from blockchain.blockchain import Blockchain

vote_chain = Blockchain()

def cast_vote(voter_id, candidate):
    vote_data = {
        "voter_id": voter_id,
        "candidate": candidate
    }
    vote_chain.add_block(vote_data)