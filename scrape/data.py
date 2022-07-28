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
            return self.to_str(x)
        if self.dtype == float:
            return self.to_float(x)
        if self.dtype == int:
            return self.to_int(x)
        if self.dtype == bool:
            return self.to_bool(x)
        if self.dtype == datetime.date:
            return self.to_date(x)
        if self.dtype == datetime.timedelta:
            return self.to_timedelta(x)
        if self.dtype == datetime.datetime:
            return self.to_datetime(x)
        raise Exception("unsupported dtype")

    @staticmethod
    def to_str(x):
        return str(x)

    @staticmethod
    def to_float(x):
        if not x:
            return np.nan
        return np.float64(x)

    @staticmethod
    def to_int(x):
        if not x:
            return np.nan
        return np.int64(x)

    @staticmethod
    def to_bool(x):
        if x:
            return True
        return False

    @staticmethod
    def to_date(x):
        if not x:
            return pd.NaT
        # assumes iso format
        return datetime.date.fromisoformat(x)

    @staticmethod
    def to_timedelta(x):
        if not x:
            return pd.NaT
        return ff1.utils.to_timedelta(x)

    @staticmethod
    def to_datetime(x):
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


def df_timedelta_to_string(row: pd.Series):
    for index, value in row.iteritems():
        if isinstance(value, datetime.timedelta):
            values = str(value).split(" ")
            if len(values) == 0:
                return ""
            value = values[-1]
            parts = value.split(".")

            if len(parts) == 0:
                return ""

            hours, minutes, seconds = parts[0].split(":")
            ms = None
            if len(parts) > 1:
                ms = parts[1]

            value = str(seconds)
            if minutes != "00" or minutes == "00" and hours != "00":
                value = f"{minutes}:{value}"
            if hours != "00":
                hours = hours.lstrip("0")
                value = f"{hours}:{value}"

            if ms:
                value = f"{value}.{ms[:3]}"
            row.at[index] = value
        elif isinstance(value, pd.Timedelta):
            print("hi")
    return row.astype(str)
