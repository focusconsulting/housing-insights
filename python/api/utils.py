def objects_divide(numerator_data, denominator_data):
    """
    Divides objects in the numerator by objects in the denominator by matching
    the appropriate groupings.

    Takes data that is formatted for output the API, i.e. a dictionary
    with key "objects", which contains a list of dictionaries each with 'grouping'
    and 'count'
    """
    objects = []
    if numerator_data["objects"] == None:
        objects = None
    else:
        for n in numerator_data["objects"]:
            # TODO what should we do when a matching obj isn't found?
            matching_d = next(
                (
                    obj
                    for obj in denominator_data["objects"]
                    if obj["group"] == n["group"]
                ),
                {"group": "_unknown", "count": None},
            )
            if matching_d["count"] == None or n["count"] == None:
                divided = None
            else:
                divided = n["count"] / matching_d["count"]

            obj = dict(
                {"group": n["group"], "count": divided}
            )  # TODO here and elsewhere need to change 'count' to 'value' for clarity, but need to fix front end to expect this first
            objects.append(obj)

    return {
        "objects": objects,
        "grouping": numerator_data["grouping"],
        "data_id": numerator_data["grouping"],
    }


def get_zone_facts_select_columns(engine):
    conn = engine.connect()
    proxy = conn.execute(
        "select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='zone_facts'"
    )
    zcolumns = [x[0] for x in proxy.fetchall()]

    ward_selects = ""
    cluster_selects = ""
    tract_selects = ""

    for c in zcolumns:
        ward_selects += ",z1." + c + " AS " + c + "_ward"
        cluster_selects += ",z2." + c + " AS " + c + "_neighborhood_cluster"
        tract_selects += ",z3." + c + " AS " + c + "_census_tract"

    return (ward_selects, cluster_selects, tract_selects)
