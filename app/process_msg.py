from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
from redis import StrictRedis
import time
import details

account_sid = details.twilio_account_sid
auth_token  = details.twilio_auth_token
client = TwilioRestClient(account_sid, auth_token)
twilio_number = details.twilio_num


r = StrictRedis(host=details.redis_addr, port=details.redis_port)


def start_convo(num, body):
    """
    Starts a convo by selecting random partner, adding
    relevant index data, and queuing a msg.
    """
    r.srem('available_nums', num)
    dest = r.srandmember('available_nums')
    state = r.smembers(num + ":state").pop()
    body = "(1/10 - " + state + ") " + body
    r.incr('total_count')

    send_msg(dest, body)

    pipe = r.pipeline()
    pipe.srem('available_nums', dest)
    pipe.sadd('in_conversation', num)
    pipe.sadd('in_conversation', dest)
    pipe.sadd(num, dest)
    pipe.sadd(dest, num)
    pipe.hset(num + ":" + dest, 'count', '1')
    pipe.hset(dest + ":" + num, 'count', '1')
    pipe.execute()


def add_msg(dest, body):
    r.rpush('message_queue', dest + ":" + body)


def process_queue():
    """Pops msgs from the msg queue and dispatches them."""
    raw = r.lpop('message_queue')
    if raw:
        mark = raw.find(':')
        dest = raw[:mark]
        body = raw[mark + 1:]
        send_msg(dest, body)


def send_msg(dest, body):
    # Trim msg body to 160 chars to prevent malicious attempts to send long
    # msgs to incur excessive msg fees. 
    body = body[:160]
    try:
        client.sms.messages.create(body=body, to=dest, from_=twilio_number)
    except TwilioRestException as e:
        print repr(e)


if __name__ == '__main__':
    while True:
        process_queue()
        time.sleep(0.5)