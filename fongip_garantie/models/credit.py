# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import xlrd
import base64

MISE_EN_PLACE = [
					('oui',"Oui"),
					('en_attente',"En attente"),
					('annulee',"Annulée"),
				]

TYPE_REMBOURSEMENT = [
						('1',"Mensuel"),
						('3',"Trimestriel"),
						('6',"Semestriel"),
						('12',"Annuel")
					 ]

RESTRUCTURATION = [
					('restructure',"Restructuré"),
					('non_restructure',"Non restructuré"),
					("archive","Archivé") ,
				  ]
CREDIT_STATUS = [
				 ('annule','Annulé'),
				 ('declasse','Déclassé'),
				 ('impaye','Impayé'),
				 ('indemnise','Indemnisé'),
				 ('non_mis_en_place','Non mis en place'),
				 ('sain','Sain'),
				 ('solde','Soldé')
				]


"""class FongipTypeCredit(models.Model):
	_name = 'fongip.type_credit'
	_description = 'type de crédit'

	name = fields.Char(string=u'Nom')"""

class FongipNatureCredit(models.Model):
	_name = 'fongip.credit.nature'
	_description = 'Nature du crédit'

	name = fields.Char(string = "Libellé")

"""class FongipEtatCredit(models.Model):
	_name = 'fongip.credit.status'
	_description = 'etat du crédit'

	name = fields.Char(string=u'Libellé')"""

class FongipCreditStatus(models.Model):
	_name = 'fongip.credit.status'
	_description = 'Etat credit'

	name = fields.Char(string = "Libellé")


