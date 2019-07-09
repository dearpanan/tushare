#!/usr/bin/python
# coding=utf-8

import os
import configparser
import traceback
from comm.utils import ProjectUtil
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy import create_engine


DEFAULT_CONFIG_FILE = './db.ini'


class MySession(object):
    my_db = None
    mylogger = ProjectUtil.get_project_logger('stock_db')
    db_engine_str = dict()
    db_session = dict()
    db_engine = dict()

    # 构造函数
    def __init__(self):
        pass

    # 析构函数
    def __del__(self):
        for session in self.db_session.values():
            self._close_saving_session(session)

    # 重载operator[]运算符
    def __getitem__(self, item):
        return self.get_session(item)

    # 解析mysql的配置文件，并保存配置
    def init(self, config_file=DEFAULT_CONFIG_FILE):
        try:
            # 读取配置文件
            source_dir = os.getcwd()
            conf_path = os.path.split(os.path.realpath(__file__))[0]
            os.chdir(conf_path)
            config = configparser.ConfigParser()
            config.read(config_file)
            os.chdir(source_dir)
            # 解析common信息
            common_item = dict(config.items('common'))
            # 解析数据库地址
            host_count = int(common_item['host_count'])
            for i in range(1, host_count + 1):
                host_item = dict(config.items('host%d' % i))
                db_name_list = host_item['db']
                # 测试每一个连接
                for db_name in db_name_list.split(','):
                    engine_format = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8&use_unicode=1"
                    engine_str = engine_format % (host_item['user'],
                                                  host_item['passwd'],
                                                  host_item['ip'],
                                                  host_item['port'],
                                                  db_name)
                    # 测试连接
                    try:
                        engine = create_engine(engine_str)
                        conn = engine.connect()
                        conn.close()
                        engine.dispose()
                        # 保存连接字符串
                        self.db_engine_str[db_name] = engine_str
                    except:
                        self.mylogger.error(traceback.format_exc())
                        print(traceback.format_exc())
            self.mylogger.info(self.db_engine_str)
            return True
        except:
            self.mylogger.error(traceback.format_exc())
            return False

    # 获取session
    def session(self, db_name):
        return self.get_session(db_name)

    # 获取session
    def get_session(self, db_name):
        try:
            # 直接取出已经创建好的session
            if db_name in self.db_session:
                session = self.db_session[db_name]
                engine = self.db_engine[db_name]
                return session, engine
            # 创建新session
            session, engine = self._create_saving_session(db_name)
            return session, engine
        except:
            self.mylogger.error(traceback.format_exc())
            return None, None

    # 创建并保存session
    def _create_saving_session(self, db_name):
        try:
            if db_name not in self.db_engine_str:
                self.mylogger.error("db_name[%s] does not have engine_str" % db_name)
                return None, None
            engine_str = self.db_engine_str[db_name]
            engine = create_engine(engine_str)
            self.db_engine[db_name] = engine
            # session = Session(bind=engine, autocommit=True)
            session = scoped_session(sessionmaker(bind=engine))
            _session = session()
            self.db_session[db_name] = _session
            return _session, engine
        except:
            self.mylogger.error(traceback.format_exc())
            return None, None

    # 关闭已保存的session
    def _close_saving_session(self, db_name):
        try:
            if db_name in self.db_session:
                session = self.db_session[db_name]
                session.close()
            if db_name in self.db_engine:
                engine = self.db_engine[db_name]
                engine.dispose()
            return True
        except:
            self.mylogger.error(traceback.format_exc())
            return None

    # 超时重连调用
    def re_connect_session(self):
        try:
            for session in self.db_session.values():
                self._close_saving_session(session)
            self.db_session = dict()
        except:
            self.mylogger.error(traceback.format_exc())

    # 创建野session(不保存)
    def create_wild_session(self, db_name):
        try:
            if db_name not in self.db_engine_str:
                self.mylogger.error("db_name[%s] does not have engine_str" % db_name)
                return None, None
            engine_str = self.db_engine_str[db_name]
            engine = create_engine(engine_str)
            session = Session(bind=engine, autocommit=False)
            return session, engine
        except:
            self.mylogger.error(traceback.format_exc())
            return None, None

    # 关闭野session
    @classmethod
    def close_wild_session(cls, session):
        try:
            if session:
                engine = session.get_bind()
                session.close()
                engine.dispose()
            return True
        except:
            cls.mylogger.error(traceback.format_exc())
            return False

    @classmethod
    def get_db_session(cls, db):
        try:
            if cls.my_db is None:
                cls.my_db = MySession()
                cls.my_db.init()
            return cls.my_db.get_session(db)
        except:
            cls.mylogger.error("can't get session of {}".format(db))
            cls.mylogger.error(traceback.format_exc())
            return None, None

    @classmethod
    def get_wild_session(cls, db):
        try:
            if cls.my_db is None:
                cls.my_db = MySession()
                cls.my_db.init()
            return cls.my_db.create_wild_session(db)
        except:
            cls.mylogger.error(traceback.format_exc())
            return None, None

    @classmethod
    def create_all_tables(self, basecls):
        try:
            basecls.metadata.create_all(self.engine)
            self.session.commit()
            return True
        except SQLAlchemyError:
            self.logger.error(traceback.format_exc())
            return False
