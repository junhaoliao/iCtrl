rm -f portscan.log

for i in {1..99}
do
echo "checking port $i"
port=$(($i+5900))
lsof -i:$port | grep 'vnc' > /dev/null && echo "$i" >> portscan.log
done
