from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import secrets
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
# Iniciar tabla
db = SQLAlchemy(app)

# Crear modelos

class users(db.Model):
	ci = db.Column(db.String(64), primary_key = True)
	phone_number = db.Column(db.Integer(), unique = True, index = True)
	points = db.Column(db.Integer(), default = 0)
	date_created = db.Column(db.DateTime, default = datetime.utcnow)

	def __repr__(self):
		return '<Cédula %r>' % self.ci

@app.route('/mybot', methods = ['POST', 'GET'])
def mybot():
	incoming_msg = request.values.get('Body', '').lower()
	resp = MessagingResponse()
	msg = resp.message()
	responded = False
	num_media = request.values.get("MediaUrl0")

	if 'nuevo' == incoming_msg.split(" ")[0]:

		new_ci = incoming_msg.split(" ")[1]
		new_phone_number = incoming_msg.split(" ")[2]
		new_user= users(ci = new_ci, phone_number = new_phone_number)

		try:
			db.session.add(new_user)
			db.session.commit()
			msg.body(f'👍🏽 Se creó la cuenta con los siguientes datos:\nCédula: *{new_ci}*, Celular: *{new_phone_number}*')
			responded = True
		except:
			msg.body(f'❌ Hubo un error al ingresar al nuevo usuario, prueba nuevamente o contácta a plasticanje. ❌')
			responded = True	

	if 'cargar' == incoming_msg.split(" ")[0]:

		ci_to_add = incoming_msg.split(" ")[1]
		points_to_add = int(incoming_msg.split(" ")[2])
		u = users.query.get(ci_to_add)

		old_points = int(u.points)
		new_points = old_points + points_to_add
		u.points = new_points

		try:
			db.session.commit()
			msg.body(f'👌🏾 Se agregaron *{points_to_add} puntos* a la cuenta de *{ci_to_add}*')
			responded = True
		except:
			msg.body(f'❌ Hubo un error al cargar los puntos ❌')
			responded = True

	if 'canjear' == incoming_msg.split(" ")[0]:

		ci_to_discount = incoming_msg.split(" ")[1]
		u = users.query.get(ci_to_discount)
		
		points_to_discount = int(incoming_msg.split(" ")[2])
		old_points = int(u.points)

		if points_to_discount <= old_points:
			new_points = old_points - points_to_discount
			u.points = new_points
			try:
				db.session.commit()
				msg.body(f'👍🏻 Se utilizaron {points_to_discount} puntos en la cuenta de {ci_to_discount}, su nuevo estado es de {new_points}')
				responded = True
			except:
				msg.body(f'❌ Hubo un error al hacer el descuento ❌')
				responded = True

		else:
			msg.body(f'⛔ Sin saldo, usted tiene {old_points} y quiere gastar {points_to_discount} ⛔')
			responded = True

	if 'puntos' == incoming_msg.split(" ")[0]:
		ci_to_ask = incoming_msg.split(" ")[1]
		u = users.query.get(ci_to_ask)
		
		try:
			msg.body(f'👏🏾 Usted tiene {u.points} puntos. 👏🏾')
			responded = True
		except:
			msg.body(f'⛔ No se pudo consultar sus puntos. ⛔')
			responded = True

	# AL FINAL
	if not responded:
		msg.body(' 👋🏽 Bienvenida/o *Plasticanje.* 👋🏽\n \n \n💁🏽‍♀️ Para registrar un _nuevo usuario_ ingrese “*Nuevo*” seguido de la *CI* y del *número de celular* .\nEj: “*Nuevo 12345678 091234567*”\n \n♻️ Para _cargar puntos_ ingrese “*Cargar*” seguido de la *CI* y el *peso del plástico* en gramos . \nEj: “*Cargar 12345678 1000*”\n \n💸 Para _canjear puntos_ ingrese “*Canjear*” seguido de la *CI* y los *puntos a canjear* . \nEj: “*Canjear 12345678 100*”\n \n🤨 Para _consultar sus puntos_ ingrese "*Puntos*" seguido de la CI \nEj: "*Puntos 12345678*"')

	return str(resp)

if __name__ =="__main__":
	app.run()