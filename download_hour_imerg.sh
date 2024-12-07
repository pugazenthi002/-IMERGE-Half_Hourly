#!/bin/bash
sday="2017-01-12"
eday="2023-12-31"
burl="https://data.rda.ucar.edu/d731000/gpm_3imerghh_v07"


curr=$sday
while true; do     
	yyn=$(date +%Y -d "$curr")
	mmn=$(date +%m -d "$curr")
	ddn=$(date +%d -d "$curr")
	mkdir -p "$yyn/$mmn/$ddn" && cd "$yyn/$mmn/$ddn"
	bburl="$burl"/"$yyn"/"$mmn"/"$ddn"/3B-HHR.MS.MRG.3IMERG."$yyn""$mmn""$ddn"-S
	for time in $(bash -c "seq -w 00 23"); do
		tt=$((10#$time))
		aa=$(printf "%04d" $((tt * 60)))  
		aaz=$((tt*60))
        aaa=$(printf "%04d" $((aaz + 30)))
		tt="$time"0000-E
		ttt="$time"3000-E
		ss="$time"2959."$aa".V07B.HDF5
		sss="$time"5959."$aaa".V07B.HDF5
		furl="$bburl""$tt""$ss"
		ffurl="$bburl""$ttt""$sss"		
		if [ "$time" == "00" ]; then
			echo -e "$furl\n$ffurl" > "down.txt"
		else
			echo -e "$furl\n$ffurl" >> "down.txt"
		fi
		done
	aria2c --auto-file-renaming=false -j48 --retry-wait=5 --user-agent="Mozilla/5.0" -i "down.txt" > "out.log"
	cd ../../../
	[ "$curr" \< "$eday" ] || break
	curr=$( date +%Y-%m-%d --date "$curr +1 day" )

done

