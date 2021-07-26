export const htmlResponseToReason = (response) => {
    const html = document.createElement('html');
    html.innerHTML = response;
    const reasonHTML = html.children[1];
    try {
        const reasonTitle = reasonHTML.children[0].innerText;
        const reasonContent = reasonHTML.children[1].innerText;
        return `${reasonTitle} - ${reasonContent}`;
    } catch (_) {
        return reasonHTML.innerText;
    }

};

// Reference: https://stackoverflow.com/questions/9038625/detect-if-device-is-ios
export const iOS = () => {
    return [
            'iPad Simulator',
            'iPhone Simulator',
            'iPod Simulator',
            'iPad',
            'iPhone',
            'iPod'
        ].includes(navigator.platform)
        // iPad on iOS 13 detection
        || (navigator.userAgent.includes('Mac') && 'ontouchend' in document);
};

export const canChangeMachine = (hostname) => {
    return hostname.endsWith('.eecg.toronto.edu') ||
        hostname.endsWith('.ecf.toronto.edu') ||
        hostname.endsWith('.eecg.utoronto.ca') ||
        hostname.endsWith('.ecf.utoronto.ca');
};