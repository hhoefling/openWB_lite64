#!/usr/bin/python3
import sys
import rct_lib
from rct_lib import rct_id
import time

# Author Heinz Hoefling
# Version 1.0 Okt.2021


# Entry point with parameter check
def main():
    start_time = time.time()
    rct_lib.init(sys.argv)

    clientsocket = rct_lib.connect_to_server()
    if clientsocket is not None:
        try:
            MyTab = []
            #           (self, msgid, idx, name, data_type, desc=''):
            MyTab.append(rct_id(0    ,  0,  '-----------------Gerät -------------------- ',0 ))
            rct_lib.add_by_name(MyTab, 'flash_param.erase_cycles')
            rct_lib.add_by_name(MyTab, 'flash_param.write_cycles')
            
            MyTab.append(rct_id(0    ,  0,  '-----------------Batterie-------------------- ',0 ))
            rct_lib.add_by_name(MyTab, 'battery.soc')
            rct_lib.add_by_name(MyTab, 'battery.efficiency')
            rct_lib.add_by_name(MyTab, 'acc_conv.i_acc_lp_fast')
            rct_lib.add_by_name(MyTab, 'battery.current')
            rct_lib.add_by_name(MyTab, 'battery.voltage')
            rct_lib.add_by_name(MyTab, 'power_mng.u_acc_lp')
            rct_lib.add_by_name(MyTab, 'power_mng.u_acc_mix_lp')
            rct_lib.add_by_name(MyTab, 'adc.u_acc')
            rct_lib.add_by_name(MyTab, 'g_sync.p_acc_lp')
            rct_lib.add_by_name(MyTab, 'energy.e_dc_total[0]')
            rct_lib.add_by_name(MyTab, 'energy.e_dc_total[1]')
            MyTab.append(rct_id(0    , 0,     '------------------- Panels A -----------------'))
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].p_dc')
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].p_dc_lp')
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].u_sg_lp')
            rct_lib.add_by_name(MyTab, 'g_sync.u_sg_avg[0]')
            MyTab.append(rct_id(0    , 0,     '----------------- Panels B --------------------'))
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].p_dc')
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].p_dc_lp')
            rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].u_sg_lp')
            rct_lib.add_by_name(MyTab, 'g_sync.u_sg_avg[1]')
            MyTab.append(rct_id(0         , 0,     '---------- WR/Netz/Haus Spannungen --------------'))
            rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[0]')
            rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[1]')
            rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[2]')
            MyTab.append(rct_id(0         , 0,     '----------------------- WR --------------------- '))
            rct_lib.add_by_name(MyTab, 'g_sync.i_dr_eff[0]')
            rct_lib.add_by_name(MyTab, 'g_sync.i_dr_eff[1]')
            rct_lib.add_by_name(MyTab, 'g_sync.i_dr_eff[2]')
            MyTab.append(rct_id(0         , 0,     '--------WR  3* U*I = Watt erzeugung des WR ------'))
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac[0]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac[1]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac[2]')
            MyTab.append(rct_id(0         , 0,     '--------------- HAUS Verbrauch --------------------'))
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_load[0]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_load[1]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_load[2]')
            MyTab.append(rct_id(0         , 0,     '--------------------- Netz ------------------' ))
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[0]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[1]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[2]')
            rct_lib.add_by_name(MyTab, 'g_sync.p_ac_grid_sum_lp')
            rct_lib.add_by_name(MyTab, 'grid_offset')
            rct_lib.add_by_name(MyTab, 'grid_pll[0].f')
            MyTab.append(rct_id(0         , 0,     '--------------------- ----- ------------------'))
            rct_lib.add_by_name(MyTab, 'nsm.p_limit')
            rct_lib.add_by_name(MyTab, 'buf_v_control.power_reduction_max_solar')
            rct_lib.add_by_name(MyTab, 'buf_v_control.power_reduction_max_solar_grid')

            rct_lib.add_by_name(MyTab, 'p_rec_lim[0]')
            rct_lib.add_by_name(MyTab, 'p_rec_lim[1]')
            rct_lib.add_by_name(MyTab, 'p_rec_lim[2]')
            
            

            MyTab.append(rct_id(0         , 0,     '--------------------- ----- ------------------'))

            rct_lib.add_by_name(MyTab, "db.temp1")
            rct_lib.add_by_name(MyTab, "db.temp2")
            rct_lib.add_by_name(MyTab, "battery.max_cell_temperature")
            rct_lib.add_by_name(MyTab, "battery.temperature")
            rct_lib.add_by_name(MyTab, "temperature.sink_temp_power_reduction")
            rct_lib.add_by_name(MyTab, "battery.min_cell_temperature")
            rct_lib.add_by_name(MyTab, "temperature.bat_temp_power_reduction")
            rct_lib.add_by_name(MyTab, "db.core_temp")

            MyTab.append(rct_id(0         , 0,     '--------------------- ----- ------------------'))

            # read via rct_id list
            response = rct_lib.read(clientsocket, MyTab)
            rct_lib.close(clientsocket)
            
            
            rct_lib.dbglog(response.format_list(time.time() - start_time))
                        
        except Exception as e:
            rct_lib.close(clientsocket)
            raise(e)

    sys.exit(0)
    

if __name__ == "__main__":
    main()
    

