export const htmlResponseToReason = (response) => {
    const html = document.createElement('html');
    html.innerHTML = response;
    const reasonHTML = html.children[1];
    try {
        const reasonTitle = reasonHTML.children[0].innerText
        const reasonContent = reasonHTML.children[1].innerText
        return `${reasonTitle} - ${reasonContent}`;
    } catch (_) {
        return reasonHTML.innerText
    }

};