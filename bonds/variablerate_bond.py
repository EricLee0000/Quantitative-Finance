'''
This file contains bond calculation functions

Created: 09/27/2018 (mm/dd/yyyy)
Last Edited: 09/28/2018 (mm/dd/yyyy)

Written by: Eric Lee
'''
import calendar
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar, minimize, newton


# *Note: all coupon payments must be in list/array/series format for correct calculation.
class BondInfo:


    def __init__(self, tDate, mDate, fv, ac, freq, ytm=np.nan, c_list=[], calendarDays=365):
        '''
        Passes on variables needed for all bond calculations.
        
        tDate = transaction date
        mDate = maturity date
        n = number of periods
        
        fv = face/par value
        ac = annual coupon rate
        c = coupon rate per period
        ytm = yield to maturity (annual)
        y = yield per period
        apmt = annual coupon
        pmt = coupon per period
        freq = coupon frequency per year
        t = days passed since last coupon
        T = days per coupon period
        '''
        if np.isnan(ytm):
            print("***WARNING*** No YTM specified!")
        if (isinstance(tDate,str) and isinstance(mDate,str)):
            self.tDate = datetime.strptime(tDate, '%d/%m/%Y')
            self.mDate = datetime.strptime(mDate, '%d/%m/%Y')
        else:
            self.tDate = tDate
            self.mDate = mDate
        # self.n = int((self.mDate - self.tDate).days / (calendarDays/freq))
        # -1 matches the calculated value on www.vbma.org.vn
        self.fv = fv
        self.ac = np.array(ac)/ 100
        self.c = self.ac/ freq
        self.ytm = ytm/ 100
        self.y = self.ytm/ freq
        self.apmt = np.array(self.ac) * fv
        self.pmt = self.apmt/ freq
        self.freq = freq
        
        if calendarDays==360:
            n, T, t = self.calendar_360()
        else:
            pass
        self.n = n
        self.t = t
        self.T = T
        self.calendarDays = calendarDays
        return
        
    # def __repr__(self):
        # return

    def simplePrice(self):
        '''
        Calculates the present value of a fixed rate bond.
        '''
        c = self.c
        pmt = self.pmt
        y = self.y
        n = self.n
        fv = self.fv
        PV = (pmt)/ y * (1 - 1/(1+y)**n) + fv/ (1+y)**n
        return PV
        
        
    def simpleYield(self):
        '''
        Calculates the simple yield also known as the Japanese simple yield.
        More relevant for buy-and-hold investors.
        '''
        PV = self.bondPrice()
        ac = self.ac
        fv = self.fv
        apmt = self.apmt
        SY = (apmt + (fv - PV)/apmt)/ PV
        return SY
        

    def approximateYield(self):
        '''
        Calculates the approximate yield of a bond
        '''
        PV = self.dirtyPrice()
        fv = self.fv
        n = self.n
        pmt = self.pmt
        AY = (pmt + (fv - PV)/n) / ((PV + fv)/2)
        return AY
    
    
    
    def calendar_360(self):
        tDate = self.tDate
        mDate = self.mDate
        
        t_year = tDate.year
        m_year = mDate.year
        t_month = tDate.month
        m_month = mDate.month
        t_day = tDate.day
        m_day = mDate.day
        
        if (t_month==2) and (t_day==calendar.monthrange(t_year,t_month)[-1]):
            t_day = 30
        if (m_month==2) and (m_day==calendar.monthrange(m_year,m_month)[-1]):
            m_day = 30
        if t_day in (30,31) and m_day==31:
            m_day = 30
        if t_day>30:
            t_day = 30
        
        n_days = 360*(m_year-t_year) + 30*(m_month-t_month) + (m_day-t_day)
        n = int(np.ceil(n_days/ 360 * self.freq))
        T = 360/ self.freq
        t = T - n_days%T
        return n, T, t

        
        
    def dirtyPrice(self):
        '''
        dirtyPrice = cleanPrice + accruedInterest
        dirtyPrice = PMT/(1+y)**(1-t/T) + PMT/(1+y)**(2-t/T)+...+(PMT+FV)/(1+y)**(N-t/T)

        accruedInterest = t/T * PMT

        pmt = coupon payment per period

        calendarDays = day_count convention (e.g. actual/360, actual/365, 30/360)
        t/T # fraction of the current coupon period that has passed
        '''

        pmt = self.pmt
        fv = self.fv
        y = self.y
        n = self.n
        t = self.t
        T = self.T
        freq = self.freq
        N = np.array(range(n)) + 1
        
        if t==T:
            dirtyPrice = sum([pmt/(1+y)**(i) for pmt,i in zip(pmt,N)]) \
                            + fv/(1+y)**(n)
            accruedInterest=0
            cleanPrice = dirtyPrice - accruedInterest
        else:
            dirtyPrice = sum([pmt/(1+y)**(i-t/T) for pmt,i in zip(pmt,N)]) \
                            + fv/(1+y)**(n-t/T)
            
            accruedInterest = (pmt[1] * (t/T))
            cleanPrice = dirtyPrice - accruedInterest
        return dirtyPrice, accruedInterest, cleanPrice
        

    
    def ytm_couponList(self, price, guess=0.05):
        fv = self.fv
        n = self.n
        t = self.t
        T = self.T
        pmt = self.pmt
        freq = self.freq
        price=price
        
        N = np.array(range(n)) + 1
        if t==T:
            equation = (lambda x: sum([pmt/(1+x)**(i) for pmt,i in zip(pmt,N)]) + fv/(1+x)**(n) - price)
        else:
            equation = (lambda x: sum([pmt/(1+x)**(i-t/T) for pmt,i in zip(pmt,N)]) \
                        + fv/(1+x)**(n-t/T) - price)
        return newton(equation, x0=0.05, maxiter=1000) * freq

		
if __name__ == '__main__':
    ac = pd.Series([8] * 20)
    bi = BondInfo(tDate='14/02/2011', mDate='15/11/2020', fv=100, ac=ac, ytm=8, freq=2, calendarDays=360)
    print(bi.dirtyPrice())
    # print(bi.calendar_360())
    
    ytm = bi.ytm_couponList(price=101.958172)
    print(ytm)