from twilio.rest import TwilioRestClient
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi, logging, urllib, fcntl, os
from send_sms import SendSMS
from secrets import sid, token, number, to_num, to_name

# globals
ip = '77.73.6.229'
port = 8090
run_file = 'back'

# setup logger
log = logging.getLogger('')
log.setLevel(logging.INFO)

# create console handler and set level to info
log_format = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(log_format)
log.addHandler(ch)

# create file handler and set to debug
fh = logging.FileHandler(__file__ + '.log')
fh.setFormatter(log_format)
log.addHandler(fh)

# http request handler
class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        call_status = form['CallStatus'].value
        # save the call status in the server instance
        self.server.call_status = call_status
        log.info("call status = %s" % call_status)

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    # check lock
    file = "/tmp/" + __file__ + ".lock"
    fd = open(file, 'w')
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        log.debug("checked lock ok")
    except IOError:
        log.warning("another process is running with lock. quitting!")
        exit(1)

    # don't run if already back
    if os.path.exists(run_file):
        log.info("already back")
        exit(0)

    # get server ready to handle callback
    server = HTTPServer((ip,port), HttpHandler)

    # twilio client
    client = TwilioRestClient(sid, token)

    # make the call
    log.info("placing call from %s to %s" % (number, to_num))
    msg_params = {"Message[0]": "hello %s, welcome back to the uk" % to_name}
    url="http://twimlets.com/message?" + urllib.urlencode(msg_params),

    call = client.calls.create(to=to_num, 
        from_=number,
        url="http://twimlets.com/message?" + urllib.urlencode(msg_params),
        status_callback="http://%s:%s" % (ip, port),
        timeout=60)
    log.debug(call.sid)

    # handle one request
    log.info("waiting for callback")
    server.handle_request()

    # get status and send message if it got through
    if server.call_status == 'completed':
        # touch a file so we don't run again
        open(run_file, 'a').close()
        log.info("sending sms")
        sms = SendSMS()
        sms.send("%s is back!" % to_name)
