(function () {

    $(function () {
        $('#LoginForm').submit(function (e) {
            e.preventDefault();
            abp.ui.setBusy(
                $('#LoginArea'),
                abp.ajax({
                    url: abp.appPath + 'Account/Login',
                    type: 'POST',
                    data: JSON.stringify({
                        tenancyName: $.trim($('#TenancyName').val()),
                        usernameOrEmailAddress: $.trim($('#EmailAddressInput').val()),
                        password: $('#PasswordInput').val(),
                        rememberMe: $('#RememberMeInput').is(':checked'),
                        returnUrlHash: $('#ReturnUrlHash').val(),
                        idaasToken: $('input[name="idaasToken"]').val()
                    })
                }).done(function (result) {
                    $("#resultMsg").show();
                })
            );
        });

        $('a.social-login-link').click(function () {
            var $a = $(this);
            var $form = $a.closest('form');
            $form.find('input[name=provider]').val($a.attr('data-provider'));
            $form.submit();
        });

        $('#ReturnUrlHash').val(location.hash);

        $('#LoginForm #EmailAddressInput').focus();
    });

})();