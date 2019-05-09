# -*- coding: utf-8 -*-

import time
import traceback
import math
import multiprocessing
import argparse
from tushare_api.tushare_process import ts_pro
from db.mysql_tables import StockFinacial, STOCK_BASE
from comm.utils import ProjectUtil
from db.mysql_alchemy import MySession


class StockBasicJob:
    name = 'stock_basic_job'
    stock_db = 'stock'

    def __init__(self, mylogger, process_num, exchange, job_type):
        self.process_num = process_num
        self.job_type = job_type
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
            self.mylogger.info("----start " + self.name)
            self.session, self.engine = MySession.get_wild_session(self.stock_db)
            if not self.session or not self.engine:
                self.mylogger.error("fail to connect to the databases! exit program!")
                exit(1)
            STOCK_BASE.metadata.create_all(self.engine)

            num_compress_process = 0
            queue = multiprocessing.Queue()
            data = ts_pro.stock_basic(exchange_id='', list_status='L', exchange=self.exchange)
            for idx, row in data.iterrows():
                    if self.process_num > 1:
                        try:
                            job = multiprocessing.Process(target=self.get_stock_basic_info,
                                                          args=(row['ts_code'],
                                                                row['name'],
                                                                queue))
                            job.start()
                            num_compress_process += 1
                            while num_compress_process == self.process_num:
                                (stock_name, status) = queue.get()
                                num_compress_process -= 1
                                if status < 0:
                                    self.mylogger.error("==exceptions occurs "
                                                        "when get info of stock:{} ".format(stock_name))
                                elif status == 0:
                                    self.mylogger.info("finish stock:{} ".format(stock_name))
                        except:
                            self.mylogger.error(traceback.format_exc())
                    else:
                        self.get_stock_basic_info(row['ts_code'], row['name'])


        except:
            self.mylogger.error(traceback.format_exc())
        finally:
            self.mylogger.info("----exit " + self.name)

    def get_stock_basic_info(self, ts_code, name, queue=None):
        while True:
            try:
                sess, _ = MySession.get_wild_session(self.stock_db)
                if not sess:
                    raise Exception
                dt_stock_finacial = StockFinacial()
                res = ts_pro.fina_indicator(ts_code=ts_code)
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
                break
            except:
                if queue:
                    queue.put((ts_code + ":" + name, -1))
                self.mylogger.error(traceback.format_exc())
                time.sleep(20)


def arg_parser():
    try:
        parser = argparse.ArgumentParser('./update_basic.py -h')
        parser.add_argument('-p', '--process', action='store', dest='process', type=int,
                            default=1, help='num of multi process')
        parser.add_argument('-e', '--exchange', action='store', dest='exchange', type=str,
                            default='SSE', help='market: SSE/SZSE')
        parser.add_argument('-t', '--type', action='store', dest='type', type=str,
                            default='good', help='task type')
        return parser
    except:
        print(traceback.format_exc())


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    logger = ProjectUtil.get_project_logger(StockBasicJob.name)
    crawler = StockBasicJob(logger, args.process, args.market, args.type)
    crawler.start()

