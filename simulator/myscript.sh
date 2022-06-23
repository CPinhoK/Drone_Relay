#!/bin/sh

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:11" ] ; then
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
	printf '11' >> /home/test.txt
fi

printf 'before 12' >> /home/test.txt

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:12" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:13" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:14" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:15
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:15" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:21" ] || [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:22" ] ; then
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
	block 6e:06:e0:03:00:23
	block 6e:06:e0:03:00:24
	block 6e:06:e0:03:00:25
	block 6e:06:e0:03:00:26
	block 6e:06:e0:03:00:27
	block 6e:06:e0:03:00:28
	block 6e:06:e0:03:00:29
	block 6e:06:e0:03:00:30
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:23" ] || [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:24" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
	block 6e:06:e0:03:00:21
	block 6e:06:e0:03:00:22
	block 6e:06:e0:03:00:25
	block 6e:06:e0:03:00:26
	block 6e:06:e0:03:00:27
	block 6e:06:e0:03:00:28
	block 6e:06:e0:03:00:29
	block 6e:06:e0:03:00:30
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:25" ] || [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:26" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:15
	block 6e:06:e0:03:00:21
	block 6e:06:e0:03:00:22
	block 6e:06:e0:03:00:23
	block 6e:06:e0:03:00:24
	block 6e:06:e0:03:00:27
	block 6e:06:e0:03:00:28
	block 6e:06:e0:03:00:29
	block 6e:06:e0:03:00:30
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:27" ] || [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:28" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:15
	block 6e:06:e0:03:00:21
	block 6e:06:e0:03:00:22
	block 6e:06:e0:03:00:23
	block 6e:06:e0:03:00:24
	block 6e:06:e0:03:00:25
	block 6e:06:e0:03:00:26
	block 6e:06:e0:03:00:29
	block 6e:06:e0:03:00:30
fi

if [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:29" ] || [ $VANETZA_MAC_ADDRESS = "6e:06:e0:03:00:30" ] ; then
	block 6e:06:e0:03:00:11
	block 6e:06:e0:03:00:12
	block 6e:06:e0:03:00:13
	block 6e:06:e0:03:00:14
	block 6e:06:e0:03:00:21
	block 6e:06:e0:03:00:22
	block 6e:06:e0:03:00:23
	block 6e:06:e0:03:00:24
	block 6e:06:e0:03:00:25
	block 6e:06:e0:03:00:26
	block 6e:06:e0:03:00:27
	block 6e:06:e0:03:00:28
fi
