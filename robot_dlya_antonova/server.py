from getpass import getpass
from mysql.connector import connect, Error
from contextlib import closing

def order_to_db(id, buy_or_sell, currency, price, volume, status):
    with closing(connect(
            host="172.18.0.1",
            port='3307',
            user="root",
            password="password",
            db='world'
	)) as connection:
        with connection.cursor() as cursor:
            query = """INSERT INTO orders (id, buy_or_sell, currency, price, volume, order_status) VALUES (%s, %s, %s, %s, %s, %s)"""
            order = (id, buy_or_sell, currency, price, volume, status)
            cursor.execute(query, order)
        
            connection.commit()
