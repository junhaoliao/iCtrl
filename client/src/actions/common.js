import axios from 'axios';

export const updateTitle = (sessionId, feature) => {
  axios.get('/api/session', {
    params: {
      id: sessionId,
    },
  }).then(response => {
    const {host, username} = response.data;
    document.title = `${feature} - ${username}@${host}`;
  });
};