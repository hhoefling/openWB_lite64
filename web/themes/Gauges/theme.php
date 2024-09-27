<?php
// heist html, wird aber von index.php geincluded
$theme = $_COOKIE['openWBTheme'];  // colors-hh oder colors

function  xgeturl($file)
{
 global $theme;
 $fn=sprintf('themes/%s/%s', $theme,$file);
 $ftime=filemtime($fn);
 return sprintf('%s?v=%d' , $fn,$ftime);
}


function makedebugreihe()
{
 global $dbdebs,$dbdeb,$debug;
 
 echo <<<END
	<!-- debug reihe  -->
	<div id="altclicker" class="container-fluid py-0 pb-2">
	  <div class="row py-0 px-0">
		<div class="rounded shadow wb-widget col-md p-2 m-1 ">
			<div id="accordion" class="accordion">
				<div class="card mb-0">
					<div class="card-header bg-secondary collapsed" data-toggle="collapse" data-target="#debugOne">
						<a class="card-title">Debug </a>
					</div>
					<div id="debugOne" class="card-body collapse" data-parent="#accordion">
						<pre id="debugdiv" style="font-size:0.7rem;">

END;
					foreach( $dbdebs as $s)
						echo "DEB:$s\n";
					if( $dbdeb > 3) { 
						echo "---- Globals---\n";
						$dbdebs="striped";	
				 		print_r($GLOBALS);
					}
echo <<<END
						</pre>
					</div>
				</div>
			</div>
		</div>
  	  </div>
	</div>
	<!-- debug reihe  -->
END;
}
?>
<!DOCTYPE html>
<html lang="de">

<head>
	<!-- theme with gauges for openWB -->
	<!-- 2020 Michael Ortenstein -->
	<!-- 2024 Modified for SmartHome by Heinz Hoefling -->

	<title>openWB</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=0">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
	<meta name="apple-mobile-web-app-title" content="openWB">
	<meta name="apple-mobile-web-app-status-bar-style" content="default">
	<link rel="apple-touch-startup-image" href="/openWB/web/img/favicons/splash1125x2436w.png"  />
	<link rel="apple-touch-startup-image" media="(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)" href="img/favicons/splash1125x2436w.png">
	<meta name="apple-mobile-web-app-title" content="openWB">

	<meta name="description" content="openWB">
	<meta name="keywords" content="openWB">
	<meta name="author" content="Michael Ortenstein">
	<link rel="apple-touch-icon" sizes="72x72" href="img/favicons/apple-icon-72x72.png">
	<link rel="apple-touch-icon" sizes="76x76" href="img/favicons/apple-icon-76x76.png">
	<link rel="apple-touch-icon" sizes="114x114" href="img/favicons/apple-icon-114x114.png">
	<link rel="apple-touch-icon" sizes="120x120" href="img/favicons/apple-icon-120x120.png">
	<link rel="apple-touch-icon" sizes="144x144" href="img/favicons/apple-icon-144x144.png">
	<link rel="apple-touch-icon" sizes="152x152" href="img/favicons/apple-icon-152x152.png">
	<link rel="apple-touch-icon" sizes="180x180" href="img/favicons/apple-icon-180x180.png">
	<link rel="icon" type="image/png" sizes="192x192"  href="img/favicons/android-icon-192x192.png">
	<link rel="icon" type="image/png" sizes="32x32" href="img/favicons/favicon-32x32.png">
	<link rel="icon" type="image/png" sizes="96x96" href="img/favicons/favicon-96x96.png">
	<link rel="icon" type="image/png" sizes="16x16" href="img/favicons/favicon-16x16.png">
	<meta name="msapplication-TileColor" content="#ffffff">
	<meta name="msapplication-TileImage" content="/ms-icon-144x144.png">
	<link rel="apple-touch-icon" sizes="57x57" href="img/favicons/apple-touch-icon-57x57.png">
	<link rel="apple-touch-icon" sizes="60x60" href="img/favicons/apple-touch-icon-60x60.png">
	<link rel="manifest" href="manifest.json">
	<link rel="shortcut icon" href="img/favicons/favicon.ico">
	<!-- <link rel="apple-touch-startup-image" href="img/loader.gif"> -->
	<meta name="msapplication-config" content="img/favicons/browserconfig.xml">
	<meta name="theme-color" content="#ffffff">

	<!-- Bootstrap -->
	<link rel="stylesheet" type="text/css" href="css/bootstrap-4.4.1/bootstrap.min.css">
	<!-- Normalize -->
	<link rel="stylesheet" type="text/css" href="css/normalize-8.0.1.css">
	<!-- Font Awesome, all styles -->
	<link rel="stylesheet" type="text/css" href="fonts/font-awesome-5.8.2/css/all.css">
	<!-- local css due to async loading of theme css -->
	<style>
		#preloader {
			background-color:black;
			position:fixed;
			top:0px;
			left:0px;
			width:100%;
			height:100%;
			z-index:999999;
		}
		#preloader-inner {
			margin-top: 150px;
			text-align: center;
		}
		#preloader-image {
			max-width: 300px;
			filter:invert(1);
		}
		#preloader-info {
			color: #e4e4e4;
		}
		#thegraph > div {
			height: 350px;
		}
		#electricityPriceChartCanvasDiv {
			height: 150px;
		}
	</style>
	<!-- important scripts to be loaded -->
	<script src="js/jquery-3.6.0.min.js"></script>
	<script src="js/bootstrap-4.4.1/bootstrap.bundle.min.js"></script>
	<script src="js/RGraph.common.core.js"></script>
	<script src="js/RGraph.common.dynamic.js"></script>
	<script src="js/RGraph.common.effects.js"></script>
	<script src="js/RGraph.gauge.js"></script>

<?php
$iscl=($iscloud) ? 'true' : 'false';
out('iscl:' . $iscl);
echo <<<END
    <script>
    function validate()
     {
        console.log('validate..');
        usern='$_CURRENT_USER->username';
        passwd='$_CURRENT_USER->passwd';
        dbdeb=$dbdeb;
        iscloud=$iscl;
		MOSQSERVER='$MOSQSERVER';
		MOSQPORT=$MOSQPORT;
		MOSQPORTSSL=$MOSQPORTSSL;
		PROJECT='$PROJECT';
        theme='$theme';
    }
    validate();
    </script>

END;
?>


	<script>
		function setCookie(name, value, days) {
			var expires = '';
			if ( days ) {
				var date = new Date();
				date.setDate(date.getDate() + days);
				expires = '; expires=' + date.toUTCString();
			}
		    document.cookie = name + "=" + (value || '')  + expires + "; path=/openWB/;SameSite=Lax";
		}

		function getCookie(cname) {
			var name = cname + '=';
			var decodedCookie = decodeURIComponent(document.cookie);
			var ca = decodedCookie.split(';');
			for(var i = 0; i <ca.length; i++) {
				var c = ca[i];
				while (c.charAt(0) == ' ') {
					c = c.substring(1);
				}
				if (c.indexOf(name) == 0) {
					return c.substring(name.length, c.length);
				}
			}
			return '';
		}
	 	$('head').append('<link rel="stylesheet" href="<?php echo xgeturl('style.css');?>">');	var debugmode=<?php echo $dbdeb;?>;

	</script>
</head>

