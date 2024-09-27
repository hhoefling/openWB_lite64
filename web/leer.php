<?php

require_once("includes/site_conf.inc");
require_once("includes/globs.inc");
require_once("includes/users.inc");

 Log2File('Leer.php');
 simpleheader();
 
 if($dbdeb<2)
    echo "<meta http-equiv=\"refresh\" content=\"10; url=./index.php\">";


 if ( $_CURRENT_USER->id <= 0 )
	echo "<div><h2>Bitte anmelden</h2></div>";
 else 
	echo "<div>Hallo ". $_CURRENT_USER->username . "</div>";
 echo '<br><a href="./index.php">Weiter.. index.php.</a>';			
 echo '<br><a href="./logon.php">Logon</a>';			
 echo '<br><a href="./logoff.php">logoff</a>';			
 echo '<br><a href="./themes/dark/theme.php">./themes/dark/theme.php</a>';			
 if($dbdeb<2)
  echo '<br><br><hr><small>Weiterleitung in 10 Sekunden.</small>';			

	 
 footer();
?>