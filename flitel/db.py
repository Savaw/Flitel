import psycopg2
from configparser import ConfigParser
from datetime import date

def config(filename="database.ini", section="postgresql"):
	parser = ConfigParser()
	parser.read(filename)

	db_params = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db_params[param[0]] = param[1]
	else:
		raise Exception("section {} not found".format(section))
	return db_params

def add_customer(customer):
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			insert_user = f"""insert into user_table (type_, username, password) 
			values('customer', '{customer['username']}', '{customer['password']}')
			returning id; """

			cursor.execute(insert_user)
			id_of_new_row = cursor.fetchone()[0]

			insert_customer = f"""insert into customer (id, national_id, name, email, phone, address) 
			values({id_of_new_row}, '{customer['national_id']}', '{customer['name']}', '{customer['email']}',
			 '{customer['phone']}', '{customer['address']}'); """
			
			cursor.execute(insert_customer)

		connection.commit()
	except Exception as e:
		return e

	return None

def get_user(username):
	user = None
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""select * from user_table where username='{username}'"""
			
			cursor.execute(query)
			result = cursor.fetchall()
			if result:
				user = {
				'username': username,
				'id': result[0][0],
				'type': result[0][1],
				'password' : result[0][3]
				}
	except Exception as e:
		return e

	return user


def get_hotels(country="", city="", name=""):
	hotels = []
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""select name, id, city_name, country_name, stars_count from hotels_info
			 where country_name ILIKE '%{country}%'
			 and city_name ILIKE '%{city}%'
			 and name ILIKE '%{name}%';"""
			
			cursor.execute(query)
			results = cursor.fetchall()
			for r in results:
				hotel = {
					'name': r[0].title(),
					'id': r[1],
					'city_name': r[2],
					'country_name': r[3],
					'stars_count': r[4]
				}
				hotels.append(hotel)
	except Exception as e:
		return e

	return hotels


def get_hotel(hotel_id):
	hotel = None
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:

			query = f"""select name, description, phone, website, address, facilities, stars_count, country_name, city_name, id, customer_rating
			from hotels_info natural join hotel where id = {hotel_id};"""
			
			cursor.execute(query)
			r = cursor.fetchone()
			if r:
				hotel = {
					'name': r[0].title(),
					'description': r[1],
					'phone': r[2],
					'website': r[3],
					'address': r[4],
					'facilities': r[5],
					'stars_count': r[6],
					'country_name': r[7],
					'city_name': r[8],
					'id': r[9],
					'customer_rating': r[10]
				}
				if hotel['customer_rating']:
					hotel['customer_rating'] = round(hotel['customer_rating'], 2)

	except Exception as e:
		return e

	return hotel

def get_rooms(hotel_id):
	rooms = []
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""select number, type_, capacity, price from hotels_rooms
			where id = {hotel_id};"""
			
			cursor.execute(query)
			results = cursor.fetchall()
			for r in results:
				room = {
					'number': r[0],
					'type': r[1],
					'capacity': r[2],
					'price': r[3]
				}
				rooms.append(room)

	except Exception as e:
		return e	
	
	return rooms

def get_flights(origin_country='', destination_city='', origin_city='', destination_country='', departure_date=None):
	flights = []
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""select airline_name, airline_id, number, price, departure_date, departure_time, type_,
			origin_city_name, origin_country_name, destination_city_name, destination_country_name, remained_seats from flight_info
			where origin_city_name ILIKE '%{origin_city}%'
			and origin_country_name ILIKE '%{origin_country}%'
			and destination_city_name ILIKE '%{destination_city}%'
			and destination_country_name ILIKE '%{destination_country}%'
			"""
			if departure_date:
				query = f"{query} and departure_date = '{departure_date}';"
 			
			cursor.execute(query)
			results = cursor.fetchall()
			for r in results:
				flight = {
					'airline_name': r[0].title(),
					'airline_id': r[1],
					'number': r[2],
					'price': r[3],
					'departure_date': r[4],
					'departure_time': r[5],
					'type_': r[6].title(),
					'origin_city_name': r[7],
					'origin_country_name': r[8],
					'destination_city_name': r[9],
					'destination_country_name': r[10],
					'remained_seats': r[11]
				}
				flights.append(flight)
	except Exception as e:
		return e

	return flights


def add_room_booking(hotel_id, room_number, user_id, from_date, to_date):
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""insert into booking (submission_date, status_, customer_id) values
			('{date.today()}', 'waiting for payment', {user_id}) returning id; """

			cursor.execute(query)
			id_of_new_row = cursor.fetchone()[0]

			query = f"""insert into room_booking (id, hotel_id, room_number, from_date, to_date) values
			('{id_of_new_row}', '{hotel_id}', '{room_number}', '{from_date}', '{to_date}'); """

			cursor.execute(query)
		
		connection.commit()
	except Exception as e:
		return e

	return None

def add_flight_booking(airline_id, flight_number, user_id):
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""insert into booking (submission_date, status_, customer_id) values
			('{date.today()}', 'waiting for payment', {user_id}) returning id; """

			cursor.execute(query)
			id_of_new_row = cursor.fetchone()[0]

			query = f"""insert into flight_booking (id, airline_id, flight_number) values
			('{id_of_new_row}', '{airline_id}', '{flight_number}'); """

			cursor.execute(query)
		
		connection.commit()
	except Exception as e:	
		return e

	return None

def get_bookings(user_id, booking_id=None):
	results = []
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			if not booking_id:
				query = f"""select * from bookings_customer_view where customer_id = {user_id};"""
			else:
				query = f"""select * from bookings_customer_view where customer_id = {user_id} and id={booking_id};"""

			cursor.execute(query)
			res = cursor.fetchall()

			for r in res:
				result = {
					'id': r[0],
					'submission_date': r[1],
					'status': r[2],
					'transaction_date': r[3],
					'transaction_amount': r[4],
					'price': r[5],
					'type': r[6],
					'customer_id': r[7],
					'hotel_or_airline_id': r[8],
					'from_date': r[9],
					'to_date': r[10]
				}
				results.append(result)
	except Exception as e:
		return e

	return results


def get_discount(discount_code):
	discount = None
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""select * from discount 
			where id = '{discount_code}' and 
			id not in (select discount_id from book_discount where discount_id=id);"""
			
			cursor.execute(query)
			res = cursor.fetchall()

			if res:
				discount = {
					'code': discount_code,
					'percent': res[0][1]
				}
	except Exception as e:
		return e

	return discount


def complete_booking(booking_id, amount, discount_code):	
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:

			if discount_code:
				query = f"""insert into book_discount values ({booking_id}, '{discount_code}');"""
				cursor.execute(query)

			query = f""" update booking SET status_ = 'completed', transaction_date = '{date.today()}', transaction_amount={amount}
			where id={booking_id};"""

			cursor.execute(query)

		connection.commit()
	except Exception as e:
		return e

	return None

def cancel(booking_id):	
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:

			query = f""" update booking SET status_ = 'cancelled'
			where id={booking_id};"""

			cursor.execute(query)

		connection.commit()
	except Exception as e:
		return e

	return None



def update_hotel_rating(booking_id, rating):	
	try:
		params = config()
		connection = psycopg2.connect(**params)
		with connection.cursor() as cursor:
			query = f"""update room_booking SET customer_rating = {rating} where id={booking_id};"""

			cursor.execute(query)

		connection.commit()
	except Exception as e:
		return e

	return None
