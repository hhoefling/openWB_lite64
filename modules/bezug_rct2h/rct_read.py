#!/usr/bin/python3
import sys
import rct_lib
from rct_lib import rct_id
from rct_lib import rct_data
import fnmatch
import time


# Entry point with parameter check
def main():
    start_time = time.time()
    rct_lib.init(sys.argv)

    clientsocket = rct_lib.connect_to_server()
    if clientsocket is not None:
        fmt = '#0x{:08X};{:6};{:20};{:'+str(rct_lib.param_len)+'};{:'+str(rct_lib.desc_len)+'};{};'
        for obj in rct_lib.id_tab:
            if rct_lib.search_id > 0 and obj.id != rct_lib.search_id:
                #rct_lib.dbglog( obj.id, obj.name)
                continue
            
            if rct_lib.search_name is not None and ( fnmatch.fnmatch(obj.name, rct_lib.search_name) == False) and  (fnmatch.fnmatch(obj.desc, rct_lib.search_name) ) == False:
                continue
            
            value = rct_lib.read(clientsocket, obj.id)
            if obj.data_type == rct_data.t_bool:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_uint8:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_int8:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_uint16:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_int16:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_uint32:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_int32:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_enum:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            elif obj.data_type == rct_data.t_float:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  str(obj.value).replace('.',',') ))
            elif obj.data_type == rct_data.t_string:
                print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  "'"+str(obj.value)+"'" ))
            elif obj.data_type == rct_data.t_log_ts:
               print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  str(obj.value) ))
            elif obj.data_type == rct_data.t_dump:
               print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))
            else:
               print(fmt.format(obj.id, obj.idx, obj.data_type, obj.name, obj.desc,  obj.value ))

#            if rct_lib.dbglog(fmt.format(obj.id, obj.idx, obj.name, obj.desc,  obj.value )) == False:
#                print( "Value:" , value)

        rct_lib.close(clientsocket)

    sys.exit(0)
    
if __name__ == "__main__":
    main()
