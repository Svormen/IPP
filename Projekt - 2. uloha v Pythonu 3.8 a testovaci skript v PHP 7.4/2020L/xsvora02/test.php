<?php

$get_int = "./interpret.py";
$get_parse = "./parse.php";
$get_parse_only = FALSE;
$get_int_only = FALSE;
$get_rec = FALSE;
$get_dir = "./";

$JXML_p = "/pub/courses/ipp/jexamxml/jexamxml.jar";
$xml_p = "/pub/courses/ipp/jexamxml/options";

function check_args(){
    global $argv;
    global $get_dir;
    global $get_rec;
    global $get_folder;
    global $get_parse_scr;
    global $get_int_scr;
    global $get_parse_only;
    global $get_int_only;
    global $xml_p;
    global $JXML_p;
    global $get_int;
    $tut_set = FALSE;
    $parse_set = FALSE;
    $int_set = FALSE;
    
    # check available arguments
    foreach($argv as $get_key => $get_value){
        if (preg_match("/--help/", $get_value, $matches)){
            $tut_set = TRUE;
        }
        else if (preg_match("/--directory=(.+)/", $get_value, $matches)){
            $get_dir = $matches[1];
        }
        else if (preg_match("/--recursive/", $get_value, $matches)){
            $get_rec = TRUE;
        }
        else if (preg_match("/--parse-script=(.+)/", $get_value, $matches)){
            $parse_set = TRUE;
            $get_parse = $matches[1];
        }
        else if (preg_match("/--int-script=(.+)/", $get_value, $matches)){
            $int_set = TRUE;
            $get_int = $matches[1];
        }
        else if (preg_match("/--parse-only/", $get_value, $matches)){
            $get_parse_only = TRUE;
        }
        else if (preg_match("/--int-only/", $get_value, $matches)){
            $get_int_only = TRUE;
        }
        else if (preg_match("/--jexamxml=(.+)/", $get_value, $matches)) {
            $JXML_p = $matches[1];
        }
        else if (preg_match("/--jexamcfg=(.+)/", $get_value, $matches)) {
            $xml_p = $matches[1]; 
        }
    }
    # check --help arguments
    if ($tut_set == TRUE){
        if (count($argv) > 2){
            fwrite(STDERR, "ERROR: --help can not be used with another arguments\n");
            exit(10);
        }
        else {
            # --help print
            echo("Available Arguments:\n");
            echo("  --help\n");
            echo("  --directory=path\n");
            echo("  --recursive\n");
            echo("  --parse-script=file\n");
            echo("  --int-script=file\n");
            echo("  --parse-only\n");
            echo("  --int-only\n");
            echo("  --jexamxml=file\n");
            echo("  --jexamcfg=file\n");
            exit(0);
        }
    }
    
    # check available combination of arguments
    if ((($get_int_only == TRUE) && ($get_parse_only == TRUE)) || (($get_parse_only == TRUE) && ($int_set == TRUE)) || (($get_int_only == TRUE) && ($parse_set == TRUE))){
        fwrite(STDERR, "ERROR: Wrong argument combination\n");
        exit(10);
    }
    
    if ($get_rec == FALSE){
        $get_folder = new DirectoryIterator($get_dir);
    }
    else{
        $get_folder = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($get_dir), RecursiveIteratorIterator::SELF_FIRST);
    }
}

function exit_outcome($my_outcome, $xml_outcome, $l_outcome){
    unlink($my_outcome);
    if (file_exists("./delta.xml")){
        unlink("./delta.xml");
    }
    if (file_exists($xml_outcome)){
        unlink($xml_outcome);
    }
    if (file_exists($l_outcome)){
        unlink($l_outcome);
    }
}

function build_new_rc($new_f){
    if (!file_exists($new_f)){
        $edit_f = fopen($new_f, "w+");
        fwrite($edit_f, "0");
        fclose($edit_f);
    }
}

function build_new_others($new_f_others){
    if (!file_exists($new_f_others)){
        $edit_f = fopen($new_f_others, "w+");
        fwrite($edit_f, "");
        fclose($edit_f);
    }
}

function build_new_out($new_f_out){
    if (!file_exists($new_f_out)){
        $edit_f = fopen($new_f_out, "w+");
        fwrite($edit_f, "");
        fclose($edit_f);
    }
}

