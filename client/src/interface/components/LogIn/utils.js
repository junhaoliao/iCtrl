export const special_symbols = [
  '!',
  '@',
  '#',
  '$',
  '%',
  '^',
  '&',
  '*',
  '(',
  ')',
  '-',
  '+'];

export const hasNumeral = (str) => {
  return str.match(/\d+/g);
};

export const hasLowerCase = (str) => {
  return str.toUpperCase() !== str;
};

export const hasUpperCase = (str) => {
  return str.toLowerCase() !== str;
};

export const hasSpecialSymbols = (str) => {
  let hasSymbol = false;
  special_symbols.forEach((item, _) => {
    if (str.indexOf(item) > 0) {
      hasSymbol = true;
    }
  });
  return hasSymbol;
};