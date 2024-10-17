/**
 * Functions to update graph and gui values via MQTT-messages
 *
 * @author Kevin Wieland
 * @author Michael Ortenstein
 * @author Lutz Bender
 * @author Lena Kümmel
 */

 function formatJsonString(str) {
	try {
		parsed = JSON.parse(str)
		if (typeof parsed === 'string') {
			return parsed
		}
		// if it is not a string, we just use the json as supplied
	} catch (e) {
		// ignore error - just use the original text
	}
	return str
}


function getIndex(topic) {

	var index
	try {
		index = topic.match(/(?:\/)([0-9]+)(?=\/)/g)[0].replace(/[^0-9]+/g, '');
	  }
    catch(err) {
  		index='';
	}


	// get occurrence of numbers between / / in topic
	// since this is supposed to be the index like in openwb/lp/4/w
	// no lookbehind supported by safari, so workaround with replace needed
	//var index = topic.match(/(?:\/)([0-9]+)(?=\/)/g)[0].replace(/[^0-9]+/g, '');
	//if ( typeof index === 'undefined' ) {
	//	index = '';
	//}
	return index;
}

function handlevar(mqttmsg, mqttpayload) {
	// receives all messages and calls respective function to process them
	processPreloader(mqttmsg);
    //console.log('handlevar' , mqttmsg,' ',mqttpayload)
	if ( mqttmsg.match( /^openwb\/lp\//i) ) {
		processLpMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/evu\//i) ) {
		processEvuMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/pv\//i) ) {
		processPvMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\//i) ) {
		processVerbraucherMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/housebattery\//i) ) {
		processBatMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/SmartHome\//i) ) {
		processSmartHomeMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/config\/get\/SmartHome\//i) ) {
		processSmartHomeDeviceMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/system\//i) ) {
		processSystemMsg(mqttmsg, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/global\//i) ) {
		processGlobalMsg(mqttmsg, mqttpayload);
	}
	else {
		console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
	}
}  // end handlevar

function processGlobalMsg (mqttmsg, mqttpayload) {
	switch(mqttmsg){
		case "openWB/global/WAllChargePoints":
			directShow(mqttpayload, '#ladeleistungAll');
			break;
		case "openWB/global/kWhCounterAllChargePoints":
			fractionDigitsShow(mqttpayload, '#kWhCounterAll');
			break;
		case "openWB/global/mqtt2mhiConfigured":
			if( mqttpayload == "1" )
				 console.log('MHI ON');
			else console.log('MHI OFF');
			break;
					
		default:
			console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
			break;
			
	}
}
function processSystemMsg (mqttmsg, mqttpayload) {
	switch(mqttmsg){
		case "openWB/system/devicename":
			$(".devicename").text(mqttpayload);
			break;
		default:
			console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
			break;
	}
}

function processEvuMsg (mqttmsg, mqttpayload) {
	switch(mqttmsg){
		case "openWB/evu/ASchieflast":
			directShow(mqttpayload, '#schieflastdiv');
			break;
		case "openWB/evu/APhase1":
			directShow(mqttpayload, '#bezuga1div');
			break;
		case "openWB/evu/APhase2":
			directShow(mqttpayload, '#bezuga2div');
			break;
		case "openWB/evu/APhase3":
			directShow(mqttpayload, '#bezuga3div');
			break;
		case "openWB/evu/WPhase1":
			impExpShow(mqttpayload, '#bezugw1div');
			break;
		case "openWB/evu/WPhase2":
			impExpShow(mqttpayload, '#bezugw2div');
			break;
		case "openWB/evu/WPhase3":
			impExpShow(mqttpayload, '#bezugw3div');
			break;
		case "openWB/evu/W":
			impExpShow(mqttpayload, '#wattbezugdiv');
			break;
		case "openWB/evu/WhExported":
			kShow(mqttpayload, "#einspeisungkwhdiv");
			break;
		case "openWB/evu/WhImported":
			kShow(mqttpayload, "#bezugkwhdiv");
			break;
		case "openWB/evu/VPhase1":
			directShow(mqttpayload, '#evuv1div');
			break;
		case "openWB/evu/VPhase2":
			directShow(mqttpayload, '#evuv2div');
			break;
		case "openWB/evu/VPhase3":
			directShow(mqttpayload, '#evuv3div');
			break;
		case "openWB/evu/Hz":
			directShow(mqttpayload, '#evuhzdiv');
			break;
		case "openWB/evu/PfPhase1":
			directShow(mqttpayload, '#evupf1div');
			break;
		case "openWB/evu/PfPhase2":
			directShow(mqttpayload, '#evupf2div');
			break;
		case "openWB/evu/PfPhase3":
			directShow(mqttpayload, '#evupf3div');
			break;
		case "openWB/evu/faultState":
			setWarningLevel(mqttpayload, '#faultStrEvuRow');
			break;
		case "openWB/evu/faultStr":
			textShow(formatJsonString(mqttpayload), '#faultStrEvu');
			break;
		default:
			console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
			break;
	}
}

function processPvMsg (mqttmsg, mqttpayload) {
	if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/.*$/i) )
	{
		var index = getIndex(mqttmsg);  // extract number between two / /
		if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/W$/i) )
		{
            // JQuery  Id inverter[1|2] dann .classnane .powerInvertrer
            // https://stackoverflow.com/questions/1944302/jquery-select-an-elements-class-and-id-at-the-same-time
			absShow(mqttpayload, '#inverter' + index + ' .powerInverter');
		}
		else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/WhCounter$/i) )
		{
			kShow(mqttpayload, '#inverter' + index + ' .yieldInverter');
		}
		// no data in openWB 1.x
		// else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/DailyYieldKwh$/i) )
		// {
		// 	fractionDigitsShow(mqttpayload, '#inverter' + index + ' .dYieldInverter');
		// }
		// else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/MonthlyYieldKwh$/i) )
		// {
		// 	fractionDigitsShow(mqttpayload, '#inverter' + index + ' .mYieldInverter');
		// }
		// else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/YearlyYieldKwh$/i) )
		// {
		// 	fractionDigitsShow(mqttpayload, '#inverter' + index + ' .yYieldInverter');
		// }
		else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/faultState$/i) )
		{
			setWarningLevel(mqttpayload, '#inverter' + index + ' .faultStrPvRow');
		}
		else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/faultStr$/i) )
		{
			textShow(formatJsonString(mqttpayload), '#inverter' + index + ' .faultStrPv');
		}
		else if ( mqttmsg.match(/^openWB\/pv\/[0-9]+\/boolPVConfigured$/i) )
		{
			visibilityCard('#inverter' + index, mqttpayload);
		}
	}
	else {
		switch(mqttmsg){
			case "openWB/pv/CounterTillStartPvCharging":
				directShow(mqttpayload, '#pvcounterdiv');
				break;
			case "openWB/pv/W":
				absShow(mqttpayload, '#pvwattdiv');
				break;
			case "openWB/pv/WhCounter":
				kShow(mqttpayload, '#pvkwhdiv');
				break;
			case "openWB/pv/DailyYieldKwh":
				fractionDigitsShow(mqttpayload, '#daily_pvkwhdiv');
				break;
			case "openWB/pv/MonthlyYieldKwh":
				fractionDigitsShow(mqttpayload, '#monthly_pvkwhdiv');
				break;
			case "openWB/pv/YearlyYieldKwh":
				fractionDigitsShow(mqttpayload, '#yearly_pvkwhdiv');
				break;
			default:
				console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
				break;
		}
	}
}