class FongipCreditGarantie(models.Model):
	_name = 'fongip.credit'
	_description = 'Crédit'
	_rec_name = 'description'

	project_id = fields.Many2one(
		'fongip.project',
		string = 'Projet',
		ondelete = 'cascade'
		)
	bank_id = fields.Many2one(
		'res.bank',
		related='project_id.bank_id'
		,string='Banque',
		ondelete = 'cascade'
		)
	partner_id = fields.Many2one(
		'res.partner',
		related='project_id.partner_id',
		string = "Entreprise"
		)
	legal_status_id = fields.Many2one(
		'legal.status',
		realted='partner_id.legal_status_id',
		string = "Forme juridique"
		)
	activity_sector_id = fields.Many2one(
		'activity.sector',
		related='partner_id.activity_sector_id',
		string = "Secteur d'activité"
		)
	filiere_id = fields.Many2one(
		'financing.filiere',
		related='partner_id.filiere_id',
		string = "Filière"
		)
	#type_credit_id = fields.Many2one('fongip.type_credit' , string=u'Type de crédit')
	nature_credit_id = fields.Many2one(
		'fongip.credit.nature',
		string = "Nature crédit"
		)
	sous_fond_id = fields.Many2one(
		'fongip.sous_fonds',
		string=u'Sous fonds'
		)
	currency_id = fields.Many2one(
		'res.currency',
		'Currency', 
        default=lambda self: self.env.company.currency_id.id
        )
	amount = fields.Monetary(string = 'Montant du crédit')
	credit_status_id = fields.Many2one(
		'fongip.credit.status',
		string = "Etat du crédit"
		)
	credit_status_name = fields.Char(
		related='credit_status_id.name',
		string = "Etat du crédit",
		store=True
		)
	state = fields.Selection(
		CREDIT_STATUS,
		string = "Etat"
		)
	guarantee_type = fields.Selection(
		GUARANTEE_TYPE,
		string = 'Type de garantie',
		default = "individuelle"
		)
	duration = fields.Integer(string = "Durée(en mois)")
	date_cgb = fields.Date(string = "Date CGB")
	diferred = fields.Boolean(string = "Différé")
	diferred_duration = fields.Integer(string="Durée du différé (en mois)") 
	amortissable = fields.Boolean(string="Crédit amortissable")
	visible = fields.Boolean(string = 'Invisible')
	quota = fields.Integer(string = 'Quotite de garantie (%)' )
	first_due_date = fields.Date(string = "Date première échéance")
	last_due_date = fields.Date(string = "Date dernière échéance")
	interest_rate = fields.Float(string = "Taux d'intérêt(%)")
	guarantee_commission_rate = fields.Float("Taux commission")
	guarantee_commission_amount = fields.Monetary(string = 'Montant commission')
	payment_amount = fields.Monetary(string = "Montant de l'échéance")
	#montant_echeance = fields.Monetary(string=u"Montant de l'échéance")
	type_remboursement = fields.Selection(
		TYPE_REMBOURSEMENT ,
		string = 'Type de remboursement'
		)
	guarantee_amount = fields.Monetary(
		string = 'Montant de la garantie',
		compute = '_compute_guarantee_amount',
		store=True
		)
	mise_en_place = fields.Selection(
		MISE_EN_PLACE,
		string = "Mise en place"
		)
	date_mise_en_place = fields.Date( string = "Date de mise en place")
	oustanding_credit = fields.Monetary(string="Encours du crédit")
	oustanding_guarantee = fields.Monetary(string=u'Encours de la garantie')
	description = fields.Text(string=u'Objet')
	nombre_echeances_impayes = fields.Integer(string=u"Nombre d'échéances impayés" , compute='compute_impayes',store=True)
	unpaid_amount = fields.Monetary(string=u"Montant total des impayés", compute='compute_impayes' , store=True)
	compensation_amount = fields.Monetary(string=u'Montant indemnisation')
	#montant_rembourse = fields.Float(string='Montant remboursé',digits=())
	observations = fields.Text(string="Observations")
	#code = fields.Float(string=u"Code")
	"""credit_impaye_ids = fields.One2many(
		'fongip.credit.impaye',
		'credit_garantie_id',
		string = 'les impayés'
		)"""
	#date_declassement = fields.Date(string="Déclassé le ")
	#date_annulation = fields.Date(string='Annulé le ')
	action = fields.Selection(
		RESTRUCTURATION ,
		string = 'Restructuration',
		default='non_restructure'
		)
	"""amortissement_line_ids = fields.One2many(
		'fongip.amortissement.line',
		'credit_garantie_id',
		string="commission_line d'amortissement"
		)"""
	region_id = fields.Many2one(
		'res.country.region' ,
		related='project_id.region_id',
		string = 'Région'
		)
	departement_id = fields.Many2one(
		'res.country.departement',
		related='project_id.departement_id',
		string = 'Département'
		)

	@api.depends('amount','quota')
	def _compute_guarantee_amount(self):
		for record in self:
			if record.amount and record.quota:
				record.guarantee_amount = (record.guarantee_amount * record.quota) /100.0


	def _compute_commission(self):
		commission_ids = self.env['fongip.commission'].search([('credit_garantie_id','=',self.id)])
		if commission_ids:
			commission_ids.unlink()
		for record in self:
			guarantee_commission_rate = record.guarantee_commission_rate
			quota = record.quota
			capitalEnDebutPeriode = record.amount
			interest_rate = record.interest_rate / 100.0
			duree = record.duration
			CapitalRembourse = 0	
			interet = 0
			capitalEnFinPeriode = 0
			nbreMoisEntreChaqueEcheance = 12
			nombre_echeance = 0
			montant_echeance = 0
			nbreCycle = 0
			try:
				nombre_echeance = duree / 12.0
				montant_echeance = round(capitalEnDebutPeriode * interest_rate / (1 -(1 + interest_rate)**(-nombre_echeance)),0)
				nbreCycle = int(nombre_echeance)
			except ZeroDivisionError:
				print("ok")

			commission_dict = {
							#'name' : "Facture G"+str(numero)+" : Durée = "+str(duree)+" mois",
							'credit_garantie_id':record.id,
							'partner_id':record.partner_id.id
							#'taux_interet':record.interest_rate,
							#'duree': record.duration,
							#'montant_pret':sum(lines.mapped('montant_pret'))
			}
			commission = self.env['fongip.commission'].create(commission_dict)
			commission_ht = 0
			commission_ttc = 0
			number = 0
			for num in range(1,nbreCycle+1):
				number = num
				interet = round(capitalEnDebutPeriode * interest_rate,0)
				CapitalRembourse = montant_echeance - interet
				capitalEnFinPeriode = capitalEnDebutPeriode - CapitalRembourse
				commission_ht = round((capitalEnDebutPeriode * guarantee_commission_rate * quota) / 10000,0)
				commission_ttc = round(commission_ht * (1 + 0.17),0)
				commission_line = {
							'periode': "Année "+str(num),
							'capital_debut_periode':capitalEnDebutPeriode,
							'capital_rembourse':CapitalRembourse,
							'interet':interet,
							'capital_fin_periode':capitalEnFinPeriode,
							'commission_ht':commission_ht,
							'commission_ttc':commission_ttc,
							'commission_id':commission.id
				}
				if capitalEnFinPeriode < 0:
					commission_line['capital_fin_periode'] = 0
				self.env['fongip.commission_line'].create(commission_line)
				capitalEnDebutPeriode  = capitalEnFinPeriode#capitalEnDebutPeriode - CapitalRembourse
			if duree % 12 != 0:#nombre_echeance > nbreCycle:
				interet = round(capitalEnDebutPeriode * interest_rate,0)
				CapitalRembourse = montant_echeance - interet
				CapitalEnFinPeriode = capitalEnDebutPeriode - CapitalRembourse
				commission_ht = round((capitalEnDebutPeriode * guarantee_commission_rate * quota) / 10000,0)
				commission_ttc = round(commission_ht * (1 + 0.17),0)
				commission_line = {
							'periode': "Année "+str(number + 1),
							'capital_debut_periode':capitalEnDebutPeriode,
							'capital_rembourse':CapitalRembourse,
							'interet':interet,
							'capital_fin_periode':0,
							'commission_ht':commission_ht,
							'commission_ttc':commission_ttc,
							'commission_id':commission.id
				}
				self.env['fongip.commission_line'].create(commission_line)
				capitalEnDebutPeriode  = capitalEnFinPeriode#capitalEnDebutPeriode - CapitalRembourse
				#commission_ht = round((capitalEnDebutPeriode * taux_commission * quotite) / 10000,0)
				#commission_ttc = round(commission_ht * (1 + 0.17),0)
	
	
	def declarer_impaye(self):
		return ""

	def return_action_to_open(self):
		#This opens the xml view specified in xml_id for the current credit garantie
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window']._for_xml_id('fongip_garantie.%s' % xml_id)
			res.update(
						context=dict(self.env.context,default_credit_garantie_id=self.id, group_by=False),
						domain=[('credit_garantie_id','=',self.id)]
					)
			return res
		return False

