#!/usr/bin/python3
import sys
import rct_lib2
import time

# Author Heinz Hoefling
# Version 1.0 Okt.2021

# Entry point with parameter check
def main():
    start_time = time.time()
    rct_lib2.init(sys.argv)

    clientsocket = rct_lib2.connect_to_server()
    if clientsocket is not None:
        try:
            # generate id list for fast bulk read
            MyTab = []
            HWDate    = rct_lib2.add_by_name(MyTab, 'flash_rtc.time_stamp_factory')
            pvVA      = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].u_sg_lp')
            pvVB      = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].u_sg_lp')
            pvPP      = rct_lib2.add_by_name(MyTab, 'buf_v_control.power_reduction_max_solar')
            pvPF      = rct_lib2.add_by_name(MyTab, 'buf_v_control.power_reduction_max_solar_grid')
            pvPR      = rct_lib2.add_by_name(MyTab, 'buf_v_control.power_reduction')

            pvWA      = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].p_dc_lp')
            pvWB      = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].p_dc_lp')
            pvWA2     = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].p_dc')
            pvWB2     = rct_lib2.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].p_dc')

            prim_sm   = rct_lib2.add_by_name(MyTab, 'prim_sm.state')



            pvEDA= rct_lib2.add_by_name(MyTab, 'energy.e_dc_day[0]')
            pvEDB= rct_lib2.add_by_name(MyTab, 'energy.e_dc_day[1]')
            pvEMA= rct_lib2.add_by_name(MyTab, 'energy.e_dc_month[0]')
            pvEMB= rct_lib2.add_by_name(MyTab, 'energy.e_dc_month[1]')
            pvEYA= rct_lib2.add_by_name(MyTab, 'energy.e_dc_year[0]')
            pvEYB= rct_lib2.add_by_name(MyTab, 'energy.e_dc_year[1]')
            pvETA= rct_lib2.add_by_name(MyTab, 'energy.e_dc_total[0]')
            pvETB= rct_lib2.add_by_name(MyTab, 'energy.e_dc_total[1]')

            flasherase= rct_lib2.add_by_name(MyTab, 'flash_param.erase_cycles')  # 0x96E32D11;550;rct_data.t_uint32;  ;Erase cycles of flash parameter                                                  ;4;
            flashwrite= rct_lib2.add_by_name(MyTab, 'flash_param.write_cycles' ) # 0x46892579;240;rct_data.t_uint32;  ;Write cycles of flash parameters                                                 ;67;
            flashresult=rct_lib2.add_by_name(MyTab, 'flash_result')              # 0xE63A3529;802;rct_data.t_uint16;  ;Flash result

    
            tc =  rct_lib2.add_by_name(MyTab,'db.core_temp') # 0xC24E85D0, 688, "db.core_temp",rct_data.t_float,   "Core temperature [C]"))
            t1 =  rct_lib2.add_by_name(MyTab, 'db.temp1')  # (0xF79D41D9, 862, "db.temp1", rct_data.t_float,   "Heat sink temperature [C]"))
            t2 =  rct_lib2.add_by_name(MyTab, 'db.temp2')  # (0x4F735D10, 276, "db.temp2", rct_data.t_float,   "Heat sink (battery actuator) temperature [C]"))
            t1max = rct_lib2.add_by_name(MyTab,'temperature.sink_temp_power_reduction')  # 0x90B53336, 520, "temperature.sink_temp_power_reduction", rct_data.t_float,   "Heat sink temperature target [C]"))
            t2max = rct_lib2.add_by_name(MyTab,'temperature.bat_temp_power_reduction')    # 0xA7447FC4, 595, "temperature.bat_temp_power_reduction", rct_data.t_float,   "Battery actuator temperature target [C]"))

            # read parameters
            response = rct_lib2.read(clientsocket, MyTab)
            rct_lib2.close(clientsocket)

            # output all response elements
            rct_lib2.dbglog("Overall access time: {:.3f} seconds".format(time.time() - start_time))

            rct_lib2.dbglog("<small>")
            rct_lib2.dbglog(rct_lib2.format_list(response))
            rct_lib2.dbglog("</small>")

            print( "Production date      : " + str(HWDate.value))

            prim_sm=  int(prim_sm.value * 100.0) / 100.0
            prim_sms= ''
            if( prim_sm == 0 ):
                prim_sms='Standby'
            if( prim_sm == 1 ):
                prim_sms='Initialization'
            if( prim_sm == 2 ):
                prim_sms='Standby'
            if( prim_sm == 3 ):
                prim_sms='Efficiency'
            if( prim_sm == 4 ):
                prim_sms='Insulation check'
            if( prim_sm == 5 ):
                prim_sms='Island check'
            if( prim_sm == 6 ):
                prim_sms='Power check'
            if( prim_sm == 7 ):
                prim_sms='Symmetry'
            if( prim_sm == 8 ):
                prim_sms='Relais test'
            if( prim_sm == 9 ):
                prim_sms='Grid passive'
            if( prim_sm == 10 ):
                prim_sms='Prepare Bat Passive'
            if( prim_sm == 11 ):
                prim_sms='Battery Passive'
            if( prim_sm == 12 ):
                prim_sms='H/W check'
            if( prim_sm == 13 ):
                prim_sms='Feed in'
            print("Primary Status       : "+ str(prim_sm) + ' [' + str(prim_sms) + ']' )

            AV =  int(pvVA.value * 100.0) / 100.0
            print( "PV String A          : " + str(AV) + ' V')
            AW =  int(pvWA.value)#  * 100.0) / 100.0
            AW2 =  int(pvWA2.value)#  * 100.0) / 100.0
            print( "PV String A          : " + str(AW) + ' W (' + str(AW2) + ' W)')
            EDA =  int(pvEDA.value) / 1000.0
            print( "PV String A Day      : " + str(EDA) + ' kWh')
            EMA =  int(pvEMA.value) / 1000.0
            print( "PV String A Month    : " + str(EMA) + ' kWh')
            EYA =  int(pvEYA.value) / 1000.0
            print( "PV String A Year     : " + str(EYA) + ' kWh')
            ETA =  int(pvETA.value) / 1000.0
            print( "PV String A Total    : " + str(ETA) + ' kWh')


            BV =  int(pvVB.value * 100.0) / 100.0
            print( "PV String B          : " + str(BV) + ' V')
            BW =  int(pvWB.value)#  * 100.0) / 100.0
            BW2 = int(pvWB2.value)#  * 100.0) / 100.0
            print( "PV String B          : " + str(BW) + ' W (' + str(BW2) + ' W)')
            EDB =  int(pvEDB.value) / 1000.0
            print( "PV String B Day      : " + str(EDB) + ' kWh')
            EMB =  int(pvEMB.value) / 1000.0
            print( "PV String B Month    : " + str(EMB) + ' kWh')
            EYB =  int(pvEYB.value) / 1000.0
            print( "PV String B Year     : " + str(EYB) + ' kWh')
            ETB =  int(pvETB.value) / 1000.0
            print( "PV String B Total    : " + str(ETB) + ' kWh')


            print ( '<hr>')

            print( "PV Peek Power        : " + str(pvPP.value) + ' W')
            PR = int( (pvPR.value+0.0049999) * 100.0) 
            print( "PV max Feed Power    : " + str(pvPF.value) + ' W, Reduced to ' + str(PR) + '%')

            print ( '<hr>')
            print( "Flash cyles          : Erase:" + str(flasherase.value) + ' Write:' + str(flashwrite.value) + ' Result:' + str(flashresult.value))

            print ( '<hr>')

            tc =  int(tc.value * 100) / 100.0
            t1 =  int(t1.value * 100) / 100.0
            t2 =  int(t2.value * 100) / 100.0
            t1max =  int(t1max.value * 100) / 100.0
            t2max =  int(t2max.value * 100) / 100.0
            print( "Core Temp.           : "  + str(tc) + ' Grad ')
            print( "Heat sink            : "  + str(t1) + ' Grad (reduce over:' + str(t1max) + ' Grad )'  )
            print( "Heat sink (Batterie) : "  + str(t2) + ' Grad (reduce over:' + str(t2max) + ' Grad )'  )

        except Exception as e:
            rct_lib2.close(clientsocket)
            raise(e)
            
    sys.exit(0)

if __name__ == "__main__":
    main()
    
