#!/usr/bin/python3
import sys
import os
import rct_lib
# import fnmatch
import time


# Author Heinz Hoefling
# Version 1.1 Okt.2023
# Fragt die Werte gebuendelt ab, nicht mit einer Connection je Wert
#


#
# Schreib und logge einen Wert in die Ramdisk
# if Same , no write, no mtime update
#
def writeRam(fn, val, rctname):
    fnn = "/var/www/html/openWB/ramdisk/" + str(fn)
    try:
        f = open(fnn, 'r')
        oldv = (f.read()).strip()
        f.close()
    except Exception as e:
        oldv = ""
        rct_lib.errlog(e)
        rct_lib.dbglog(e)

    if(str(oldv) != str(val)):
        if rct_lib.bVerbose is True:
            rct_lib.dbglog("RCT field " + str(fn) + " newval:[" + str(val) + "] oldval:[" + str(oldv) + "] " + str(rctname))
        f = open(fnn, 'w')
        f.write(str(val))
        f.close()
    else:
        if rct_lib.bVerbose is True:
            rct_lib.dbglog("RCT Same field " + str(fn) + " [" + str(val) + "] " + str(rctname))


# Entry point with parameter check
def main():
    start_time = time.time()
    rct_lib.init(sys.argv)
    rct_lib.dbglog("RCT bInfo=", str(rct_lib.bInfo))
    rct_lib.dbglog("RCT bVerbose", str(rct_lib.bVerbose))
    rct_lib.dbglog("RCT EVU bb=", str(rct_lib.bb))
    rct_lib.dbglog("RCT WR  wr=", str(rct_lib.wr))
    rct_lib.dbglog("RCT BAT sp=", str(rct_lib.sp))
    rct_lib.dbglog('RCT 5M  bm5 ', str(rct_lib.bm5), " get all counter only every 5 minutes")
    clientsocket = rct_lib.connect_to_server()
    if clientsocket is not None:
        try:
            MyTab = []
            #  Bezug ###########################
            if rct_lib.bb:
                p_ac_sc_sum = rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc_sum')
                volt1 = rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[0]')
                volt2 = rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[1]')
                volt3 = rct_lib.add_by_name(MyTab, 'g_sync.u_l_rms[2]')
                watt1 = rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[0]')
                watt2 = rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[1]')
                watt3 = rct_lib.add_by_name(MyTab, 'g_sync.p_ac_sc[2]')
                freq = rct_lib.add_by_name(MyTab, 'grid_pll[0].f')
                stat1 = rct_lib.add_by_name(MyTab, 'fault[0].flt')
                stat2 = rct_lib.add_by_name(MyTab, 'fault[1].flt')
                stat3 = rct_lib.add_by_name(MyTab, 'fault[2].flt')
                stat4 = rct_lib.add_by_name(MyTab, 'fault[3].flt')
            #  WR ###########################
            if rct_lib.wr:
                pv1watt = rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[0].p_dc')
                pv2watt = rct_lib.add_by_name(MyTab, 'dc_conv.dc_conv_struct[1].p_dc')
                pvEwatt = rct_lib.add_by_name(MyTab, 'io_board.s0_external_power')
            #  BAT ###########################
            if rct_lib.sp:
                bsocx = rct_lib.add_by_name(MyTab, 'battery.soc')
                bsocsoll = rct_lib.add_by_name(MyTab, 'battery.soc_target')
                bwatt1 = rct_lib.add_by_name(MyTab, 'g_sync.p_acc_lp')
                bstat1 = rct_lib.add_by_name(MyTab, 'battery.bat_status')
                bstat2 = rct_lib.add_by_name(MyTab, 'battery.status')
                bstat3 = rct_lib.add_by_name(MyTab, 'battery.status2')
                # pmngsocmax = rct_lib.add_by_name(MyTab, 'power_mng.soc_max')
                # 0xC642B9D6 acc_conv.i_discharge_max 20.0
                discharge_max = rct_lib.add_by_name(MyTab, 'acc_conv.i_discharge_max')
                loadWatt = rct_lib.add_by_name(MyTab, 'power_mng.soc_charge_power')


