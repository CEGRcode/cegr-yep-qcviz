#! /usr/bin/perl/

die "Input_File\tOutput_File\n" unless $#ARGV == 1;
my($input, $output) = @ARGV;
open(IN, "<$input") or die "Can't open $input for reading!\n";
open(OUT, ">$output") or die "Can't open $output for reading!\n";

print OUT "{\n" ;
print OUT "\"compositePlot\": {\n";

print OUT "    \"Xaxis\": \"";
$line = <IN>;
chomp($line);
@array = split(/\t/, $line);
shift(@array);
print OUT join(",", @array);
print OUT "\",\n";

print OUT "    \"sampleSenseYaxis\": \"";
$line = <IN>;
chomp($line);
@array = split(/\t/, $line);
shift(@array);
print OUT sprintf("%.4f", $array[0]);
for($x = 1; $x <= $#array; $x++) { print OUT ",",sprintf("%.4f", $array[$x]); }
print OUT "\",\n";

print OUT "    \"sampleAntiYaxis\": \"";
$line = <IN>;
chomp($line);
@array = split(/\t/, $line);
shift(@array);
print OUT sprintf("%.4f", $array[0]);
for($x = 1; $x <= $#array; $x++) { print OUT ",",sprintf("%.4f", $array[$x]); }
print OUT "\"\n";

print OUT "}\n";
print OUT "}\n";
close IN;
close OUT;
