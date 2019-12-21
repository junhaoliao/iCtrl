#ifndef ugProfile

#include <nlohmann/json.hpp>
#include <cryptopp/base64.h>

#include <iostream>
#include <string>
#include <iomanip>
#include <fstream>
#include <conio.h>

using json = nlohmann::json;

#define PASSWD_MAX_LEN 1024

std::string getEncodedPassword();

class ugProfile {
    json profile;
    std::string username;
    std::string encodedPasswd;
    std::string encodedVNCPassword;
    int machine = -1;
    unsigned port = 1;
public:
    ugProfile() {
        std::cout << "Please have your Lab username and password on hand. You will also need to setup another password for securing your remote control.\n" << std::endl;
        std::cout << "Although we will encryt your password and store it locally, you still don't want to use this script on a public computer.\n" << std::endl; 
        std::cout << "Any bad guy who gains access to your account can cause serious consequences.\n" << std::endl;
        std::cout << "You can continue if you understand the risk [y/n]:" << std::endl;
        char consent;
        std::cin >> consent;
        if (!(consent == 'y' || consent == 'Y')) {
            system("CLS");
            std::cout << "Sorry to see you leave... Feel free to check out the source code on my GitHub page, and come back when you feel safe to do so." << std::endl;
            system("pause");
            exit(3);
        }

        system("CLS");
        std::cout << "Please enter your UG Lab Username UTORid: " << std::endl;
        std::cin >> username;

        // prompt for password 
        std::cout << "Please enter your UG Lab Password: " << std::endl;
        encodedPasswd = getEncodedPassword();

        // prompt for VNC password
        std::cout << "Please set up a VNC Password(at least 6 characters): " << std::endl;
        encodedVNCPassword = getEncodedPassword();
        
        profile["username"] = username;
        profile["passwd"] = encodedPasswd;
        profile["vncpasswd"] = encodedVNCPassword;
        profile["machine"] = machine;
        profile["port"] = port;

        std::ofstream outputJson("profile.json");
        outputJson << std::setw(4) << profile << std::endl;
        outputJson.close();
    }
    ugProfile(const char* jsonPath) {
        std::ifstream inJson(jsonPath);
        inJson >> profile;
        username = profile["username"];
        encodedPasswd = profile["passwd"];
        encodedVNCPassword = profile["vncpasswd"];
        machine = profile["machine"];
        port = profile["port"];
    }
    std::string getUsername() {
        return username;
    }
    std::string getPasswd() {
        std::string decoded;
        CryptoPP::StringSource ssD(encodedPasswd, true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded)));
        return decoded;
    }
    std::string getVNCPasswd() {
        std::string decoded;
        CryptoPP::StringSource ssD(encodedVNCPassword, true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded)));
        return decoded;
    }
    int getMachine() {
        return machine;
    }
    unsigned getPort() {
        return port;
    }
    int changeMachine(const int machineNbr) {
        profile["machine"] = machineNbr;

        std::ofstream outputJson("profile.json");
        outputJson << std::setw(4) << profile << std::endl;
        outputJson.close();
        return 0;
    }

    int changePort(const unsigned portNbr) {
        profile["port"] = portNbr;

        std::ofstream outputJson("profile.json");
        outputJson << std::setw(4) << profile << std::endl;
        outputJson.close();
        return 0;
    }
};

std::string getEncodedPassword(){
    unsigned passwdLen;
    CryptoPP::byte passwd[PASSWD_MAX_LEN];
    for (int i = 0; i < PASSWD_MAX_LEN; i++) {
        passwd[i] = _getch();
        if (passwd[i] == 8) {
            if (i > 0) {
                i -= 2;
                std::cout << "\b\033[K";
            }
            continue;
        }
        else if (passwd[i] == 13) {
            passwdLen = i;
            break;
        }
        _putch('*');
    }
    std::cout << std::endl;
    // encrypt the password by Base64
    std::string result;
    CryptoPP::StringSource ssE(passwd, passwdLen,
        true, new CryptoPP::Base64Encoder(new CryptoPP::StringSink(result)));
    return result;
}

#endif // !ugProfile

