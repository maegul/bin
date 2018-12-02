# Need to deal with fact that time after 4 year mark is not part time
# Just flip the scaling to 1 after 4 years?


fouryrdate="2019_08_19_0_0"

tm_fmt="%Y_%m_%d_%H_%M"

secs_in_yr=$(echo "scale=0; 60*60*24*365.25" | bc)
secs_in_mnth=$(echo "scale=0; $secs_in_yr/12" | bc)
secs_in_day=$(echo "scale=0; $secs_in_yr/365.25" | bc)

rate=0.5



now="$(date -j +'%s')"

fouryrmk="$(date -j -f $tm_fmt $fouryrdate +'%s')"

# expressed in years
four_yr_diff_secs=$(echo "scale=4;($now-$fouryrmk)*$rate" | bc)
four_yr_diff=$(echo "scale=4;($four_yr_diff_secs)/($secs_in_yr)" | bc)

time_secs=$(echo "scale=4; (4*$secs_in_yr)+$four_yr_diff_secs" | bc)

years=$(echo "scale=0; $time_secs/$secs_in_yr" | bc)

# scale of zero necessary for modulo operations (to be integers)
sub_yr_diff_secs=$(echo "scale=0;$time_secs%$secs_in_yr" | bc)
mnths=$(echo "scale=0; $sub_yr_diff_secs/$secs_in_mnth" | bc)

sub_mnth_diff_secs=$(echo "scale=0;$time_secs%$secs_in_mnth" | bc)
days=$(echo "scale=0; $sub_mnth_diff_secs/$secs_in_day" | bc)


time=$(echo "scale=4; (4+$four_yr_diff)" | bc)

echo $time


echo $years, $mnths, $days

if [[ $1 ]]; then 
	# echo 'hello arg'
	# Presuming, for now, that input time is less than 4

	fut_time_diff_secs=$(echo "scale=0; (4-$1) * $secs_in_yr * 2" | bc)
	fut_time_secs=$(echo "scale=0; ($fouryrmk - $fut_time_diff_secs)" | bc | awk '{print int($1+0.5)}')

	fut_time="$(date -j -f "%s" $fut_time_secs +"%d %m %Y")"
	echo $fut_time

fi
