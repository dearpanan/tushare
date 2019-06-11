# -*- coding: utf-8 -*-


from sqlalchemy import Column
from sqlalchemy.dialects.mysql import VARCHAR, TEXT, INTEGER, FLOAT, DATE
from sqlalchemy.ext.declarative import declarative_base

STOCK_BASE = declarative_base(name='stock_base')


class StockDaily(STOCK_BASE):
    __tablename__ = 'stock_daily'
    ts_code = Column(VARCHAR(64), primary_key=True)  # 股票代码
    trade_date = Column(DATE, primary_key=True)  # 交易日期
    open = Column(FLOAT)  # 开盘价
    high = Column(FLOAT)  # 最高价
    low = Column(FLOAT)  # 最低价
    close = Column(FLOAT)  # 收盘价
    pre_close = Column(FLOAT)  # 昨收价
    change = Column(FLOAT)  # 涨跌额
    pct_chg = Column(FLOAT, index=True)  # 涨跌幅 （未复权，如果是复权请用通用行情接口 ）
    vol = Column(FLOAT, index=True)  # 成交量 （手）
    amount = Column(FLOAT)  # 成交额 （千元）


class StockCompany(STOCK_BASE):
    __tablename__ = 'stock_company'
    ts_code = Column(VARCHAR(64), primary_key=True)   # 股票代码
    exchange = Column(VARCHAR(64))  # 交易所代码 ，SSE上交所,SZSE深交所
    chairman = Column(VARCHAR(64))  # 法人代表
    manager = Column(VARCHAR(64))   # 总经理
    secretary = Column(VARCHAR(64))  # 董秘
    reg_capital = Column(FLOAT(), default=0.0)  # 注册资本
    setup_date = Column(VARCHAR(64))  # 注册日期
    province = Column(VARCHAR(64))  # 所在省份
    city = Column(VARCHAR(64))  # 所在城市
    introduction = Column(TEXT)  # 公司介绍
    website = Column(VARCHAR(64))  # 公司主页
    email = Column(VARCHAR(64))  # 电子邮件
    office = Column(TEXT)  # 办公室
    employees = Column(INTEGER)  # 员工人数
    main_business = Column(TEXT)  # 主要业务及产品
    business_scope = Column(TEXT)  # 经营范围


class StockMoneyFlow(STOCK_BASE):
    __tablename__ = 'stock_money_flow'
    ts_code = Column(VARCHAR(64), primary_key=True)   # TS代码
    trade_date = Column(DATE, primary_key=True)  # 交易日期
    buy_sm_amount = Column(FLOAT(), default=0.0)  # 小单买入金额（万元）
    sell_sm_vol = Column(INTEGER(), default=0.0)  # 小单卖出量（手）
    sell_sm_amount = Column(FLOAT(), default=0.0)  # 小单卖出金额（万元）
    buy_md_vol = Column(INTEGER(), default=0.0)  # 中单买入量（手）
    buy_md_amount = Column(FLOAT(), default=0.0)  # 中单买入金额（万元）
    sell_md_vol = Column(INTEGER(), default=0.0)  # 中单卖出量（手）
    sell_md_amount = Column(FLOAT(), default=0.0)  # 中单卖出金额（万元）
    buy_lg_vol = Column(INTEGER(), default=0.0)  # 大单买入量（手）
    buy_lg_amount = Column(FLOAT(), default=0.0)  # 大单买入金额（万元）
    sell_lg_vol = Column(INTEGER(), default=0.0)  # 大单卖出量（手）
    sell_lg_amount = Column(FLOAT(), default=0.0)  # 大单卖出金额（万元）
    buy_elg_vol = Column(INTEGER(), default=0.0)  # 特大单买入量（手）
    buy_elg_amount = Column(FLOAT(), default=0.0)  # 特大单买入金额（万元）
    sell_elg_vol = Column(INTEGER(), default=0.0)  # 特大单卖出量（手）
    sell_elg_amount = Column(FLOAT(), default=0.0)  # 特大单卖出金额（万元）
    net_mf_vol = Column(INTEGER(), default=0.0)  # 净流入量（手）
    net_mf_amount = Column(FLOAT(), default=0.0)  # 净流入额（万元）


