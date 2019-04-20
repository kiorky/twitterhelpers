# twitter utilities

Idea is to help myself to fight twitter bots harrassments (nationalists, porn bots spamming and making noise on all of my accounts)

Config file must contain access to a main account to access
twitter api and a list of access to accounts to operate on.


- Those simple scripts can help to automate some twitter tasks:
    - ``tblock``: block ids for all users and also synchronise all blocked list (one per line in list_ids.csv)
    - ``tpin``: get an oauth bearer token from cli
    - ``tget``: get user ids from usernames (one per line in users.csv)
    - ``tlist``: list last followers and notifiying accounts in
      an ordered way to spot possible spammers and block
      them via tblock

to get ``wat`` config knob: open your browser and get ``auth_token`` from loggued in session