function processBatMsg (mqttmsg, mqttpayload) {
	switch(mqttmsg){
		case "openWB/housebattery/boolHouseBatteryConfigured":
			visibilityCard('#speicher', mqttpayload);
			break;
		case "openWB/housebattery/WhImported":
			kShow(mqttpayload, '#speicherikwhdiv');
			break;
		case "openWB/housebattery/WhExported":
			kShow(mqttpayload, '#speicherekwhdiv');
			break;
		case "openWB/housebattery/W":
			BatShow(mqttpayload, '#wBatDiv');
			break;
		case "openWB/housebattery/%Soc":
			directShow(mqttpayload, '#socBatDiv');
			break;
		case "openWB/housebattery/boolHouseBatteryConfigured":
			visibilityCard('#speicher', mqttpayload);
			break;
		case "openWB/housebattery/faultState":
			setWarningLevel(mqttpayload, '#faultStrBatRow');
			break;
		case "openWB/housebattery/faultStr":
			textShow(formatJsonString(mqttpayload), '#faultStrBat');
			break;
		default:
			console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
			break;
	}
}

function processSmartHomeDeviceMsg(mqttmsg, mqttpayload)
{
 var index = getIndex(mqttmsg);  // extract number between two / /
 console.log(index, mqttmsg, mqttpayload);
 if ( mqttmsg.match(/device_configured$/i ) ) {
   visibilityCard('#device'+index, mqttpayload);
 }
 else if ( mqttmsg.match(/device_name$/i ) ) {
	textShow(mqttpayload, '#device'+index+'_name');
 }
 else if ( mqttmsg.match(/device_type$/i ) ) {
	textShow(mqttpayload, '#device'+index+'_typ');
 }
}


