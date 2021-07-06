export const htmlResponseToReason = (response) => {
    const html = document.createElement('html');
    html.innerHTML = response;
    const reasonHTML = html.children[1];
    return reasonHTML.innerText;
};