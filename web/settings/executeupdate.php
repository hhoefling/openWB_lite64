<?php
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
	error_log('Diese Seite muss als HTTP-POST aufgerufen werden.');
	exit('Diese Seite muss als HTTP-POST aufgerufen werden.');
}

function  getdateurl($dir,$file)
	{
 			$fn=sprintf('%s/%s', $dir,$file);
			$ftime=filemtime("./$file");
			return sprintf('%s?w=%d' , $fn,$ftime);
	
 	}
?>
<!DOCTYPE html>
<html lang="de">

	<head>
		<base href="/openWB/web/">

		<meta charset="UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>openWB Update</title>
		<meta name="author" content="Kevin Wieland, Michael Ortenstein" />
		<!-- Favicons (created with http://realfavicongenerator.net/)-->
		<link rel="apple-touch-icon" sizes="57x57" href="img/favicons/apple-touch-icon-57x57.png">
		<link rel="apple-touch-icon" sizes="60x60" href="img/favicons/apple-touch-icon-60x60.png">
		<link rel="icon" type="image/png" href="img/favicons/favicon-32x32.png" sizes="32x32">
		<link rel="icon" type="image/png" href="img/favicons/favicon-16x16.png" sizes="16x16">
		<link rel="manifest" href="manifest.json">
		<link rel="shortcut icon" href="img/favicons/favicon.ico">
		<meta name="msapplication-TileColor" content="#00a8ff">
		<meta name="msapplication-config" content="img/favicons/browserconfig.xml">
		<meta name="theme-color" content="#ffffff">

		<!-- Bootstrap -->
		<link rel="stylesheet" type="text/css" href="css/bootstrap-4.4.1/bootstrap.min.css">
		<!-- Normalize -->
		<link rel="stylesheet" type="text/css" href="css/normalize-8.0.1.css">
		<!-- include settings-style -->
		<link rel="stylesheet" type="text/css" href="css/settings_style.css">

		<!-- important scripts to be loaded -->
		<script src="js/jquery-3.6.0.min.js"></script>
		<script src="js/bootstrap-4.4.1/bootstrap.bundle.min.js"></script>
		<!-- load helper functions -->
		<script src = "<?php echo getdateurl('settings','helperFunctions.js');?>"></script>
		
	</head>

	<body>

		<header>
			<!-- Fixed navbar -->
			<nav class="navbar navbar-expand-sm bg-dark navbar-dark fixed-top">
				<div class="navbar-brand">
					openWB
				</div>
			</nav>
		</header>

		<div role="main" class="container" style="margin-top:20px">

			<div class="card border-secondary">
				<div class="card-header bg-secondary">
					Update
				</div>
				<div class="card-body">
					<div id="infoText" class="alert alert-info"></div>
					<div class="row">
						<div class="cssload-loader text-center">
							<div class="cssload-inner cssload-one"></div>
							<div class="cssload-inner cssload-two"></div>
							<div class="cssload-inner cssload-three"></div>
						</div>
					</div>
				</div>
			</div>

		</div>  <!-- container -->

		<footer class="footer bg-dark text-light font-small">
			<div class="container text-center">
				<small>Sie befinden sich hier: System/Update</small>
			</div>
		</footer>

		<script>
			$(document).ready(function(){
				infoText = $("#infoText");

				infoText.text("Update der openWB angefordert...");

				$.post({ url: "settings/updatePerformNow.php", cache: false }).done(function() {
					infoText.text("Update läuft... bitte warten, die Weiterleitung erfolgt automatisch.");
					infoText.removeClass("alert-info");
					infoText.addClass("alert-success");
					setTimeout(function() { window.location.href = "index.php"; }, 20000);
				});

			});
		</script>

	</body>
</html>
