<?php
/**
 * AUTHOR
 *
 *	Dougal Scott <dougal.scott@gmail.com>
 *	Code mostly copied from
 *      Noah Spurrier <noah@noah.org>
 *      http://www.noah.org/wiki/MediaWiki_Include
 *
 * @package extensions
 * @copyright Copyright 2022 @author Dougal Scott
 *
 */

class Hostinfo
{
    /*********************************************************************************/
    public static function hostinfo( &$parser )
    {
        $parser->setHook('hostinfo', 'Hostinfo::renderHostinfo');

        return true;
    }

    /*********************************************************************************/
    private static function crit_format($crit)
    {
        $crit=str_replace('!=','.ne.',$crit);
        $crit=str_replace('=','.eq.',$crit);
        $crit=str_replace('<','.lt.',$crit);
        $crit=str_replace('>','.gt.',$crit);
        $crit=str_replace('~','.ss.',$crit);
        $crit=str_replace('/','.slash.',$crit);
        return $crit;
    }

    /*********************************************************************************/
    public static function renderHostinfo( $input , $argv, $parser )
    {
        $urlbase = "http://hostinfo";

        if ( ! isset($argv['type']))
            return "ERROR: <hostinfo> tag is missing 'type' attribute.";
        #$parser->disableCache();		# Remove when production

        # Tables
        if ($argv['type'] == "table") {
            $criteria="";
            $printable="";
            $ordering="";
            foreach (explode("\n",$input) as $line) {
                $nline=trim($line);
                if ($nline) {
                    if (strpos($nline, 'print ')===0)
                        $printable.=",".substr($nline, 6);
                    elseif (strpos($nline, 'order ')===0)
                        $ordering=substr($nline, 6);
                    else
                        $criteria.="/".Hostinfo::crit_format($nline);
                }
            }
            $url="/mediawiki/hostable".$criteria;
            if ($printable!="") {
                $printable=substr($printable,1);	# Trim first comma
                $url.="/print=".$printable;
                }
            if ($ordering!="") {
                $url.="/order=".$ordering;
                }
        }
        # Restricted value list
        elseif ($argv['type']=="rvlist") {
            if (isset($argv['key']))
                $key=$argv['key'];
            else
                $key=trim($input);
            $url="/mediawiki/rvlist/".$key;
        }
        # List of hosts
        elseif ($argv['type']=="hostlist") {
            $criteria="";
            foreach (explode("\n",$input) as $line) {
                $nline=trim($line);
                if ($nline)
                    $criteria.="/".Hostinfo::crit_format($nline);
                }
            $url="/mediawiki/hostlist".$criteria;
        }
        # Host page
        elseif ($argv['type']=="hostpage") {
            if ( isset($argv['name']))
                $hostname=$argv['name'];
            else
                $hostname=trim($input);
            $url="/mediawiki/host_summary/".$hostname;
        }
        elseif ($argv['type']=="showall") {
            if ( isset($argv['name']))
                $hostname=$argv['name'];
            else
                $hostname=trim($input);
            $url="/mediawiki/host/".$hostname;
        }
        # Unrealised future expansion
        else
            return "Error unknown type ".$argv['type'];

        $fullurl=$urlbase.$url;
        $output=file_get_contents($fullurl);
        if ($output === False)
            return "ERROR: hostinfo details (".$fullurl.") couldn't be read";

        $parsedText = $parser->parse($output, $parser->mTitle, $parser->mOptions, false, false);
        $output = $parsedText->getText();
        return $output;
    }
}
?>
