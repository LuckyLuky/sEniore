$(function() {
  var $showPasswordButton = $('#btn-show-password');
  var $hidePasswordButton = $('#btn-hide-password');
  var $passwordInput = $('.password-input');
  if (!$showPasswordButton || !$hidePasswordButton || !$passwordInput) {
    return;
  }

  $showPasswordButton.click(function(e) {
    e.preventDefault();
    $showPasswordButton.css('display', 'none');
    $hidePasswordButton.css('display', 'block');
    $passwordInput.attr('type', 'text');
  });

  $hidePasswordButton.click(function(e) {
    e.preventDefault();
    $hidePasswordButton.css('display', 'none');
    $showPasswordButton.css('display', 'block');
    $passwordInput.attr('type', 'password');
  });
});
