import requests
from procuraga.shortcuts import compact
from procuraga import query
from urllib.parse import urlparse
import statistics
import inflect

def awards(request):
	award = requests.get('http://philgeps.cloudapp.net:5000/api/action/datastore_search_sql?sql='+
		query.get('539525df-fc9a-4adf-b33d-04747e95f120', int(request.GET['page']), int(request.GET['number']))).json()['result']['records']

	return compact("award")

def bids(request):
	bids = requests.get('http://philgeps.cloudapp.net:5000/api/action/datastore_search_sql?sql='+
		query.year('539525df-fc9a-4adf-b33d-04747e95f120', '2009')).json()
	return compact("bids")

def pperunit(request):

	p = inflect.engine()

	year = request.GET['year'] if 'year' in request.GET else None

	pperunit = requests.get('http://philgeps.cloudapp.net:5000/api/action/datastore_search_sql?sql='+
		query.pperunit('"daa80cd8-da5d-4b9d-bb6d-217a360ff7c1" as item, "baccd784-45a2-4c0c-82a6-61694cd68c9d" as bid, "ec10e1c4-4eb3-4f29-97fe-f09ea950cdf1" as org',year)).json()['result']['records']

	# return compact("pperunit")

	item_names = []

	[item_names.append(item['item_name']) for item in pperunit if item['item_name'] not in item_names]

	item_names.sort()

	items = []

	for item_name in item_names:
		item_budgets = [int(item['budget'])/int(item['qty']) for item in pperunit if item['item_name'] == item_name]

		item_qties = []
		[item_qties.append(item['qty']) for item in pperunit if item['item_name'] == item_name]
		item_qty = sum(item_qties)

		business_categories = []
		[business_categories.append(item['business_category']) for item in pperunit if item['item_name'] == item_name and item['business_category'] not in business_categories]

		bidders = []
		[
			bidders.append({
				"bidder": item['org_name'],
				"item_desc": item['item_description'],
				"date": item['publish_date'],
				"budget": item['budget'],
				"qty": str(item['qty']) + " " + p.plural(item['uom'], item['qty']).lower(),
				"uom": item['uom'],
				"budget_qty": item['budget']/item['qty'],
				"loc": "%s - %s" % (item['region'], item['province']),
			})
			for item in pperunit if item['item_name'] == item_name and
			{
				"bidder": item['org_name'],
				"item_desc": item['item_description'],
				"date": item['publish_date'],
				"budget": item['budget'],
				"qty": str(item['qty']) + " " + p.plural(item['uom'], item['qty']).lower(),
				"uom": item['uom'],
				"budget_qty": item['budget']/item['qty'],
				"loc": "%s - %s" % (item['region'], item['province'])
			} not in bidders
		]

		minimum = min(item_budgets)
		maximum = max(item_budgets)
		mean = statistics.mean(item_budgets)
		median = statistics.median(item_budgets)

		try:
			mode = statistics.mode(item_budgets)
		except statistics.StatisticsError:
			mode = "N/A"

		items.append({
			"item_name": item_name,
			"min": minimum,
			"max": maximum,
			"count": len(bidders),
			"qty" : str(item_qty) + " " + p.plural(bidders[0]['uom'].lower(), item_qty),
			"mean" : mean,
			"median" : median,
			"mode" : mode,
			"business_category" : business_categories,
			"bidders": bidders
		})

	if year is None: year = 2009

	return compact("items")
