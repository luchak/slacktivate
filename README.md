# Chat message saver

Pull messages out of SPC Slack based on reactions and put them into more useful places.

To get started:
* `virtualenv -p python3 venv`
* `source ./venv/bin/activate`
* `pip install -r requirements.txt`
* ```
    cat > slacktivate.cfg << EOF
    SLACK_TOKEN = "XXXXXX"
    EOF
```
* `./start.sh`

slacktivate.cfg
