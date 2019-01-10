@echo on 
set /a ranMachine=132+(%random%*49/32768) 
kitty_portable.exe -ssh -L 5901:127.0.0.1:5901 liaojunh@ug%ranMachine%.eecg.toronto.edu -pw 1003824891 -cmd "ece297vnc stop all \n \p \p  ece297vnc start" 
