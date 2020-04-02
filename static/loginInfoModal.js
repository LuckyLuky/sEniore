$(function() {
  if (!window.localStorage) {
    return;
  }

  var key = 'seniore/login-page-map-info';

  const item = window.localStorage.getItem(key);
  if (item) {
    return;
  }

  $('#login-info-modal').modal();
  
  window.localStorage.setItem(key, (new Date()).toISOString());
});