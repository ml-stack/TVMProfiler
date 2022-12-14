from model_profiler.db import postgre_executor
from . import save_client
import psycopg2
from model_profiler.internal import record


class PostGreClient(save_client.SaveClient):
    """
    this class is used to provide crud api for actions
    """

    def __init__(self, database_name, user_name, password, host, port, model_record_table, op_record_table,
                 table_schema):
        """
        todo using config as the parameter
        :param database_name:
        :param user_name:
        :param password:
        :param host:
        :param port:
        :param model_record_table:
        :param op_record_table:
        :param table_schema:
        """
        self.executor = postgre_executor.PostGreExecutor(database_name, user_name, password, host, port)
        self.model_record_table = model_record_table
        self.op_record_table = op_record_table
        self.table_schema = table_schema
        self.op_record_table_columns = self.get_columns(op_record_table)
        self.model_record_table_columns = self.get_columns(model_record_table)

    def get_columns(self, table_name):
        """
        get columns of the table
        :return:
        """
        sql = "select string_agg(column_name,',') " \
              "from information_schema.columns " \
              "where table_schema='{}' and table_name='{}'" \
            .format(self.table_schema, table_name)
        columns_str = (self.executor.ExceQuery(sql))[0][0]
        columns = columns_str.split(",")
        return columns

    # @staticmethod
    # def new_exeucte_id():
    #     return uuid.uuid1(), time.time()

    def insert_model_record(self, model_record):
        if isinstance(model_record.start_time, float):
            model_record.start_time = psycopg2.TimestampFromTicks(model_record.start_time)
        sql = "INSERT INTO {}(execution_id, start_time, num_ops, model_name) " \
              "VALUES ('{}'::UUID, {}, '{}', '{}');".format(
            self.model_record_table,
            model_record.get("execution_id"),
            model_record.get("start_time"),
            model_record.get("num_ops"),
            model_record.get("model_name")
        )
        insert_res = self.executor.ExecNonQuery(sql) and self.insert_op_records(model_record.op_records)
        return insert_res

    def insert_op_record(self, op_record):

        """
        insert one record
        :param input_dict:
        :return:
        """
        if isinstance(op_record.node_start_time, float):
            op_record.node_start_time = psycopg2.TimestampFromTicks(op_record.node_start_time)
        sql = "INSERT INTO {}(execution_id , node_id, node_name, node_start_time, time_list, avg_time) \
        VALUES ('{}'::UUID, {}, '{}', {}, array{}, {});" \
            .format(
            self.op_record_table,
            op_record.get("execution_id"),
            op_record.get("node_id"),
            op_record.get("node_name"),
            op_record.get("node_start_time"),
            op_record.get("time_list"),
            op_record.get("avg_time")
        )
        return self.executor.ExecNonQuery(sql)

    def insert_op_records(self, op_records):
        num = len(op_records)
        sql = "INSERT INTO {}" \
              "(execution_id, node_id, node_name, node_start_time, time_list, avg_time) VALUES" \
            .format(self.op_record_table)
        for i in range(num):
            if isinstance(op_records[i].node_start_time, float):
                op_records[i].node_start_time = psycopg2.TimestampFromTicks(op_records[i].node_start_time)
            sql += " ('{}'::UUID, {}, '{}', {}, array{}, {})".format(
                op_records[i].get("execution_id"),
                op_records[i].get("node_id"),
                op_records[i].get("node_name"),
                op_records[i].get("node_start_time"),
                op_records[i].get("time_list"),
                op_records[i].get("avg_time")
            )
            if i < num - 1:
                sql += ","
            else:
                sql += ";"
        return self.executor.ExecNonQuery(sql)

    def query_by_execution_id(self, execution_id):
        """
        query by primary key(executor_id,
        :param execution_id: uuid
        :return:
        """
        sql = "SELECT * FROM {} WHERE execution_id='{}';".format(self.model_record_table, execution_id)
        query_result = self.executor.ExceQuery(sql)
        # todo len should be 1
        model_record = record.ModelRecord(**dict(zip(self.model_record_table_columns, query_result[0])))
        sql = "SELECT * FROM {} WHERE execution_id='{}';".format(self.op_record_table, execution_id)
        op_records = self.executor.ExceQuery(sql)
        for op_record in op_records:
            model_record.op_records.append(record.OPRecord(**dict(zip(self.op_record_table_columns, op_record))))
        # print(model_record)
        return model_record

    def delete_by_execution_id(self, execution_id):
        """
        delete all record of one execution
        :param execution_id: uuid
        :return:
        """
        sql = "DELETE FROM {} WHERE execution_id='{}';".format(self.op_record_table_columns, execution_id)
        res1 = self.executor.ExecNonQuery(sql)
        sql = "DELETE FROM {} WHERE execution_id='{}';".format(self.op_record_table, execution_id)
        res2 = self.executor.ExecNonQuery(sql)
        return res1 & res2

    def query_all_execution_ids(self):
        sql = "SELECT {} FROM {}".format("execution_id", self.model_record_table)
        execution_ids = self.executor.ExceQuery(sql)
        return [item[0] for item in execution_ids]
