#include "./ugProfile.h"
#include "./ugSession.h"
#include "./showPortStatus.h"

#include <iostream>
#include <filesystem>

int main()
{
	if (!std::filesystem::exists("profile.json")) { // no profile found, creating a new one
		std::cout << "Hi! Seems like you are a new user. Creating a new profile for you...\n" << std::endl;
		ugProfile newProfile;

		std::string command_sendPortCheckScript = "pscp.exe -pw " + newProfile.getPasswd() + " checkPort.sh " + newProfile.getUsername() + "@ug251.eecg.toronto.edu:checkPort.sh";
		//std::cout << command_sendPortCheckScript << std::endl;
		system(command_sendPortCheckScript.c_str());

		ugSession newSession(newProfile.getUsername().c_str(), newProfile.getPasswd().c_str(), 251);
		char scripts[7][256] = {
		"killall Xtigervnc\n\0",
		"rm -rf .vnc\n\0",
		"vncpasswd\n\0",
		"",
		"",
		"n\n\0",
		"chmod u+x checkPort.sh\n\0"
		};
		std::string vncPasswdScript = newProfile.getVNCPasswd() + "\n\0";
		strcpy_s(scripts[3], vncPasswdScript.c_str());
		strcpy_s(scripts[4], vncPasswdScript.c_str());

		newSession.automatic_shell_session(scripts, 7);

		std::string command_getVncEncryption = "pscp.exe -pw " + newProfile.getPasswd() + " " + newProfile.getUsername() + "@ug251.eecg.toronto.edu:./.vnc/passwd passwd";
		system(command_getVncEncryption.c_str());

		system("CLS");
		std::cout << "Hey, setup is done!! You can now close this window and launch the program again." << std::endl;
		system("pause");
	}
	else {
		std::cout << "Yep, we have just found a profile. If anything goes wrong, you can reset the profile by entering DEL.\n" << std::endl;
		ugProfile myProfile("profile.json");
		std::string selection;

		if (myProfile.getMachine() == -1) {
			std::cout << "Congrats on finishing the initialization. Start your first session below: \n\n";
			goto newConnection;
		}
	selectOp:
		std::cout << "Continue the last session? [y/n]" << std::endl;

		std::cin >> selection;
		if (selection.compare("del") == 0 || selection.compare("DEL") == 0) {
		delProfile:
			std::remove("profile.json");
			std::remove("portscan.log");
			system("CLS");
			std::cout << "Profile deleted. You can setup a new one by restarting the program." << std::endl;
			system("pause");
		}
		else if (selection.compare("y") == 0 || selection.compare("Y") == 0) {
			unsigned machine = myProfile.getMachine();
			unsigned port = myProfile.getPort();

			std::string command_setTunnel = "start kitty_portable.exe -ssh -L " + std::to_string(port + 5900) + ":localhost:" + std::to_string(port + 5900)
				+ " " + myProfile.getUsername() + "@ug" + std::to_string(machine) + ".eecg.toronto.edu -pw " + myProfile.getPasswd();
			//std::cout << command_setTunnel << std::endl;
			system(command_setTunnel.c_str());
			{
				using namespace std::literals;
				std::this_thread::sleep_for(2s);// 4 second
			}
			std::string command_launchVNC = "vncviewer64-1.9.0.exe -passwd passwd 127.0.0.1:" + std::to_string(port);
			system(command_launchVNC.c_str());
		}
		else if (selection.compare("n") == 0 || selection.compare("N") == 0) {
		newConnection:
			std::remove("portscan.log");
			std::string selction;

			std::cout << "Please enter the new machine # (Recommended: 132-180, 200-250)" << std::endl;
			std::cin >> selction;
			if (selction.compare("del") == 0 || selction.compare("DEL") == 0) {
				goto delProfile;
			}
			unsigned machine = std::atoi(selction.c_str());
			myProfile.changeMachine(machine);
			ugSession newSession(myProfile.getUsername().c_str(), myProfile.getPasswd().c_str(), machine);
			char scripts[2][256] = {
				"killall Xtigervnc\n\0",
				"./checkPort.sh\n\0",
			};
			newSession.automatic_shell_session(scripts, 2);
			std::string command_getPortStatus = "pscp.exe -pw " + myProfile.getPasswd() + " " + myProfile.getUsername() + "@ug251.eecg.toronto.edu:./portscan.log portscan.log";
			system(command_getPortStatus.c_str());
			//system("pause");
			showPortStatus();
			unsigned port;
			std::cout << "Please enter the new port # (the red ones are busy)" << std::endl;
			std::cin >> port;
			myProfile.changePort(port);
			std::string command_setTunnel = "start kitty_portable.exe -ssh -L " + std::to_string(port + 5900) + ":localhost:" + std::to_string(port + 5900)
				+ " " + myProfile.getUsername() + "@ug" + std::to_string(machine) + ".eecg.toronto.edu -pw " + myProfile.getPasswd() + " -cmd \"vncserver :"
				+ std::to_string(port) + "\\n\"";
			std::cout << command_setTunnel << std::endl;
			system(command_setTunnel.c_str());
			{
				using namespace std::literals;
				std::this_thread::sleep_for(4s);// 4 second
			}
			std::string command_launchVNC = "vncviewer64-1.9.0.exe -passwd passwd 127.0.0.1:" + std::to_string(port);
			system(command_launchVNC.c_str());
		}
		else {
			std::cout << "The selection is invalid. Please try again." << std::endl;
			goto selectOp;
		}
	}


}