################################
            # read via rct_id list
            response = rct_lib.read(clientsocket, MyTab)
            rct_lib.close(clientsocket)

            # output all response elements
            rct_lib.infolog(rct_lib.format_list(response))
            rct_lib.dbglog("RCT Overall connetion time: {:.3f} seconds".format(time.time() - start_time))
        except Exception as e:
            rct_lib.close(clientsocket)
            raise(e)
###################################

# Werte weckpacken
        if rct_lib.bb:
            p_ac_sc_sum = p_ac_sc_sum.value
            writeRam('wattbezug', int(p_ac_sc_sum) * 1, '#0x6002891F g_sync.p_ac_sc_sum')

            volt1 = int(volt1.value)
            volt1 = int(volt1 * 10) / 10.0
            writeRam('evuv1', volt1, '0xCF053085 g_sync.u_l_rms[0] ')

            volt2 = int(volt2.value)
            volt2 = int(volt2 * 10) / 10.0
            writeRam('evuv2', volt2, '0x54B4684E g_sync.u_l_rms[1] ')

            volt3 = int(volt3.value)
            volt3 = int(volt3 * 10) / 10.0
            writeRam('evuv3', volt3, '0x2545E22D g_sync.u_l_rms[2] ')

            watt1 = int(watt1.value)
            writeRam('bezugw1', watt1, '0x27BE51D9 als Watt g_sync.p_ac_sc[0]')
            ampere = int(watt1 / volt1 * 100.0) / 100.0
            writeRam('bezuga1', ampere, '0x27BE51D9 als Ampere g_sync.p_ac_sc[0]')

            watt2 = int(watt2.value)
            writeRam('bezugw2', watt2, '0xF5584F90 als Watt g_sync.p_ac_sc[1]')
            ampere = int(watt2 / volt2 * 100.0) / 100.0
            writeRam('bezuga2', ampere, '0xF5584F90 als Ampere g_sync.p_ac_sc[1]')

            watt3 = int(watt3.value)
            writeRam('bezugw3', watt3, '0xB221BCFA als Watt g_sync.p_ac_sc[2]')
            ampere = int(watt3 / volt3 * 100.0) / 100.0
            writeRam('bezuga3', ampere, '0xF5584F90 als Ampere g_sync.p_ac_sc[2]')

            freq = freq.value
            freq = int(freq * 100) / 100.0
            writeRam('evuhz', freq, '0x1C4A665F grid_pll[0].f')
#    die Standart-openWB2 liefert keine Frequenz ab
#    nehme die vom EVU stattdessen
#            writeRam('llhz', freq, '0x1C4A665F grid_pll[0].f')

            stat1 = int(stat1.value)
            stat2 = int(stat2.value)
            stat3 = int(stat3.value)
            stat4 = int(stat4.value)
            faultStr = ' '
            faultState = 0

            if (stat1 + stat2 + stat3 + stat4) > 0:
                faultStr = "EVU ALARM Status 1:" + str(stat1) + " 2:" + str(stat2) + " 3:" + str(stat3) + " 4:" + str(stat4)
                faultState = 2
                rct_lib.dbglog("RCT faultstate: ", faultState, faultStr)
                # speicher in mqtt
                os.system('mosquitto_pub -r -t openWB/set/evu/faultState -m "' + str(faultState) + '"')
                os.system('mosquitto_pub -r -t openWB/set/evu/faultStr -m "' + str(faultStr) + '"')
#            else:
#                # Kein fehler loesche alle 5 mintuen den statzus
#                if rct_lib.bm5:
#                    rct_lib.dbglog("RCT clear evu faultstate: ")
#                    os.system('mosquitto_pub -r -t openWB/set/evu/faultState -m "' + str(faultState) + '"')
#                    os.system('mosquitto_pub -r -t openWB/set/evu/faultStr -m "' + str(faultStr) + '"')

