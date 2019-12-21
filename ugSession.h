#ifndef ugSession

#include <libssh/libsshpp.hpp>

#include <iostream>
#include <string>
#include <io.h>
#include <conio.h>
#include <thread>

class ugSession {
	ssh_session my_ssh_session;
public:
	ugSession(const char* username, const char* password, unsigned machine) {
		my_ssh_session = ssh_new();
		if (my_ssh_session == NULL)
			exit(-1);
		int port = 22;
		std::string hostname = "ug" + std::to_string(machine) + ".eecg.toronto.edu\0";
		ssh_options_set(my_ssh_session, SSH_OPTIONS_USER, username);
		ssh_options_set(my_ssh_session, SSH_OPTIONS_HOST, hostname.c_str());
		ssh_options_set(my_ssh_session, SSH_OPTIONS_PORT, &port);
		
		std::cout << "Hostname: " << hostname << std::endl;

		/*
		int verbosity = SSH_LOG_PROTOCOL;
		ssh_options_set(my_ssh_session, SSH_OPTIONS_LOG_VERBOSITY, &verbosity);
		*/
		// open connection
		int rc = ssh_connect(my_ssh_session);
		if (rc != SSH_OK)
		{
			fprintf(stderr, "Error connecting to localhost: %s\n",
				ssh_get_error(my_ssh_session));
			exit(-1);
		}

		// authenticate with password
		rc = ssh_userauth_password(my_ssh_session, NULL, password);
		if (rc != SSH_AUTH_SUCCESS)
		{
			fprintf(stderr, "Error authenticating with password: %s\n",
				ssh_get_error(my_ssh_session));
			ssh_disconnect(my_ssh_session);
			ssh_free(my_ssh_session);
			exit(-1);
		}
	}

	int automatic_shell_session(char scripts[][256], unsigned commandCount) {
		ssh_channel channel = ssh_channel_new(my_ssh_session);
		if (channel == NULL) return SSH_ERROR;

		// open session
		int rc = ssh_channel_open_session(channel);
		if (rc != SSH_OK)
		{
			ssh_channel_free(channel);
			return rc;
		}
		// interative session
		char buffer[256];
		int nbytes, nwritten;

		// request interative shell
		rc = ssh_channel_request_pty(channel);
		if (rc != SSH_OK) return rc;
		rc = ssh_channel_change_pty_size(channel, 80, 24);
		if (rc != SSH_OK) return rc;
		rc = ssh_channel_request_shell(channel);
		if (rc != SSH_OK) return rc;

		// auto script
		bool scriptFinished = false;
		while (ssh_channel_is_open(channel) &&
			!ssh_channel_is_eof(channel) && !scriptFinished)
		{
			nbytes = ssh_channel_read_nonblocking(channel, buffer, sizeof(buffer), 0);
			if (nbytes < 0) return SSH_ERROR;
			if (nbytes > 0)
			{
				nwritten = _write(1, buffer, nbytes);
				if (nwritten != nbytes) return SSH_ERROR;
			}

			for (unsigned i = 0; i < commandCount; i++) {
				nbytes = strlen(scripts[i]);
				//std::cout << "Bytes:" << nbytes << std::endl;
				if (nbytes > 0)
				{
					nwritten = ssh_channel_write(channel, scripts[i], nbytes);
					if (nwritten != nbytes) return SSH_ERROR;
				}

				using namespace std::literals;
				std::this_thread::sleep_for(0.5s);// 0.5 second

				while (true) {
					nbytes = ssh_channel_read_nonblocking(channel, buffer, sizeof(buffer), 0);
					if (nbytes < 0) return SSH_ERROR;
					if (nbytes == 0) break;
					if (nbytes > 0)
					{
						nwritten = _write(1, buffer, nbytes);
						if (nwritten != nbytes) return SSH_ERROR;
						std::this_thread::sleep_for(100ms);// 0.1 second
					}
				}
				std::this_thread::sleep_for(0.5s);// 0.5 second
			}
			scriptFinished = true;
		}
		std::cout << "script finished" << std::endl;
		ssh_channel_close(channel);
		ssh_channel_send_eof(channel);
		ssh_channel_free(channel);
		return rc;
	}
	int exec_shell_session(char scripts[][256], unsigned commandCount) {
		ssh_channel channel = ssh_channel_new(my_ssh_session);
		if (channel == NULL) return SSH_ERROR;

		// open session
		int rc = ssh_channel_open_session(channel);
		if (rc != SSH_OK)
		{
			ssh_channel_free(channel);
			return rc;
		}
		for(unsigned i =0; i<commandCount;i++){
			rc = ssh_channel_request_exec(channel, scripts[i]);
			if (rc != SSH_OK)
			{
				ssh_channel_close(channel);
				ssh_channel_free(channel);
				return rc;
			}

			// read session
			char buffer[256];
			int nbytes, nwritten;

			nbytes = ssh_channel_read(channel, buffer, sizeof(buffer), 0);
			while (nbytes > 0)
			{
				if (fwrite(buffer, 1, nbytes, stdout) != nbytes)
				{
					ssh_channel_close(channel);
					ssh_channel_free(channel);
					return SSH_ERROR;
				}
				nbytes = ssh_channel_read(channel, buffer, sizeof(buffer), 0);
			}

			if (nbytes < 0)
			{
				ssh_channel_close(channel);
				ssh_channel_free(channel);
				return SSH_ERROR;
			}
		}
		std::cout << "exec finished" << std::endl;
		ssh_channel_close(channel);
		ssh_channel_send_eof(channel);
		ssh_channel_free(channel);
		return SSH_OK;
	}
	~ugSession() {
		ssh_disconnect(my_ssh_session);
		ssh_free(my_ssh_session);
	}
};

#endif // !ugSession
