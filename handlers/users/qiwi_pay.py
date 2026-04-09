import logging
import time
from pyqiwip2p import QiwiP2P
from data.config import *
from utils.db_api.baza import*
import time


p2p = QiwiP2P(auth_key=admins_setting_info()[0])

def create_payment_link(amount):
    new_bil = p2p.bill(amount=amount, lifetime=30)
    return [new_bil.pay_url, new_bil.bill_id]

def reject_payment_form(bill_id):
    try:
        p2p.reject(bill_id=bill_id)
        return True
    except Exception as err:
        logging.exception(err)


def check_payment(bill_id):
    status = p2p.check(bill_id=bill_id).status
    time.sleep(0.2)
    return status
        
