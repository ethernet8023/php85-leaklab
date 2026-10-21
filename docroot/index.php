<?php
// Lab readback endpoint: shows what the upload-progress UAF corrupted.
session_start();
header('Content-Type: text/plain');
echo "SID=" . session_id() . "\n";
echo "SESSION=" . var_export($_SESSION, true) . "\n";
echo "POSTCOUNT=" . count($_POST) . "\n";
