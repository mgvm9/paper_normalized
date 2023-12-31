
from implicit_data import ImplicitData
from BISGD import BISGD
from ISGD import ISGD
from LocalUBISGD import LocalUBISGD
from Model import Model
from RAISGD import RAISGD
from UBISGD import UBISGD
from UserKNN import UserKNN
from Model import Model
import numpy as np
import pandas as pd
import time
import random

class EvalPrequential:

    def __init__(self, model: Model, data: ImplicitData, metrics = ["Recall@20"], seed: int = None):
        # TODO: Input checks
        self.model = model
        self.data = data
        self.metrics = metrics
        self.seed = seed


    def EvaluateTime(self, start_eval = 0, count = 0, interleaved = 1):
        results = dict()
        time_get_tuple = []
        time_recommend = []
        time_eval_point = []
        time_update = []
        random.seed(self.seed)

        if not count:
            count = self.data.size

        count = min(count, self.data.size)

        for metric in self.metrics:
            results[metric] = []

        for i in range(count):
            start_get_tuple = time.time()
            uid, iid = self.data.GetTuple(i)
            end_get_tuple = time.time()
            time_get_tuple.append(end_get_tuple - start_get_tuple)

            if i >= start_eval and random.random() <= 1/interleaved and i>100:
                #print("First If")
                #print("This is iid")
                #print(int(iid))
                #print("\n")
                #print(self.model.data.GetUserItems(uid, False))
                #if int(iid) not in self.model.data.GetUserItems(uid, False):
                start_recommend = time.time()
                reclist = self.model.Recommend(uid, 20)
                #print("I got here")
                #print(uid)
                #print(reclist)
                end_recommend = time.time()
                time_recommend.append(end_recommend - start_recommend)

                start_eval_point = time.time()
                results[metric].append(self.__EvalPoint(iid, reclist))
                #print(results[metric])
                end_eval_point = time.time()
                time_eval_point.append(end_eval_point - start_eval_point)

            start_update = time.time()
            self.model.IncrTrain(uid, iid)
            end_update = time.time()
            time_update.append(end_update - start_update)

        results['time_get_tuple'] = time_get_tuple
        results['time_recommend'] = time_recommend
        results['time_eval_point'] = time_eval_point
        results['time_update'] = time_update

        return results

    def Evaluate(self, start_eval = 0, count = 0, interleaved = 1):
        results = dict()

        if not count:
            count = self.data.size

        count = min(count, self.data.size)

        for metric in self.metrics:
            results[metric] = []

        for i in range(count):
            uid, iid = self.data.GetTuple(i)
            if i >= start_eval and random.random() <= 1/interleaved and i>100:
                reclist = self.model.Recommend(uid)
                results[metric].append(self.__EvalPoint(iid, reclist))
            self.model.IncrTrain(uid, iid)

        return results

    def __EvalPoint(self, item_id, reclist):
        result = 0
        
        if len(reclist) == 0:
            return 0
        for metric in self.metrics:
            #print("i got here")
            if metric == "Recall@20":
                #print(reclist)
                #print(int(item_id))
                #print([int(x) for x in reclist[:20,0]])
                result = int(item_id in [x for x in reclist[:20,0]])
                #print(result)
        return result