class FongipCreditImport(models.Model):
	_name = 'fongip.credit.import'
	_description = 'Import credit data'

	import_date = fields.Datetime(
		string = "Date d'import",
		default=lambda self: fields.Datetime.now()
		)
    filename = fields.Char('File Name')
    data = fields.Binary('Importer le fichier')
    credit_import_line_ids = fields.One2many(
    	'fongip.credit.import.line',
    	'credit_import_id',
    	string = "Lignes de crédit"
    	)
    imported_by = fields.Many2one(
    	'res.users',
    	string = "Importé par",
    	default = lambda self: self.env.user.id
    	)
    state = fields.Selection(
    	[('draft','Brouillon'),('confirmed','Confirmé'),('cancelled','Annulé')],
    	default='draft',
    	string = "Etat"
    	)
    individuel_guarantee = fields.Boolean(string = "Garantie individuelle")
    wallet_guarantee = fields.Boolean(string = "Garantie portefeuille")


    def cancel(self):
    	for record in self:
    		record.state = "cancelled"

    def confirm(self):
    	#creer les dossiers et lier les dossiers aux crédits
    	for record in self:
    		if record.credit_import_line_ids:#insert data in the real table
    			#dico = {}
    			credit = {}
    			project = {}
    			partner_dict = {}
    			activity_sector_dict = {}
    			filiere_dict = {}
    			departement_dict = {}
    			for line in record.credit_import_line_ids:
    				project['guarantee_type'] = line.guarantee_type
    				project['date_cgb'] = line.date_cgb
    				if line.bank_name:
    					bank = self.env['res.bank'].search([('name','=',line.bank_name)], limit = 1)
    					if bank:
    						project['bank_id'] = bank.id
    					else:
    						bank = self.env['res.bank'].create({'name':line.bank_name})
    						if bank:
    							project['bank_id'] = bank.id
    				credit['mise_en_place'] = line.mise_en_place
    				credit['date_mise_en_place'] = line.date_mise_en_place
    				credit['first_due_date'] = line.first_due_date
    				credit['last_due_date'] = line.last_due_date
    				if line.nature_credit_name:
    					nature_credit = self.env['fongip.credit.nature'].search([('name','=',line.nature_credit_name)], limit = 1)
    					if nature_credit:
    						credit['nature_credit_id'] = nature_credit.id
    					else:
    						nature_credit = self.env['fongip.credit.nature'].create({'name':line.nature_credit_name})
    						if nature_credit:
    							credit['nature_credit_id'] = nature_credit.id
    				if line.legal_status_name:
    					legal_status = self.env['legal.status'].search([('name','=',line.legal_status_name)], limit = 1)
    					if legal_status:
    						partner_dict['legal_status_id'] = legal_status.id
    					else:
    						legal_status = self.env['legal.status'].create({'name':line.legal_status_name})
    						if legal_status:
    							partner_dict['legal_status_id'] = legal_status.id

    				if line.sous_fonds_name:
    					sous_fonds = self.env['fongip.sous_fonds'].search([('name','=',line.sous_fonds_name)], limit = 1)
    					if sous_fonds:
    						project['sous_fonds_id'] = sous_fonds.id
    					else:
    						sous_fonds = self.env['fongip.sous_fonds'].create({'name':line.sous_fonds_name})
    						if sous_fonds:
    							project['sous_fonds_id'] = sous_fonds.id
    				project['product_type'] = line.product_type
    				if line.psp_name:
    					psp = self.env['financing.psp'].search([('name','=',line.psp_name)], limit = 1)
    					if psp:
    						activity_sector_dict['psp_id'] = psp.id
    					else:
    						psp = self.env['financing.psp'].create({'name':line.psp_name})
    						if psp:
    							activity_sector_dict['psp_id'] = psp.id
    				if line.activity_sector_name:
    					activity_sector_dict['name'] = line.activity_sector_name
    					activity_sector = self.env['activity.sector'].search([('name','=',line.activity_sector_name)], limit = 1)
    					if activity_sector:
    						partner_dict['activity_sector_id'] = activity_sector.id
    						filiere_dict['activity_sector_id'] = activity_sector.id
    					else:
    						activity_sector = self.env['activity.sector'].create(activity_sector_dict)
    						if activity_sector:
    							partner_dict['activity_sector_id'] = activity_sector.id 
    							filiere_dict['activity_sector_id'] = activity_sector.id
    				if line.filiere_name:
    					filiere_dict['name'] = line.filiere_name
    					filiere = self.env['financing.filiere'].search([('name','=',line.filiere_name)], limit = 1)
    					if filiere:
    						partner_dict['filiere_id'] = filiere.id
    					else:
    						filiere = self.env['financing.filiere'].create(filiere_dict)
    						partner_dict['filiere_id'] = filiere.id
    				if line.reseau_name:
    					reseau = self.env['fongip.reseau'].search([('name','=',line.reseau_name)], limit = 1)
    					if reseau:
    						project['reseau_id'] = reseau.id
    					else:
    						reseau = self.env['fongip.reseau'].create({'name':line.reseau_name})
    						if reseau:
    							project['reseau_id'] = reseau.id
    				if line.region_name:
    					region = self.env['res.country.region'].search([('name','=',line.region_name)], limit = 1)
    					if region:
    						project['region_id'] = region.id
    						departement_dict['region_id'] = region.id
    					else:
    						region = self.env['res.country.region'].create({'name':line.region_name})
    						if region:
    							project['region_id'] = region.id
    							departement_dict['region_id'] = region.id
    				if line.departement_name:
    					departement_dict['name'] = line.departement_name
    					departement = self.env['res.country.department'].search([('name','=',line.departement_name)], limit = 1)
    					if departement:
    						project['departement_id'] = department.id
    					else:
    						departement = self.env['res.country.department'].create(departement_dict)
    						if departement:
    							project['departement_id'] = department.id
    				project['funding_amount'] = line.funding_amount
    				credit['credit_amount'] = line.credit_amount
    				credit['guarantee_amount'] = line.guarantee_amount
    				credit['quota'] = line.quota,
    				credit['interest_rate'] = line.interest_rate
    				credit['duration'] = line.duration,
    				credit['diferred_duration'] = line.diferred_duration
    				credit['guarantee_commission_rate'] = line.guarantee_commission_rate
    				credit['guarantee_commission_amount'] = line.guarantee_commission_amount
    				project['number_jobs'] = line.number_jobs
    				credit['payment_amount'] = line.payment_amount
    				credit['oustanding_credit'] = line.oustanding_credit
    				credit['oustanding_guarantee'] = line.oustanding_guarantee
    				credit['state'] = line.state
    				credit['nombre_echeances_impayes'] = line.nombre_echeances_impayes
    				credit['unpaid_amount'] = line.unpaid_amount
    				credit['compensation_amount'] = line.compensation_amount
    				credit['observations'] = line.observations
    				#credit['code'] = line.code
    				if line.code == 0:
    					credit['action'] = 'non_restructure'
    					project['action'] = 'non_restructure'
    				if line.code == 1:
    					credit['action'] = 'archive'
    					project['action'] = 'archive'
    				if line.code == 2:
    					credit['action'] = 'restructure'
    					project['action'] = 'restructure'
    				if line.country:
    					country = self.env['res.country'].search([('name','=',line.country)], limit = 1)
    					if country:
    						project['country_id'] = country.id
    				#credit['code_benef'] = line.code_benef
    				if line.guarantee_type == 'individuelle':
    					project_name = get_partner_name_for_individuel_guarantee(line.project_name)
    					#project = self.env['project'].search([('name','=',project_name)], limit = 1)
    					partner = self.env['res.partner'].search([('name','=',project_name)], limit = 1)
    					if partner:
    						project['partner_id'] = partner.id
    						#project_record = self.
    					else:
    						partner_dict['name'] = line.project_name
    						partner = self.env['res.partner'].create(partner_dict)
    						if partner:
    							project['partner_id'] = partner.id
    					project_record = self.env['project'].search([('name','=',project_name)])
    					if project_record:
    						credit['project_id'] = project_record.id
    					else:
    						project_record = self.env['project'].create(project)
    						if project_record:
    							credit['project_id'] = project_record.id
    					self.env['fongip.credit'].create(credit)
    				else:
    					pass
    					


    @api.onchange('data')
    def import_credit_lines(self):
    	if self.data:
    		wb = xlrd.open_workbook(file_contents=base64.decodestring(self.data))
    		sheet = wb.sheets()[0]
    		values = []
    		for row in range(1,sheet.nrows):
    			col_value = []
    			for col in range(1,sheet.ncols):
    				if col == 37:#compteur nombre de crédits (une colonne inutile pour nous)
    					continue
    				value = sheet.cell(row,col).value
    				col_value.append(value)
    			values.append(col_value)
    		dicos = self.fusion(values)
    		lines = []
    		for dico in dicos:
    			lines.append((0,0,dico))
    		self.credit_import_line_ids = lines

    def clear_all_lines(self):
    	self.credit_import_line_ids.unlink()
    	self.data = False
    	return

    def fusion(self,liste):
    	columns = [
    				'guarantee_type',
    				'date_cgb',
    				'bank_name',
    				'mise_en_place',
    				'date_mise_en_place',
    				'first_due_date',
    				'last_due_date',
    				'project_name',
    				'nature_credit_name',
    				'legal_status_name',
    				'sous_fonds_name',
    				'product_type',
    				'psp_name',
    				'activity_sector_name',
    				'filiere_name',
    				'reseau_name',
    				'region_name',
    				'departement_name',
    				'funding_amount',
    				'credit_amount',
    				'guarantee_amount',
    				'quota',
    				'interest_rate',
    				'duration',
    				'diferred_duration',
    				'guarantee_commission_rate',
    				'guarantee_commission_amount',
    				'number_jobs',
    				'payment_amount',
    				'oustanding_credit',
    				'oustanding_guarantee',
    				#'status_name',
    				'state',
    				'nombre_echeances_impayes',
    				'unpaid_amount',
    				'compensation_amount',
    				'observations',
    				'code',
    				'country',
    				'code_benef'
    			  ]
    	dicos = []
    	for i in range(len(liste)):
    		dicos.append(dict(zip(columns,liste[i])))
    	for i in range(len(dicos)):
    		for key in dicos[i]:
    			if 'guarantee_type' == key and dicos[i][key]:
    				guarantee_type = dicos[i][key]
    				if guarantee_type.strip().lower() == "garantie individuelle":
    					dicos[i][key] = "individuelle"
    				else:
    					dicos[i][key] = "portefeuille"
    			if 'date_cgb' == key and dicos[i][key]:
    				dicos[i][key] = excel_utility.convert_excel_date_to_python_date(dicos[i][key])
    			if 'mise_en_place' == key and dicos[i][key]:
    				if dicos[i][key] == "Oui":
    					dicos[i][key] = "oui"
    				if dicos[i][key] == "Annulée":
    					dicos[i][key] = "annulee"
    				else:
    					dicos[i][key] = "en_attente"
    			if 'date_mise_en_place' == key and dicos[i][key]:
    				dicos[i][key] = excel_utility.convert_excel_date_to_python_date(dicos[i][key])
    			if 'first_due_date' == key and dicos[i][key]:
    				dicos[i][key] = excel_utility.convert_excel_date_to_python_date(dicos[i][key])
    			if 'last_due_date' == key and dicos[i][key]:
    				dicos[i][key] = excel_utility.convert_excel_date_to_python_date(dicos[i][key])
    			if 'product_type' == key and dicos[i][key]:
    				if dicos[i][key] == "Investissement création":
    					dicos[i][key] = "investissement_creation"
    				if dicos[i][key] == "Investissement extension":
    					dicos[i][key] = "investissement_extension"
    				else:
    					dicos[i][key] = "exploitation"
    			if 'state' == key and dicos[i][key]:
    				state = dicos[i][key]
    				if state.strip().lower() == 'annulé':
    					dicos[i][key] = 'annule'
    				elif state.strip().lower() == 'déclassé':
    					dicos[i][key] = 'declasse'
    				elif state.strip().lower() == 'impayé':
    					dicos[i][key] = 'impaye'
    				elif state.strip().lower() == 'indemnisé':
    					dicos[i][key] = 'indemnise'
    				elif state.strip().lower() == 'non mis en place':
    					dicos[i][key] = 'non_mis_en_place'
    				elif state.strip().lower() == 'sain':
    					dicos[i][key] = 'sain'
    				else:
    					dicos[i][key] = 'solde'

    	return dicos

