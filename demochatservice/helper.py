from flask import jsonify


def to_json(data, use_to_dict=True):
    if type(data) == list:
        if use_to_dict:
            return jsonify([m[0].to_dict() for m in data])
        else:
            return jsonify([m[0] for m in data])
    elif type(data) == tuple:
        if use_to_dict:
            return jsonify(data[0].to_dict())
        else:
            return jsonify(data[0])
    else:
        if use_to_dict:
            return jsonify(data.to_dict())
        else:
            return jsonify(data)

