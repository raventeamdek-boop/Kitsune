import random


def generate_id():
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    generated_id = ''
    for _ in range(10):
        generated_id += random.choice(chars)
    return generated_id
