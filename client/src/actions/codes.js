export const STEP_DONE = 31;
const ERROR_GENERAL = 100;

class VNCError {
  static GENERAL = ERROR_GENERAL + 20;
  static PASSWD_MISSING = this.GENERAL + 1;
  static QUOTA_EXCEEDED = this.GENERAL + 2;
}

class SSHError {
  static GENERAL = 200;
  static HOST_UNREACHABLE = this.GENERAL + 1;
  static AUTH_MISSING = this.GENERAL + 2;
  static AUTH_WRONG = this.GENERAL + 3;
  static OVER_LOADED = this.GENERAL + 4;
}

export const ICtrlError = {
  VNC: VNCError,
  SSH: SSHError,
};

const VNCStepCodes = {
  SSH_AUTH: 0,
  CHECK_LOAD: 1,
  PARSE_PASSWD: 2,
  LAUNCH_VNC: 3,
  CREATE_TUNNEL: 4,
  DONE: STEP_DONE,
};

const TermStepCodes = {
  SSH_AUTH: 0,
  CHECK_LOAD: 1,
  LAUNCH_SHELL: 2,
  DONE: STEP_DONE,
};

export const ICtrlStep = {
  VNC: VNCStepCodes,
  Term: TermStepCodes,
};