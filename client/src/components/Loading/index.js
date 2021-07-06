import React from 'react';
import {
    Box,
    Button,
    LinearProgress,
    Stack,
    Step,
    StepContent,
    StepLabel,
    Stepper,
    TextField,
    Typography
} from '@material-ui/core';

function LinearProgressWithLabel(props) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ width: '100%', mr: 1 }}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box sx={{ minWidth: 35 }}>
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
            authInput: '',
            authHelperText: ' '
        };
    }

    handleAuthInputChange = (ev) => {
        const newAuthInput = ev.target.value;

        this.setState({
            authInput: newAuthInput,
            authHelperText: this.props.authentication.validator(newAuthInput)
        });
    };

    render() {
        const {currentStep, steps, authentication} = this.props
        return (<div>
            <div style={{position: 'fixed', bottom: 0, width: '100vw'}}>
                <Stepper style={{maxWidth: 480, margin: 'auto'}} activeStep={currentStep} orientation="vertical">
                    {steps.map((step, index) => (
                        <Step key={step.label}>
                            <StepLabel>
                                <Typography variant={'h5'}>{step.label}</Typography>
                            </StepLabel>
                            <StepContent>
                                <Typography color={'dimgrey'} variant={'body1'}>{step.description}</Typography>
                                <br/>
                            </StepContent>
                            {Boolean(authentication) && index === currentStep && <StepLabel error>
                                <Typography variant={'h5'}>{authentication.label}</Typography>
                            </StepLabel>}
                            {Boolean(authentication) && index === currentStep && <StepContent>
                                <Typography color={'dimgrey'}
                                            variant={'body2'}>{authentication.description}</Typography>
                                <br/>
                                <form onSubmit={(ev)=>{
                                    authentication.submitter(this.state.authInput);
                                    ev.preventDefault();
                                }}>
                                    <Stack spacing={2} direction="row">
                                    <TextField
                                        fullWidth
                                        label="Password"
                                        variant={'standard'}
                                        id="auth-input"
                                        value={this.state.authInput}
                                        onChange={this.handleAuthInputChange}
                                        type={'password'}
                                        autoComplete={'new-password'}
                                        helperText={this.state.authHelperText}
                                        error={this.state.authHelperText !== ' '}
                                    />
                                    <Button
                                        type={'submit'}
                                        style={{width: 150, height: 36, alignSelf: 'center'}}
                                        variant={'contained'}
                                        disabled={this.state.authInput === '' || this.state.authHelperText !== ' '}
                                    >
                                        Confirm
                                    </Button>
                                </Stack>
                                </form>
                            </StepContent>}
                        </Step>
                    ))}
                </Stepper>
                <br/><br/>
                <LinearProgressWithLabel variant="determinate" value={currentStep/(steps.length-1)*100} />
            </div>
        </div>



        );
    }

}