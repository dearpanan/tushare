# -*- coding: utf-8 -*-

import time
import math
import multiprocessing
import argparse
import pandas as pd
import datetime as dt
from tushare_api.tushare_process import ts_pro
from db.mysql_tables import STOCK_BASE, StockFinacial, StockDaily, StockForecast, StockExpress, StockMoneyFlow
from comm.utils import ProjectUtil
from db.mysql_alchemy import MySession


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

            job_list = []
            if self.job_type.find('daily') >= 0 or self.job_type.find('all') >= 0:
                job_list.append(self.get_stock_daily)
            if self.job_type.find('fina') >= 0 or self.job_type.find('all') >= 0:
                job_list.append(self.get_stock_fina)
            if self.job_type.find('forecast') >= 0 or self.job_type.find('all') >= 0:
                job_list.append(self.get_stock_forecast)
            if self.job_type.find('express') >= 0 or self.job_type.find('all') >= 0:
                job_list.append(self.get_stock_express)
            if self.job_type.find('moneyflow') >= 0 or self.job_type.find('all') >= 0:
                job_list.append(self.get_stock_moneyflow)
            if not job_list:
                raise Exception("wrong job type: {}!".format(self.job_type))

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
                        job = multiprocessing.Process(target=self.process_job,
                                                      args=(job_list, code,
                                                            row['name'], queue))
                        job.start()
                        num_compress_process += 1
                        while num_compress_process == self.process_num:
                            (stock_info, status) = queue.get()
                            num_compress_process -= 1
                            if status < 0:
                                self.mylogger.error("==exceptions occurs "
                                                    "when get info of job-{}:{}!".format(self.job_type,
                                                                                         stock_info))
                            elif status == 0:
                                self.mylogger.info("finish job-{}:{}!".format(self.job_type,
                                                                              stock_info))
                    except Exception as e:
                        self.mylogger.error(e)
                else:
                    self.process_job(job_list, code, row['name'])
                    self.mylogger.info("finish job-{}:{}-{}!".format(self.job_type,
                                                                     code, row['name']))
        except Exception as e:
            self.mylogger.error(e)
        finally:
            if self.session:
                MySession.close_wild_session(self.session)
            self.mylogger.info("----exit {}!".format(self.job_type))

    def process_job(self, job_list, ts_code, name, queue=None):
        try:
            sess, _ = MySession.get_wild_session(self.stock_db)
            if not sess:
                raise Exception("获取数据库连接失败！")
            for myjob in job_list:
                myjob(sess, ts_code, name, queue)
            if queue:
                queue.put((ts_code + "-" + name, 0))
        except Exception as e:
            if queue:
                queue.put((ts_code + "-" + name, -1))
            self.mylogger.error(e)
        finally:
            if sess:
                MySession.close_wild_session(sess)

    def get_stock_daily(self, sess, ts_code, name, queue=None):
        try:
            # query lastest date
            sd, ed = self.get_update_dates(sess, ts_code, StockDaily.trade_date,
                                           self.start_date, self.end_date)
            data = self.exe_until_success(ts_pro.daily, ts_code=ts_code,
                                          start_date=sd, end_date=ed)
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
            self.mylogger.info("  get stock-{} daily from {} to {} ".format(ts_code,
                                                                            sd, ed))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.error("  fail to get stock-{} daily from {} to {} ".format(ts_code,
                                                                                     sd, ed))

    def get_stock_forecast(self, sess, ts_code, name, queue=None):
        try:
            sd, ed = self.get_update_dates(sess, ts_code, StockForecast.ann_date,
                                           self.start_date, self.end_date)
            res = self.exe_until_success(ts_pro.forecast, ts_code=ts_code,
                                         start_date=sd, end_date=ed)
            for idx1, row1 in res.iterrows():
                dt_stock_forecast = StockForecast()
                dt_stock_forecast.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_forecast, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_forecast, field, value)
                sess.merge(dt_stock_forecast)
                sess.commit()
            self.mylogger.info("  get stock-{} forecast from {} to {} ".format(ts_code,
                                                                               sd, ed))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.error("  fail to get stock-{} forecast from {} to {} ".format(ts_code,
                                                                                        sd, ed))

    def get_stock_express(self, sess, ts_code, name, queue=None):
        try:
            sd, ed = self.get_update_dates(sess, ts_code, StockExpress.ann_date,
                                           self.start_date, self.end_date)
            res = self.exe_until_success(ts_pro.express, ts_code=ts_code,
                                         start_date=sd, end_date=ed)
            for idx1, row1 in res.iterrows():
                dt_stock_express = StockExpress()
                dt_stock_express.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_express, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_express, field, value)
                sess.merge(dt_stock_express)
                sess.commit()
            self.mylogger.info("  get stock-{} express from {} to {} ".format(ts_code,
                                                                              sd, ed))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.error("  fail to get stock-{} express from {} to {} ".format(ts_code,
                                                                                       sd, ed))

    def get_stock_fina(self, sess, ts_code, name, queue=None):
        try:
            sd, ed = self.get_update_dates(sess, ts_code, StockFinacial.end_date,
                                           self.start_date, self.end_date)
            res = self.exe_until_success(ts_pro.fina_indicator, ts_code=ts_code,
                                         start_date=sd, end_date=ed)
            for idx1, row1 in res.iterrows():
                dt_stock_finacial = StockFinacial()
                dt_stock_finacial.name = name
                for field in row1.keys():
                    if hasattr(dt_stock_finacial, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_finacial, field, value)
                sess.merge(dt_stock_finacial)
                sess.commit()
            self.mylogger.info("  get stock-{} fina from {} to {} ".format(ts_code,
                                                                           sd, ed))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.error("  fail to get stock-{} fina from {} to {} ".format(ts_code,
                                                                                    sd, ed))

    def get_stock_moneyflow(self, sess, ts_code, name, queue=None):
        try:
            sd, ed = self.get_update_dates(sess, ts_code, StockMoneyFlow.trade_date,
                                           self.start_date, self.end_date)
            res = self.exe_until_success(ts_pro.moneyflow, ts_code=ts_code,
                                         start_date=sd, end_date=ed)
            for idx1, row1 in res.iterrows():
                dt_stock_moneyflow = StockMoneyFlow()
                for field in row1.keys():
                    if hasattr(dt_stock_moneyflow, field):
                        value = row1[field]
                        if isinstance(value, float) and math.isnan(value):
                            value = None
                        setattr(dt_stock_moneyflow, field, value)
                sess.merge(dt_stock_moneyflow)
                sess.commit()
            self.mylogger.info("  get stock-{} moneyflow from {} to {} ".format(ts_code,
                                                                                sd, ed))
        except Exception as e:
            if queue:
                queue.put((ts_code + ":" + name, -1))
            self.mylogger.error(e)
            self.mylogger.error("  fail to get stock-{} moneyflow from {} to {} ".format(ts_code,
                                                                                         sd, ed))

    def exe_until_success(self, func, **params):
        while True:
            try:
                data = func(**params)
                return data
            except Exception as e:
                self.mylogger.error(e)
                self.mylogger.info("  wait 20s : {}, stock-{}!".format(func.args[0],
                                                                       params['ts_code']))
                time.sleep(20)

    def get_update_dates(self, sess, code, field, sd, ed, bw=270):
        row = None
        if not sd:
            try:
                row = sess.query(field).filter_by(
                    ts_code=code).order_by(field.desc()).first()
            except Exception as e:
                self.mylogger.error(e)
            if row:
                sd_date = row[0] + dt.timedelta(days=1)
            else:
                sd_date = dt.datetime.now() - dt.timedelta(weeks=bw)
            sd = sd_date.strftime("%Y%m%d")
        if not ed:
            ed = dt.datetime.now().strftime("%Y%m%d")
        return sd, ed


def arg_parser():
    try:
        myparser = argparse.ArgumentParser('./update_stock.py -h')
        myparser.add_argument('-p', '--process', action='store', dest='process', type=int,
                              default=1, help='num of multi process')
        myparser.add_argument('-e', '--exchange', action='store', dest='exchange', type=str,
                              default='all', help='market: all/sh/sz')
        myparser.add_argument('-t', '--type', action='store', dest='type', type=str,
                              default='all', help='task type: daily/fina/forecast/express/moneyflow/all')
        myparser.add_argument('--sd', action='store', dest='start_d', type=str,
                              default='', help='start date')
        myparser.add_argument('--ed', action='store', dest='end_d', type=str,
                              default='', help='end date')
        return myparser
    except Exception as e:
        print(e)


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    logger = ProjectUtil.get_project_logger(StockBasicJob.name)
    crawler = StockBasicJob(logger, args.process, args.exchange, args.type, args.start_d, args.end_d)
    crawler.start()

