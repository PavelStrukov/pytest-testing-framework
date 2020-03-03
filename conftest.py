import yaml

from defenitions import ROOT_DIR
from src.database_manager import DatabaseManager


def get_manager(manager_type=None):
    """configuring manager"""
    if manager_type is None:
        with open(str(ROOT_DIR) + "/configs/databaseconfig.yml", "r") as yml_file:
            dbcfg = yaml.load(yml_file, Loader=yaml.FullLoader)['mysql']
            manager = DatabaseManager([dbcfg['user'], dbcfg['password']], dbcfg['host'], dbcfg['port'], dbcfg['db'])
            return manager
    else:
        with open(str(ROOT_DIR) + "/configs/database_replication_config.yml", "r") as yml_file:
            db_cfg = yaml.load(yml_file, Loader=yaml.FullLoader)['mysql']
            if manager_type == "master":
                db_master_cfg = db_cfg['master']
            elif manager_type == "slave":
                db_master_cfg = db_cfg['slave']

            manager = DatabaseManager([db_master_cfg['user'], db_master_cfg['password']], db_master_cfg['host'],
                                      db_master_cfg['port'])
            return manager
