"""
Provides functions for bond calculations given the provided format from the TCBS database.

Created: 10/10/2018
Last Edit: 10/29/2018
"""

from scipy.optimize import newton, fsolve


def IRR(cash_flows, N, estimate=0.05):
    """Calculates internal rate of return given parameter values.
    
        Parameters:
            cash_flows: payments arising from coupons and par (array)
            N : number of periods (array)
    """
    estimate2 = (cash_flows[0] / price)
    if estimate2 < price:
        estimate = estimate2

    try:
        equation = (lambda y: sum([pmt / (1 + y)**n for pmt, n in zip(cash_flows, N)]) - price)
        return newton(equation, estimate, maxiter=300)
    except RuntimeError:
        return np.nan
    
    
class BondCalc():
    def __init__(self, price, par, coupon_rates, coupon_dates, maturity_date):
        return