function processSmartHomeMsg (mqttmsg, mqttpayload) 
{
	var index = getIndex(mqttmsg);  // extract number between two / /
	console.log("processSmartHomeMsg.", index, mqttmsg, mqttpayload);

	if ( mqttmsg.match(/maxspeicherladung$/i ) ) 
			directShow(mqttpayload, '#wmaxspeicherladung');
	else if ( mqttmsg.match(/wattschalt$/i ) ) 
			directShow(mqttpayload, '#wwattschalt');
	else if ( mqttmsg.match(/wattnichtschalt$/i ) ) 
			directShow(mqttpayload, '#wwattnichtschalt');
	else if ( mqttmsg.match(/uberschuss$/i ) ) 
			directShow(mqttpayload, '#wuberschuss');
	else if ( mqttmsg.match(/uberschussoffset$/i ) ) 
			directShow(mqttpayload, '#wuberschussoffset');
	else if ( mqttmsg.match(/Watt$/i ) ) 
			directShow(mqttpayload, '#device'+index+' .shWatt');
	else if ( mqttmsg.match(/Wh$/i ) ) 
			kShow(mqttpayload, '#device'+index+' .importsh');
	else if ( mqttmsg.match(/Whe$/i ) ) 
			kShow(mqttpayload, '#device'+index+' .exportsh');
	else
			console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
}

function processVerbraucherMsg (mqttmsg, mqttpayload) {
	var index = getIndex(mqttmsg);  // extract number between two / /
    console.log('Verbraucher:' , index, mqttmsg, mqttpayload);
	if ( mqttmsg.match( /^openwb\/verbraucher\/[1-2]\/configured$/i ) ) {
		visibilityCard('#loads'+index, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\/[1-2]\/Watt$/i ) ) {
		directShow(mqttpayload, '#loads'+index+' .verbraucherWatt');
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\/[1-2]\/WhImported$/i ) ) {
		kShow0(mqttpayload, '#loads'+index+' .TotalimportVerbraucher');
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\/[1-2]\/WhExported$/i ) ) {
		kShow0(mqttpayload, '#loads'+index+' .TotalexportVerbraucher');
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\/[1-2]\/DailyYieldImportkWh$/i ) ) {
		kShow0(mqttpayload, '#loads'+index+' .importVerbraucher');
	}
	else if ( mqttmsg.match( /^openwb\/Verbraucher\/[1-2]\/DailyYieldExportkWh$/i ) ) {
		kShow0(mqttpayload, '#loads'+index+' .exportVerbraucher');
	}
}

