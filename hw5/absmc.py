import ast

#static area
#[area_size, {ID: offset}]
static_area = [0,{}]

def g_scan_static():
    global static_area
    for cid in ast.classtable:
        cur_cls = ast.classtable[cid]
        for fieldname in cur_cls.fields:
            cur_field = cur_cls.fields[fieldname]
            if cur_field.storage == 'static':
                static_area[1].update({cur_field.id:static_area[0]})
                static_area[0] += 1






#class layouts
#{class_name, layout}
class_layouts = {}
#layout
#[size, {field_ID:offset}]


def g_obtain_cls_layouts():
    global class_layouts
    for cid in ast.classtable:
        cur_cls = ast.classtable[cid]
        cls_tree = get_cls_tree(cur_cls)
        layout = build_layout(cls_tree)
        class_layouts.update({cur_cls.name: layout})




def build_layout(cls_tree):
    ret = [0,{}]
    for cur_cls in cls_tree:
        f_list = cur_cls.fields
        for f_id in f_list:
            f = f_list[f_id]
            if(f.storage != "static"):
                ret[1].update({f.id:ret[0]})
                ret[0] += 1
    return ret



def get_cls_tree(input_class):
    ret = [input_class]
    while(input_class.superclass != None):
        ret.insert(0,input_class.superclass)
        input_class = input_class.superclass
    return ret