function empty_f($edit_f){
    return !file_get_contents($edit_f);
}

# main function
function main(){
    # check arguments
    check_args();
    HtmlGenerator::write_html();

    global $argv;
    global $get_folder; 
    global $get_dir; 
    global $get_parse; 
    global $get_int; 
    global $get_parse_only; 
    global $JXML_p; 
    global $xml_p; 
    global $get_rec; 
    global $get_int_only; 

    $test_counter = 0;
    $test_ok_counter = 0;
    $main_try_d = $get_dir;
    $late_d = "";

    foreach($get_folder as $sourc_out){
        $tmp = "";
        $source_way = $sourc_out->getPathname();

        if($sourc_out->getExtension() == "src"){
            $test_counter = $test_counter + 1;
            $f_not_ext = dirname($source_way)."/".basename($sourc_out->getFilename(), ".".$sourc_out->getExtension());

            $cut_p = substr($sourc_out, strlen($main_try_d));
            $cut_d = basename($main_try_d)."/".substr(dirname($source_way), strlen($main_try_d));
            #if ($late_d !== $cut_d){
                #HtmlGenerator::write_check_name($cut_d);
            #}
            $late_d = $cut_d;

            $new_f = $f_not_ext.".rc";
            $new_f_out = $f_not_ext.".out";
            $new_f_in = $f_not_ext.".in";
            $my_outcome = $f_not_ext.".our_out";
            $xml_outcome = $f_not_ext.".tp_xml";
            
            build_new_rc($new_f);
            build_new_out($new_f_out);
            build_new_others($new_f_in);

            $wanted_f = intval(explode(' ',trim(file_get_contents($new_f)))[0]);
            $parse_OK_f = FALSE;
            $parse_OK_f_out = FALSE;
            $int_OK_f = FALSE;
            $int_OK_f_out = FALSE;
            if($get_parse_only){
                exec("php7.4 $get_parse < \"$source_way\" > \"$my_outcome\"", $tmp, $my_parse);
                exec("java -jar \"$JXML_p\" \"$new_f_out\" \"$my_outcome\" delta.xml /D \"$xml_p\"", $tmp, $jxml_f);

                if ($wanted_f != 0){
                    if (is_file_empty($new_f_out) && is_file_empty($my_outcome)){
                        $parse_OK_f_out = TRUE;
                    }
                }
                else {
                    $parse_OK_f_out = $jxml_f == 0;
                }
                $parse_OK_f = $my_parse == $wanted_f;
                $test_OK = $parse_OK_f && $parse_OK_f_out;
                HtmlGenerator::write_check_name($sourc_out->getFilename(), $cut_d);
				HtmlGenerator::write_outcome($wanted_f, $my_parse, $parse_OK_f_out);	
				HtmlGenerator::write_outcome(NULL, NULL, NULL);
            }
            else if($get_int_only){
                exec("python3.8 $get_int --source=\"$source_way\" < \"$new_f_in\" > \"$my_outcome\"", $tmp, $int_only);
                exec("diff \"$new_f_out\" \"$my_outcome\"", $tmp, $differ_f);

                $int_OK_f = $int_only == $wanted_f;
                $int_OK_f_out = $differ_f == 0;
                $test_OK = $int_OK_f && $int_OK_f_out;
                HtmlGenerator::write_check_name($sourc_out->getFilename(), $cut_d);
				HtmlGenerator::write_outcome(NULL, NULL, NULL);	
				HtmlGenerator::write_outcome($wanted_f, $int_only, $int_OK_f_out);
            }
            else{
                exec("php7.4 $get_parse < \"$source_way\" > \"$xml_outcome\"", $tmp, $my_parse);
                exec("python3.8 $get_int --source=\"$xml_outcome\" < \"$new_f_in\" > \"$my_outcome\"", $tmp, $int_only);
                exec("diff \"$new_f_out\" \"$my_outcome\"", $tmp, $differ_f);

                $parse_OK_f = $my_parse == $wanted_f;
                $int_OK_f_out = $differ_f == 0;
                $test_OK = $parse_OK_f && $parse_OK_f_out;
                HtmlGenerator::write_check_name($sourc_out->getFilename(), $cut_d);
				HtmlGenerator::write_outcome(NULL, $parse_OK_f, NULL);	
				HtmlGenerator::write_outcome($wanted_f, $int_only, $int_OK_f_out);

            }
            if($test_OK){
                HtmlGenerator::write_res_ok();
				$test_ok_counter = $test_ok_counter + 1;
            }
            else{
                HtmlGenerator::write_res_wrong();
            }
            #exit_outcome($my_outcome, $xml_outcome, $new_f_out.".log");
        }
    }
    HtmlGenerator::get_all($test_counter, $test_ok_counter);
}


