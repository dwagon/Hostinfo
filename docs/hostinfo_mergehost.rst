hostinfo_mergehost
==================

Take the details of the two hosts and combine them into one::

    % host_merge [opts] --src srchost --dst dsthost
        -k        Just kidding, don't do anything
        -v        Be verbose about what is happening
        -f        Force collisions to be resolved in the dst hosts favour

* All srchost data will be copied to the dsthost, unless the dsthost already has that key set
* The srchost will be deleted after the data has been copied across
* This is used for when two hosts have been accidentally created with different names and then someone realises that they are actually the same host.
