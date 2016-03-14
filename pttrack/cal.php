<!DOCTYPE html>
<head><title>Hannah's Calculator mod2</title></head>


<?php
$num1 = $_GET['num1'];
$num2 = $_GET['num2'];
$result = $num1 + $num2;
echo "sum= " .$result;

$num1 = $_GET['num1'];
$num2 = $_GET['num2'];
$result = $num1 - $num2;
echo "difference= " .$result;

$num1 = $_GET['num1'];
$num2 = $_GET['num2'];
$result = $num1 * $num2;
echo "product= " .$result;

$num1 = $_GET['num1'];
$num2 = $_GET['num2'];
$result = $num2 / $num1;
echo "quotient= " .$result;
echo "remainder= " .$num2 % $num2;



?>