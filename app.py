#  -*- coding: utf-8 -*-
import json
from multiprocessing.dummy import Pool as ThreadPool

from avito import grab as avito_grab
from youla import grab as youla_grab


def grab(task):
    print(task)
    if task["module"] == "avito":
        avito_grab(task)
    elif task["module"] == "youla":
        youla_grab(task)
    else:
        print("Module {} not found.".format(task["module"]))


with open("config.json", mode="r", encoding="utf-8") as f:
    configurationStr = f.read()
# Загружаем файл конфигурации
configuration = json.loads(configurationStr)
tasks = configuration['tasks']

# Готовим пул
pool = ThreadPool(configuration["threadCount"])
pool.map(grab, tasks)
pool.close()
pool.join()
