from redis import StrictRedis
from app import app
import process_msg
import details

r = StrictRedis(host=details.redis_addr, port=details.redis_port)
logger = app.logger


def is_num_registered(num):
    return r.sismember('registered_nums', num)


def register_num(data):
    num = data['from']
    city = data['from_city']
    zipcode = data['from_zip']
    state = data['from_state']
    logger.info('Registering ' + num)

    pipe = r.pipeline()
    pipe.sadd('registered_nums', num)
    pipe.sadd('available_nums', num)
    pipe.sadd('cities:' + city, num)
    pipe.sadd('zipcodes:' + zipcode, num)
    pipe.sadd(num + ':state', state)
    pipe.sadd(num + ':zipcode', zipcode)
    pipe.sadd(num + ':city', city)
    pipe.sadd('cities', city)
    pipe.sadd('zipcodes', zipcode)
    pipe.sadd('states', state)
    pipe.execute()


def register_num(data):
    sender = data['from']
    body = data['body']
    register = check_for_register(body)
    if not register:
        return "Welcome to LostNum, an invite-only national random chat service by SMS. Send 'YES' to continue and login. Send 'NO' to stop and do nothing."
    elif register == 'True':
        register_num(data)
        return "Sweet! You've enabled LostNum! Enter 'START' followed by your message to start a chat. Enter 'DONE' any time to exit a chat. Enter 'OFFLINE' to not receive any chats."
    elif register == 'False':
        return "Okay, you won't get any more messages from LostNum."
        

def check_for_register(body):
    body = body.lower()
    if 'yes' in body:
        return 'True'
    elif 'no' in body:
        return 'False'
    else:
        return None


def check_for(data, command):
    if data['body']:
        body = data['body']
        return command in body


def start_convo(data):
    body = data['body']
    num = data['from']
    body = body.replace('START', '')
    logger.info('Starting convo from {0}'.format(num))
    process_msg.start_convo(num, body)


def check_in_convo(num):
    return r.sismember('in_conversation', num)


def forward_convo(data):
    sender = data['from']
    convo_count = get_convo_count(sender)
    if convo_count >= 10:
        end_convo(sender)
    else:
        incr_convo_count(sender)
        dest = get_partner(sender)
        logger.info('Forwarding message from {0} to {1}'.format(sender, dest))
        state = r.smembers(sender + ":state").pop()
        body = '(' + str(convo_count) + "/10 - " + state + ") " + data['body']
        process_msg.add_msg(dest, body)
        r.incr('total_count')


def able_to_start():
    size = r.scard('available_nums')
    return size >= 2


def get_convo_count(num):
    partner = get_partner(num)
    return int(r.hget(partner + ":" + num, 'count'))


def get_partner(num):
    return r.smembers(num).pop()


def incr_convo_count(num):
    original = get_convo_count(num)
    incr = str(original + 1)
    partner = get_partner(num)
    r.hset(partner + ":" + num, 'count', incr)
    r.hset(num + ":" + partner, 'count', incr)


def end_convo(num):
    partner = get_partner(num)
    logger.info('Ending convo between {0} and {1}'.format(num, partner))
    pipe = r.pipeline()
    pipe.srem('in_conversation', num)
    pipe.srem('in_conversation', partner)
    pipe.srem(num, partner)
    pipe.srem(partner, num)
    pipe.hdel(num + ":" + partner, 'count')
    pipe.hdel(partner + ":" + num, 'count')
    pipe.sadd('available_nums', num)
    pipe.sadd('available_nums', partner)
    pipe.execute()

    process_msg.add_msg(num, 'LostNum: End of conversation.')
    process_msg.add_msg(partner, 'LostNum: End of conversation.')


def handle_offline(data):
    num = data['from']
    logger.info('Setting {0} to offline mode.'.format(num))
    pipe = r.pipeline()
    pipe.srem('available_nums', num)
    pipe.sadd('offline_nums', num)
    pipe.execute()


def check_offline(data):
    num = data['from']
    return r.sismember('offline_nums', num)


def handle_online(data):
    num = data['from']
    logger.info('Setting {0} to online mode.'.format(num))
    pipe = r.pipeline()
    pipe.sadd('available_nums', num)
    pipe.srem('offline_nums', num)
    pipe.execute()