class FongipCreditLine(models.Model):
	_name = 'fongip.credit.import.line'
	_description = 'Credit import line'

	credit_import_id = fields.Many2one(
		'fongip.credit.import',
		string = 'Crédit'
		)
	guarantee_type = fields.Selection(
		GUARANTEE_TYPE, 
		string = 'Type de garantie')
	date_cgb = fields.Date(string = 'Date CGB')
	bank_name = fields.Char(string = "Banque")
	mise_en_place = fields.Selection(
		MISE_EN_PLACE,
		string = "Mise en place")
	date_mise_en_place = fields.Date(string = 'Date de mise en place')
	first_due_date = fields.Date(string = "Date première échéance")
	last_due_date = fields.Date(string = "Date dernière échéance")
	project_name = fields.Char(string = 'Nom dossier')
	nature_credit_name = fields.Char(string = 'Nature du crédit')
	legal_status_name = fields.Char(string = "Forme juridique")
	sous_fonds_name = fields.Char(string = "Sous fonds")
	product_type = fields.Selection(
		PRODUCT_TYPE,
		string = "Type de produit"
		)
	psp_name = fields.Char(string = "PSP")
	activity_sector_name = fields.Char(string = "Secteur d'activité")
	filiere_name = fields.Char(string = "Filière")
	reseau_name = fields.Char(string = "Réseau")
	region_name = fields.Char(string = "Région")
	departement_name = fields.Char(string = "Département")
	funding_amount = fields.Monetary(string = "Montant du financement")
	credit_amount = fields.Monetary(string = "Montant du crédit")
	currency_id = fields.Many2one(
		'res.currency',
		'Currency',
		default=lambda self: self.env.company.currency_id.id
		)
	guarantee_amount = fields.Monetary(string = "Montant de la garantie")
	quota = fields.Float(string = "Quotité")
	interest_rate = fields.Float(string = "Taux d'interet")
	duration = fields.Integer(string = "Durée")
	diferred_duration = fields.Integer(string = "Différée")
	guarantee_commission_rate = fields.Float(string = "Commission de garantie")
	guarantee_commission_amount = fields.Monetary(string = "Montant de la commission de garantie")
	number_jobs = fields.Integer(string = "Nombre d'emplois créés et consolidés")
	payment_amount = fields.Monetary(string = "Montant de l'échéance")
	oustanding_credit = fields.Monetary(string = "Encours du crédit")
	oustanding_guarantee = fields.Monetary(string = "Encours de la garantie")
	#status_name = fields.Char(string = "Etat")
	state = fields.Selection(
		CREDIT_STATUS,
		string = "Etat"
		)
	nombre_echeances_impayes = fields.Integer(string = "Nombre d'échéances impayés")
	unpaid_amount = fields.Monetary(string = "Monatnt des impayés")
	compensation_amount = fields.Monetary(string = "Montant de l'indemnisation")
	observations = fields.Text(string = "Observations")
	code = fields.Integer(string = "Code")
	country = fields.Char(string = "Pays")
	code_benef = fields.Integer(string = "Code bénéf")


class Beneficiary(models.Model):
	_name = 'fongip.portefeuille.beneficiary'
	_description = 'Bénéficiaire portefeuille'
	_rec_name = 'partner_id'

	partner_id = fields.Many2one(
		'res.partner',
		string = "Bénéficiaire"
		)

class PortefeuilleLine(models.Model):
	_name = 'fongip.portefeuille.line'
	_description = 'Portefeuille line'

	beneficiary_id = fields.Many2one(
		'fongip.portefeuille.beneficiary',
		string = "Bénéficiaire"
		)
	project_id = fields.Many2one(
		'fongip.project',
		string = "Dossier"
		)