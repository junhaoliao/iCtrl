#ifndef showPortStatus

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

#define RESET   "\033[0m"
#define BLACK   "\033[30m"      /* Black */
#define RED     "\033[31m"      /* Red */
#define GREEN   "\033[32m"      /* Green */
#define YELLOW  "\033[33m"      /* Yellow */
#define BLUE    "\033[34m"      /* Blue */
#define MAGENTA "\033[35m"      /* Magenta */
#define CYAN    "\033[36m"      /* Cyan */
#define WHITE   "\033[37m"      /* White */

class showPortStatus {
	bool ports[100] = {false};
public:
	showPortStatus() {
        system("CLS");
		std::ifstream file("portscan.log");
        if (file.is_open()) {
            std::string line;
            while (std::getline(file, line)) {
                ports[atoi(line.c_str())] = true;
            }
            file.close();
        }
        for (unsigned i = 0; i < 10; i++) {
                unsigned j;
            for (j = 0; j < 10; j++) {
                /*
                if (i == 0 && j == 0) {
                    std::cout << "©° ";
                }
                else if (i == 0) {
                    std::cout << "©Ð ";
                }
                else if (i == 9 && j == 0) {
                    std::cout << "©¸ ";
                }
                else if (i == 9) {
                    std::cout << "©Ø ";
                }
                else if (j == 0) {
                    std::cout << "©À ";
                }
                else {
                    std::cout << "©à ";
                }*/
                if (i == 0 && j == 0) {
                    std::cout << "|";
                }
                else {
                    std::cout << "|" << std::setw(2) << std::setfill(' ') << i * 10 + j;
                }

                if (i==0&&j==0) {
                    std::cout << " 000 " << RESET;
                }
                else if (ports[i * 10 + j]) {
                    std::cout << RED << " X " << RESET;
                }
                else {
                    std::cout << GREEN << " O " << RESET;
                }
            }
            std::cout << "|"<< std::endl << std::endl;
            /*
            if (i == 0) {
                std::cout << "©´\n" << std::endl;
            }
            else if (i==9) {
                std::cout << "©¼\n" << std::endl;
            }
            else {
                std::cout << "©È\n" << std::endl;
            }*/

        }
	}


};

#endif // !showPortStatus
