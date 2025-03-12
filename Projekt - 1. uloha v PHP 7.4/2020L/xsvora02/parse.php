<?php
/**
 * Súbor: parse.php
 * Autor: Slavomír Svorada (xsvora02)
 */

ini_set('display_errors', 'stderr');

// Load arguments
checkArguments();

// object for syn. and lex. analysis of inctructions
$instr = new Instruction();

// object for writting XML
$out_writter = new xml_writter();
while($instr->get_follow())
{
    if (isset($instr->name_instruction))
    {
        $out_writter->xml_writter_instruction($instr->name_instruction);
        foreach($instr->argument_instruction as $arg)
        {
            foreach($arg as $type => $value)
            {
                // listing of arguments
                $out_writter->xml_writter_argument($type, $value);
            }
        }
        // end of instruction element
        $out_writter->xml_end();
    }
}
// listing XML on STDOUT
$out_writter->xml_writter_end();

function checkArguments()
{
    global $argc, $argv;
    //$options = getopt(null, ["help", "comments", "loc", "stats:"]);

    // Without argument
    if ($argc == 1)
    {
        return;
    } elseif ($argc == 2) // one argument
    {
        if ($argv[1] == "--help")
        {
            echo("Skript typu filtr (parse.php v jazyku PHP 7.4) načíta zo štandartného vstupu zdrojový kód v IPPcode21\n");
            echo("Ďalej skontroluje lexikálnu a syntaktickú správnosť kódu\n");
            echo("Následne vypíše na štandartný výstup XML\n");
            exit(0);
        } else{
            fprintf(STDERR, "Wrong Argument --help\n");
            exit(10);
        }
    } else {
        fprintf(STDERR, "Wrong Arguments\n");
        exit(10);
    }
}

class Instruction
{
    private $increase;

    // name of instruction
    public $name_instruction;
    // argument of instruction
    public $argument_instruction;

    public function __construct()
    {
        $this->increase = 0;
    }

    public function get_follow()
    {
       $this->increase++;
       unset($this->name_instruction);
       $this->argument_instruction = [];

       // error opening input files
       if ((!($line = fgets(STDIN))) && ($this->increase == 1))
       {
           fprintf(STDERR, "ERROR: Wrong input - Empty file.\n");
           exit(11);
       } elseif ($line == false)
       {
           return false;
       }
       // TODO: remove -1 a added
       $line = trim(preg_replace("/#.*$/", "", $line, -1, $added));
       $divide = explode(' ', $line);

       if ($this->increase == 1) // check first line
       {

           if ($divide == false )
           {
            fprintf(STDERR, "ERROR: Header is written incorrectly\n");
            exit(21);
           } else
           {
               // check if first line is .IPPCODE21
               $divide[0] = strtoupper($divide[0]);    
               if ($divide[0] != '.IPPCODE21') 
               {
                   fprintf(STDERR, "ERROR: Header is written incorrectly\n");
                   exit(21);
                  
               } elseif ($divide[0] == '.IPPCODE21' && (count($divide) > 1))
               {
                   fprintf(STDERR, "ERROR: Header is written incorrectly\n");
                   exit(21);
               }
                else
               {
                   return true;
               }
           }
       }
       // without instruction, get new line
       if (($divide[0] == "") || ($divide == false))
       {
           $this->get_follow();
       }
       else
       {
           // check syntax
           $check_syntax_result = $this->Syntax_check($divide);
           if ($check_syntax_result == false)
           {
               fprintf(STDERR, "ERROR: Lexical or Syntax wrong\n");
               exit(23);
           } else
                return true;
       }
       return true;
    }

    // check the syntax of the instruction
    private function Syntax_check($divide)
    {
        // correct number of arguments
        if ((count($divide) > 0) && (count($divide) < 5))
        {
            // change to uppercase
            $divide[0] = strtoupper($divide[0]);
            switch($divide[0])
            {
                // nothing
                case 'CREATEFRAME':
                case 'PUSHFRAME':
                case 'POPFRAME':
                case 'BREAK':
                case 'RETURN':
                    if (count($divide) == 1)
                    {
                        $this->name_instruction = $divide[0];
                        return true;
                    }
                    break;

                // <var>
                case 'DEFVAR':
                case 'POPS':
                    if (count($divide) == 2)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->var_check($divide[1]);
                    }
                    break;

                // <symb>
                case 'PUSHS':
                case 'WRITE':
                case 'EXIT':
                case 'DPRINT':
                    if (count($divide) == 2)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->symb_check($divide[1]);
                    }
                    break;

                // <label>
                case 'CALL':
                case 'LABEL':
                case 'JUMP':
                    if (count($divide) == 2)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->label_check($divide[1]);
                    }
                    break;
                