class HtmlGenerator{
    /**
     * Print html code to stdout
     */ 	
    
    public static function write_html(){
        echo '<!DOCTYPE html>
        <html>
        <body>
        
            <head>
                <style>
                table, th, td {
                  border: 2px solid black;
                  border-collapse: collapse;
                }
                th, td {
                  padding: 5px;
                  text-align: center;    
                }
                th{
                    background-color: #4CAF50;
                    text-transform: uppercase;
                }
                h1{
                    text-align: center;
                }
                table.center {
                    margin-left: auto; 
                    margin-right: auto;
                }
                .nadpis th{
                    background-color: lightgray;
                }
                .spodok{
                    background-color: #4CAF50;
                }
                .write_name{
                    border-bottom: none !important;
                }
                .ok {
                    color: green;
                }
                .bad {
                    color: red;
                }
                </style>
                </head>
        
        <h1>IPP 2021 Výsledná tabuľka</h1>
        
        <table style="width:80%" class="center">
          <tr>
            <th rowspan="2">Adresár</th>
            <th rowspan="2">Názov</th>
            <th colspan="4">parse.php</th> 
            <th colspan="4">interpret.py</th>
            <th rowspan="2">Celkovo</th>
          </tr>
          <tr class="nadpis">
            <th>Očakávané</th>
            <th>Získané</th>
            <th>RC</th>
            <th>OUT</th>
            <th>Očakávané</th>
            <th>Získané</th>
            <th>RC</th>
            <th>OUT</th>
          </tr>
           
       '."\n";
    }
    public static function write_names($navg){
        echo '<tr class="write_name">
                <td>'.$navg.'</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>	
                <td></td>	
                <td></td>		
            </tr>'."\n";
    }
    public static function write_check_name($name, $navg){
        echo '<tr><td>'.$navg.'</td>'."\n".'<td>'.$name.'</td>'."\n";
    }
    public static function write_outcome($wanted_vrb_rc, $get_vrb_rc, $outcome){
        $wrong_vrb_rc = FALSE;
    
        if(is_null($wanted_vrb_rc)){
            $wrong_vrb_rc = TRUE;
            $wanted_vrb_rc = "--";
        }
        if(is_null($get_vrb_rc)){
            $wrong_vrb_rc = TRUE;
            $get_vrb_rc = "--";
        }
    
        echo '<td>'.$wanted_vrb_rc.'</td>'."\n".'<td>'.$get_vrb_rc.'</td>'."\n";
    
        if($wrong_vrb_rc){
            echo '<td>--</td>'."\n";
        }else{
            if($wanted_vrb_rc == $get_vrb_rc){
                echo '<td class="ok">OK</td>'."\n";
            } else{
                echo '<td class="bad">BAD</td>'."\n";
            }		
        }
        if(is_null($outcome)){
            echo '<td>--</td>'."\n";
        }else{
            if($outcome == TRUE)	{
                echo '<td class="ok">OK</td>'."\n";
            } else{
                echo '<td class="bad">BAD</td>'."\n";
            }	
        }
    }
    
    public static function write_res_ok(){
    
        echo '<td class="ok">OK</td>'."\n".'</tr>'."\n";
    }
    
    public static function write_res_wrong(){
    
        echo '<td class="bad">BAD</td>'."\n".'</tr>'."\n";
    }
    
    public static function get_all($get_ever, $get_ok){
    
        echo '
            </tbody>
            <tr class="spodok">
                <td colspan="10">Výsledok</td>
                <td>'."$get_ok/$get_ever".'</td>
            </tr>
            </table>
        
            </body>
            </html>'."\n";	
    }
}

# call main function
main();

?> 