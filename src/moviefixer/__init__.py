'''
Created on 23 Apr 2022

@author: jackisback
'''
import datetime
import importlib
from itertools import count
import json
import logging, logging.config
from multiprocessing import Process, Event
from textwrap import indent
import time
import traceback

import moviefixer.configuration as conf
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error
from moviefixer.movielibrary import MovieLibrary
from moviefixer.task import Task


class Moviefixer:
    __configuration = []
    __task_registry = []
    __movie_library = {}
    __task_namespace = "moviefixer.task"
    __execution_start_time = time.time()
    
    def __init__(self, config_file, mode):
        conf.load_configuration(config_file, mode)
        
        logging.config.fileConfig(conf.getValue("log_config_file"))
        log_debug("#" * 120)
        log("Running (Mode='%s')...", mode)
        #log_debug("Config: " + json.dumps(conf.getConfig(), indent=2))
        
        self.__movie_library = MovieLibrary(db_file = conf.getValue("library_db"))
        self.__setup_task_registry()
        self.__runTasks()
        
        total_run = time.time() - self.__execution_start_time
        log("Done[%s].", datetime.timedelta(seconds=total_run))
    

    def __runTasks(self):
        interrupt_requested = False
        task_count = len(self.__task_registry)
        error_count = 0
        i = 0
        log("Running %s tasks...", task_count)
        
        while i < task_count:
            try:
                self.__runTask(i)
                i = i + 1
            except KeyboardInterrupt:
                interrupt_requested = True
                break
            except Exception as err:
                log_error('Task module error: %s', err)
                log_debug("Exception: %s", traceback.format_exc())
                error_count = error_count + 1
        
        if interrupt_requested:
            raise RuntimeError("User interrupt.")
        
        log("All tasks finished running (Errors: %s).", error_count)
    
    
    #===========================================================================
    # Use this: https://fedingo.com/how-to-stop-python-code-after-certain-amount-of-time/
    #===========================================================================
    def __runTask(self, task_index):
        task_item = self.__task_registry[task_index]
        task_count = len(self.__task_registry)
        run_count = task_index + 1
        max_process_time = conf.getValue("max_process_time", 3600)
        process_overtime_strategy = conf.getValue("process_overtime_strategy", "interrupt")

        task_name = task_item["task"]
        if ("name" in task_item):
            task_name = "{}({})".format(task_item["name"], task_item["task"])
            
        total_run = time.time() - self.__execution_start_time
        if total_run > max_process_time:
            log_warn("Skipping process %s - time is up!", task_name)
            return
        
        log("Running task[%s/%s]: %s", run_count, task_count, task_name)
        task_process = task_item["process"]
        task_process.start()
        
        while task_process.is_alive():
            task_process.join(timeout=1)
            if not task_process.is_alive():
                break
            
            total_run = time.time() - self.__execution_start_time
            #log("Process running[%s].", datetime.timedelta(seconds=total_run))
            if total_run > max_process_time:
                if process_overtime_strategy == "interrupt":
                    log_warn("Max process time(%ss) reached!", max_process_time)
                    log_warn("Interrupting process...")
                    task_process.terminate()
                elif process_overtime_strategy == "end_task":
                    stop_event = task_item["end_event"]
                    if not stop_event.is_set():
                        log_warn("Max process time(%ss) reached!", max_process_time)
                        log_warn("Requesting process to end...")
                        stop_event.set()
                    else:
                        log_warn("Waiting for process to end...")
                
        
        log("Task ended[%s].", datetime.timedelta(seconds=total_run))
        
    
    def __setup_task_registry(self):
        log("Setting up task registry...")

        task_list: list = conf.getValue("tasks")
        
        for task_item in task_list:
            task_name = task_item["task"]
            if ("name" in task_item):
                task_name = "{}({})".format(task_item["name"], task_item["task"])

            if not "enabled" in task_item or not task_item["enabled"]:
                log("Task(%s) is not enabled! Skipping.", task_name)
                continue
            
            # Get the Task instance
            try:
                task_class_filename = task_item["task"]
                task = self.get_task_class_instance(task_class_filename)
            except ModuleNotFoundError as err:
                log_warn("Task(%s) not found! %s Skipping.", task_name, err)
                continue
            except NotImplementedError as err:
                log_error("Bad Task(%s)! %s Skipping.", task_name, err)
                continue
            except RuntimeError as err:
                log_error(
                    "Task(%s) runtime error! %s Skipping.", task_name, err)
                continue
            
            # Configure the Task instance
            try:
                params = {}
                if "params" in task_item:
                    params = task_item["params"]
                task.configure(params)
            except Exception as err:
                log_error("Task(%s) configuration error! %s Skipping.", task_name, err)
                continue
            
            #task_item["instance"] = task
            task_item["process"] = Process(target=task.run)
            task_item["end_event"] = task.getStopEvent()
            self.__task_registry.append(task_item)

        #log_debug("Tasks registered: %s", self.__task_registry)
    
    def get_task_class_instance(self, module_name):
        module_name_ns = '{0}.{1}'.format(self.__task_namespace, module_name)

        try:
            module = importlib.import_module(module_name_ns)
        except ModuleNotFoundError as err:
            raise RuntimeError("Module load error! {}".format(err))

        task_class = None
        for obj in module.__dict__.values():
            if isinstance(obj, type) and issubclass(obj, Task) and obj != Task:
                task_class = obj
                break

        if not task_class:
            raise NotImplementedError("There is no subclass of Task class in module: {}".format(module_name_ns))

        try:
            stop_event = Event()
            # Create new task instance (inject dependencies)
            instance = task_class(library = self.__movie_library, stop_event = stop_event)
        except BaseException as err:
            raise RuntimeError("Instance creation error! {}".format(err))

        return instance
        
    def __getConfig(self, config_file, mode):
        f = open(config_file)
        data = json.load(f)
        f.close()
        return data[mode]
        