class StockForecast(STOCK_BASE):
    __tablename__ = 'stock_forecast'
    ts_code = Column(VARCHAR(64), primary_key=True)
    ann_date = Column(DATE, index=True)     # 公告日期
    end_date = Column(DATE, primary_key=True)     # 报告期
    type = Column(VARCHAR(64))  # 业绩预告类型(预增 | 预减 | 扭亏 | 首亏 | 续亏 | 续盈 | 略增 | 略减)
    p_change_min = Column(FLOAT(), default=0.0)    # 预告净利润变动幅度下限（ % ）
    p_change_max = Column(FLOAT(), default=0.0)     # 预告净利润变动幅度上限（ % ）
    net_profit_min = Column(FLOAT(), default=0.0)   # 预告净利润下限（万元）
    net_profit_max = Column(FLOAT(), default=0.0)   # 预告净利润上限（万元）
    last_parent_net = Column(FLOAT(), default=0.0)  # 上年同期归属母公司净利润
    first_ann_date = Column(DATE)     # 首次公告日
    summary = Column(TEXT)  # 业绩预告摘要
    change_reason = Column(TEXT)  # 业绩变动原因


class StockExpress(STOCK_BASE):
    __tablename__ = 'stock_express'
    ts_code = Column(VARCHAR(64), primary_key=True)
    ann_date = Column(DATE, index=True)     # 公告日期
    end_date = Column(DATE, primary_key=True)     # 报告期
    revenue = Column(FLOAT(), default=0.0)  # 营业收入(元)
    operate_profit = Column(FLOAT(), default=0.0)  # 营业利润(元)
    total_profit = Column(FLOAT(), default=0.0)  # 利润总额(元)
    n_income = Column(FLOAT(), default=0.0)  # 净利润(元)
    total_assets = Column(FLOAT(), default=0.0)  # 总资产(元)
    total_hldr_eqy_exc_min_int = Column(FLOAT(), default=0.0)  # 股东权益合计(不含少数股东权益)(元)
    diluted_eps = Column(FLOAT(), default=0.0)  # 每股收益(摊薄)(元)
    diluted_roe = Column(FLOAT(), default=0.0)  # 净资产收益率(摊薄)( %)
    yoy_net_profit = Column(FLOAT(), default=0.0)  # 去年同期修正后净利润
    bps = Column(FLOAT(), default=0.0)  # 每股净资产
    yoy_sales = Column(FLOAT(), default=0.0)  # 同比增长率: 营业收入
    yoy_op = Column(FLOAT(), default=0.0)  # 同比增长率: 营业利润
    yoy_tp = Column(FLOAT(), default=0.0)  # 同比增长率: 利润总额
    yoy_dedu_np = Column(FLOAT(), default=0.0)  # 同比增长率: 归属母公司股东的净利润
    yoy_eps = Column(FLOAT(), default=0.0)  # 同比增长率: 基本每股收益
    yoy_roe = Column(FLOAT(), default=0.0)  # 同比增减: 加权平均净资产收益率
    growth_assets = Column(FLOAT(), default=0.0)  # 比年初增长率: 总资产
    yoy_equity = Column(FLOAT(), default=0.0)  # 比年初增长率: 归属母公司的股东权益
    growth_bps = Column(FLOAT(), default=0.0)  # 比年初增长率: 归属于母公司股东的每股净资产
    or_last_year = Column(FLOAT(), default=0.0)  # 去年同期营业收入
    op_last_year = Column(FLOAT(), default=0.0)  # 去年同期营业利润
    tp_last_year = Column(FLOAT(), default=0.0)  # 去年同期利润总额
    np_last_year = Column(FLOAT(), default=0.0)  # 去年同期净利润
    eps_last_year = Column(FLOAT(), default=0.0)  # 去年同期每股收益
    open_net_assets = Column(FLOAT(), default=0.0)  # 期初净资产
    open_bps = Column(FLOAT(), default=0.0)  # 期初每股净资产
    perf_summary = Column(TEXT)  # 业绩简要说明
    is_audit = Column(INTEGER)  # 是否审计： 1是, 0否
    remark = Column(TEXT)  # 备注


