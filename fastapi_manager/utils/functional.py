from fastapi_manager.db.base import BaseTable


def compare_2_dicts(dict1: dict, dict2: dict):
    for key in dict2:
        if key not in dict1 or dict1[key] != dict2[key]:
            dict1[key] = dict2[key]
    return dict1


def compare_instance_2_dict(instance: BaseTable, dict1: dict):
    for key in dict1:
        if key not in instance.__dict__:
            raise Exception(f"{instance} does not have column with name '{key}'")
        if instance.__dict__[key] != dict1[key]:
            instance.__dict__[key] = dict1[key]
    return instance