###################################

        if rct_lib.wr:
            # wrfaultStr = ' '
            # wrfaultState = 0
            # aktuell
            pv1watt = int(pv1watt.value)
            pv2watt = int(pv2watt.value)
            pvEwatt = int(pvEwatt.value)
            writeRam('pv1wattString1', int(pv1watt), 'pv1watt')
            writeRam('pv1wattString2', int(pv2watt), 'pv2watt')
            pvwatt = ((pv1watt + pv2watt + pvEwatt) * -1)
            writeRam('pvwatt', int(pvwatt), 'negative Summe von pv1/2/3watt')

            # Alternative wr_ac out statt dc_in summe
            # pvwatt = int(rct_lib.read(clientsocket,0x4E49AEC5) ) *-1   #  g_sync.p_ac_sum 2580.68408203125
            # writeRam('pvwatt', int(pvwatt), 'wr out')

##############################
        if rct_lib.sp:
            # Speicher
            spfaultStr = ' '
            spfaultState = 0
            bsocx = bsocx.value
            soc = int(bsocx * 1.0)
            discharge_max=discharge_max.value
            loadWatt=loadWatt.value
            bsocsoll = int(bsocsoll.value * 1.0)
            bstat1 = int(bstat1.value)
            bstat2 = int(bstat2.value)
            bstat3 = int(bstat3.value)

            writeRam('HB_discharge_max', discharge_max, '0xC642B9D6 acc_conv.i_discharge_max')
            writeRam('HB_loadWatt', loadWatt, '0x1D2994EA power_mng.soc_charge_power')

            # akuelles Ladeziel des Hausspeichers fuer die Anzeige weitereeichen. 
            if( bsocsoll==97 and int(bstat1) == 0):
                writeRam('HB_iskalib', "0", "is_kalib")
            else:
                writeRam('HB_iskalib', "1", "is_kalib") 

            s = str(int(discharge_max)) + " " + str(bsocsoll)
            writeRam('HB_soctarget', s, 'soc target')

            writeRam('speichersoc', soc, '0x959930BF battery.soc')

            # akuelles Ladeziel des Hausspeichers fuer die Anzeige weitereeichen.
            # rct_lib.dbglog("RCT publish openWB/housebattery/soctarget: " + str(bsocsoll))
            # os.system('mosquitto_pub -r -t openWB/housebattery/soctarget -m "' + str(bsocsoll) + '"')

            bwatt1 = int(bwatt1.value * -1.0)
            writeRam('speicherleistung', bwatt1, '0x400F015B g_sync.p_acc_lp')

            spfaultStr = ' '
            spfaultState = 0
            if (bstat1 + bstat2 + bstat3) > 0:
                if(bstat1 == 256):
                    spfaultStr = "??? (bat_status C256)"
                    spfaultState = 1
                elif(bstat1 == 512):
                    spfaultStr = "Leistungstest (bat_status C512)"
                    spfaultState = 1
                elif(bstat1 == 1024):
                    spfaultStr = "Battery Balancing aktive (bat_status C1024)"
                    spfaultState = 1
                elif(bstat1 == 8):
                    spfaultStr = "Battery Balancing aktive (bat_status C8)"
                    spfaultState = 1
                else:
                    spfaultStr = "Battery ALARM Battery-Status " + str(bstat1) + " " + str(bstat2) + " " + str(bstat3)
                    spfaultState = 2
                rct_lib.dbglog("RCT Sp-Status ", bstat1, bstat2, bstat3)
                rct_lib.dbglog("RCT spfaultstate: ", spfaultState, spfaultStr)
                # speicher in mqtt
                os.system('mosquitto_pub -r -t openWB/set/houseBattery/faultState -m "' + str(spfaultState) + '"')
                os.system('mosquitto_pub -r -t openWB/set/houseBattery/faultStr -m "' + str(spfaultStr) + '"')


