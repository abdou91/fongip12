# -*- coding: utf-8 -*-

liste_nature_credit = ['CCT','CMT' , 'CLT','Découvert','Crédit-Bail','Crédit Campagne',"Crédit d'exploitation",'Aval de traite']
other_words = ['Rallonge','Restructuré','(restructuré)','sain','impayé','Renouvellement','Aval','premier','tirage 1','tirage 2','Deuxième','restructuré','Réechelonné','réechelonné','renouvellement','Renouvellement 2']
def get_partner_name_for_individuel_guarantee(data):
	for nature_credit in liste_nature_credit:
		if data.__contains__(nature_credit):
			data.replace(nature_credit,"")
	for word in other_words:
		if data.__contains__(word):
			data.replace(word,"")
	return data

def get_partner_name_for_portefeuille_guarantee(data):
	vals = {'partner':'','beneficiary':''}
	if data.__contains__('Portefeuille') and data.__contains__('/'):
		data = data.split('/')[1]
		if data.__contains__('-'):
			data = data.split('-')[0]
			return data
		return data


def get_beneficiary(data):

	if 'portefeuille' in data and '/' in data:
		if 
		da = data.split('/')[1]
		if '-' in da:
			return da.split('-')[1]
		return 
