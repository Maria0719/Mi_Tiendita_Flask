# filters.py
from app import app

@app.template_filter('money')
def money_format(value):
    try:
        return "${:,.0f}".format(value or 0).replace(",", ".")
    except:
        return "$0"
