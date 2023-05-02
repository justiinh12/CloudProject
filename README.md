# CloudProject
Cloud Computing Group Repo

## Installation

### flask

```bash
git clone git@github.com:justiinh12/CloudProject.git
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```

You need to have two env variables in your environment, SUPABASE_URL and SUPABASE_KEY to run python3 app.py. You can obtain a relevant supabase key to do so. The table schema for prices is an int8 id, varchar loc, timestamptz created_at, and float4 daily_price.

### lambda
This stuff goes into the gce console.

### station data

this stuff populates static station data into a database to get around network requests, faulty requests, rate limiting, throttling, and captcha requests.


