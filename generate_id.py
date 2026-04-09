import random

def generate_id():
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    generate_id = ''
    for _ in range(10):
        generate_id += random.choice(chars)
    return generate_id
