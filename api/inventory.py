import falcon
import redis
import json
import logging
from wsgiref import simple_server

class Inventory:
    def __init__(self):
        self.db = redis.Redis(host='redis', port=6379, db=0)
        self.logger = logging.getLogger('inventory.' + __name__)

    def on_get(self, req, resp):
        item = req.get_param("product_id") or None
        res_dir = {}
        try:
            if(item):
                products = [item]
            else:
                products = self.db.keys("product-*")
            for product in products:
                product = product.decode('utf-8')
                val = self.db.get(product).decode('utf-8')
                res_dir[product] = val
        except Exception as ex:
            self.logger.error(ex)
            raise falcon.HTTPServiceUnavailable(
                title='Service Outage',
                description=ex,
                retry_after=30)

        resp.status = falcon.HTTP_200
        resp.media = json.dumps(res_dir)

    def on_post(self, req, resp):
        try:
            body = req.media
        except AttributeError:
            self.logger.error("No data provided")
            raise falcon.HTTPBadRequest(
                title='Missing data',
                description="You must provide an array of objects in json format as follows: \
                            `[{ 'product-id': <String>, 'amount': <Integer>, 'order_threshold': <Integer> }]`.")

        for item in body:
            key = "product-" + str(item["product-id"])
            val = {
                'amount': item["amount"] if ("amount" in item.keys()) else 0,
                'order_threshold': item["order_threshold"] if ("order_threshold" in item.keys()) else None
            }
            self.db.set(key, json.dumps(val))

        resp.status = falcon.HTTP_204

    def on_delete(self, req, resp):
        try:
            body = req.media
        except AttributeError:
            self.logger.error("No data provided")
            raise falcon.HTTPBadRequest(
                title='Missing data',
                description="You must provide an array of product(s) in json format as follows: \
                            `[{ 'product-id': <String> }]`.")

        for item in body:
            key = "product-" + str(item["product-id"])
            self.db.delete(key)

        resp.status = falcon.HTTP_204


app = falcon.App()
app.add_route('/inventory', Inventory())
