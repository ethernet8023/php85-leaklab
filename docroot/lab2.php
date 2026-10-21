<?php
// raw readback of the session store, mid-upload or after
session_start();
header('Content-Type: text/plain');
echo "ini: enabled=" . ini_get('session.upload_progress.enabled')
   . " cleanup=" . ini_get('session.upload_progress.cleanup')
   . " freq=" . ini_get('session.upload_progress.freq')
   . " min_freq=" . ini_get('session.upload_progress.min_freq')
   . " save_path=" . (ini_get('session.save_path') ?: '(sys)') . "\n";
echo "keys=" . json_encode(array_keys($_SESSION)) . "\n";
$k = 'upload_progress_' . ($_GET['k'] ?? 'x');
if (isset($_SESSION[$k])) {
    $d = $_SESSION[$k];
    echo "bytes_processed=" . var_export($d['bytes_processed'] ?? null, true) . "\n";
    foreach (($d['files'] ?? []) as $i => $f) {
        echo "file[$i]: name_len=" . strlen($f['name'] ?? '')
           . " bytes_processed=" . var_export($f['bytes_processed'] ?? null, true) . "\n";
    }
}
