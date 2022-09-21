import json


class OPRecord:
    """
    this class is used to describe a operator's executing record
    """

    def __init__(self, execution_id, node_id, node_start_time, node_name, time_list, avg_time):
        self.execution_id = execution_id
        self.node_id = node_id
        self.node_start_time = node_start_time
        self.node_name = node_name
        self.time_list = time_list
        self.avg_time = avg_time

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self, item):
        return self.__dict__[item]



class ModelRecord:
    """
    this class is using to describe a model's inference record
    """

    def __init__(self, execution_id, start_time, num_ops, model_name):
        self.execution_id = execution_id
        self.start_time = start_time
        self.num_ops = num_ops
        self.model_name = model_name
        self.op_records = []

    def add_op_record(self, op_record):
        self.op_records = self.op_records.append(op_record)

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def get(self, key):
        return self.__getitem__(key)

    def __getitem__(self, item):
        return self.__dict__[item]

    def getInsertFormat(self):
        return "VALUE(')"