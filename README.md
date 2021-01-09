# FGI validator server

This is a tool designed for FurryGamesIndex contributors to verify that the data files they want to create/modify are free of syntax errors and to check the display effects.

## Deploy

### Run on local/generic server

Change 5000 to the port number you want to bind.

```
git clone https://github.com/FurryGamesIndex/validator-server --recursive
cd validator-server
pip3 install -r requirements.txt
PORT=5000 ./server.py
```

### Deploy to heroku

Just push to heroku's git repo.

Deploy button and deploy in web is not supported due to git submodules.