                // <var> <symb>
                case 'MOVE':
                case 'INT2CHAR':
                case 'STRLEN':
                case 'TYPE':
                case 'NOT':
                    if (count($divide) == 3)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->var_check($divide[1]) && $this->symb_check($divide[2]);
                    }                   
                    break;

                // <var> <type>
                case 'READ':
                    if (count($divide) == 3)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->var_check($divide[1]) && $this->type_check($divide[2]);
                    }
                    break;

                // <var> <symb> <symb> 
                case 'ADD':
                case 'SUB':
                case 'MUL':
                case 'IDIV':
                case 'LT':
                case 'GT':
                case 'EQ':
                case 'AND':
                case 'OR':              
                case 'STRI2INT':
                case 'CONCAT':                
                case 'GETCHAR':
                case 'SETCHAR':
                    if (count($divide) == 4)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->var_check($divide[1]) && $this->symb_check($divide[2]) && $this->symb_check($divide[3]);
                    }
                    break;

                // <label> <symb> <symb>
                case 'JUMPIFEQ':
                case 'JUMPIFNEQ':
                    if (count($divide) == 4)
                    {
                        $this->name_instruction = $divide[0];
                        return $this->label_check($divide[1]) && $this->symb_check($divide[2]) && $this->symb_check($divide[3]);
                    }
                    break;

                // nothing what we want, will return error code 22
                default:
                    fprintf(STDERR, "ERROR: Unknown or wrong operation code.\n");
                    exit(22);#return false;           
            }
        } else // invalid number of arguments, error code 23
        return false;
    }
    private function var_check($x)
    {
        if (preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[a-zA-Z])(_|-|\$|&|%|\*|!|\?|[a-zA-Z0-9])*$/', $x))
        {
            $x_var = ['var' => $x];
            array_push($this->argument_instruction, $x_var);
            return true;
        } else
            return false;
    }

    private function symb_check($x)
    {
        if (preg_match('/^(string|int|bool|nil)@.*$/', $x))
        {
            $x = explode('@', $x, 2);  
            if ($x[0] == 'string')
            {
                if (preg_match('/^(\\\\[0-9]{3}|[^\\\\])*$/', $x[1]))
                {
                    $x_string = ['string' => $x[1]];
                    array_push($this->argument_instruction, $x_string);
                    return true;
                } else
                    return false;
            } elseif ($x[0] == 'int')
            {
                // int can not be empty
                if ($x[1] != "")
                {
                    $x_int = ['int' => $x[1]];
                    array_push($this->argument_instruction, $x_int);
                    return true;
                } else
                    return false;
            } elseif ($x[0] == 'bool')
            {
                if (preg_match('/^(true|false)$/', $x[1]))
                {
                    $x_bool = ['bool' => $x[1]];
                    array_push($this->argument_instruction, $x_bool);
                    return true;
                } else
                    return false;
            } elseif ($x[0] == 'nil')
            {
                if ($x[1] == 'nil')
                {
                    $x_nil = ['nil' => $x[1]];
                    array_push($this->argument_instruction, $x_nil);
                    return true; 
                } else
                    return false;
            }
        } elseif (preg_match('/^(GF|LF|TF)@.*$/', $x))
        {
            return $this->var_check($x);
        } else
            return false;
    }

    // check syntax of label, inserting a syntactically correct argument into the $argument_instruction
    private function label_check($x)
    {
        if (preg_match('/^(_|-|\$|&|%|\*|!|\?|[a-zA-Z])(_|-|\$|&|%|\*|!|\?|[a-zA-Z0-9])*$/', $x))
        {
            $x_label = ['label' => $x];
            array_push($this->argument_instruction, $x_label);
            return true;
        } else
            return false;
    }


    // check syntax of type, inserting a syntactically correct argument into the $argument_instruction
    private function type_check($x)
    {
        if (preg_match('/^(string|int|bool)$/', $x))
        {
            $x_type = ['type' => $x];
            array_push($this->argument_instruction, $x_type);
            return true;
        } else
            return false;
    } 
}

// generate XML
class xml_writter
    {
        private $out;
        private $writter_instruction;
        private $arg_writter_instruction;

        // constructor
        public function xml_writter()
        {
            $this->writter_instruction = 1;
            $this->out = new XMLWriter();
            $this->out->openMemory();
            $this->out->setIndent(true);
            $this->out->setIndentString("  ");
            $this->out->startDocument('1.0', 'UTF-8');
            $this->out->startElement('program');
            $this->out->writeAttribute('language', 'IPPcode21');
        }

        // writting element instruction into the XML
        public function xml_writter_instruction($inst)
        {
            $this->arg_writter_instruction = 1;
            $inst = strtoupper($inst);
            $this->out->startElement('instruction');
            $this->out->writeAttribute('order', $this->writter_instruction);
            $this->out->writeAttribute('opcode', $inst);
            $this->writter_instruction++;
        }

        // writting element arg into the XML
        public function xml_writter_argument($type, $value)
        {
            $type = strtolower($type);
            if ($type == 'bool')
            {
                // bool = must be lowercase
                $value = strtolower($value);
            }
            $this->out->startElement('arg'.$this->arg_writter_instruction);
            $this->out->writeAttribute('type', $type);
            $this->out->text($value);
            $this->out->endElement();
            $this->arg_writter_instruction++;
        }

        // writes the end element to XML
        public function xml_end()
        {
            $this->out->endElement();
        }

        // XML to STDOUT
        public function xml_writter_end()
        {
            $this->out->endDocument();
            echo $this->out->outputMemory();
        }
    }
