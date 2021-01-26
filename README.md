# Barscreen Web

Barscreen was a small business idea I worked on with a friend which ultiamtely didn't work out.

You can still use this to see an example of web design/python backend.

# Running Locally

To run this project locally you need to use python 2.7, below are the steps to run the server locally:

```
$ git clone git@github.com:cameron-williams/barscreen-web.git
$ cd ./barscreen-web
$ virtualenv -p python2.7 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ ./scripts/debug_server

=> Running on http://127.0.0.1:5000/
```

If you run into an error with open-cv, you are probably missing libsm6, libxext6, or libxrender-dev:

```
$ apt install -y libsm6 libxext6 libxrender-dev
```