<body>
	<!-- Preloader with Progress Bar -->
	<!-- style instead of css due to async loading of theme css -->
	<div id="preloader">
		<div id="preloader-inner">
			<div class="row">
				<div class="mx-auto d-block justify-content-center">
					<img id="preloader-image" src="img/favicons/preloader-image-transparent.png" alt="openWB">
				</div>
			</div>
			<div id="preloader-info" class="row justify-content-center mt-2">
				<div class="col-10 col-sm-6">
					Bitte warten, während die Seite aufgebaut wird.
					<div class="devicename">openWB</div>
				</div>
			</div>
			<div class="row justify-content-center mt-2">
				<div class="col-10 col-sm-6">
					<div class="progress active">
						<div class="progress-bar progress-bar-success progress-bar-striped progress-bar-animated" id="preloaderbar" role="progressbar">
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Landing Page -->
	<div id="nav-placeholder"></div>
	<div class="container">
		<div class="row py-1 verySmallTextSize text-black bg-darkgrey">
			<div id="date" class="col text-left">
				&nbsp;
			</div>
			<div class="col-5 text-center">
				<button type="button" class="btn btn-sm btn-secondary cursor-pointer regularTextSize" id="chargeModeSelectBtn">
					<span id="chargeModeSelectBtnText">Lademodus</span>
					<span id="priorityEvBattery">
						<span class="fas fa-car" id="priorityEvBatteryIcon">&nbsp;</span>
					</span>
				</button>
			</div>
			<div id="time" class="col text-right">
				&nbsp;
			</div>
		</div>

		<div class="row justify-content-center">
			<div class="col-6 col-md-3 pvInfoStyle text-center">
				<div class="">Photovoltaik</div>
				<canvas id="pvData">
					Sorry, no canvas support
				</canvas>
			</div>
			<div class="col-6 col-md-3 pvInfoStyle text-center" id="battDataDiv">
				<div>Speicher</div>
				<canvas id="battData">
					Sorry, no canvas support
				</canvas>
			</div>
			<div class="col-6 col-md-3 pvInfoStyle text-center">
				<div>Energienetz</div>
				<canvas id="evuData">
					Sorry, no canvas support
				</canvas>
			</div>
			<div class="col-6 col-md-3 pvInfoStyle text-center">
				<div>Hausverbrauch</div>
				<canvas id="homeData">
					Sorry, no canvas support
				</canvas>
			</div>
		</div>
		<div class="row justify-content-center regularTextSize font-weight-bold text-center text-grey">
			<div class="col bg-lightgrey">
				Ladeleistung: <span id="powerAllLp">lade Daten</span>
			</div>
		</div>
		<div id="strompreis" class="row justify-content-center regularTextSize font-weight-bold text-center text-black hide">
			<div class="col-sm bg-rose">
				<span class="smallTextSize">aktueller Strompreis: <span id="aktuellerStrompreis"> lade Daten</span></span>
			</div>
		</div>

		<div id="verbraucher" class="row justify-content-center regularTextSize font-weight-bold text-center openwb-devices hide">
			<div id="verbraucher1" class="col-sm hide">
				<span class="smallTextSize"><span id="verbraucher1name">Verbraucher 1</span>: <span id="verbraucher1leistung">lade Daten</span></span><span class="verySmallTextSize" id="verbraucher1dailyyield"></span>
			</div>
			<div id="verbraucher2" class="col-sm hide">
				<span class="smallTextSize"><span id="verbraucher2name">Verbraucher 2</span>: <span id="verbraucher2leistung">lade Daten</span></span><span class="verySmallTextSize" id="verbraucher2dailyyield"></span>
			</div>
		</div>

		<div class="row justify-content-center regularTextSize font-weight-bold text-center text-black">
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="1">
				<span class="actualTemp0Device"></span>
			</div>
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="1">
				<span class="actualTemp1Device"></span>
			</div>
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="1">
				<span class="actualTemp2Device"></span>
			</div>
		</div>

		<div class="row justify-content-center regularTextSize font-weight-bold text-center text-black">
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="2">
				<span class="actualTemp0Device"></span>
			</div>
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="2">
				<span class="actualTemp1Device"></span>
			</div>
			<div class="hide bg-lightblue col-sm SmartHomeTemp" data-dev="2">
				<span class="actualTemp2Device"></span>
			</div>
		</div>

		<div id="webhooks" class="row justify-content-center regularTextSize font-weight-bold text-center text-black bg-darkgrey">
			<div id="hook1" class="col-3 m-1 bg-danger hide">
				ext. Gerät 1
			</div>
			<div id="hook2" class="col-3 m-1 bg-danger hide">
				ext. Gerät 2
			</div>
			<div id="hook3" class="col-3 m-1 bg-danger hide">
				ext. Gerät 3
			</div>
		</div>

		<!-- interactive chart.js -->
		<!-- will be refreshed using MQTT (in livechart.js)-->
		<div class="row justify-content-center my-2" id="thegraph">
			<div class="col-sm-12 text-center smallTextSize">
				<div id="waitforgraphloadingdiv">
					Graph lädt, bitte warten...
				</div>
				<canvas id="canvas"></canvas>
			</div>
		</div>

		<div class="row text-center bg-darkgrey">
			<div class="col">
				<span id="lastregelungaktiv" class="regularTextSize text-red animate-alertPulsation"></span>
			</div>
		</div>

		<!-- chargepoint info header -->
		<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-darkgrey text-grey font-weight-bold">
			<div class="col-3 px-0">
				Ladepunkt <span id="etproviderEnabledIcon" class="fa fa-chart-line hide"></span>
			</div>
			<div class="col-3 px-0">
				Ladeparameter
			</div>
			<div class="col-4 px-0">
				geladen
			</div>
			<div class="col-2 px-0">
				SoC
			</div>
		</div>

		<!-- chargepoint info data lp1-->
		<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey" data-lp="1">
			<div class="col-3 px-0">
				<span class="cursor-pointer font-weight-bold lpDisabledStyle enableLp nameLp">LP Name</span>
				<span class="fa fa-xs fa-plug text-orange hide plugstatLp"></span>
				<span class="fa fa-xs fa-flag-checkered hide targetChargingLp"></span>
				<span class="fa fa-xs fa-moon hide nightChargingLp"></span>
			</div>
			<div class="col-3 px-0">
				<span class="actualPowerLp">lade Daten</span><span class="phasesInUseLp"></span><span class="targetCurrentLp"></span>
			</div>
			<div class="col-4 px-0">
				<span class="energyChargedLp">lade Daten</span><span class="kmChargedLp" data-consumption="0"></span>
			</div>
			<div class="col-2 px-0 socNotConfiguredLp text-center">
				--
			</div>
			<div class="col-2 px-0 hide socConfiguredLp text-center cursor-pointer">
				<span class="socLp"></span> %
				<i class="small reloadLpSoc fas fa-redo-alt"></i>
				<i class="manualSocSymbol fas fa-edit hide"></i>
			</div>
		</div>

		<!-- chargepoint info data lp2-->
		<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-lp="2">
			<div class="col-3 px-0">
				<span class="cursor-pointer font-weight-bold lpDisabledStyle enableLp nameLp">LP Name</span>
				<span class="fa fa-xs fa-plug text-orange hide plugstatLp"></span>
				<span class="fa fa-xs fa-flag-checkered hide targetChargingLp"></span>
				<span class="fa fa-xs fa-moon hide nightChargingLp"></span>
			</div>
			<div class="col-3 px-0">
				<span class="actualPowerLp">lade Daten</span><span class="phasesInUseLp"></span><span class="targetCurrentLp"></span>
			</div>
			<div class="col-4 px-0">
				<span class="energyChargedLp">lade Daten</span><span class="kmChargedLp" data-consumption="0"></span>
			</div>
			<div class="col-2 px-0 socNotConfiguredLp text-center">
				--
			</div>
			<div class="col-2 px-0 hide socConfiguredLp text-center cursor-pointer">
				<span class="socLp"></span> %
				<i class="small reloadLpSoc fas fa-redo-alt"></i>
				<i class="manualSocSymbol fas fa-edit hide"></i>
			</div>
		</div>

		<!-- chargepoint info data lp3-->
		<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-lp="3">
			<div class="col-3 px-0">
				<span class="cursor-pointer font-weight-bold lpDisabledStyle enableLp nameLp">LP Name</span>
				<span class="fa fa-xs fa-plug text-orange hide plugstatLp"></span>
				<span class="fa fa-xs fa-flag-checkered hide targetChargingLp"></span>
				<span class="fa fa-xs fa-moon hide nightChargingLp"></span>
			</div>
			<div class="col-3 px-0">
				<span class="actualPowerLp">lade Daten</span><span class="phasesInUseLp"></span><span class="targetCurrentLp"></span>
			</div>
			<div class="col-4 px-0">
				<span class="energyChargedLp">lade Daten</span><span class="kmChargedLp" data-consumption="0"></span>
			</div>
			<div class="col-2 px-0 socNotConfiguredLp text-center">
				--
			</div>
			<div class="col-2 px-0 hide socConfiguredLp text-center">
				<span class="socLp"></span> %
				<i class="small reloadLpSoc fas fa-redo-alt"></i>
				<i class="manualSocSymbol fas fa-edit hide"></i>
			</div>
		</div>


		<div class="smartHome hide">
			<hr class="border-secondary">

			<!-- SmartHome info header -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-darkgrey text-grey font-weight-bold">
				<div class="col-3 px-0">
					Gerät
				</div>
				<div class="col-3 px-0">
					Verbrauch
				</div>
				<div class="col-3 px-0">
					Modus
				</div>
				<div class="col-3 px-0">
					Laufzeit
				</div>
			</div>

			<!-- SmartHome Device 1 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="1">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>

				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 2 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="2">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 3 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="3">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 4 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="4">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 5 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="5">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 6 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="6">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 7 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="7">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 8 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="8">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>

			<!-- SmartHome Device 9 data -->
			<div class="row no-gutter py-1 py-md-0 smallTextSize text-center bg-lightgrey text-grey hide" data-dev="9">
				<div class="col-3 px-0">
					<span class="cursor-pointer font-weight-bold lpEnabledStyle enableDevice nameDevice">SmartHomeDevice</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualPowerDevice">lade Daten</span><span class="actualDailyYieldDevice"></span>
				</div>
				<div class="col-3 px-0">
					<span class="cursor-pointer actualModeDevice changeSHMode">lade Daten</span>
				</div>
				<div class="col-3 px-0">
					<span class="actualRunningTimeDevice">lade Daten</span>
				</div>
			</div>
		</div>  <!-- end smart home -->

		<!-- depending on charge mode show options -->
		<form id="minundpvladenEinstellungen" class="hide">
			<hr class="border-secondary">
			<div class="row justify-content-center">
				<h3 class="font-weight-bold text-center text-lightgrey">Minimal Stromstärke</h3>
			</div>

			<div class="form-row form-group mb-1 vaRow regularTextSize" data-lp="1">
				<label for="minCurrentMinPv" class="col-3 col-form-label text-right"></label>
				<div class="col">
					<input type="range" class="form-control-range rangeInput" id="minCurrentMinPv" min="6" max="16" step="1" value="6" data-initialized="0" data-topicprefix="openWB/config/get/pv/">
				</div>
				<label for="minCurrentMinPv" class="col-3 col-form-label valueLabel" suffix="A"></label>
			</div>
		</form>

		<form id="sofortladenEinstellungen" class="hide">
			<div class="hide" id="priceBasedCharging">
				<hr class="border-secondary">
				<div class="row justify-content-center">
					<h3 class="font-weight-bold text-center text-lightgrey">preisbasiertes Laden</h3>
				</div>
				<div class="row justify-content-center my-2">
					<div id="electricityPriceChartCanvasDiv" class="col text-center">
						<canvas id="electricityPriceChartCanvas"></canvas>
					</div>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize">
					<label for="MaxPriceForCharging" class="col-3 col-form-label text-right">max. Preis:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="MaxPriceForCharging" min="-25" max="95" step="0.1" value="0" data-topicprefix="openWB/global/awattar/">
					</div>
					<label for="MaxPriceForCharging" class="col-3 col-form-label valueLabel" suffix="ct/kWh"></label>
				</div>
				<div class="row justify-content-center regularTextSize vaRow">
					<button type="button" class="btn btn-secondary mr-3 priceLess"><i class="fa fa-minus-square"></i></button>
					Preis
					<button type="button" class="btn btn-secondary ml-3 priceMore"><i class="fa fa-plus-square"></i></button>
				</div>
			</div>  <!-- priceBasedCharging -->
			<hr class="border-secondary">
			<div class="row justify-content-center">
				<h3 class="font-weight-bold text-center text-lightgrey">Sofortladen Stromstärke</h3>
			</div>

			<div class="form-row form-group mb-1 vaRow regularTextSize" data-lp="1">
				<label for="lp/1/current" class="col-3 col-form-label text-right"><span class="nameLp">LP1</span>:</label>
				<div class="col">
					<input type="range" class="form-control-range rangeInput" id="lp/1/current" min="6" max="32" step="1" value="6" data-initialized="0" data-topicprefix="openWB/config/get/sofort/">
				</div>
				<label for="lp/1/current" class="col-3 col-form-label valueLabel" suffix="A"></label>
			</div>
			<div class="form-row form-group mb-1 vaRow regularTextSize" data-lp="2">
				<label for="lp/2/current" class="col-3 col-form-label text-right"><span class="nameLp">LP2</span>:</label>
				<div class="col">
					<input type="range" class="form-control-range rangeInput" id="lp/2/current" min="6" max="32" step="1" value="6" data-initialized="0" data-topicprefix="openWB/config/get/sofort/">
				</div>
				<label for="lp/2/current" class="col-3 col-form-label valueLabel" suffix="A"></label>
			</div>
			<div class="form-row form-group mb-1 vaRow regularTextSize" data-lp="3">
				<label for="lp/3/current" class="col-3 col-form-label text-right"><span class="nameLp">LP3</span>:</label>
				<div class="col">
					<input type="range" class="form-control-range rangeInput" id="lp/3/current" min="6" max="32" step="1" value="6" data-initialized="0" data-topicprefix="openWB/config/get/sofort/">
				</div>
				<label for="lp/3/current" class="col-3 col-form-label valueLabel" suffix="A"></label>
			</div>

			<div class="chargeLimitation" data-lp="1">
				<hr class="border-secondary">
				<div class="row justify-content-center">
					<h3 class="font-weight-bold text-center text-lightgrey">Lademengenbegrenzung <span class="nameLp"></span></h3>
				</div>
				<div class="form-row vaRow form-group mt-1 justify-content-center" data-lp="1">
					<div class="col btn-group btn-group-toggle" id="lp/1/chargeLimitation" data-toggle="buttons" data-topicprefix="openWB/config/get/sofort/">
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/1/chargeLimitation" data-option="0"> keine
						</label>
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/1/chargeLimitation" data-option="1"> Energiemenge
						</label>
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/1/chargeLimitation" data-option="2"> EV-SoC
						</label>
					</div>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize" data-option="1">
					<label for="lp/1/energyToCharge" class="col-3 col-form-label text-right">Energie:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="lp/1/energyToCharge" min="2" max="100" step="2" value="2" data-topicprefix="openWB/config/get/sofort/">
					</div>
					<label for="lp/1/energyToCharge" class="col-3 col-form-label valueLabel" suffix="kWh"></label>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize" data-option="2">
					<label for="lp/1/socToChargeTo" class="col-3 col-form-label text-right">SoC:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="lp/1/socToChargeTo" min="5" max="100" step="5" value="5" data-topicprefix="openWB/config/get/sofort/">
					</div>
					<label for="lp/1/socToChargeTo" class="col-3 col-form-label valueLabel" suffix="%"></label>
				</div>
				<div class="form-row mt-2 justify-content-center regularTextSize" data-option="1">
					<div class="col col-sm-6">
						<span class="progress-label">Fortschritt: </span>
						<span class="restzeitLp pull-right"></span>
						<div class="progress active limitation-progress">
							<div class="progress-bar progress-bar-success progress-bar-striped" role="progressbar" data-actualCharged="0">
							</div>
						</div>
					</div>
					<input class="btn btn-sm btn-primary regularTextSize ml-2" type="button" id="lp/1/resetEnergyToCharge" value="Reset" data-topicprefix="openWB/config/get/sofort/">
				</div>
			</div>

			<div class="chargeLimitation" data-lp="2">
				<hr class="border-secondary">
				<div class="row justify-content-center">
					<h3 class="font-weight-bold text-center text-lightgrey">Lademengenbegrenzung <span class="nameLp"></span></h3>
				</div>
				<div class="form-row vaRow form-group mt-1 justify-content-center" data-lp="2">
					<div class="col btn-group btn-group-toggle" id="lp/2/chargeLimitation" data-toggle="buttons" data-topicprefix="openWB/config/get/sofort/">
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/2/chargeLimitation" data-option="0"> keine
						</label>
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/2/chargeLimitation" data-option="1"> Energiemenge
						</label>
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/2/chargeLimitation" data-option="2"> EV-SoC
						</label>
					</div>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize" data-option="1">
					<label for="lp/2/energyToCharge" class="col-3 col-form-label text-right">Energie:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="lp/2/energyToCharge" min="2" max="100" step="2" value="2" data-topicprefix="openWB/config/get/sofort/">
					</div>
					<label for="lp/2/energyToCharge" class="col-3 col-form-label valueLabel" suffix="kWh"></label>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize" data-option="2">
					<label for="lp/2/socToChargeTo" class="col-3 col-form-label text-right">SoC:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="lp/2/socToChargeTo" min="5" max="100" step="5" value="5" data-topicprefix="openWB/config/get/sofort/">
					</div>
					<label for="lp/2/socToChargeTo" class="col-3 col-form-label valueLabel" suffix="%"></label>
				</div>
				<div class="form-row mt-2 justify-content-center regularTextSize" data-option="1">
					<div class="col col-sm-6">
						<span class="progress-label">Fortschritt: </span>
						<span class="restzeitLp pull-right"></span>
						<div class="progress active limitation-progress">
							<div class="progress-bar progress-bar-success progress-bar-striped" role="progressbar" data-actualCharged="0">
							</div>
						</div>
					</div>
					<input class="btn btn-sm btn-primary regularTextSize ml-2" type="button" id="lp/2/resetEnergyToCharge" value="Reset" data-topicprefix="openWB/config/get/sofort/">
				</div>
			</div>

			<div class="chargeLimitation" data-lp="3">
				<hr class="border-secondary">
				<div class="row justify-content-center">
					<h3 class="font-weight-bold text-center text-lightgrey">Lademengenbegrenzung <span class="nameLp"></span></h3>
				</div>
				<div class="form-row vaRow form-group mt-1 justify-content-center" data-lp="3">
					<div class="col btn-group btn-group-toggle" id="lp/3/chargeLimitation" data-toggle="buttons" data-topicprefix="openWB/config/get/sofort/">
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/3/chargeLimitation" data-option="0"> keine
						</label>
						<label class="btn btn-sm btn-outline-info btn-toggle regularTextSize">
							<input type="radio" name="lp/3/chargeLimitation" data-option="1"> Energiemenge
						</label>
					</div>
				</div>
				<div class="form-row form-group mb-1 vaRow regularTextSize" data-option="1">
					<label for="lp/3/energyToCharge" class="col-3 col-form-label text-right">Energie:</label>
					<div class="col">
						<input type="range" class="form-control-range rangeInput" id="lp/3/energyToCharge" min="2" max="100" step="2" value="2" data-topicprefix="openWB/config/get/sofort/">
					</div>
					<label for="lp/3/energyToCharge" class="col-3 col-form-label valueLabel" suffix="kWh"></label>
				</div>
				<div class="form-row mt-2 justify-content-center regularTextSize" data-option="1">
					<div class="col col-sm-6">
						<span class="progress-label">Fortschritt: </span>
						<span class="restzeitLp pull-right"></span>
						<div class="progress active limitation-progress">
							<div class="progress-bar progress-bar-success progress-bar-striped" role="progressbar" data-actualCharged="0">
							</div>
						</div>
					</div>
					<input class="btn btn-sm btn-primary regularTextSize ml-2" type="button" id="lp/3/resetEnergyToCharge" value="Reset" data-topicprefix="openWB/config/get/sofort/">
				</div>
			</div>
		</form>

		<!-- modal chargemode-select-window -->
		<div class="modal fade" id="chargeModeModal">
			<div class="modal-dialog">
				<div class="modal-content">

					<!-- modal header -->
					<div class="modal-header bg-success">
						<h4 class="modal-title">Lademodus-Auswahl</h4>
					</div>

					<!-- modal body -->
					<div class="modal-body">
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button id="chargeModeSofortBtn" type="button" class="chargeModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" chargeMode="0">Sofort</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 order-first order-sm-last py-1">
								<button id="chargeModePVBtn" type="button" class="chargeModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" chargeMode="2">PV</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button id="chargeModeMinPVBtn" type="button" class="chargeModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" chargeMode="1">Min + PV</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button id="chargeModeStdbyBtn" type="button" class="chargeModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" chargeMode="4">Standby</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button id="chargeModeStopBtn" type="button" class="chargeModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" chargeMode="3">Stop</button>
							</div>
						</div>
						<div id="priorityModeBtns" class="hide">
							<hr>
							<div class="row">
								<div class="col text-center text-grey">
									Vorrang im Lademodus PV-Laden:
								</div>
							</div>
							<div class="row justify-content-center">
								<div class="col-sm-5 py-1">
									<button id="evPriorityBtn" type="button" class="priorityModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" priority="1">
										EV <span class="fas fa-car">&nbsp;</span>
									</button>
								</div>
							</div>
							<div class="row justify-content-center">
								<div class="col-sm-5 py-1">
									<button id="batteryPriorityBtn" type="button" class="priorityModeBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal" priority="0">
										Speicher <span class="fas fa-car-battery">&nbsp;</span>
									</button>
								</div>
							</div>
						</div>
						<div id="70ModeBtn" class="hide">
							<hr>
							<div class="row">
								<div class="col text-center text-grey">
									70% beachten im Lademodus PV-Laden:
								</div>
							</div>
							<div class="row justify-content-center">
								<div class="col-sm-5 py-1">
									<button id="70PvBtn" type="button" class=" 70PvBtn btn btn-lg btn-block btn-secondary" data-dismiss="modal">
										70 % beachten
									</button>
								</div>
							</div>
						</div>

					</div> <!-- /modal body -->

					<!-- no modal footer -->
				</div>
			</div>
		</div>

		<!-- modal SoC-window -->
		<div class="modal fade" id="socModal">
			<div class="modal-dialog">
				<div class="modal-content">
					<!-- modal header -->
					<div class="modal-header bg-warning">
						<h4 class="modal-title text-dark">Manuelle SoC-Eingabe - Ladepunkt <span class="socLp"></span></h4>
					</div>
					<!-- modal body -->
					<div class="modal-body">
						<div class="row justify-content-center">
							<div class="col-2 px-1 py-1">
								<button type="button" id="manualSocDecrement" class="btn btn-block btn-secondary">-</button>
							</div>
							<div class="col-5 py-1">
								<div class="input-group">
									<input id="manualSocBox" type="number" min="0" max="100" step="1" value="0" name="socBox" class="form-control text-right">
									<div class="input-group-append">
										<div class="input-group-text">
											%
										</div>
									</div>
								</div>
							</div>
							<div class="col-2 px-1 py-1">
								<button type="button" id="manualSocIncrement" class="btn btn-block btn-secondary">+</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button type="button" id="manualSocOk" class="btn btn-lg btn-block btn-success" data-dismiss="modal">Übernehmen</button>
							</div>
						</div>
						<div class="row justify-content-center">
							<div class="col-sm-5 py-1">
								<button type="button" id="manualSocCancel" class="btn btn-lg btn-block btn-secondary" data-dismiss="modal">Abbrechen</button>
							</div>
						</div>
					</div>
				</div>
			</div>
			<script>
				function clearSocForm(){
					$("#manualSocBox").val("0");
				}

				function submitSocForm() {
					var currentLp = $('#socModal').find('.socLp').text();
					var manualSoc = $("#manualSocBox").val();
					// console.log("SoC for LP"+currentLp+": "+manualSoc);
					publish(manualSoc, "openWB/set/lp/"+currentLp+"/manualSoc");
					// reset input after publishing
					clearSocForm();
				};
				$(document).ready(function(){

					$('#manualSocDecrement').click(function() {
						var newValue = parseInt($('#manualSocBox').val()) - 1;
						if( newValue < 0 ){
							newValue = 0;
						}
						$('#manualSocBox').val(newValue);
					});

					$('#manualSocIncrement').click(function() {
						var newValue = parseInt($('#manualSocBox').val()) + 1;
						if( newValue > 100 ){
							newValue = 100;
						}
						$('#manualSocBox').val(newValue);
					});

					$('#manualSocCancel').click(function() {
						clearSocForm();
					});

					$('#manualSocOk').click(function() {
						submitSocForm();
					});

				});
			</script>
		</div>

		<!-- modal reset-gauge-limits-window -->
		<div class="modal fade" id="resetGaugeLimitsModal" role="dialog">
			<div class="modal-dialog" role="document">
				<div class="modal-content">
					<!-- modal header -->
					<div class="modal-header bg-danger">
						<h4 class="modal-title text-light">Achtung</h4>
					</div>
					<!-- modal body -->
					<div class="modal-body text-center text-black">
						<p>
							Sollen die Limits für diese Gauge wirklich zurückgesetzt werden?
						</p>
					</div>
					<!-- modal footer -->
					<div class="modal-footer d-flex justify-content-center">
						<button type="button" class="btn btn-success" data-dismiss="modal" id="resetGaugeLimitsBtn" data-gaugeID="">Fortfahren</button>
						<button type="button" class="btn btn-danger" data-dismiss="modal" id="resetGaugeLimitsCancelBtn">Abbruch</button>
					</div>
				</div>
			</div>
		</div>
	</div>


	<script>
		var defaultScaleCounter = 8640;  // ca. 12 Stunden Gauge Auto-Rescale

		// load navbar, be careful: it loads asynchronous
		$.get(
			{ url: "themes/navbar.html", cache: false },
			function(data){
				$("#nav-placeholder").replaceWith(data);
			}
		);

		var timeOfLastMqttMessage = 0;  // holds timestamp of last received message
		var landingpageShown = false;  // holds flag for landing page being shown

		function chargeLimitationOptionsShowHide(btnGrp, option) {
			// show/hide all option-parameters in form-rows for selected option
			var parent = btnGrp.closest('.chargeLimitation[data-lp]');  // get parent div element for charge limitation options
			$(parent).find('.form-row[data-option*=' + option + ']').show();  // now show option elements for selected option
			$(parent).find('.form-row[data-option]').not('[data-option*=' + option + ']').hide();  // hide all other option elements
		}

		function processPreloader(mqttTopic) {
			// sets flag for topic received in topic-array
			// and updates the preloader progress bar
			if ( !landingpageShown ) {
				var countTopicsReceived = 0;
				for ( var index = 0; index < topicsToSubscribe.length; index ++) {
					if ( topicsToSubscribe[index][0] == mqttTopic && topicsToSubscribe[index][1] == 0 ) {
						// topic found in array
						topicsToSubscribe[index][1] = 1;  // mark topic as received
					};
					if ( topicsToSubscribe[index][1] > 0 ) {
						countTopicsReceived++;
					}
				};
				// countTopicsToBeReceived holds all topics flagged 1 and not only those for preloader
				countTopicsReceived = countTopicsReceived - countTopicsNotForPreloader;
				var countTopicsToBeReceived = topicsToSubscribe.length - countTopicsNotForPreloader;
				var percentageReceived = (countTopicsReceived / countTopicsToBeReceived * 100).toFixed(0);
				var timeBetweenTwoMessages = Date.now() - timeOfLastMqttMessage;
				if ( timeBetweenTwoMessages > 3000 ) {
					// latest after 3 sec without new messages
					percentageReceived = 100;
					// debug output
					topicsToSubscribe.forEach((item, i) => {
						if ( item[1] == 0 ) {
							console.log('not received: ' + item[0]);
						}
					});

				}
				timeOfLastMqttMessage = Date.now();
				$("#preloaderbar").width(percentageReceived+"%");
				$("#preloaderbar").text(percentageReceived+" %");
				if ( percentageReceived == 100 ) {
					landingpageShown = true;
					setTimeout(function (){
						// delay a little bit
						$("#preloader").fadeOut(1000);
					}, 500);
				}
			}
		}

		var delayUserInput = (function () {
			// sets a timeout on call and resets timeout if called again for same id before timeout fires
			var timeoutHandles = {};
			return function (id, callback, ms) {
				if ( timeoutHandles[id] ) {
					clearTimeout(timeoutHandles[id]);
				};
				timeoutHandles[id] = setTimeout(function(){
					delete timeoutHandles[id];
					callback(id);
				}, ms);
			};
		})();

		function getScaleCookie (cookie) {
			// reads cookie for gauge-scale and returns default if not set
			var cookieValue = getCookie(cookie);
			if ( isNaN (parseInt(cookieValue)) ) {
				return 1000;
			} else {
				return cookieValue;
			}
		}

		function setGaugeInitialMinMax(gauge) {
			gauge.max = getScaleCookie('GaugesScaleMax_' + gauge.id);
			if ( gauge.isSymmetric ) {
				gauge.min = gauge.max * -1;
			}
			// farbigen Rand anpassen
			gauge.set('colorsRanges', [[gauge.min, 0, 'red', 3], [0, gauge.max, 'green', 3]]);
			// Labels in kW
			gauge.set('labelsSpecific', [(gauge.min/gauge.scaleBase), ((gauge.max-Math.abs(gauge.min))/(2*gauge.scaleBase)), (gauge.max/gauge.scaleBase)]);
			gauge.grow()
		}

		function updateGaugeValue(gauge, value, text) {
			// gauge: zu erneuernde Gauge
			// value: neuer Wert
			// text: ggf. neuer Text
			if( isNaN(parseFloat(value)) ){
				// es wurde keine Zahl als Wert übergeben
					return;  // gleich wieder zurück
			}
			var needsScaling = false;
			var newGaugeMax = Math.ceil((Math.abs(value) / gauge.scaleBase)) * gauge.scaleBase;
			if ( gauge.max < newGaugeMax ) {
				// benötigtes Maximum ist größer als Skala
				gauge.max = newGaugeMax;  // Skala positiv anpassen
				gauge.scaleCounter = defaultScaleCounter;  // Counter reset
				needsScaling = true;
				if ( !gauge.autoRescale ) {
					// neues Maximum der Gauge als Cookie speichern
					setCookie('GaugesScaleMax_' + gauge.id, newGaugeMax, 365);
				}
			} else if ( gauge.max > newGaugeMax ) {
				// Skala ist aktuell eigentlich zu groß
				if ( gauge.autoRescale ) {
					// und Anpassung soll automatisch erfolgen
					gauge.scaleCounter -= 1; // dann Counter reduzieren
					if ( gauge.scaleCounter == 0 ) {
						// wenn Zeit rum
						gauge.scaleCounter = defaultScaleCounter;  // Counter reset
						gauge.max = gauge.max-(Math.ceil((gauge.max-newGaugeMax) / (2 * gauge.scaleBase)) * gauge.scaleBase);  // Skala anpassen
						needsScaling = true;
					}
				}
			} else {
				// Skala soll bleiben, keine automatische Anpassung
				if ( gauge.scaleCounter < defaultScaleCounter ) {
					// aber Zähler zum Wechsel ist schon angelaufen
					gauge.scaleCounter = defaultScaleCounter;  // Counter reset
				}
			}
			if ( needsScaling ) {
				// wenn Skala angepasst werden muss
				if ( gauge.isSymmetric ) {
					// bei symmetrischer Gauge die negative Skala angleichen
					gauge.min = gauge.max * -1;
				}
				// farbigen Rand anpassen
				gauge.set('colorsRanges', [[gauge.min, 0, 'red', 3], [0, gauge.max, 'green', 3]]);
				// Labels in kW
				gauge.set('labelsSpecific', [(gauge.min/gauge.scaleBase), ((gauge.max-Math.abs(gauge.min))/(2*gauge.scaleBase)), (gauge.max/gauge.scaleBase)]);
			}
			// neuen Wert für Gauge setzen, ggf. Text im Label ändern
			gauge.value = value;
			if ( gauge.setText ) {
				gauge.set('titleBottom', text);
				// Farben der Schrift ggf. anpassen
				if ( value < 0 ) {
					gauge.set('titleBottomColor', 'red');
				} else {
					gauge.set('titleBottomColor', 'green');
				}
			}
			// und Anzeige erneuern
			gauge.grow();
		}

		function prepareGauges() {
			// prepares all gauges and their settings for ui
			responsiveGaugeSettings = [
				{maxWidth: 400, width: 145, height: 145,
					options: {
						radius:65, marginTop: 30, shadowBlur: 3, titleTopPos: 0.28,
						titleTopSize: 7, titleBottomSize: 6, labelsValueSize: 10, labelsSize: 8
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				},
				{maxWidth: 575, width: 155, height: 155,
					options: {
						radius: 70, marginTop: 30, shadowBlur: 3, titleTopPos: 0.3,
						titleTopSize: 7, titleBottomSize: 7, labelsValueSize: 10, labelsSize: 8
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				},
				{maxWidth: 767, width: 220, height: 220,
					options: {
						radius: 95, marginTop: 20, shadowBlur: 5, titleTopPos: 0.4,
						titleTopSize: 11, titleBottomSize: 8, labelsValueSize: 10, labelsSize: 11
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				},
				{maxWidth: 991, width: 150, height: 150,
					options: {
						radius: 72, marginTop: 35, shadowBlur: 4, titleTopPos: 0.30,
						titleTopSize: 10, titleBottomSize: 8, labelsValueSize: 11, labelsSize: 9
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				},
				{maxWidth: 1199, width: 200, height: 200,
					options: {
						radius: 92, marginTop: 35, shadowBlur: 6, titleTopPos: 0.36,
						titleTopSize: 12, titleBottomSize: 9, labelsValueSize: 12, labelsSize: 11
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				},
				{maxWidth: null, width: 220, height: 220,
					options: {
						radius: 102, marginTop: 35, shadowBlur: 6, titleTopPos: 0.38,
						titleTopSize: 14, titleBottomSize: 10, labelsValueSize: 13, labelsSize: 13
					},
					callback: function (obj){
						if ( obj.autoScale ) {
							setGaugeInitialMinMax(obj);
						}
					}
				}
			];

			gaugePV = new RGraph.Gauge({
				id: 'pvData',
				min: 0,
				max: 1000,
				value: 0,
				options: {
					marginLeft: 0,
					marginRight: 0,
					titleTop: 'kW',
					labelsCount: 2,
					labelsSpecific: ['0', '0.5', '1'],
					tickmarksLarge: 4,
					tickmarksSmall: 20,
					shadow: true,
					shadowColor: '#E9E9E9',
					backgroundColor: 'Gradient(white:#BEFEBE)',
					borderWidth: 1,
					borderInner: '#739B73',
					centerpinColor: '#8E8E8B',
					labelsValue: true,
					labelsValueBounding: false,
					labelsValueUnitsPost: ' W',
					labelsValueBold: true,
					labelsValueItalic: true,
					titleBottomPos: 0.61,
					titleBottomBold: true,
					adjustable: false,
					textAccessible: false,
					colorsRanges: [[0, 1000, 'green', 3]],
					anglesStart: RGraph.PI - 0.55,
					anglesEnd: RGraph.TWOPI + 0.55
				}
			}).draw().responsive(responsiveGaugeSettings);
			gaugePV.scaleCounter = defaultScaleCounter;  // Attribut zur Gauge hinzufügen
			gaugePV.isSymmetric = false;  // nur Werte > 0
			gaugePV.autoScale = true;  // Skalierung automatisch vergrößern
			gaugePV.autoRescale = false;  // neue Skalierung wird nicht von selbst wieder verkleinert
			gaugePV.setText = false;  // Text und Farbe des Labels anpassen
			gaugePV.scaleBase = 1000;  // 1000 W ist Basisgröße

			// Add the context menu click listener
			gaugePV.canvas.ondblclick = function (e)
			{
				e.stopPropagation();  // Stops the window.dblclick event from firing
				var gaugeID = e.srcElement.__object__.id;
				if ( gaugeID == 'pvData' ) {
					$("#resetGaugeLimitsBtn").data("gaugeID", gaugeID);
					$("#resetGaugeLimitsModal").modal("show");  // if resetGaugeLimitsBtn is clicked, event handler will reset limits
				}
			}

			gaugeBatt = new RGraph.Gauge({
				id: 'battData',
				min: -1000,
				max: 1000,
				value: 0,
				options: {
					marginLeft: 0,
					marginRight: 0,
					titleTop: 'kW',
					labelsCount: 2,
					labelsSpecific: ['-1', '0', '1'],
					tickmarksLarge: 4,
					tickmarksSmall: 20,
					shadow: true,
					shadowColor: '#E9E9E9',
					backgroundColor: 'Gradient(white:#FCBE1E)',
					borderWidth: 1,
					borderInner: '#BA8C16',
					centerpinColor: '#8E8E8B',
					labelsValue: true,
					labelsValueBounding: false,
					labelsValueUnitsPost: ' W',
					labelsValueBold: true,
					labelsValueItalic: true,
					titleBottomPos: 0.61,
					titleBottomBold: true,
					adjustable: false,
					textAccessible: false,
					colorsRanges: [[-1000, 0, 'red', 3], [0, 1000, 'green', 3]],
					anglesStart: RGraph.PI - 0.55,
					anglesEnd: RGraph.TWOPI + 0.55
				}
			}).draw().responsive(responsiveGaugeSettings);
			gaugeBatt.scaleCounter = defaultScaleCounter;  // Attribut zur Gauge hinzufügen
			gaugeBatt.isSymmetric = true;  // Werte +-
			gaugeBatt.autoScale = true;  // Skalierung automatisch vergrößern
			gaugeBatt.autoRescale = false;  // neue Skalierung wird nicht von selbst wieder verkleinert
			gaugeBatt.setText = false;  // Text und Farbe des Labels anpassen
			gaugeBatt.scaleBase = 1000;  // 1000 W ist Basisgröße

			gaugeEVU = new RGraph.Gauge({
				id: 'evuData',
				min: -1000,
				max: 1000,
				value: 0,
				options: {
					marginLeft: 0,
					marginRight: 0,
					titleTop: 'kW',
					labelsCount: 2,
					labelsSpecific: ['-1', '0', '1'],
					tickmarksLarge: 4,
					tickmarksSmall: 20,
					shadow: true,
					shadowColor: '#E9E9E9',
					backgroundColor: 'Gradient(white:#FEBEBE)',
					borderWidth: 1,
					borderInner: '#A07676',
					centerpinColor: '#8E8E8B',
					labelsValue: true,
					labelsValueBounding: false,
					labelsValueUnitsPost: ' W',
					labelsValueBold: true,
					labelsValueItalic: true,
					labelsValueSize: 17,
					titleBottomPos: 0.61,
					titleBottomBold: true,
					titleBottomSize: 11,
					adjustable: false,
					textAccessible: false,
					colorsRanges: [[-1000, 0, 'red', 3], [0, 1000, 'green', 3]],
					anglesStart: RGraph.PI - 0.55,
					anglesEnd: RGraph.TWOPI + 0.55
				}
			}).draw().responsive(responsiveGaugeSettings);
			gaugeEVU.scaleCounter = defaultScaleCounter;  // Attribut zur Gauge hinzufügen
			gaugeEVU.isSymmetric = true;  // Werte +-
			gaugeEVU.autoScale = true;  // Skalierung automatisch vergrößern
			gaugeEVU.autoRescale = false;  // neue Skalierung wird nicht von selbst wieder verkleinert
			gaugeEVU.setText = true;  // Text und Farbe des Labels anpassen
			gaugeEVU.scaleBase = 1000;  // 1000 W ist Basisgröße

			gaugeEVU.canvas.ondblclick = function (e)
			{
				e.stopPropagation();  // Stops the window.ondblclick event from firing
				var gaugeID = e.srcElement.__object__.id;
				if ( gaugeID == 'evuData' ) {
					$("#resetGaugeLimitsBtn").data("gaugeID", gaugeID);
					$("#resetGaugeLimitsModal").modal("show");  // if resetGaugeLimitsBtn is clicked, event handler will reset limits
				}
			}

			gaugeHome = new RGraph.Gauge({
				id: 'homeData',
				min: 0,
				max: 1000,
				value: 0,
				options: {
					marginLeft: 0,
					marginRight: 0,
					titleTop: 'kW',
					labelsCount: 2,
					labelsSpecific: ['0', '0.5', '1'],
					tickmarksLarge: 4,
					tickmarksSmall: 20,
					shadow: true,
					shadowColor: '#E9E9E9',
					backgroundColor: 'Gradient(white:#B5F1FF)',
					borderWidth: 1,
					borderInner: '#6E939B',
					centerpinColor: '#8E8E8B',
					labelsValue: true,
					labelsValueBounding: false,
					labelsValueUnitsPost: ' W',
					labelsValueBold: true,
					labelsValueItalic: true,
					labelsValueSize: 17,
					titleBottomPos: 0.61,
					titleBottomBold: true,
					adjustable: false,
					textAccessible: false,
					colorsRanges: [[0, 1000, 'green', 3]],
					colorsRedWidth: 0,
					colorsYellowWidth: 0,
					anglesStart: RGraph.PI - 0.55,
					anglesEnd: RGraph.TWOPI + 0.55
				}
			}).draw().responsive(responsiveGaugeSettings);
			gaugeHome.scaleCounter = defaultScaleCounter;  // Attribut zur Gauge hinzufügen
			gaugeHome.isSymmetric = false;  // Werte > 0
			gaugeHome.autoScale = true;  // Skalierung automatisch vergrößern
			gaugeHome.autoRescale = true;  // neue Skalierung wird von selbst wieder verkleinert
			gaugeHome.setText = false;  // Text und Farbe des Labels nicht anpassen
			gaugeHome.scaleBase = 1000;  // 1000 W ist Basisgröße

			setGaugeInitialMinMax(gaugePV);
			setGaugeInitialMinMax(gaugeEVU);
			setGaugeInitialMinMax(gaugeBatt);
		}

		$(document).ready(function(){
			console.log('ready main');

			// load scripts synchronously in order specified
			var scriptsToLoad = [
				'js/Chart.bundle.min.js',					// load Chart.js library
				'js/chartjs-plugin-annotation.min.js',		// load Chart.js annotation plugin
				'js/mqttws31.js',							// load mqtt library
				'<?php echo xgeturl('helperFunctions.js');?>',		// some helper functions			
				'<?php echo xgeturl('setupMqttServices.js');?>',		// functions performing mqtt and start mqtt-service
				'<?php echo xgeturl('processAllMqttMsg.js');?>',		// functions for processing messages			
				'<?php echo xgeturl('livechart.js');?>',				// functions performing mqtt and start mqtt-service
				'<?php echo xgeturl('electricityPriceChart.js');?>' 	// functions performing mqtt and start mqtt-service
			];
			scriptsToLoad.forEach(function(src) {
				var script = document.createElement('script');
				script.src = src;
				script.async = false;
				document.body.appendChild(script);
			});

			prepareGauges();

			$('.enableLp').click(function(event){
				// send mqtt set to enable/disable charge point after click
				var lp = parseInt($(this).closest('[data-lp]').data('lp'));  // get attribute lp-# of parent element
				if ( !isNaN(lp) && lp > 0 && lp < 4 ) {
					var isEnabled = $(this).hasClass("lpEnabledStyle")
					if ( isEnabled ) {
						publish("0", "openWB/set/lp/" + lp + "/ChargePointEnabled");
					} else {
						publish("1", "openWB/set/lp/" + lp + "/ChargePointEnabled");
					}
				}
			});

			$('.socConfiguredLp').click(function(event){
				// send mqtt set to force reload of charge point SoC after click
				var lp = parseInt($(this).closest('[data-lp]').data('lp'));  // get attribute lp-# of parent element
				if ( !isNaN(parseInt(lp)) && lp > 0 && lp < 4 ) {
					if ( $(this).hasClass('manualSoC') ) {
						var currentSoc = $(this).find('.socLp').text();
						$('#socModal').find('.socLp').text(lp);
						$("#manualSocBox").val(currentSoc);
						$('#socModal').modal("show");
					} else {
						var spinner = $(this).find('.reloadLpSoc');
						var isRunning = spinner.hasClass("fa-spin");
						if ( !isRunning ) {
							spinner.addClass("fa-spin");
							publish("1", "openWB/set/lp/" + lp + "/ForceSoCUpdate");
						}
					}
				}
			});

			$('.enableDevice').click(function(event){
				// send mqtt set to enable/disable Device after click
				var dev = parseInt($(this).closest('[data-dev]').data('dev'));  // get attribute device-# of parent element
				var isLocked = $(this).hasClass("locked");
				if ( isLocked ) {
					if ( !isNaN(dev) && dev > 0 && dev < 10 ) {
						var isEnabled = $(this).hasClass("lpEnabledStyle")
						if ( isEnabled ) {
							publish("0", "openWB/config/set/SmartHome/Devices/" + dev + "/device_manual_control");
							$(this).removeClass('lpEnabledStyle').removeClass('lpDisabledStyle').addClass('lpWaitingStyle');
						} else {
							publish("1", "openWB/config/set/SmartHome/Devices/" + dev + "/device_manual_control");
							$(this).removeClass('lpEnabledStyle').removeClass('lpDisabledStyle').addClass('lpWaitingStyle');

						}
					}
				}
			});

			$('.changeSHMode').click(function(event){
				// send mqtt set to enable/disable Device after click
				var dev = parseInt($(this).closest('[data-dev]').data('dev'));  // get attribute device-# of parent element
				if ( $(this).text() == "Automatik" ) {
						publish("1", "openWB/config/set/SmartHome/Devices/" + dev + "/mode");
					} else {
						publish("0", "openWB/config/set/SmartHome/Devices/" + dev + "/mode");
				}
			});

			$('#chargeModeSelectBtn').click(function(event){
				$("#chargeModeModal").modal("show");
			});

			$('.chargeModeBtn').click(function(event){
				var chargeMode = $(this).attr("chargeMode")
				publish(chargeMode, "openWB/set/ChargeMode");
			});

			$('.priorityModeBtn').click(function(event){
				// priority: 0 = battery, 1 = ev
				var priority = $(this).attr('priority');
				if ( priority == '0' || priority == '1' ) {
					publish(priority, 'openWB/config/set/pv/priorityModeEVBattery');
				}
			});

			$('.70PvBtn').click(function(event){
				// 0 deaktiviert, 1 aktiviert
				var element = document.getElementById('70PvBtn');
				if ( element.classList.contains("btn-success") ) {
					publish("0", "openWB/set/pv/NurPV70Status");
				} else {
					publish("1", "openWB/set/pv/NurPV70Status");
				}
			});

			$('#resetGaugeLimitsBtn').click(function(event){
				var gaugeID = $("#resetGaugeLimitsBtn").data("gaugeID");
				if ( gaugeID == 'pvData' ) {
					setCookie('GaugesScaleMax_pvData', gaugePV.scaleBase, 365);
					document.location.reload(true);
				} else if ( gaugeID == 'evuData' ) {
					setCookie('GaugesScaleMax_evuData', gaugeEVU.scaleBase, 365);
					document.location.reload(true);
				}
			});

			$('#resetGaugeLimitsCancelBtn').click(function(event){
				$("#resetGaugeLimitsBtn").data("gaugeID", "");
			});

			$('.btn[value="Reset"]').click(function(event){
				var topic = getTopicToSendTo($(this).attr('id'));
				publish("1", topic);
			});

			$('.sofortladenLadezielSelektor').change(function(event){
				// switches the visibility of the settings-divs according to dropdown selection
				var selectorId = '#' + event.target.id;
				var divAusId = selectorId.slice(0, 8) + 'n' + selectorId.slice(8);
				var divSocId = selectorId.slice(0, 8) + 's' + selectorId.slice(8);
				var divMengeId = selectorId.slice(0, 8) + 'm' + selectorId.slice(8);
				switch ($(selectorId).val()) {
					case '0':
						$(divAusId).removeClass('hide');
						$(divSocId).addClass('hide');
						$(divMengeId).addClass('hide');
						break;
					case '1':
						$(divAusId).addClass('hide');
						$(divSocId).addClass('hide');
						$(divMengeId).removeClass('hide');
						break;
					case '2':
						$(divAusId).addClass('hide');
						$(divSocId).removeClass('hide');
						$(divMengeId).addClass('hide');
						break;
				}
			});

			$('.btn-group-toggle').change(function(event){
				// only charge limitation has class btn-group-toggle so far
				// option: 0 = keine, 1 = Energiemenge, 2 = EV-SoC
				var elementId = $(this).attr('id');
				var option = $('input[name="' + elementId + '"]:checked').data('option').toString();
				var topic = getTopicToSendTo(elementId);
				publish(option, topic);
				// show/hide respective option-values and progress
				chargeLimitationOptionsShowHide(this, option);
			});

			$('.priceMore, .priceLess').click(function(event){
				// change Slider upon click on buttons
				event.preventDefault();
				var currentMaxPrice = parseFloat($('#MaxPriceForCharging').val());
				var rangeMin = parseFloat($('#MaxPriceForCharging').attr('min'));
				var rangeMax = parseFloat($('#MaxPriceForCharging').attr('max'));
				var step = parseFloat($('#MaxPriceForCharging').attr('step'));
				if ( $(this).hasClass ('priceLess') ) {
					currentMaxPrice -= step;
				} else {
					currentMaxPrice += step;
				}
				// prevent timeout of delayUserInput when clicking "beyond" range
				if ( currentMaxPrice < rangeMin ) {
					currentMaxPrice = rangeMin;
				} else if ( currentMaxPrice > rangeMax ) {
					currentMaxPrice = rangeMax;
				}
				$('#MaxPriceForCharging').val(currentMaxPrice);
				$('#MaxPriceForCharging').trigger('input');
			});

			$('.rangeInput').on('input', function() {
				// show slider value in label of class valueLabel
				var elementId = $(this).attr('id');
				updateLabel(elementId);
				var element = $('#' + $.escapeSelector(elementId));
				var label = $('label[for="' + elementId + '"].valueLabel');
				label.addClass('text-danger');
				 if ( $.escapeSelector(elementId) == 'MaxPriceForCharging') {
					// marks times in the price chart where the price is low enough so charging would be allowed
	 				var priceAnnotations = createPriceAnnotations();
	 			 	electricityPricechart.options.annotation.annotations = priceAnnotations;
	 			 	electricityPricechart.update();
				 }
				delayUserInput(elementId, function (id) {
					// gets executed on callback, 2000ms after last input-change
					// changes label color back to normal and sends input-value by mqtt
					var elem = $('#' + $.escapeSelector(id));
					var value = elem.val();
					var topic = getTopicToSendTo(id);
					publish(value, topic);
					var label = $('label[for="' + id + '"].valueLabel');
					label.removeClass('text-danger');
					// if rangeInput is for chargeLimitation, recalculate progress
					if ( id.includes('/energyToCharge') ) {
						var parent = elem.closest('.chargeLimitation')  // get parent div element for charge limitation
						var element = parent.find('.progress-bar');  // now get parents progressbar
						var actualCharged = element.data('actualCharged');  // get stored value
						if ( isNaN(parseFloat(actualCharged)) ) {
							actualCharged = 0;  // minimum value
						}
						var progress = (actualCharged / value * 100).toFixed(0);
						element.width(progress+"%");
					}
				}, 2000);
			});

			// register an event listener for changes in visibility
			let hidden;
			let visibilityChange;
			if (typeof document.hidden !== 'undefined') { // Opera 12.10 and Firefox 18 and later support
				hidden = 'hidden';
				visibilityChange = 'visibilitychange';
			} else if (typeof document.msHidden !== 'undefined') {
				hidden = 'msHidden';
				visibilityChange = 'msvisibilitychange';
			} else if (typeof document.webkitHidden !== 'undefined') {
				hidden = 'webkitHidden';
				visibilityChange = 'webkitvisibilitychange';
			}
			window.document.addEventListener(visibilityChange, () => {
				if (!document[hidden]) {
					// once page is unhidden... reload graph completely
					initialread = 0;
					all1 = 0;
					all2 = 0;
					all3 = 0;
					all4 = 0;
					all5 = 0;
					all6 = 0;
					all7 = 0;
					all8 = 0;
					all9 = 0;
					all10 = 0;
					all11 = 0;
					all12 = 0;
					all13 = 0;
					all14 = 0;
					all15 = 0;
					all16 = 0;

					subscribeMqttGraphSegments();
				}
			});

			$("#homebutton").addClass("hide");

		});  // end document ready
	</script>


<?php
	 if($dbdeb>0)
	 {
		$lines="striped";
		$owbconf="striped";
   		makedebugreihe();
	 }
?>

	<div id="footer">
		<footer class="bg-dark fixed-bottom small text-light">
			<div class="container text-center">
				openWB_lite <span id='spanversion' class='spanversion'></span>, die modulare Wallbox
			</div>
		</footer>
	</div>



</body>

</html>
