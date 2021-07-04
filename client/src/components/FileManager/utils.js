// https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string/10420404
export const humanFileSize = (size_in_bytes) => {
    const i = (size_in_bytes === 0) ? 0 : Math.floor(Math.log(size_in_bytes) / Math.log(1024));
    return (size_in_bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
};

export const htmlResponseToReason = (response) => {
    const html = document.createElement('html');
    html.innerHTML = response;
    const reasonHTML = html.children[1];
    return reasonHTML.innerText;
};
