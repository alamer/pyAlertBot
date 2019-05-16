#  -*- coding: utf-8 -*-
import json
import sys
from multiprocessing.dummy import Pool as ThreadPool

from avito import Avito
from youla import Youla


def grab(task):
    print(task)
    if task["module"] == "avito":
        avito = Avito(task)
        avito.grab()
    elif task["module"] == "youla":
        youla =Youla(task)
        youla.grab()
    else:
        print("Module {} not found.".format(task["module"]))


if len(sys.argv) == 1:
    print("Configuration file not provided")
    quit()
configuration_file = sys.argv[1]
print("Configuration file: {}".format(configuration_file))
with open(configuration_file, mode="r", encoding="utf-8") as f:
    configurationStr = f.read()
# Загружаем файл конфигурации
configuration = json.loads(configurationStr)
tasks = configuration['tasks']

# Готовим пул
pool = ThreadPool(configuration["threadCount"])
pool.map(grab, tasks)
pool.close()
pool.join()
