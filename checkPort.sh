rm -f portscan.log
for i in {1..99}
do
echo "checking port $i"
port=$(($i+5900))
sh -c "nc -z -nv 127.0.0.1 $port 2>&1" | grep 'succeeded' > /dev/null && echo "$i" >> portscan.log
done