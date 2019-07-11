# -*- coding: utf-8 -*-

import time
import math
import multiprocessing
import argparse
import pandas as pd
from tushare_api.tushare_process import ts_pro
from db.mysql_tables import StockFinacial, StockDaily, StockForecast, StockExpress, STOCK_BASE
from comm.utils import ProjectUtil
from db.mysql_alchemy import MySession
from datetime import datetime as dt

class StockBasicJob:
    name = 'stock_job'
    stock_db = 'stock'

    def __init__(self, mylogger, process_num, exchange, job_type, start_date, end_date):
        self.process_num = process_num
        self.job_type = job_type
        self.start_date = start_date
        self.end_date = end_date
        self.session = None
        self.engine = None
        self.mylogger = None
        self.exchange = exchange

        if mylogger:
            self.mylogger = mylogger
        else:
            self.mylogger = ProjectUtil.get_project_logger(self.name)

    def start(self):
        try:
            self.mylogger.info("----start " + self.job_type)
            self.session, self.engine = MySession.get_wild_session(self.stock_db)
            if not self.session or not self.engine:
                self.mylogger.error("fail to connect to the databases! exit program!")
                exit(1)
            STOCK_BASE.metadata.create_all(self.engine)

            job_func = None
            if self.job_type == 'daily':
                job_func = self.get_stock_daily
            elif self.job_type == 'fina':
                job_func = self.get_stock_fina
            elif self.job_type == 'forecast':
                job_func = self.get_stock_forecast
            elif self.job_type == 'express':
                job_func = self.get_stock_express
            else:
                raise Exception("wrong job type: {}!".format(job_func))

            if self.exchange not in ('all', 'sh', 'sz'):
                raise Exception("wrong exchange: {}!".format(self.exchange))
            data = pd.DataFrame()
            if self.exchange in ('all', 'sh'):
                # SSE 上交所
                data1 = self.exe_until_success(ts_pro.stock_basic,
                                               exchange_id='', list_status='L', exchange='SSE')
                data1.set_index(["ts_code"], inplace=True)
                data = data.append(data1)
            if self.exchange in ('all', 'sz'):
                # SSE 深交所
                data2 = self.exe_until_success(ts_pro.stock_basic,
                                               exchange_id='', list_status='L', exchange='SZSE')
                data2.set_index(["ts_code"], inplace=True)
                data = data.append(data2)

            num_compress_process = 0
            queue = multiprocessing.Queue()
            for code, row in data.iterrows():
                if self.process_num > 1:
                    try:
                        job = multiprocessing.Process(target=job_func,
                                                      args=(code,
                                                            row['name'],
                                                            queue))
                        job.start()
                        num_compress_process += 1
                        while num_compress_process == self.process_num:
                            (stock_name, status) = queue.get()
                            num_compress_process -= 1
                            if status < 0:
                                self.mylogger.error("==exceptions occurs "
                                                    "when get info of {}:{}-{} ".format(self.job_type,
                                                                                        code,
                                                                                        stock_name))
                            elif status == 0:
                                self.mylogger.info("finish stock-{}:{} ".format(self.job_type,
                                                                                code,
                                                                                stock_name))
                    except Exception as e:
                        self.mylogger.error(e)
                else:
                    job_func(code, row['name'])
                    self.mylogger.info("finish stock-{}:{}-{} ".format(self.job_type,
                                                                       code,
                                                                       row['name']))
        except Exception as e:
            self.mylogger.error(e)
        finally:
            self.mylogger.info("----exit {}".format(self.job_type))

    def get_stock_forecast(self, ts_code, name, queue=None):
        try:
            sess, _ = MySession.get_wild_session(self.stock_db)
            if not sess:
                raise Exception
            dt_stock_forecast = StockForecast()
            res = self.exe_until_success(ts_pro.forecast, ts_code=ts_code)
            for idx1, row1 in res.iterrows():
                dt_stock_forecast.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_forecast, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_forecast, field, value)
                sess.merge(dt_stock_forecast)
                sess.commit()
            if queue:
                queue.put((ts_code + ":" + name, 0))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)

    def get_stock_express(self, ts_code, name, queue=None):
        try:
            sess, _ = MySession.get_wild_session(self.stock_db)
            if not sess:
                raise Exception
            dt_stock_express = StockExpress()
            res = self.exe_until_success(ts_pro.express,
                                         ts_code=ts_code, start_date=self.start_date, end_date=self.end_date)
            for idx1, row1 in res.iterrows():
                dt_stock_express.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_express, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_express, field, value)
                sess.merge(dt_stock_express)
                sess.commit()
            if queue:
                queue.put((ts_code + ":" + name, 0))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)

    def get_stock_fina(self, ts_code, name, queue=None):
        try:
            sess, _ = MySession.get_wild_session(self.stock_db)
            if not sess:
                raise Exception('')
            dt_stock_finacial = StockFinacial()
            res = self.exe_until_success(ts_pro.fina_indicator, ts_code=ts_code)
            for idx1, row1 in res.iterrows():
                dt_stock_finacial.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_finacial, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_finacial, field, value)
                sess.merge(dt_stock_finacial)
                sess.commit()
            if queue:
                queue.put((ts_code + ":" + name, 0))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)

    def get_stock_daily(self, ts_code, name, queue=None):
        try:
            sess, _ = MySession.get_wild_session(self.stock_db)
            if not sess:
                raise Exception('')
            # query lastest date
            row = sess.query(StockDaily).filter_by(
                ts_code=ts_code).order_by(
                StockDaily.trade_date.desc()).first()
            if row and not self.start_date:
                self.start_date = row.trade_date.strftime("%Y%m%d")
            if not self.end_date:
                self.end_date = dt.now().strftime("%Y%m%d")

            data = self.exe_until_success(ts_pro.daily,
                                          ts_code=ts_code, start_date=self.start_date, end_date=self.end_date)

            dt_daily = StockDaily()
            for idx, row in data.iterrows():
                for field in row.keys():
                    if hasattr(dt_daily, field):
                        value = row[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_daily, field, value)
                sess.merge(dt_daily)
                sess.commit()
            if queue:
                queue.put((ts_code + ":" + name, 0))
            self.mylogger.info("get stock-{} daily data from {} to {} ".format(ts_code,
                                                                               self.start_date,
                                                                               self.end_date))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.info("fail to get stock-{} daily data from {} to {} ".format(ts_code,
                                                                                       self.start_date,
                                                                                       self.end_date))

    def exe_until_success(self, func, **params):
        while True:
            try:
                data = func(**params)
                return data
            except Exception as e:
                self.mylogger.error(e)
                time.sleep(20)


def arg_parser():
    try:
        parser = argparse.ArgumentParser('./update_stock.py -h')
        parser.add_argument('-p', '--process', action='store', dest='process', type=int,
                            default=1, help='num of multi process')
        parser.add_argument('-e', '--exchange', action='store', dest='exchange', type=str,
                            default='all', help='market: all/sh/sz')
        parser.add_argument('-t', '--type', action='store', dest='type', type=str,
                            default='daily', help='task type: daily/fina/forecast/express')
        parser.add_argument('--sd', action='store', dest='start_d', type=str,
                            default='', help='start date')
        parser.add_argument('--ed', action='store', dest='end_d', type=str,
                            default='', help='end date')
        return parser
    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    logger = ProjectUtil.get_project_logger(StockBasicJob.name)
    crawler = StockBasicJob(logger, args.process, args.exchange, args.type, args.start_d, args.end_d)
    crawler.start()

