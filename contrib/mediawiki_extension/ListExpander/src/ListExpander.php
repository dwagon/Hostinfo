<?php
/*
    'name' => 'ListExpander',
    'version' => '$Revision: 782 $',
    'url' => 'http://www.mediawiki.org/wiki/Extension:ListExpander',
    'author' => 'Dougal Scott',
    'description' => 'Use whitespace separated lists.'
*/
 
class ListExpander
{ 
    public static function onParserFirstCallInit(Parser $parser) {
        $parser->setFunctionHook( 'listexpand', [self::class, 'render'] );
    }

    # For every item in the list, replace it with $string, with '%%' replaced by the item
    public static function render( Parser $parser, $list='', $string='') {
        $parser->getOutput()->updateCacheExpiry(0);
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
}
#EOF
