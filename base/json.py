# -*- coding: utf-8 -*-

# Importations
# Python3
import datetime
import json

# Règles
encode_regles = {
	# Objets Datetime
	datetime.date: ('datetime.date', 'isoformat'),
	datetime.time: ('datetime.time', 'isoformat'),
	datetime.datetime: ('datetime.datetime', 'isoformat'),
}

decode_regles = {
	# Objets Datetime
	'datetime.date': lambda obj: datetime.date(*[int(x) for x in obj.split('-')]),
	'datetime.time': lambda obj: datetime.time(*[int(y) for x in obj.split(':') for y in x.split('.')]),
	'datetime.datetime': lambda obj: datetime.datetime(*[int(a) for x in obj.split('-') for y in x.split('T') for z in y.split(':') for a in z.split('.')]),
}

# Encoder
class AllEncoder(json.JSONEncoder):
	def default(self, obj):
		for classe, regle in encode_regles.items():
			if isinstance(obj, classe):
				return '{}#{}'.format(regle[0], getattr(obj, regle[1])())
		
		return super(AllEncoder, self).default(obj)

# Decoder
class AllDecoder(json.JSONDecoder):
	def scan(self, obj):
		n_obj = {}
		
		for cle, val in obj.items():
			if isinstance(cle, str):
				try:
					classe, valv = cle.split('#')
					cle = decode_regles[classe](valv)
				except:
					pass
			
			if isinstance(val, str):
				try:
					classe, valv = val.split('#')
					val = decode_regles[classe](valv)
				except:
					pass
			
			n_obj[cle] = val
		
		return n_obj
