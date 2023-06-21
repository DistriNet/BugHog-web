from flask import make_response, Blueprint


demo = Blueprint('demo', __name__, template_folder="templates/demo")

@demo.route('/', host='domaina.com:5000')
def csp_upgrade_insecure():
    #url = "%68ttp:%2f/adition.com/?secret=12345"
    url = "http://adition.com/?secret=12345"
    resp = make_response("<iframe src=\"data:image/svg+xml,<svg%20xmlns='%68ttp:%2f/www.w3.org/2000/svg'%20xmlns:xlink='%68ttp:%2f/www.w3.org/1999/xlink'><image%20xlink:hr%65f='" + url + "'></image></svg>\"></iframe>")
    resp = make_response("<iframe><img src='http://adition.com/?secret2=12345></iframe>")
    resp = make_response("<iframe src=\"data:text/html,<script src='http://adition.com/scriptje'>\"></iframe>")
    #resp = make_response("<img src=\"data:image/svg+xml,<svg%20xmlns='%68ttp:%2f/www.w3.org/2000/svg'%20xmlns:xlink='%68ttp:%2f/www.w3.org/1999/xlink'><image%20xlink:hr%65f='" + url + "'></image></svg>\">")
    resp.headers["Content-Security-Policy"] = "block-all-mixed-content"
    return resp