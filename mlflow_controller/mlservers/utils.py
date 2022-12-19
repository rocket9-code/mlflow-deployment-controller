import json


def mlflow_model_search(lookup_key, json_dict, search_result=[]):
    if type(json_dict) == dict:
        for key, value in json_dict.items():
            if key == lookup_key:
                search_result.append(value)
            mlflow_model_search(lookup_key, value, search_result)
    elif type(json_dict) == list:
        for element in json_dict:
            mlflow_model_search(lookup_key, element, search_result)
    return search_result


def update_modeluris(json_para, search_para, replace_para):
    def decode_dict(a_dict):
        if search_para in a_dict.values():
            for key, value in a_dict.items():
                if value == search_para:
                    a_dict[key] = replace_para
        return a_dict

    return json.loads(json.dumps(json_para), object_hook=decode_dict)
