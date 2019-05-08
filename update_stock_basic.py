# -*- coding: utf-8 -*-

import time
import traceback
import json
import re
import os
import multiprocessing
import argparse
from tushare_api.tushare_process import ts_pro
from db.mysql_tables import StockFinacial, STOCK_BASE
from comm.utils import ProjectUtil
from db.mysql_alchemy import MySession


class StockBasicJob:
    name = 'stock_basic_job'
    stock_db = 'stock'

    def __init__(self, mylogger, process_num, job_type):
        self.process_num = process_num
        self.job_type = job_type
        self.session = None
        self.engine = None
        self.mylogger = None

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
            data = ts_pro.stock_basic(exchange_id='', list_status='L')
            for idx, row in data.iterrows():
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
        except:
            self.mylogger.error(traceback.format_exc())
        finally:
            self.mylogger.info("----exit " + self.name)

    def get_stock_basic_info(self, ts_code, name, queue):
        while True:
            try:
                sess, _ = MySession.get_wild_session(self.stock_db)
                if not sess:
                    raise Exception
                dt_stock_finacial = StockFinacial()
                res = ts_pro.fina_indicator(ts_code=ts_code)
                for idx1, row1 in res:
                    dt_stock_finacial.ts_code = ts_code
                    dt_stock_finacial.name = name
                    dt_stock_finacial.ann_date = row1['ann_date']
                    dt_stock_finacial.end_date = row1['end_date']
                    dt_stock_finacial.eps = row1['eps']  # 基本每股收益
                    dt_stock_finacial.dt_eps = row1['dt_eps']  # 稀释每股收益
                    dt_stock_finacial.total_revenue_ps = row1['total_revenue_ps']  # 每股营业总收入
                    dt_stock_finacial.revenue_ps = row1['revenue_ps']  # 每股营业收入
                    dt_stock_finacial.capital_rese_ps = row1['capital_rese_ps']  # 每股资本公积
                    dt_stock_finacial.surplus_rese_ps = row1['surplus_rese_ps']  # 每股盈余公积
                    dt_stock_finacial.undist_profit_ps = row1['undist_profit_ps']  # 每股未分配利润
                    dt_stock_finacial.extra_item = row1['extra_item']  # 非经常性损益
                    dt_stock_finacial.profit_dedt = row1['profit_dedt']  # 扣除非经常性损益后的净利润
                    dt_stock_finacial.gross_margin = row1['gross_margin']  # 毛利
                    dt_stock_finacial.current_ratio = row1['current_ratio']  # 流动比率
                    dt_stock_finacial.quick_ratio = row1['quick_ratio']  # 速动比率
                    dt_stock_finacial.cash_ratio = row1['cash_ratio']  # 保守速动比率
                    dt_stock_finacial.invturn_days = row1['invturn_days']  # 存货周转天数
                    dt_stock_finacial.arturn_days = row1['arturn_days']  # 应收账款周转天数
                    dt_stock_finacial.inv_turn = row1['inv_turn']  # 存货周转率
                    dt_stock_finacial.ar_turn = row1['ar_turn']  # 应收账款周转率
                    dt_stock_finacial.ca_turn = row1['ca_turn']  # 流动资产周转率
                    dt_stock_finacial.fa_turn = row1['fa_turn']  # 固定资产周转率
                    dt_stock_finacial.assets_turn = row1['assets_turn']  # 总资产周转率
                    dt_stock_finacial.op_income = row1['op_income']  # 经营活动净收益
                    dt_stock_finacial.valuechange_income = row1['valuechange_income']  # 价值变动净收益
                    dt_stock_finacial.interst_income = row1['interst_income']  # 利息费用
                    dt_stock_finacial.daa = row1['daa']  # 折旧与摊销
                    dt_stock_finacial.ebit = row1['ebit']  # 息税前利润
                    dt_stock_finacial.ebitda = row1['ebitda']  # 息税折旧摊销前利润
                    dt_stock_finacial.fcff = row1['fcff']  # 企业自由现金流量
                    dt_stock_finacial.fcfe = row1['fcfe']  # 股权自由现金流量
                    dt_stock_finacial.current_exint = row1['current_exint']  # 无息流动负债
                    dt_stock_finacial.noncurrent_exint = row1['noncurrent_exint']  # 无息非流动负债
                    dt_stock_finacial.interestdebt = row1['interestdebt']  # 带息债务
                    dt_stock_finacial.netdebt = row1['netdebt']  # 净债务
                    dt_stock_finacial.tangible_asset = row1['tangible_asset']  # 有形资产
                    dt_stock_finacial.working_capital = row1['working_capital']  # 营运资金
                    dt_stock_finacial.networking_capital = row1['networking_capital']  # 营运流动资本
                    dt_stock_finacial.invest_capital = row1['invest_capital']  # 全部投入资本
                    dt_stock_finacial.retained_earnings = row1['retained_earnings']  # 留存收益
                    dt_stock_finacial.diluted2_eps = row1['diluted2_eps']  # 期末摊薄每股收益
                    dt_stock_finacial.bps = row1['bps']  # 每股净资产
                    dt_stock_finacial.ocfps = row1['ocfps']  # 每股经营活动产生的现金流量净额
                    dt_stock_finacial.retainedps = row1['retainedps']  # 每股留存收益
                    dt_stock_finacial.cfps = row1['cfps']  # 每股现金流量净额
                    dt_stock_finacial.ebit_ps = row1['ebit_ps']  # 每股息税前利润
                    dt_stock_finacial.fcff_ps = row1['fcff_ps']  # 每股企业自由现金流量
                    dt_stock_finacial.fcfe_ps = row1['fcfe_ps']  # 每股股东自由现金流量
                    dt_stock_finacial.netprofit_margin = row1['netprofit_margin'] # 销售净利率
                    dt_stock_finacial.grossprofit_margin = row1['grossprofit_margin']  # 销售毛利率
                    dt_stock_finacial.cogs_of_sales = row1['cogs_of_sales']  # 销售成本率
                    dt_stock_finacial.expense_of_sales = row1['expense_of_sales']  # 销售期间费用率
                    dt_stock_finacial.profit_to_gr = row1['profit_to_gr']  # 净利润 / 营业总收入
                    dt_stock_finacial.saleexp_to_gr = row1['saleexp_to_gr']  # 销售费用 / 营业总收入
                    dt_stock_finacial.adminexp_of_gr = row1['adminexp_of_gr']  # 管理费用 / 营业总收入
                    dt_stock_finacial.finaexp_of_gr = row1['finaexp_of_gr']  # 财务费用 / 营业总收入
                    dt_stock_finacial.impai_ttm = row1['impai_ttm']  # 资产减值损失 / 营业总收入
                    dt_stock_finacial.gc_of_gr = row1['gc_of_gr']  # 营业总成本 / 营业总收入
                    dt_stock_finacial.op_of_gr = row1['op_of_gr']  # 营业利润 / 营业总收入
                    dt_stock_finacial.ebit_of_gr = row1['ebit_of_gr']  # 息税前利润 / 营业总收入
                    dt_stock_finacial.roe = row1['roe']  # 净资产收益率
                    dt_stock_finacial.roe_waa = row1['roe_waa']  # 加权平均净资产收益率
                    dt_stock_finacial.roe_dt = row1['roe_dt']  # 净资产收益率(扣除非经常损益)
                    dt_stock_finacial.roa = row1['roa']  # 总资产报酬率
                    dt_stock_finacial.npta = row1['npta']  # 总资产净利润
                    dt_stock_finacial.roic = row1['roic']  # 投入资本回报率
                    dt_stock_finacial.roe_yearly = row1['roe_yearly']  # 年化净资产收益率
                    dt_stock_finacial.roa2_yearly = row1['roa2_yearly']  # 年化总资产报酬率
                    dt_stock_finacial.roe_avg = row1['roe_avg']  # 平均净资产收益率(增发条件)
                    dt_stock_finacial.opincome_of_ebt = row1['opincome_of_ebt']  # 经营活动净收益 / 利润总额
                    dt_stock_finacial.investincome_of_ebt = row1['investincome_of_ebt']  # 价值变动净收益 / 利润总额
                    dt_stock_finacial.n_op_profit_of_ebt = row1['n_op_profit_of_ebt']  # 营业外收支净额 / 利润总额
                    dt_stock_finacial.tax_to_ebt = row1['tax_to_ebt']  # 所得税 / 利润总额
                    dt_stock_finacial.dtprofit_to_profit = row1['dtprofit_to_profit']  # 扣除非经常损益后的净利润 / 净利润
                    dt_stock_finacial.salescash_to_or = row1['salescash_to_or']  # 销售商品提供劳务收到的现金 / 营业收入
                    dt_stock_finacial.ocf_to_or = row1['ocf_to_or']  # 经营活动产生的现金流量净额 / 营业收入
                    dt_stock_finacial.ocf_to_opincome = row1['ocf_to_opincome']  # 经营活动产生的现金流量净额 / 经营活动净收益
                    dt_stock_finacial.capitalized_to_da = row1['capitalized_to_da']  # 资本支出 / 折旧和摊销
                    dt_stock_finacial.debt_to_assets = row1['debt_to_assets']  # 资产负债率
                    dt_stock_finacial.assets_to_eqt = row1['assets_to_eqt']  # 权益乘数
                    dt_stock_finacial.dp_assets_to_eqt = row1['dp_assets_to_eqt']  # 权益乘数(杜邦分析)
                    dt_stock_finacial.ca_to_assets = row1['ca_to_assets']  # 流动资产 / 总资产
                    dt_stock_finacial.nca_to_assets = row1['nca_to_assets']  # 非流动资产 / 总资产
                    dt_stock_finacial.tbassets_to_totalassets = row1['tbassets_to_totalassets']  # 有形资产 / 总资产
                    dt_stock_finacial.int_to_talcap = row1['int_to_talcap']  # 带息债务 / 全部投入资本
                    dt_stock_finacial.eqt_to_talcapital = row1['eqt_to_talcapital']  # 归属于母公司的股东权益 / 全部投入资本
                    dt_stock_finacial.currentdebt_to_debt = row1['currentdebt_to_debt']  # 流动负债 / 负债合计
                    dt_stock_finacial.longdeb_to_debt = row1['longdeb_to_debt']  # 非流动负债 / 负债合计
                    dt_stock_finacial.ocf_to_shortdebt = row1['ocf_to_shortdebt']  # 经营活动产生的现金流量净额 / 流动负债
                    dt_stock_finacial.debt_to_eqt = row1['debt_to_eqt']  # 产权比率
                    dt_stock_finacial.eqt_to_debt = row1['eqt_to_debt']  # 归属于母公司的股东权益 / 负债合计
                    dt_stock_finacial.eqt_to_interestdebt = row1['eqt_to_interestdebt']  # 归属于母公司的股东权益 / 带息债务
                    dt_stock_finacial.tangibleasset_to_debt = row1['tangibleasset_to_debt']  # 有形资产 / 负债合计
                    dt_stock_finacial.tangasset_to_intdebt = row1['tangasset_to_intdebt']  # 有形资产 / 带息债务
                    dt_stock_finacial.tangibleasset_to_netdebt = row1['tangibleasset_to_netdebt']  # 有形资产 / 净债务
                    dt_stock_finacial.ocf_to_debt = row1['ocf_to_debt']  # 经营活动产生的现金流量净额 / 负债合计
                    dt_stock_finacial.ocf_to_interestdebt = row1['ocf_to_interestdebt']  # 经营活动产生的现金流量净额 / 带息债务
                    dt_stock_finacial.ocf_to_netdebt = row1['ocf_to_netdebt']  # 经营活动产生的现金流量净额 / 净债务
                    dt_stock_finacial.ebit_to_interest = row1['ebit_to_interest']  # 已获利息倍数(EBIT / 利息费用)
                    dt_stock_finacial.longdebt_to_workingcapital = row1['longdebt_to_workingcapital']  # 长期债务与营运资金比率
                    dt_stock_finacial.ebitda_to_debt = row1['ebitda_to_debt']  # 息税折旧摊销前利润 / 负债合计
                    dt_stock_finacial.turn_days = row1['turn_days']  # 营业周期
                    dt_stock_finacial.roa_yearly = row1['roa_yearly']  # 年化总资产净利率
                    dt_stock_finacial.roa_dp = row1['roa_dp']  # 总资产净利率(杜邦分析)
                    dt_stock_finacial.fixed_assets = row1['fixed_assets']  # 固定资产合计
                    dt_stock_finacial.profit_prefin_exp = row1['profit_prefin_exp']  # 扣除财务费用前营业利润
                    dt_stock_finacial.non_op_profit = row1['non_op_profit']  # 非营业利润
                    dt_stock_finacial.op_to_ebt = row1['op_to_ebt']  # 营业利润／利润总额
                    dt_stock_finacial.nop_to_ebt = row1['nop_to_ebt']  # 非营业利润／利润总额
                    dt_stock_finacial.ocf_to_profit = row1['ocf_to_profit']  # 经营活动产生的现金流量净额／营业利润
                    dt_stock_finacial.cash_to_liqdebt = row1['cash_to_liqdebt']  # 货币资金／流动负债
                    dt_stock_finacial.cash_to_liqdebt_withinterest = row1['cash_to_liqdebt_withinterest']  # 货币资金／带息流动负债
                    dt_stock_finacial.op_to_liqdebt = row1['op_to_liqdebt']  # 营业利润／流动负债
                    dt_stock_finacial.op_to_debt = row1['op_to_debt']  # 营业利润／负债合计
                    dt_stock_finacial.roic_yearly = row1['roic_yearly']  # 年化投入资本回报率
                    dt_stock_finacial.profit_to_op = row1['profit_to_op']  # 利润总额／营业收入
                    dt_stock_finacial.q_opincome = row1['q_opincome']  # 经营活动单季度净收益
                    dt_stock_finacial.q_investincome = row1['q_investincome']  # 价值变动单季度净收益
                    dt_stock_finacial.q_dtprofit = row1['q_dtprofit']  # 扣除非经常损益后的单季度净利润
                    dt_stock_finacial.q_eps = row1['q_eps']  # 每股收益(单季度)
                    dt_stock_finacial.q_netprofit_margin = row1['q_netprofit_margin']  # 销售净利率(单季度)
                    dt_stock_finacial.q_gsprofit_margin = row1['q_gsprofit_margin']  # 销售毛利率(单季度)
                    dt_stock_finacial.q_exp_to_sales = row1['q_exp_to_sales']  # 销售期间费用率(单季度)
                    dt_stock_finacial.q_profit_to_gr = row1['q_profit_to_gr']  # 净利润／营业总收入(单季度)
                    dt_stock_finacial.q_saleexp_to_gr = row1['q_saleexp_to_gr']  # 销售费用／营业总收入(单季度)
                    dt_stock_finacial.q_adminexp_to_gr = row1['q_adminexp_to_gr']  # 管理费用／营业总收入(单季度)
                    dt_stock_finacial.q_finaexp_to_gr = row1['q_finaexp_to_gr']  # 财务费用／营业总收入(单季度)
                    dt_stock_finacial.q_impair_to_gr_ttm = row1['q_impair_to_gr_ttm']  # 资产减值损失／营业总收入(单季度)
                    dt_stock_finacial.q_gc_to_gr = row1['q_gc_to_gr']  # 营业总成本／营业总收入(单季度)
                    dt_stock_finacial.q_op_to_gr = row1['q_op_to_gr']  # 营业利润／营业总收入(单季度)
                    dt_stock_finacial.q_roe = row1['q_roe']  # 净资产收益率(单季度)
                    dt_stock_finacial.q_dt_roe = row1['q_dt_roe']  # 净资产单季度收益率(扣除非经常损益)
                    dt_stock_finacial.q_npta = row1['q_npta']  # 总资产净利润(单季度)
                    dt_stock_finacial.q_opincome_to_ebt = row1['q_opincome_to_ebt']  # 经营活动净收益／利润总额(单季度)
                    dt_stock_finacial.q_investincome_to_ebt = row1['q_investincome_to_ebt']  # 价值变动净收益／利润总额(单季度)
                    dt_stock_finacial.q_dtprofit_to_profit = row1['q_dtprofit_to_profit']  # 扣除非经常损益后的净利润／净利润(单季度)
                    dt_stock_finacial.q_salescash_to_or = row1['q_salescash_to_or']  # 销售商品提供劳务收到的现金／营业收入(单季度)
                    dt_stock_finacial.q_ocf_to_sales = row1['q_ocf_to_sales']  # 经营活动产生的现金流量净额／营业收入(单季度)
                    dt_stock_finacial.q_ocf_to_or = row1['q_ocf_to_or']  # 经营活动产生的现金流量净额／经营活动净收益(单季度)
                    dt_stock_finacial.basic_eps_yoy = row1['basic_eps_yoy']  # 基本每股收益同比增长率( %)
                    dt_stock_finacial.dt_eps_yoy = row1['dt_eps_yoy']  # 稀释每股收益同比增长率( %)
                    dt_stock_finacial.cfps_yoy = row1['cfps_yoy']  # 每股经营活动产生的现金流量净额同比增长率( %)
                    dt_stock_finacial.op_yoy = row1['op_yoy']  # 营业利润同比增长率( %)
                    dt_stock_finacial.ebt_yoy = row1['ebt_yoy']  # 利润总额同比增长率( %)
                    dt_stock_finacial.netprofit_yoy = row1['netprofit_yoy']  # 归属母公司股东的净利润同比增长率( %)
                    dt_stock_finacial.dt_netprofit_yoy = row1['dt_netprofit_yoy']  # 归属母公司股东的净利润 - 扣除非经常损益同比增长率( %)
                    dt_stock_finacial.ocf_yoy = row1['ocf_yoy']  # 经营活动产生的现金流量净额同比增长率( %)
                    dt_stock_finacial.roe_yoy = row1['roe_yoy']  # 净资产收益率(摊薄) 同比增长率( %)
                    dt_stock_finacial.bps_yoy = row1['bps_yoy']  # 每股净资产相对年初增长率( %)
                    dt_stock_finacial.assets_yoy = row1['assets_yoy']  # 资产总计相对年初增长率( %)
                    dt_stock_finacial.eqt_yoy = row1['eqt_yoy']  # 归属母公司的股东权益相对年初增长率( %)
                    dt_stock_finacial.tr_yoy = row1['tr_yoy']  # 营业总收入同比增长率( %)
                    dt_stock_finacial.or_yoy = row1['or_yoy']  # 营业收入同比增长率( %)
                    dt_stock_finacial.q_gr_yoy = row1['q_gr_yoy']  # 营业总收入同比增长率( %)(单季度)
                    dt_stock_finacial.q_gr_qoq = row1['q_gr_qoq']  # 营业总收入环比增长率( %)(单季度)
                    dt_stock_finacial.q_sales_yoy = row1['q_sales_yoy']  # 营业收入同比增长率( %)(单季度)
                    dt_stock_finacial.q_sales_qoq = row1['q_sales_qoq']  # 营业收入环比增长率( %)(单季度)
                    dt_stock_finacial.q_op_yoy = row1['q_op_yoy']  # 营业利润同比增长率( %)(单季度)
                    dt_stock_finacial.q_op_qoq = row1['q_op_qoq']  # 营业利润环比增长率( %)(单季度)
                    dt_stock_finacial.q_profit_yoy = row1['q_profit_yoy']  # 净利润同比增长率( %)(单季度)
                    dt_stock_finacial.q_profit_qoq = row1['q_profit_qoq']  # 净利润环比增长率( %)(单季度)
                    dt_stock_finacial.q_netprofit_yoy = row1['q_netprofit_yoy']  # 归属母公司股东的净利润同比增长率( %)(单季度)
                    dt_stock_finacial.q_netprofit_qoq = row1['q_netprofit_qoq']  # 归属母公司股东的净利润环比增长率( %)(单季度)
                    dt_stock_finacial.equity_yoy = row1['equity_yoy']  # 净资产同比增长率
                    dt_stock_finacial.rd_exp = row1['rd_exp']  # 研发费用
                    sess.merge(dt_stock_finacial)
                    sess.commit()
                queue.put((ts_code + ":" + name, 0))
                break
            except:
                queue.put((ts_code + ":" + name, -1))
                self.mylogger.error(traceback.format_exc())
                time.sleep(20)


def arg_parser():
    try:
        parser = argparse.ArgumentParser('./update_basic.py -h')
        parser.add_argument('-p', '--process', action='store', dest='process', type=int,
                            default=4, help='num of multi process')
        parser.add_argument('-t', '--type', action='store', dest='type', type=str,
                            default='good', help='task type')
        return parser
    except:
        print(traceback.format_exc())


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    logger = ProjectUtil.get_project_logger(StockBasicJob.name)
    crawler = StockBasicJob(logger, args.process, args.type)
    crawler.start()