# ######################################################
    if rct_lib.bm5:
        clientsocket = rct_lib.connect_to_server()
        if clientsocket is not None:
            try:
                MyTab = []
                # notfound = rct_lib.add_by_name(MyTab, 'notfound')
                # rct_lib.dbglog("RCT --m5 set, get EVU totals")
                totalfeed = rct_lib.add_by_name(MyTab, 'energy.e_grid_feed_total')
                totalload = rct_lib.add_by_name(MyTab, 'energy.e_grid_load_total')

                # rct_lib.dbglog("RCT --m5 set, get WR totals")
                # dA = rct_lib.add_by_name(MyTab, 'energy.e_dc_day[0]')
                # dB = rct_lib.add_by_name(MyTab, 'energy.e_dc_day[1]')
                # dE = rct_lib.add_by_name(MyTab, 'energy.e_ext_day')
                mA = rct_lib.add_by_name(MyTab, 'energy.e_dc_month[0]')
                mB = rct_lib.add_by_name(MyTab, 'energy.e_dc_month[1]')
                mE = rct_lib.add_by_name(MyTab, 'energy.e_ext_month')
                yA = rct_lib.add_by_name(MyTab, 'energy.e_dc_year[0]')
                yB = rct_lib.add_by_name(MyTab, 'energy.e_dc_year[1]')
                yE = rct_lib.add_by_name(MyTab, 'energy.e_ext_year')
                pv1total = rct_lib.add_by_name(MyTab, 'energy.e_dc_total[0]')
                pv2total = rct_lib.add_by_name(MyTab, 'energy.e_dc_total[1]')
                pvEtotal = rct_lib.add_by_name(MyTab, 'energy.e_ext_total')
                pLimit = rct_lib.add_by_name(MyTab, 'p_rec_lim[2]')     # max. AC power according to RCT Power
                bwatt2 = rct_lib.add_by_name(MyTab, 'battery.stored_energy')
                bwatt3 = rct_lib.add_by_name(MyTab, 'battery.used_energy')

################################
                # read via rct_id list
                response = rct_lib.read(clientsocket, MyTab)
                rct_lib.close(clientsocket)

                # output all response elements
                rct_lib.infolog(rct_lib.format_list(response))
                rct_lib.dbglog("RCT Overall connetion time: {:.3f} seconds".format(time.time() - start_time))
            except Exception as e:
                rct_lib.close(clientsocket)
                raise(e)
###################################

        rct_lib.dbglog("RCT --m5 set, update EVU totals")
        # Counter nur alle 5 Mintuen auslesen
        totalfeed = int(totalfeed.value * -1.0)
        writeRam('einspeisungkwh', totalfeed, '0x44D4C533 energy.e_grid_feed_total')
        totalload = int(totalload.value)
        writeRam('bezugkwh', totalload, '#0x62FBE7DC energy.e_grid_load_total')
        rct_lib.dbglog("RCT --m5 set, update WR totals")
        writeRam('maxACkW', int(pLimit.value), 'Maximale zur Ladung verwendete AC-Leistung des Wechselrichters')
        # monthly
        mA = int(mA.value)  # energy.e_dc_month[0]  WH
        mB = int(mB.value)  # energy.e_dc_month[1]  WH
        mE = int(mE.value)  # energy.e_ext_month    WH
        monthly_pvkwhk = (mA + mB + mE) / 1000.0   # -> KW
        writeRam('monthly_pvkwhk', monthly_pvkwhk, 'monthly_pvkwhk')

        # yearly
        yA = int(yA.value)  # energy.e_dc_total[0]  WH
        yB = int(yB.value)  # energy.e_dc_total[1]  WH
        yE = int(yE.value)  # energy.e_ext_total    WH
        yearly_pvkwhk = (yA + yB + yE) / 1000.0   # -> KW
        writeRam('yearly_pvkwhk', yearly_pvkwhk, 'yearly_pvkwhk')

        # total
        pv1total = int(pv1total.value)    # energy.e_dc_total[0]
        pv2total = int(pv2total.value)    # energy.e_dc_total[1]
        pvEtotal = int(pvEtotal.value)    # energy.e_ext_total
        pvkwh = (pv1total + pv2total + pvEtotal)
        writeRam('pvkwh', pvkwh, 'Summe von pv1total pv2total pvEtotal')
        rct_lib.dbglog("RCT --m5 set, Update BAT totals")
        bwatt2 = int(bwatt2.value)
        # rct_lib.dbglog("RCT speicherikwh will be battery.stored_energy "+ str(bwatt2))
        writeRam('speicherikwh', bwatt2, '0x5570401B battery.stored_energy')

        bwatt3 = int(bwatt3.value)
        # rct_lib.dbglog("RCT speicherekwh will be battery.used_energy "+ str(bwatt3))
        writeRam('speicherekwh', bwatt3, '#0xA9033880 battery.used_energy')

    sys.exit(0)


if __name__ == "__main__":
    main()
