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
            # product = req.get_param("product") or None
            body = req.media
        except AttributeError:
            self.logger.error("No data provided")
            raise falcon.HTTPBadRequest(
                title='Missing data',
                description='You must provide a product(s) and amount(s) in json format as follows: \
                            `{ product: amount }`. If no known amount put 0 as a placeholder.')

        for item in body:
            self.db.set(item, body[item])

        resp.status = falcon.HTTP_201



app = falcon.App()
app.add_route('/inventory', Inventory())
