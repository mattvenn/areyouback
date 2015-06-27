# Are You Back?

My first test of Twilio. This little app runs on my server once a day, and if
a friend is back in the UK then the call connects and he gets a creepy message
and I get a text.

Text is done with a different service because Twilio doesn't do SMS in the UK
without buying a Twilio number.

# Useful bits

## Docs

[Python Twilio docs](https://twilio-python.readthedocs.org/en/latest/)

## Testing HttpHandler

To test the httphandler I setup an endpoint on
[http://requestb.in/](http://requestb.in/). This got me the raw data from
Twilio's callback service.

I can then test my handler before running the app on my server with this:

curl -X POST http://localhost:8080 --data @data.txt

## Twimlet

If the call is answered, I play a message read by the Twilio computer using this
[twimlet](https://www.twilio.com/labs/twimlets/message)
