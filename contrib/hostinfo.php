<?php
/**
 * NAME
 *
 *      <hostinfo/>
 *
 * SYNOPSIS
 *
 *      <hostinfo print="" criteria=""/>
 *
 * INSTALL
 *
 *      Put this script on your server in your MediaWiki extensions directory:
 *          "$IP/extensions/hostinfo.php"
 *      where $IP is the Install Path of your MediaWiki.
 *      Then add this line to LocalSettings.php:
 *          require_once("$IP/extensions/hostinfo.php");
 *
 * EXAMPLES
 *
 *          <hostinfo print="os,osrev" criteria="hardware=v490,site=qv"/>
 *
 * AUTHOR
 *
 *	Dougal Scott <dougal.scott@gmail.com>
 *	Code mostly copied from
 *      Noah Spurrier <noah@noah.org>
 *      http://www.noah.org/wiki/MediaWiki_Include
 *
 * @package extensions
 * @version 6
 * @copyright Copyright 2012 @author Dougal Scott
 * @license public domain -- free of any licenses and restrictions
 *
 * $Id: hostinfo.php 124 2012-12-05 21:17:22Z dougal.scott@gmail.com $
 * vi:ts=4:sw=4:expandtab:ft=php:
 */

$wgExtensionFunctions[] = "wf_hostinfo";
$wgExtensionCredits['other'][] = array
(
    'name' => 'hostinfo',
    'author' => 'Dougal Scott',
    'description' => 'Include dynamic hostinfo documentation for a server',
);

function wf_hostinfo()
{
    global $wgParser;
    $wgParser->setHook( "hostinfo", "render_hostinfo" );
}

function crit_format($crit)
{
    $crit=str_replace('!=','.ne.',$crit);
    $crit=str_replace('=','.eq.',$crit);
    $crit=str_replace('<','.lt.',$crit);
    $crit=str_replace('>','.gt.',$crit);
    $crit=str_replace('~','.ss.',$crit);
    $crit=str_replace('/','.slash.',$crit);
    return $crit;
}

/**
 * render_hostinfo
 *
 * This is called automatically by the MediaWiki parser extension system.
 * This does the work of loading a file and returning the text content.
 * $argv is an associative array of arguments passed in the <hostinfo> tag as
 * attributes.
 *
 * @param mixed $input unused
 * @param mixed $argv associative array
 * @param mixed $parser unused
 * @access public
 * @return string
 */
function render_hostinfo ( $input , $argv, &$parser )
{
    $urlbase = "http://localhost:8000";

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
		    $criteria.="/".crit_format($nline);
		}
	    }
	$url="/hostinfo/hostwikitable".$criteria;
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
	$url="/hostinfo/rvlist/".$key."/wiki";
    	}
    # List of hosts
    elseif ($argv['type']=="hostlist") {
    	$criteria="";
	foreach (explode("\n",$input) as $line) {
	    $nline=trim($line);
	    if ($nline)
		$criteria.="/".crit_format($nline);
	    }
	$url="/hostinfo/hostwiki".$criteria;
    	}
    # Host page
    elseif ($argv['type']=="hostpage") {
    	if ( isset($argv['name']))
	    $hostname=$argv['name'];
	else
	    $hostname=trim($input);
	$url="/hostinfo/host_summary/".$hostname."/wiki";
    	}
    elseif ($argv['type']=="showall") {
    	if ( isset($argv['name']))
	    $hostname=$argv['name'];
	else
	    $hostname=trim($input);
	$url="/hostinfo/host/".$hostname."/wiki";
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
?>