class StockFinacial(STOCK_BASE):
    __tablename__ = 'stock_finacial'
    ts_code = Column(VARCHAR(64), primary_key=True)
    name = Column(VARCHAR(64))
    ann_date = Column(DATE, index=True)  # 公告日期
    end_date = Column(DATE, primary_key=True)  # 报告期
    eps = Column(FLOAT(), default=0.0)  # 基本每股收益
    dt_eps = Column(FLOAT(), default=0.0)  # 稀释每股收益
    total_revenue_ps = Column(FLOAT(), default=0.0)  # 每股营业总收入
    revenue_ps = Column(FLOAT(), default=0.0)  # 每股营业收入
    capital_rese_ps = Column(FLOAT(), default=0.0)  # 每股资本公积
    surplus_rese_ps = Column(FLOAT(), default=0.0)  # 每股盈余公积
    undist_profit_ps = Column(FLOAT(), default=0.0)  # 每股未分配利润
    extra_item = Column(FLOAT(), default=0.0)  # 非经常性损益
    profit_dedt = Column(FLOAT(), default=0.0)  # 扣除非经常性损益后的净利润
    gross_margin = Column(FLOAT(), default=0.0)  # 毛利
    current_ratio = Column(FLOAT(), default=0.0)  # 流动比率
    quick_ratio = Column(FLOAT(), default=0.0)  # 速动比率
    cash_ratio = Column(FLOAT(), default=0.0)  # 保守速动比率
    invturn_days = Column(FLOAT(), default=0.0)  # 存货周转天数
    arturn_days = Column(FLOAT(), default=0.0)  # 应收账款周转天数
    inv_turn = Column(FLOAT(), default=0.0)  # 存货周转率
    ar_turn = Column(FLOAT(), default=0.0)  # 应收账款周转率
    ca_turn = Column(FLOAT(), default=0.0)  # 流动资产周转率
    fa_turn = Column(FLOAT(), default=0.0)  # 固定资产周转率
    assets_turn = Column(FLOAT(), default=0.0)  # 总资产周转率
    op_income = Column(FLOAT(), default=0.0)  # 经营活动净收益
    valuechange_income = Column(FLOAT(), default=0.0)  # 价值变动净收益
    interst_income = Column(FLOAT(), default=0.0)  # 利息费用
    daa = Column(FLOAT(), default=0.0)  # 折旧与摊销
    ebit = Column(FLOAT(), default=0.0)  # 息税前利润
    ebitda = Column(FLOAT(), default=0.0)  # 息税折旧摊销前利润
    fcff = Column(FLOAT(), default=0.0)  # 企业自由现金流量
    fcfe = Column(FLOAT(), default=0.0)  # 股权自由现金流量
    current_exint = Column(FLOAT(), default=0.0)  # 无息流动负债
    noncurrent_exint = Column(FLOAT(), default=0.0)  # 无息非流动负债
    interestdebt = Column(FLOAT(), default=0.0)  # 带息债务
    netdebt = Column(FLOAT(), default=0.0)  # 净债务
    tangible_asset = Column(FLOAT(), default=0.0)  # 有形资产
    working_capital = Column(FLOAT(), default=0.0)  # 营运资金
    networking_capital = Column(FLOAT(), default=0.0)  # 营运流动资本
    invest_capital = Column(FLOAT(), default=0.0)  # 全部投入资本
    retained_earnings = Column(FLOAT(), default=0.0)  # 留存收益
    diluted2_eps = Column(FLOAT(), default=0.0)  # 期末摊薄每股收益
    bps = Column(FLOAT(), default=0.0)  # 每股净资产
    ocfps = Column(FLOAT(), default=0.0)  # 每股经营活动产生的现金流量净额
    retainedps = Column(FLOAT(), default=0.0)  # 每股留存收益
    cfps = Column(FLOAT(), default=0.0)  # 每股现金流量净额
    ebit_ps = Column(FLOAT(), default=0.0)  # 每股息税前利润
    fcff_ps = Column(FLOAT(), default=0.0)  # 每股企业自由现金流量
    fcfe_ps = Column(FLOAT(), default=0.0)  # 每股股东自由现金流量
    netprofit_margin = Column(FLOAT(), default=0.0)  # 销售净利率
    grossprofit_margin = Column(FLOAT(), default=0.0)  # 销售毛利率
    cogs_of_sales = Column(FLOAT(), default=0.0)  # 销售成本率
    expense_of_sales = Column(FLOAT(), default=0.0)  # 销售期间费用率
    profit_to_gr = Column(FLOAT(), default=0.0)  # 净利润 / 营业总收入
    saleexp_to_gr = Column(FLOAT(), default=0.0)  # 销售费用 / 营业总收入
    adminexp_of_gr = Column(FLOAT(), default=0.0)  # 管理费用 / 营业总收入
    finaexp_of_gr = Column(FLOAT(), default=0.0)  # 财务费用 / 营业总收入
    impai_ttm = Column(FLOAT(), default=0.0)  # 资产减值损失 / 营业总收入
    gc_of_gr = Column(FLOAT(), default=0.0)  # 营业总成本 / 营业总收入
    op_of_gr = Column(FLOAT(), default=0.0)  # 营业利润 / 营业总收入
    ebit_of_gr = Column(FLOAT(), default=0.0)  # 息税前利润 / 营业总收入
    roe = Column(FLOAT(), default=0.0)  # 净资产收益率
    roe_waa = Column(FLOAT(), default=0.0)  # 加权平均净资产收益率
    roe_dt = Column(FLOAT(), default=0.0)  # 净资产收益率(扣除非经常损益)
    roa = Column(FLOAT(), default=0.0)  # 总资产报酬率
    npta = Column(FLOAT(), default=0.0)  # 总资产净利润
    roic = Column(FLOAT(), default=0.0)  # 投入资本回报率
    roe_yearly = Column(FLOAT(), default=0.0)  # 年化净资产收益率
    roa2_yearly = Column(FLOAT(), default=0.0)  # 年化总资产报酬率
    roe_avg = Column(FLOAT(), default=0.0)  # 平均净资产收益率(增发条件)
    opincome_of_ebt = Column(FLOAT(), default=0.0)  # 经营活动净收益 / 利润总额
    investincome_of_ebt = Column(FLOAT(), default=0.0)  # 价值变动净收益 / 利润总额
    n_op_profit_of_ebt = Column(FLOAT(), default=0.0)  # 营业外收支净额 / 利润总额
    tax_to_ebt = Column(FLOAT(), default=0.0)  # 所得税 / 利润总额
    dtprofit_to_profit = Column(FLOAT(), default=0.0)  # 扣除非经常损益后的净利润 / 净利润
    salescash_to_or = Column(FLOAT(), default=0.0)  # 销售商品提供劳务收到的现金 / 营业收入
    ocf_to_or = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 营业收入
    ocf_to_opincome = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 经营活动净收益
    capitalized_to_da = Column(FLOAT(), default=0.0)  # 资本支出 / 折旧和摊销
    debt_to_assets = Column(FLOAT(), default=0.0)  # 资产负债率
    assets_to_eqt = Column(FLOAT(), default=0.0)  # 权益乘数
    dp_assets_to_eqt = Column(FLOAT(), default=0.0)  # 权益乘数(杜邦分析)
    ca_to_assets = Column(FLOAT(), default=0.0)  # 流动资产 / 总资产
    nca_to_assets = Column(FLOAT(), default=0.0)  # 非流动资产 / 总资产
    tbassets_to_totalassets = Column(FLOAT(), default=0.0)  # 有形资产 / 总资产
    int_to_talcap = Column(FLOAT(), default=0.0)  # 带息债务 / 全部投入资本
    eqt_to_talcapital = Column(FLOAT(), default=0.0)  # 归属于母公司的股东权益 / 全部投入资本
    currentdebt_to_debt = Column(FLOAT(), default=0.0)  # 流动负债 / 负债合计
    longdeb_to_debt = Column(FLOAT(), default=0.0)  # 非流动负债 / 负债合计
    ocf_to_shortdebt = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 流动负债
    debt_to_eqt = Column(FLOAT(), default=0.0)  # 产权比率
    eqt_to_debt = Column(FLOAT(), default=0.0)  # 归属于母公司的股东权益 / 负债合计
    eqt_to_interestdebt = Column(FLOAT(), default=0.0)  # 归属于母公司的股东权益 / 带息债务
    tangibleasset_to_debt = Column(FLOAT(), default=0.0)  # 有形资产 / 负债合计
    tangasset_to_intdebt = Column(FLOAT(), default=0.0)  # 有形资产 / 带息债务
    tangibleasset_to_netdebt = Column(FLOAT(), default=0.0)  # 有形资产 / 净债务
    ocf_to_debt = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 负债合计
    ocf_to_interestdebt = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 带息债务
    ocf_to_netdebt = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额 / 净债务
    ebit_to_interest = Column(FLOAT(), default=0.0)  # 已获利息倍数(EBIT / 利息费用)
    longdebt_to_workingcapital = Column(FLOAT(), default=0.0)  # 长期债务与营运资金比率
    ebitda_to_debt = Column(FLOAT(), default=0.0)  # 息税折旧摊销前利润 / 负债合计
    turn_days = Column(FLOAT(), default=0.0)  # 营业周期
    roa_yearly = Column(FLOAT(), default=0.0)  # 年化总资产净利率
    roa_dp = Column(FLOAT(), default=0.0)  # 总资产净利率(杜邦分析)
    fixed_assets = Column(FLOAT(), default=0.0)  # 固定资产合计
    profit_prefin_exp = Column(FLOAT(), default=0.0)  # 扣除财务费用前营业利润
    non_op_profit = Column(FLOAT(), default=0.0)  # 非营业利润
    op_to_ebt = Column(FLOAT(), default=0.0)  # 营业利润／利润总额
    nop_to_ebt = Column(FLOAT(), default=0.0)  # 非营业利润／利润总额
    ocf_to_profit = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额／营业利润
    cash_to_liqdebt = Column(FLOAT(), default=0.0)  # 货币资金／流动负债
    cash_to_liqdebt_withinterest = Column(FLOAT(), default=0.0)  # 货币资金／带息流动负债
    op_to_liqdebt = Column(FLOAT(), default=0.0)  # 营业利润／流动负债
    op_to_debt = Column(FLOAT(), default=0.0)  # 营业利润／负债合计
    roic_yearly = Column(FLOAT(), default=0.0)  # 年化投入资本回报率
    profit_to_op = Column(FLOAT(), default=0.0)  # 利润总额／营业收入
    q_opincome = Column(FLOAT(), default=0.0)  # 经营活动单季度净收益
    q_investincome = Column(FLOAT(), default=0.0)  # 价值变动单季度净收益
    q_dtprofit = Column(FLOAT(), default=0.0)  # 扣除非经常损益后的单季度净利润
    q_eps = Column(FLOAT(), default=0.0)  # 每股收益(单季度)
    q_netprofit_margin = Column(FLOAT(), default=0.0)  # 销售净利率(单季度)
    q_gsprofit_margin = Column(FLOAT(), default=0.0)  # 销售毛利率(单季度)
    q_exp_to_sales = Column(FLOAT(), default=0.0)  # 销售期间费用率(单季度)
    q_profit_to_gr = Column(FLOAT(), default=0.0)  # 净利润／营业总收入(单季度)
    q_saleexp_to_gr = Column(FLOAT(), default=0.0)  # 销售费用／营业总收入(单季度)
    q_adminexp_to_gr = Column(FLOAT(), default=0.0)  # 管理费用／营业总收入(单季度)
    q_finaexp_to_gr = Column(FLOAT(), default=0.0)  # 财务费用／营业总收入(单季度)
    q_impair_to_gr_ttm = Column(FLOAT(), default=0.0)  # 资产减值损失／营业总收入(单季度)
    q_gc_to_gr = Column(FLOAT(), default=0.0)  # 营业总成本／营业总收入(单季度)
    q_op_to_gr = Column(FLOAT(), default=0.0)  # 营业利润／营业总收入(单季度)
    q_roe = Column(FLOAT(), default=0.0)  # 净资产收益率(单季度)
    q_dt_roe = Column(FLOAT(), default=0.0)  # 净资产单季度收益率(扣除非经常损益)
    q_npta = Column(FLOAT(), default=0.0)  # 总资产净利润(单季度)
    q_opincome_to_ebt = Column(FLOAT(), default=0.0)  # 经营活动净收益／利润总额(单季度)
    q_investincome_to_ebt = Column(FLOAT(), default=0.0)  # 价值变动净收益／利润总额(单季度)
    q_dtprofit_to_profit = Column(FLOAT(), default=0.0)  # 扣除非经常损益后的净利润／净利润(单季度)
    q_salescash_to_or = Column(FLOAT(), default=0.0)  # 销售商品提供劳务收到的现金／营业收入(单季度)
    q_ocf_to_sales = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额／营业收入(单季度)
    q_ocf_to_or = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额／经营活动净收益(单季度)
    basic_eps_yoy = Column(FLOAT(), default=0.0)  # 基本每股收益同比增长率( %)
    dt_eps_yoy = Column(FLOAT(), default=0.0)  # 稀释每股收益同比增长率( %)
    cfps_yoy = Column(FLOAT(), default=0.0)  # 每股经营活动产生的现金流量净额同比增长率( %)
    op_yoy = Column(FLOAT(), default=0.0)  # 营业利润同比增长率( %)
    ebt_yoy = Column(FLOAT(), default=0.0)  # 利润总额同比增长率( %)
    netprofit_yoy = Column(FLOAT(), default=0.0)  # 归属母公司股东的净利润同比增长率( %)
    dt_netprofit_yoy = Column(FLOAT(), default=0.0)  # 归属母公司股东的净利润 - 扣除非经常损益同比增长率( %)
    ocf_yoy = Column(FLOAT(), default=0.0)  # 经营活动产生的现金流量净额同比增长率( %)
    roe_yoy = Column(FLOAT(), default=0.0)  # 净资产收益率(摊薄) 同比增长率( %)
    bps_yoy = Column(FLOAT(), default=0.0)  # 每股净资产相对年初增长率( %)
    assets_yoy = Column(FLOAT(), default=0.0)  # 资产总计相对年初增长率( %)
    eqt_yoy = Column(FLOAT(), default=0.0)  # 归属母公司的股东权益相对年初增长率( %)
    tr_yoy = Column(FLOAT(), default=0.0)  # 营业总收入同比增长率( %)
    or_yoy = Column(FLOAT(), default=0.0)  # 营业收入同比增长率( %)
    q_gr_yoy = Column(FLOAT(), default=0.0)  # 营业总收入同比增长率( %)(单季度)
    q_gr_qoq = Column(FLOAT(), default=0.0)  # 营业总收入环比增长率( %)(单季度)
    q_sales_yoy = Column(FLOAT(), default=0.0)  # 营业收入同比增长率( %)(单季度)
    q_sales_qoq = Column(FLOAT(), default=0.0)  # 营业收入环比增长率( %)(单季度)
    q_op_yoy = Column(FLOAT(), default=0.0)  # 营业利润同比增长率( %)(单季度)
    q_op_qoq = Column(FLOAT(), default=0.0)  # 营业利润环比增长率( %)(单季度)
    q_profit_yoy = Column(FLOAT(), default=0.0)  # 净利润同比增长率( %)(单季度)
    q_profit_qoq = Column(FLOAT(), default=0.0)  # 净利润环比增长率( %)(单季度)
    q_netprofit_yoy = Column(FLOAT(), default=0.0)  # 归属母公司股东的净利润同比增长率( %)(单季度)
    q_netprofit_qoq = Column(FLOAT(), default=0.0)  # 归属母公司股东的净利润环比增长率( %)(单季度)
    equity_yoy = Column(FLOAT(), default=0.0)  # 净资产同比增长率
    rd_exp = Column(FLOAT(), default=0.0)  # 研发费用

