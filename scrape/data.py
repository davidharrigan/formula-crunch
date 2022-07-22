import datetime
import re

import pandas as pd
import numpy as np
import fastf1 as ff1


class DataMapping:
    def __init__(self, column: str, dtype: type = str):
        self.column = column
        self.dtype = dtype

    def transform(self, x):
        if self.dtype == str:
            return self.__str(x)
        if self.dtype == float:
            return self.__float(x)
        if self.dtype == int:
            return self.__int(x)
        if self.dtype == bool:
            return self.__bool(x)
        if self.dtype == datetime.date:
            return self.__date(x)
        if self.dtype == datetime.timedelta:
            return self.__timedelta(x)
        if self.dtype == datetime.datetime:
            return self.__datetime(x)
        raise Exception("unsupported dtype")

    @staticmethod
    def __str(x):
        return str(x)

    @staticmethod
    def __float(x):
        if not x:
            return np.nan
        return np.float64(x)

    @staticmethod
    def __int(x):
        if not x:
            return np.nan
        return np.int64(x)

    @staticmethod
    def __bool(x):
        if x:
            return pd.Series(True, dtype=bool)
        return pd.Series(False, dtype=bool)

    @staticmethod
    def __date(x):
        if not x:
            return pd.NaT
        # assumes iso format
        return datetime.date.fromisoformat(x)

    @staticmethod
    def __timedelta(x):
        if not x:
            return pd.NaT
        return ff1.utils.to_timedelta(x)

    @staticmethod
    def __datetime(x):
        if not x:
            return pd.NaT
        return ff1.utils.to_datetime(x)


def flatten(mydict: dict, sep="."):
    new_dict = {}
    for key, value in mydict.items():
        if isinstance(value, dict):
            _dict = {sep.join([key, _key]): _value for _key, _value in flatten(value).items()}
            new_dict.update(_dict)
        elif isinstance(value, list):
            _dict = {}
            for i, v in enumerate(value):
                if isinstance(v, dict):
                    _dict.update(
                        {
                            sep.join([key, f"[{i}]", _key]): _value
                            for _key, _value in flatten(v).items()
                        }
                    )
                else:
                    _dict.update({sep.join([key, f"[{i}]"]): v})
            new_dict.update(_dict)
        else:
            new_dict[key] = value
    return new_dict


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def to_db_fields(data: pd.Series) -> dict:
    ret = {}
    for k, v in data.items():
        value = v
        if "numpy" in str(type(v)):
            value = value.item()
        ret[camel_to_snake(k)] = value
    return ret


def get_one_from_df(df: pd.DataFrame, query: str) -> pd.Series:
    selected = df.query(query)
    if len(selected) != 1:
        raise Exception(f"expected only 1 result from the query, got {len(selected)}")
    return selected.iloc[0]
