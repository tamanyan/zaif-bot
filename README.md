# Zaif Trade Bot

Automate BTC/JPY Trade Bot at Zaif

This projects works in GAE


## Install dependencies


```
pip install -t lib -r requirements.txt
```

## Setup settings.py


```
cp zaif/settings.py.example zaif/settings.py
```

You need to edit settings.py and set your KEY and SECRET which are provided from zaif.


```python
KEY='your key'
SECRET='your secret'
```


## How to start develop server

```
dev_appserver.py . app.yaml worker.yaml
```

## How to deploy

```
gcloud app deploy app.yaml worker.yaml
```
