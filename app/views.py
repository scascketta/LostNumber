from app import app
from flask import Flask, request, url_for, redirect, session, Response
import twilio.twiml
import handle_msg

SECRET_KEY = 'thespicemustflow'

CONFUSED_MSG = "LostNum is an invite-only national random chat service by SMS. Enter 'START' followed by your message to start a chat. Enter 'DONE' any time to exit a chat. Enter 'OFFLINE' to not receive any chats."
NEW_OFFLINE_MSG = "You are now offline and won't receive any chats. To change this and go online, send 'ONLINE'."
NEW_ONLINE_MSG = "You are now online and can receive chats. Send 'START' followed by a message to start a chat."
OFFLINE_MSG = "You are offline and won't receive any chats. To change this and go online, send 'ONLINE'."
NOT_ENOUGH_USERS_MSG = "Sorry, there aren't enough available users to start a conversation right now. Try again later."

logger = app.logger


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.values.get('From') == 'None' or request.method == 'GET':
        return empty_twiml_resp()

    data = unpack_data(request)
    sender = data['from']
    logger.info('====START OF REQUEST====')
    logger.debug('FROM: ' + sender)
    logger.debug('BODY: ' + data['body'])
    registered = handle_msg.is_num_registered(sender)
    logger.debug('REGISTERED: ' + str(registered))

    if not registered:
        logger.info(sender + ' is not registered.')
        msg = handle_msg.register_num(data)
        return twiml_response(msg)
    else:
        return handle_registered(data, sender)


def handle_registered(data, sender):
    confused = handle_msg.check_for(data, 'CONFUSED')
    go_offline = handle_msg.check_for(data, 'OFFLINE')
    logger.debug('CONFUSED: ' + str(confused))
    logger.debug('GO_OFFLINE: ' + str(go_offline))

    if confused:
        logger.info(sender + ' is confused.')
        return twiml_response(CONFUSED_MSG)

    elif go_offline:
        logger.info(sender + ' wants to go offline.')
        handle_msg.handle_offline(data)
        return twiml_response(NEW_OFFLINE_MSG)

    else:
        offline = handle_msg.check_offline(data)
        logger.debug('OFFLINE: ' + str(offline))

        if offline:
            return handle_offline_user(data, sender)

        in_convo = handle_msg.check_in_convo(sender)
        logger.debug('IN CONVO: ' + str(in_convo))

        if in_convo:
            handle_user_in_convo(data, sender)
        else:
            start = handle_msg.check_for(data, 'START')
            logger.debug('START CONVO: ' + str(start))

            if start:
                if not handle_msg.able_to_start():
                    logger.info('Cannot start a convo, not enough users.')
                    return twiml_response(NOT_ENOUGH_USERS_MSG)
                handle_user_start_convo(data, sender)

            else:
                return twiml_response(CONFUSED_MSG)
        return empty_twiml_resp()


def handle_offline_user(data, sender):
    go_online = handle_msg.check_for(data, 'ONLINE')
    logger.debug('GO ONLINE: ' + str(go_online))
    if go_online:
        logger.info(sender + ' wants to go online.')
        handle_msg.handle_online(data)
        return twiml_response(NEW_ONLINE_MSG)
    else:
        return twiml_response(OFFLINE_MSG)


def handle_user_in_convo(data, sender):
    if handle_msg.check_for(data, 'DONE'):
        logger.info(sender + ' wants to end the convo.')
        handle_msg.end_convo(sender)
        logger.debug('====END OF REQUEST====')
    else:
        logger.info('Forwarding message from ' + sender)
        handle_msg.forward_convo(data)
        logger.debug('====END OF REQUEST====')


def handle_user_start_convo(data, sender):
    logger.info(sender + ' wants to start a convo.')
    handle_msg.start_convo(data)
    logger.debug('====END OF REQUEST====')


def twiml_response(msg):
    resp = twilio.twiml.Response()
    resp.message(msg)
    logger.debug('====END OF REQUEST====')
    return str(resp)


def empty_twiml_resp():
    resp = twilio.twiml.Response()
    return str(resp)


def unpack_data(request):
    data = {}
    data['from'] = request.values.get('From')
    data['to'] = request.values.get('To')
    data['body'] = request.values.get('Body')
    data['from_city'] = request.values.get('FromCity')
    data['to_city'] = request.values.get('ToCity')
    data['from_zip'] = request.values.get('FromZip')
    data['to_zip'] = request.values.get('ToZip')
    data['from_state'] = request.values.get('FromState')
    data['to_state'] = request.values.get('ToState')
    return data
