# -*- coding: utf-8 -*-
from contextlib import closing
from django.db import connection
from config.utils.db_helpers import *
from datetime import timedelta, date
from collections import OrderedDict
import json

def get_debtors():
    sql_query = """
       SELECT c.id AS client_id, json_build_object(
							'firstname', c.firstname,
							'lastname', c.lastname,
							'company_name', c.company_name,
							'inn', c.inn
							) as client,
							o.id AS order_id,  o.price - COALESCE(SUM(opc.price), 0) + o.delivery_price  AS remaining_balance
        FROM client_client AS c
        JOIN order_order AS o ON c.id = o.client_id
        LEFT JOIN order_orderpricechange AS opc ON o.id = opc.order_id
        where o.status_id = 4
        GROUP BY c.id, o.id, o.price
        HAVING COALESCE(SUM(opc.price), 0) + o.delivery_price < o.price
        """
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchall(cursor)
    return items

def get_debtors_count():
    sql_query = """
       SELECT COUNT(*) AS count
            FROM (
                SELECT c.id AS client_id,
                    o.id AS order_id,
                    o.price - COALESCE(SUM(opc.price), 0) AS remaining_balance
                FROM client_client AS c
                JOIN order_order AS o ON c.id = o.client_id
                LEFT JOIN order_orderpricechange AS opc ON o.id = opc.order_id
                where o.status_id = 4
                GROUP BY c.id, o.id, o.price
                HAVING COALESCE(SUM(opc.price), 0) < o.price
            ) AS subquery;
        """
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchone(cursor)
    return items




def get_today_production_products_income():
    sql_query = f"""
                SELECT
            pp.id AS production_product_id,
            ppi.name AS production_product_name,
            pc.name AS production_product_category_name,
            pt.name as product_type,
            ppi.images AS production_product_images,
            ppi.price AS production_product_price,
            pp.amount as production_product_amount,
            pcurrency.name as currency_name,
            pp.created_at::date as pp_date,
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
        JOIN 
            products_categories as pc
        ON 
            pc.id = ppi.category_id
        JOIN 
            products_type as pt
        ON
            pc.type_id = pt.id
        JOIN 
            products_currency as pcurrency
        ON
            ppi.currency_id = pcurrency.id
        GROUP BY
            pp.id, ppi.name, pc.name, pt.name, ppi.images, ppi.price, pcurrency.name
        ORDER BY
            pp.created_at desc;
"""
    with closing(connection.cursor()) as cursor:
        cursor.execute(sql_query)
        items = dictfetchall(cursor)
    price = 0
    for item in items:
        item = _format_products_income(item)
        if item['pp_created_at'] == date.today():
            price += (item['production_product_price'] - item['stock_products_price'])
    return {
        'price': price
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
        ('pp_created_at', item['pp_date'])
    ])