function processLpMsg (mqttmsg, mqttpayload) {
	var index = getIndex(mqttmsg);  // extract number between two / /
	if( index > 3 ){ return; }
	
	//console.log('msg:'  , mqttmsg, mqttpayload );
	
	if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/boolChargePointConfigured$/i ) ) {
		visibilityCard('#lp' + index, mqttpayload);
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/APhase1$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .stromstaerkeP1');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/APhase2$/i ) ) {		
		directShow(mqttpayload, '#lp' + index + ' .stromstaerkeP2');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/APhase3$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .stromstaerkeP3');
	} 
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/AConfigured$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .stromvorgabe');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/kWhCounter$/i ) ) {
		fractionDigitsShow(mqttpayload, '#lp' + index + ' .kWhCounter');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/VPhase1$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .spannungP1');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/VPhase2$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .spannungP2');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/VPhase3$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .spannungP3');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/W$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .ladeleistung');
	}
	else if ( mqttmsg.match( /^openWB\/lp\/[1-9][0-9]*\/boolSocConfigured$/i )) {
		if( mqttpayload == "1" ){
			showSection('#lp' + index + ' .socRow');
		} else {
			hideSection('#lp' + index + ' .socRow');
		}
	}
	//*******************************
	else if ( mqttmsg.match( /^openWB\/lp\/[1-9][0-9]*\/boolPlugStat$/i )) {
		if( mqttpayload == "1" )
           textShow('(Pluged)', '#lp' + index + ' .boolPlugStat');
		else   	
           textShow('', '#lp' + index + ' .boolPlugStat');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/%Soc$/i ) ) {
		directShow(mqttpayload, '#lp' + index + ' .soc');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/faultState$/i ) ) {
		setWarningLevel(mqttpayload, '#lp' + index + ' .faultStrLpRow');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/faultStr$/i ) ) {
		textShow(formatJsonString(mqttpayload), '#lp' + index + ' .faultStrLp');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/socFaultState$/i ) ) {
		setWarningLevel(mqttpayload, '#lp' + index + ' .faultStrSocLpRow');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/socFaultStr$/i ) ) {
		textShow(formatJsonString(mqttpayload), '#lp' + index + ' .faultStrSocLp');
	}
	else if ( mqttmsg.match( /^openwb\/lp\/[1-9][0-9]*\/MeterSerialNumber$/i ) ) {
		textShow('(SN:'+mqttpayload+')', '#lp' + index + ' .MeterSerialNumber');
	}
	else {
		switch (mqttmsg) {
			case "openWB/lp/1/PfPhase1":
				showSection('#lp1 .powerFaktorRow');
				directShow(mqttpayload, '#lp1 .powerFaktorP1');
				break;
			case "openWB/lp/1/PfPhase2":
				showSection('#lp1 .powerFaktorRow');
				directShow(mqttpayload, '#lp1 .powerFaktorP2');
				break;
			case "openWB/lp/1/PfPhase3":
				showSection('#lp1 .powerFaktorRow');
				directShow(mqttpayload, '#lp1 .powerFaktorP3');
				break;
			default:
				console.log("Unknown topic: "+mqttmsg+": "+mqttpayload);
				break;
		}
	}
}

// don't parse value
function directShow(mqttpayload, variable) {
		var value = parseFloat(mqttpayload);
		if ( isNaN(value) ) {
			value = 0;
		}
		var valueStr = value.toLocaleString(undefined) ;
		$(variable).text(valueStr);
}

// show missing value or zero value as --
function noZeroShow(mqttpayload, variable) {
    //console.log('noZeroShow( ' , mqttpayload, ',' , variable,')' )
	var value = parseFloat(mqttpayload);
	if ( isNaN(value) || (value == 0) ) {
		valueStr = "--";
	}
	else {
		var valueStr = value.toLocaleString(undefined);
	}
	$(variable).text(valueStr);
}

//show with imp/exp
function impExpShow(mqttpayload, variable) {
	// zur Anzeige Wert um "Bezug"/"Einspeisung" ergänzen
	var value = parseInt(mqttpayload);
	var valueStr = Math.abs(value).toLocaleString(undefined);
    if(value > 0)
       h = '<span style="background-color:#FFCFD0"><small>&nbsp;Import&nbsp;</small> ' + valueStr + '&nbsp;</span>'; 
    else
       h = '<span style="background-color:#ACFFAB"><small>&nbsp;Export&nbsp;</small> ' + valueStr + '&nbsp;</span>'; 
	$(variable).html(h);
}

// show value as kilo
function kShow(mqttpayload, variable) {
	var value = parseFloat(mqttpayload);
	value = value / 1000
	var valueStr = value.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1});
    // var valueStr = value.toLocaleString(); // undefined, {minimumFractionDigits: 3, maximumFractionDigits: 3}) ;
	$(variable).text(valueStr);
    //console.log('kShow( ' , mqttpayload, ',' , variable,') ',valueStr )
}

// show value as kilo
function kShow0(mqttpayload, variable) {
	var value = parseFloat(mqttpayload);
	value = value / 1000
	if ( value == 0.0 )
	{
	  $(variable).parent().addClass('hide');
      updateFormFieldVisibility();
	
	} else
	{
	  var valueStr = value.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 3});
      // var valueStr = value.toLocaleString(); // undefined, {minimumFractionDigits: 3, maximumFractionDigits: 3}) ;
	  $(variable).text(valueStr);
      //console.log('kShow( ' , mqttpayload, ',' , variable,') ',valueStr )
	}  
}

