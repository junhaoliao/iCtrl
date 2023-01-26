/*
 * Copyright (c) 2021-2023 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import React from 'react';
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  LinearProgress,
  Stack,
  Step,
  StepContent,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from '@mui/material';

import {STEP_DONE} from '../../../actions/codes';
import {LoadingButton} from '@mui/lab';
import ChangeMachine from '../ChangeMachine';
import FileCleaner from '../FileCleaner';
import {COLOR_CHANGE_MACHINE} from '../../constants';

function LinearProgressWithLabel(props) {
  return (
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        marginLeft: '12px',
        marginRight: '12px',
      }}>
        <Box sx={{width: '100%', mr: 1}}>
          <LinearProgress variant="determinate" {...props} />
        </Box>
        <Box sx={{minWidth: 35}}>
          <Typography variant="body2" color="text.secondary">{`${Math.round(
              props.value,
          )}%`}</Typography>
        </Box>
      </Box>
  );
}

export default class Loading extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      authSave: true,
      authInput: '',
      authHelperText: ' ',
      submitting: false,
      showChangeMachine: false,
      showFileCleaner: false,
    };
  }

  handleAuthInputChange = (ev) => {
    const newAuthInput = ev.target.value;

    this.setState({
      authInput: newAuthInput,
      authHelperText: this.props.authentication.validator(newAuthInput),
    });
  };

  handleInputSubmit = (ev) => {
    this.setState({
      submitting: true,
    });
    const {authInput, authSave} = this.state;

    this.props.authentication.submitter(authInput, authSave);
    ev.preventDefault();
  };

  handleNoLoadCheck = (_) => {
    const newURL = new URL(window.location);
    newURL.searchParams.set('load-check', 'false');
    window.location = newURL.toString();
  };

  handleShowChangeMachine = (_) => {
    this.setState({
      showChangeMachine: true,
    });
  };

  handleCloseChangeMachine = (_) => {
    this.setState({
      showChangeMachine: false,
    });
  };

  handleShowFileCleaner = (_) => {
    this.setState({
      showFileCleaner: true,
    });
  };

  handleCloseFileCleaner = (_) => {
    this.setState({
      showFileCleaner: false,
    });
  };

  render() {
    const {
      currentStep,
      steps,
      authentication,
      isOverloaded,
      quotaExceeded,
      sessionId,
    } = this.props;
    const {
      authSave,
      submitting,
      showChangeMachine,
      showFileCleaner,
    } = this.state;
    const progressValue = (currentStep === -1) ? 0 :
        ((currentStep === STEP_DONE) ?
            100 :
            currentStep / (steps.length - 1) * 100);
    return (<div style={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}>
          <div style={{flexGrow: 1}}/>
          <div style={{width: '100vw'}}>
            <Stepper style={{maxWidth: 480, margin: 'auto'}}
                     activeStep={currentStep} orientation="vertical">
              {steps.map((step, index) => (
                  <Step key={step.label}>
                    <StepLabel>
                      <Typography
                          variant={'h5'}>{step.label}</Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography color={'dimgrey'}
                                  variant={'body1'}>{step.description}</Typography>
                      <br/>
                    </StepContent>
                    {Boolean(authentication) && index ===
                        currentStep && <>
                          <StepLabel error>
                            <Typography
                                variant={'h5'}>{authentication.label}</Typography>
                          </StepLabel>
                          <StepContent>
                            <Typography color={'dimgrey'}
                                        variant={'body2'}>{authentication.description}</Typography>
                            <br/>
                            <form
                                onSubmit={this.handleInputSubmit}>
                              <Stack spacing={2}
                                     direction="row">
                                <TextField
                                    style={Boolean(
                                        authentication.validator) ?
                                        {} :
                                        {visibility: 'hidden'}}
                                    disabled={submitting}
                                    fullWidth
                                    label="Password"
                                    variant={'standard'}
                                    id="auth-input"
                                    value={this.state.authInput}
                                    onChange={this.handleAuthInputChange}
                                    type={'password'}
                                    autoComplete={'new-password'}
                                    helperText={this.state.authHelperText}
                                    error={this.state.authHelperText !==
                                        ' '}
                                />
                                <LoadingButton
                                    type={'submit'}
                                    style={{
                                      width: 150,
                                      height: 36,
                                      alignSelf: 'center',
                                    }}
                                    variant={'contained'}
                                    loading={submitting}
                                    disabled={Boolean(
                                            authentication.validator) &&
                                        (this.state.authInput ===
                                            '' ||
                                            this.state.authHelperText !==
                                            ' ')}
                                >
                                  {authentication.submitterName}
                                </LoadingButton>
                              </Stack>
                              {authentication.enableSave && <FormControlLabel
                                  control={<Checkbox checked={authSave}
                                                     onChange={(ev) => {
                                                       this.setState(
                                                           {authSave: ev.target.checked});
                                                     }}
                                  />}
                                  label={'Save Credentials'}
                              />}
                            </form>
                          </StepContent>
                        </>}
                    {Boolean(isOverloaded) && index ===
                        currentStep && <>
                          <StepLabel error>
                            <Typography variant={'h5'}>Someone
                              else using the
                              machine?</Typography>
                          </StepLabel>
                          <StepContent>
                            <Typography color={'dimgrey'}
                                        variant={'body2'}>
                              There is more than one user
                              using this machine,
                              or the load on this machine is
                              unusually high.
                              If you are not reusing a
                              session,
                              please consider changing the target machine.
                            </Typography>
                            <br/>
                            <Button onClick={this.handleNoLoadCheck}>
                              Continue
                            </Button>
                            <Button onClick={this.handleShowChangeMachine}
                                    variant={'contained'}
                                    color={'success'}
                                    sx={{
                                      background: COLOR_CHANGE_MACHINE,
                                      '&:hover': {
                                        background: 'rgb(60,140,60)',
                                      },
                                      color: 'white',
                                    }}>
                              Change Machine
                            </Button>
                          </StepContent>
                        </>}
                    {Boolean(quotaExceeded) && index ===
                        currentStep && <>
                          <StepLabel error>
                            <Typography variant={'h5'}>Quota
                              Exceeded</Typography>
                          </StepLabel>
                          <StepContent>
                            <Typography color={'dimgrey'}
                                        variant={'body2'}>
                              iCtrl is unable to perform the
                              action because your disk quota
                              has exceeded.
                              Please clean up any unused
                              files.
                            </Typography>
                            <br/>
                            <Button
                                onClick={this.handleShowFileCleaner}
                                variant={'contained'}>
                              File Cleaner
                            </Button>
                          </StepContent>
                        </>}
                  </Step>
              ))}
            </Stepper>
            <br/><br/>
            <LinearProgressWithLabel
                variant="determinate"
                color={Boolean(authentication) ? 'error' : 'primary'}
                value={progressValue}/>
          </div>
          {showChangeMachine &&
              <ChangeMachine
                  session_id={sessionId}
                  domain={null}
                  onChangeMenuClose={this.handleCloseChangeMachine}/>}
          {showFileCleaner && <FileCleaner sessionID={sessionId}
                                           onClose={this.handleCloseFileCleaner}/>}
        </div>

    );
  }

}