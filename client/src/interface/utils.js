export const changeFavicon = (href) => {
  const link = document.getElementById('favicon');
  link.href = href;
};

export const addScript = (scriptLink) => {
  const script = document.createElement('script');
  script.src = scriptLink;
  script.async = true;

  document.body.appendChild(script);
};