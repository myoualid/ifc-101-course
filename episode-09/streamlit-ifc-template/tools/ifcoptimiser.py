import ifcopenshell
from toposort import toposort_flatten as toposort

def optimise(file):
    def generate_instances_and_references():
        """
        Generator which yields an entity id and 
        the set of all of its references contained in its attributes. 
        """
        for inst in f:
            yield inst.id(), set(i.id() for i in f.traverse(inst)[1:] if i.id())

    def map_value(v):
        """
        Recursive function which replicates an entity instance, with 
        its attributes, mapping references to already registered
        instances. Indeed, because of the toposort we know that 
        forward attribute value instances are mapped before the instances
        that reference them.
        """
        if isinstance(v, (list, tuple)):
            # lists are recursively traversed
            return type(v)(map(map_value, v))
        elif isinstance(v, ifcopenshell.entity_instance):
            if v.id() == 0:
                # express simple types are not part of the toposort and just copied
                return g.create_entity(v.is_a(), v[0])
            return instance_mapping[v]
        else:
            # a plain python value can just be returned
            return v

    f = file
    g = ifcopenshell.file(schema=f.schema)
       
    instance_mapping = {}
    info_to_id = {}
    for id in toposort(dict(generate_instances_and_references())):
        inst = f[id]
        info = inst.get_info(include_identifier=False, recursive=True, return_type=frozenset)
        if info in info_to_id:
            mapped = instance_mapping[inst] = instance_mapping[f[info_to_id[info]]]
        else:
            try:
                info_to_id[info] = id
                print(id)
                instance_mapping[inst] = g.create_entity(
                    inst.is_a(),
                    *map(map_value, inst)
                )
            except:
                pass
    return g