function BatShow(mqttpayload, variable) {
		var value = parseFloat(mqttpayload);
		if ( isNaN(value) ) {
			value = 0;
		}
		var valueStr = value.toLocaleString(undefined) ;
		if ( value < 0 )
			valueStr = '<small>(Entladen)</small> ' + valueStr;
		else
			valueStr = '<small>(Laden)</small> ' + valueStr;
		$(variable).html(valueStr );
}

// show absolute value (always >0)
function absShow(mqttpayload, variable) {
    //console.log('absShow( ' , mqttpayload, ',' , variable,')' )
	var value = Math.abs(parseInt(mqttpayload));
	var valueStr = value.toLocaleString(undefined) ;
	$(variable).text(valueStr);
}

//show kilo-payloads with 3 fraction digits
function fractionDigitsShow(mqttpayload, variable) {
    //console.log('fractionDigitsShow( ' , mqttpayload, ',' , variable,')' )
	var value = parseFloat(mqttpayload);
	if ( isNaN(value) ) {
		value = 0;
	}
	var valueStr = value.toLocaleString(undefined, {minimumFractionDigits: 1, maximumFractionDigits: 1});
	$(variable).text(valueStr);
}

function textShow(mqttpayload, variable) {
    //console.log('textShow( ' , mqttpayload, ',' , variable,')' )
	$(variable).text(mqttpayload);
}

// shows table row colored regarding to the fault state
function setWarningLevel(mqttpayload, variable) {
	switch (mqttpayload) {
		case "0":
			$(variable).removeClass("text-warning").removeClass("text-danger");
			hideSection(variable);
			break;
		case "1":
			$(variable).addClass("text-warning").removeClass("text-danger");
			showSection(variable);
			break;
		case "2":
			$(variable).addClass("text-danger").removeClass("text-warning");
			showSection(variable);
			break;
	}
}

//show only values over 100
//Der String ist mit einem Tausender-Punkt versehen. Daher den Payload für die if-Abfrage verwenden.
function visibilityMin(row, mqttpayload) {
	var value = parseFloat(mqttpayload) * -1;
	if (value>100) { 
		showSection(row);
	}
	else {
		hideSection(row);
	}
}

//show/hide row with only one value
function visibilityValue(row, variable){
	var value = parseFloat($(variable).text()); // zu Berücksichtigung von 0,00
	if (( value != 0) && ( $(variable).text() != "")) {
		showSection(row);
	}
	else {
		hideSection(row);
	}
	var valueStr = value.toLocaleString(undefined, {minimumFractionDigits: 3, maximumFractionDigits: 3});
	$(variable).text(valueStr);
}

//show/hide complete row, if all three values are zero or empty
function visibilityRow(row, var1, var2, var3) {
	var val1 = parseFloat($(var1).text()); // zu Berücksichtigung von 0,00
	var val2 = parseFloat($(var2).text());
	var val3 = parseFloat($(var3).text());
	if ( ( (val1 == 0) || ($(var1).text() == "") ) &&
		 ( (val2 == 0) || ($(var2).text() == "") ) &&
		 ( (val3 == 0) || ($(var3).text() == "") ) ) {
		hideSection(row);
	}
	else {
		showSection(row);
	}
}

var lpGesCardShown = false; // flag, show lpGes-Card if any other cp than cp1 is configured
var pv1 = 0;
var pv2 = 0;

//show/hide card, if module is configured
function visibilityCard(card, mqttpayload) {
	var value = parseInt(mqttpayload);
    console.log('visibilityCard ', card, ' ', value  );
	if (value == 0) {
		hideSection(card);
	} else 
	{
		showSection(card);
		if ( (card.match( /^[#]lp[2-3]$/i)) && lpGesCardShown == false ) {
			showSection('#lpges');
			lpGesCardShown = true;
		}
		else if ( card.match(/^[#]inverter[1-2]+$/i) ) 
		{
			if ( card == "#inverter1" ) {
				pv1 = value;
			} else {
				pv2 = value;
			}
			if( (pv1+pv2)==0 )		// war vorher String-Add statt int Int-Add
			 {
			    visibilityCard('#pvGes',"0");
				hideSection('#inverter1');
				hideSection('#inverter2');
			}
			 else if( (pv1+pv2)==1 )
			 {
			    visibilityCard('#pvGes',"1");
				hideSection('#inverter1');
				hideSection('#inverter2');
			}
			 else if( (pv1+pv2)==2)
			 {
			    visibilityCard('#pvGes',"1");
				showSection('#inverter1');
				showSection('#inverter2');
			 }
		}
	}
}

