# -*- coding: utf-8 -*-
from django.http.response import JsonResponse
from contextlib import closing
from collections import OrderedDict
import json
from django.db import connection
from django.conf import settings
from config.utils.db_helpers import *
from datetime import datetime as dt


def get_production_products(request):
    sql_query = """
    select new.production_product_id, 
    new.production_product_name, new.production_product_category_name, new.product_type, new.production_product_images,
    new.production_product_price, new.currency_name, sum(production_product_amount) as production_product_amount ,
    array_agg(
        json_build_object(
        'i', new.stock_product_info
        )
    ) as stocks
    from(SELECT
        pp.id AS production_productID,
        ppi.id AS production_product_id,
        ppi.name AS production_product_name,
        pc.name AS production_product_category_name,
        pt.name as product_type,
        ppi.images AS production_product_images,
        ppi.price AS production_product_price,
        pp.amount as production_product_amount,
        pcurrency.name as currency_name,
        ARRAY_AGG(
            json_build_object(
                'stock_product_id', sp.id,
                'stock_product_name', sp.name,
                'stock_product_category_id', sp.category_id,
                'stock_product_images', sp.images,
                'stock_product_amount', ps.amount,
                'stock_product_defect_amount', ps.defect_amount
            )
        ) AS stock_product_info
        FROM
            products_productionproduct AS pp
        JOIN
            products_productionproductstockitem AS ps
        ON
            pp.id = ps.production_product_id
        JOIN
            products_productionproductinfo AS ppi
        ON
            pp.production_product_id = ppi.id
        JOIN
            products_products AS sp
        ON
            ps.stock_product_id = sp.id
        join 
            products_categories as pc
        on 
            pc.id = ppi.category_id
        join 
        	products_type as pt
        on
        	pc.type_id = pt.id
        join 
        	products_currency as pcurrency
        on
        	ppi.currency_id = pcurrency.id
        GROUP BY
            pp.id, ppi.id, ppi.name, pc.name, pt."name", ppi.images, ppi.price, pcurrency.name
        ORDER BY
            pp.created_at desc
       ) as new
group by new.production_product_id, new.production_product_name, new.production_product_category_name, new.product_type, 
new.production_product_images, new.production_product_price, new.currency_name
order by new.production_product_id desc
        """
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchall(cursor)
    result = []
    checking = {}
    price_change = request.GET.get('price_change', 'A')

    for _item in items:
        result.append(_format_products(_item, price_change))

    return {
        'items': result
    }


def _format_products(item, price_change):
    from collections import defaultdict

    def sum_dicts_by_key(lists, key):
        result_dict = defaultdict(
            lambda: {"stock_product_name": None, "stock_product_amount": 0, "stock_product_defect_amount": 0})

        for lst in lists:
            for item in lst:
                item_key = item[key]
                result_item = result_dict[item_key]
                result_item["stock_product_name"] = item_key
                result_item["stock_product_amount"] += item["stock_product_amount"]
                result_item["stock_product_defect_amount"] += item["stock_product_defect_amount"]

        result_list = list(result_dict.values())
        return result_list
    stocks = []
    for j in item['stocks']:
        stocks.append(j['i'])

    stocks = sum_dicts_by_key(stocks, key='stock_product_name')
    return OrderedDict([
        ("production_product_id", item['production_product_id']),
        ("production_product_name", item['production_product_name']),
        ("production_product_category_name", item['production_product_category_name']),
        ("production_product_type", item['product_type']),
        ("production_product_images", item['production_product_images']),
        ("production_product_price_all",
         json.loads(item['production_product_price']) if item['production_product_price'] else None),
        ("production_product_price",
         json.loads(item['production_product_price'])[price_change] if item['production_product_price'] else None),
        ("production_product_currency", item['currency_name']),
        ("production_product_amount", item['production_product_amount']),
        ("stock_product_info", stocks)
    ])


def get_production_products_income(request):
    sql_query = """
        SELECT
        pp.id AS production_product_id,
        ppi.name AS production_product_name,
        pc.name AS production_product_category_name,
        pt.name as product_type,
        ppi.images AS production_product_images,
        ppi.price AS production_product_price,
        pp.amount as production_product_amount,
        pcurrency.name as currency_name,
        ARRAY_AGG(
            json_build_object(
                'stock_product_id', sp.id,
                'stock_product_name', sp.name,
                'stock_product_category_id', sp.category_id,
                'stock_product_images', sp.images,
                'stock_product_amount', ps.amount,
                'stock_product_price', sp.price,
                'stock_product_defect_amount', ps.defect_amount
            )
        ) AS stock_product_info
        FROM
            products_productionproduct AS pp
        JOIN
            products_productionproductstockitem AS ps
        ON
            pp.id = ps.production_product_id
        JOIN
            products_productionproductinfo AS ppi
        ON
            pp.production_product_id = ppi.id
        JOIN
            products_products AS sp
        ON
            ps.stock_product_id = sp.id
        join 
            products_categories as pc
        on 
            pc.id = ppi.category_id
        join 
        	products_type as pt
        on
        	pc.type_id = pt.id
        join 
        	products_currency as pcurrency
        on
        	ppi.currency_id = pcurrency.id
        GROUP BY
            pp.id, ppi.name, pc.name, pt."name", ppi.images, ppi.price, pcurrency.name
        ORDER BY
            pp.created_at desc;
        """
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchall(cursor)
    result = []
    for item in items:
        item = _format_products_income(item)
        item['income'] = item['production_product_price'] - item['stock_products_price']
        result.append(item)
    return {
        'items': result
    }


def _format_products_income(item):
    sum_price = 0
    for i in item['stock_product_info']:
        try:
            sum_price += float(i['stock_product_amount']) * float(i['stock_product_price'])
        except:
            sum_price += 0
    return OrderedDict([
        ("production_product_id", item['production_product_id']),
        ("production_product_name", item['production_product_name']),
        ("production_product_type", item['product_type']),
        ("production_product_price_all",
         json.loads(item['production_product_price']) if item['production_product_price'] else None),
        ("production_product_price",
         float(json.loads(item['production_product_price'])['A']) * float(item['production_product_amount']) if item['production_product_price'] else 0),
        ("production_product_currency", item['currency_name']),
        ("production_product_amount", item['production_product_amount']),
        ("stock_product_info", item['stock_product_info']),
        ("stock_products_price", round(sum_price, 2)),
    ])


def get_defect_products(request):
    sql_query = """
            select pq.*, pp.name as product_name, uu.firstname , uu.lastname 
            from products_quantitychange pq 
            inner join products_products pp on pq.product_id = pp.id
            inner join user_user uu on pq.user_id = uu.id 
            order by pq.created_at desc
            """
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchall(cursor)
    result = []
    return {
        'items': items
    }
