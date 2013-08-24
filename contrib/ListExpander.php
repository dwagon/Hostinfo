<?php
 
if ( !defined( 'MEDIAWIKI' ) ) {
    die( 'This file is a MediaWiki extension, it is not a valid entry point' );
}
 
$wgExtensionFunctions[] = 'wfSetupListExpander_Setup';
$wgHooks['LanguageGetMagic'][] = 'wfSetupListExpander_Magic';
 
$wgExtensionCredits['parserhook'][] = array(
    'path' => __FILE__,
    'name' => 'ListExpander',
    'version' => '$Revision: 7 $',
    'url' => 'http://www.mediawiki.org/wiki/Extension:ListExpander',
    'author' => 'Dougal Scott',
    'description' => 'Use whitespace separated lists.'
);  

function wfSetupListExpander_Setup() {
    global $wgParser;
 
    $wgParser->setFunctionHook( 'listexpand', 'ListExpander_expand' );
}

# For every item in the list, replace it with $string, with '%%' replaced by the item
function ListExpander_expand( &$parser, $list='', $string='') {
    $ans='';
    $splitlist=explode(' ', $list);
    foreach ($splitlist as $item) {
    	if ( trim($item) ) {
	    $ans.=str_replace('%%', trim($item), $string);	
	    $ans.=' ';
	    }
	}
    $ans.='';
    return array($ans, 'noparse'=>false);
}
 
function wfSetupListExpander_Magic( &$magicWords, $langCode) {
    $magicWords['listexpand'] = array(0, 'listexpand');
    return true;
}

#EOF
