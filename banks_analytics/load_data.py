#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import numpy as np

import sys
reload(sys)
sys.setdefaultencoding('UTF8')


def subtract_month(date):  # subtract month from string date ('yyyy-mm-dd')
    year1 = int(date[:4]); month1 = int(date[5:7])
    year2 = year1; month2 = month1 - 1
    if month2 == 0:
        year2 -= 1; month2 = 12
    if month2 < 10:
        return str(year2) + '-0' + str(month2) + '-01'
    else:
        return str(year2) + '-' + str(month2) + '-01'

        
def extract_value_to_var(variable, html, keyword, pos, num_format_func = float):
    # html is organized in dictionary-like form: LABEL1:VALUE1, LABEL2:VALUE2, ...
    # so we are trying to find the label stored in 'keyword' arg and to append corresponding value to 'variable' arg
    k = html.find(keyword, pos); k += len(keyword)  # starting position
    kk = html.find(',', k)  # ending position
    if html[k:kk] == 'null':
        variable.append(np.nan)
    else:
        try:
            variable.append(num_format_func(html[k:kk]))
        except ValueError: # the end of the html file is reached
            return -1
    return kk


def parse_banki_ru(ind_num, date_begin):
    # ind_num -- number of indicator (see dictionary)
    # date_begin -- since we are going back in time, it is the latter month in our dataset (string 'yyyy-mm-dd')

    date1 = date_begin  # the date as of which we collect the data
    stop_message = 'К сожалению, по вашему запросу ничего не найдено. Попробуйте изменить параметры запроса.' # this message appears when no data is available
    url_template = 'http://www.banki.ru/banks/ratings/?PAGEN_1=1&search%5Btype%5D=name&sort_param=rating&sort_order=ASC&PROPERTY_ID=#insert_ind_num_here#&REGION_ID=0&date1=#insert_date1_here#&date2=#insert_date2_here#&IS_SHOW_GROUP=0&IS_SHOW_LIABILITIES=0'

    data = []  # list containing collected data, one month - one dataframe

    while True: # loop until stop message appears

        # progress print
        print 'Indicator #' + str(ind_num) + ',  date: ' + date1

        date2 = subtract_month(date1)  # the date which is used to calculate absolute and percent difference 
  
        response = urllib2.urlopen(url_template.replace('#insert_ind_num_here#', str(ind_num)).replace('#insert_date1_here#', date1).replace('#insert_date2_here#', date2))
        html = response.read()
        if html.find(stop_message) >= 0:
            break

        html = html.replace('"', '').replace(' ', '')
    
        # saving html source code for debuging
        f = open('html.txt', 'w')
        f.write(html)
        f.close()

        pos = 0 # current position of "cursor" in html
        # so we are going to get these kinds of data:
        license_num = []; value = []; diff_abs = []; diff_prc = []

        while pos >= 0: # while not eof   
            pos = extract_value_to_var(value, html, ',VALUE:', pos)
            pos = extract_value_to_var(diff_abs, html, ',ABSOLUTE_DIFF:', pos)
            pos = extract_value_to_var(diff_prc, html, ',PERCENT_DIFF:', pos)
            pos = extract_value_to_var(license_num, html, ',PROPERTY_LICENCE_VALUE:', pos)

        # debug print
        #print [date1, date2]
        #print [len(value), len(diff_abs), len(diff_prc), len(license_num)]
        #print [value[-1], diff_abs[-1], diff_prc[-1], license_num[-1]]

        data.append(np.c_[license_num, value, diff_abs, diff_prc])
        date1 = date2
        
    return data



