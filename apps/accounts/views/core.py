import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from hhs_oauth_server.hhs_oauth_server_context import IsAppInstalled

from ..forms import *
from ..models import *
from ..emails import send_invite_request_notices
from ..utils import validate_activation_key
from django.conf import settings

logger = logging.getLogger('hhs_server.%s' % __name__)


def request_developer_invite(request):
    name = 'Request a Developer Invite to the CMS Blue Button API'
    additional_info = """
    <p>The CMS Blue Button API is a new feature from Medicare. CMS Blue Button
    API enables beneficiaries to connect their data to applications and
    research programs they trust.</p>
    <p>Register an account and an application and you can empower beneficiaries
    to download their claims information to the innovative apps you create
    to help them stay healthy.</p>
    <p>We are rolling out CMS Blue Button API in phases to gather feedback on
    the new features. To become a CMS Blue Button API developer you must
    request an invitation code by filling in this form. We will send you an
    email with the invitation link.</p>
    <h4>Let's get started...</h4>
    """
    # FIXME: variable not used
    # u_type = 'DEV'
    if request.method == 'POST':
        form = RequestDeveloperInviteForm(request.POST)
        if form.is_valid():

            invite_request = form.save()
            # Set the invite user_type to DEV
            invite_request.user_type = "DEV"
            invited_email = invite_request.email
            invite_request.save()

            send_invite_request_notices(invite_request)

            messages.success(
                request,
                _('Your invite request has been received.  '
                  'You will be contacted by email when your '
                  'invitation is ready.'),
            )
            if IsAppInstalled('apps.extapi'):
                # Installation Specific code
                logger.debug("email to invite:%s" % invited_email)
                issued_invite = issue_invite(invited_email, user_type="DEV")
                if issued_invite:
                    logger.debug("Invite Code:%s" % issued_invite)
                    return HttpResponseRedirect(reverse('accounts_create_developer'))
            if settings.MFA:
                return HttpResponseRedirect(reverse('mfa_login'))
            else:
                return HttpResponseRedirect(reverse('login'))
        else:
            return render(request, 'generic/bootstrapform.html', {
                'name': name,
                'form': form,
                'additional_info': additional_info,
            })
    else:
        # this is an HTTP  GET
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name,
                       'form': RequestDeveloperInviteForm(),
                       'additional_info': additional_info})


def request_user_invite(request):
    name = 'Request an Invite to CMS Blue Button API'
    additional_info = """
    <p>CMS Blue Button API is a new feature from Medicare. CMS Blue Button API
    connects your data to applications and research programs you trust.</p>
    <p>Authorize an application and it will download data automatically on
    your behalf.</p>
    <p>We are rolling out CMS Blue Button API in phases to gather feedback on
    the new features. To try CMS Blue Button API for yourself you must request
    an invitation code by filling in this form. We will send you an email
    with the invitation link. You must click on the link in the email to
    add the CMS Blue Button API to your Medicare account.</p>
    <h4>Let's get started...</h4>
    """
    # FIXME: variable not used
    # u_type = 'BEN'
    if request.method == 'POST':
        form = RequestUserInviteForm(request.POST)
        if form.is_valid():

            invite_request = form.save()
            # Set the invite user_type to BEN
            invite_request.user_type = "BEN"
            invited_email = invite_request.email

            invite_request = form.save()

            send_invite_request_notices(invite_request)

            messages.success(
                request,
                _('Your invite request has been received.  '
                  'You will be contacted by email when your '
                  'invitation is ready.'),
            )
            if IsAppInstalled('apps.extapi'):
                # Installation Specific code
                logger.debug("email to invite:%s" % invited_email)
                issued_invite = issue_invite(invited_email, user_type="BEN")
                if issued_invite:
                    logger.debug("Invite Code:%s" % issued_invite)
                    return HttpResponseRedirect(reverse('accounts_create_user'))

            if settings.MFA:
                return HttpResponseRedirect(reverse('mfa_login'))
            else:
                return HttpResponseRedirect(reverse('login'))
        else:
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name,
                           'form': form,
                           'additional_info': additional_info})
    else:
        # this is an HTTP  GET
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name,
                       'form': RequestUserInviteForm(),
                       'additional_info': additional_info})


def mylogout(request):
    logout(request)
    messages.success(request, _('You have been logged out.'))
    if settings.MFA:
        return HttpResponseRedirect(reverse('mfa_login'))
    else:
        return HttpResponseRedirect(reverse('login'))


def simple_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    next_param = request.GET.get('next', '')
                    if next_param:
                        # If a next is in the URL, then go there
                        return HttpResponseRedirect(next_param)
                    # otherwise just go to home.
                    return HttpResponseRedirect(reverse('home'))
                else:
                    # The user exists but is_active=False
                    messages.error(request,
                                   _('Please check your email for a link to '
                                     'activate your account.'))
                    return render(request, 'login.html', {'form': form})
            else:
                messages.error(request, _('Invalid username or password.'))
                return render(request, 'login.html', {'form': form})

        else:
            return render(request, 'login.html', {'form': form})
    # this is a GET
    return render(request, 'login.html', {'form': LoginForm()})


@login_required
def display_api_keys(request):
    up = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'display-api-keys.html', {'up': up})


@login_required
def reissue_api_keys(request):
    up = get_object_or_404(UserProfile, user=request.user)
    up.access_key_reset = True
    up.save()
    messages.success(request, _('Your API credentials have been reissued.'))
    return HttpResponseRedirect(reverse('display_api_keys'))


def create_developer(request):
    """ Replaced by create_developer_generic """

    name = "Create a Developer Account"

    if request.method == 'POST':
        form = SignupDeveloperForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             _("Your developer account was created. Please "
                               "check your email to verify your account."))

            if settings.MFA:
                return HttpResponseRedirect(reverse('mfa_login'))
            else:
                return HttpResponseRedirect(reverse('login'))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        messages.info(request,
                      _("An invitation code is required to register."))
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name, 'form': SignupDeveloperForm()})


def create_user(request):
    """ Replaced by create_user_generic """

    name = "Create a Medicare Beneficiary Account"

    if request.method == 'POST':
        form = SignupUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             _("Your account was created. Please "
                               "check your email to verify your account."))

            if settings.MFA:
                return HttpResponseRedirect(reverse('mfa_login'))
            else:
                return HttpResponseRedirect(reverse('login'))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        messages.info(request,
                      _("An invitation code is required to register."))
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name, 'form': SignupUserForm()})


def create_developer_generic(request):
    """ Pass through to create_account """

    mode = {"type": "DEV",
            "name": "Create a Developer Account"}
    return create_account(request, mode)


def create_user_generic(request):
    """ Pass through to create_account """

    mode = {"type": "BEN",
            "name": "Create a Beneficiary Account"}
    return create_account(request, mode)


def create_account(request, mode={"type": "BEN"}):
    """ Generic Create Account """
    if mode['type'] == "DEV":
        long_type = "Developer"
    elif mode['type'] == "BEN":
        long_type = "Beneficiary"
    else:
        long_type = "User"

    if 'name' in mode:
        name = mode['name']
    if name:
        pass
    elif mode['type'] == "BEN":
        name = "Create a Beneficiary Account"
    elif mode['type'] == "DEV":
        name = "Create a Developer Account"
    else:
        name = "Create an Account"

    if request.method == 'POST':
        if mode['type'] == "DEV":
            form = SignupDeveloperForm(request.POST)
        else:
            form = SignupUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             _("Your %s account was created. "
                               "Please check your email to verify "
                               "your account." % long_type))

            if settings.MFA:
                return HttpResponseRedirect(reverse('mfa_login'))
            else:
                return HttpResponseRedirect(reverse('login'))
        else:
            # return the bound form with errors
            return render(request,
                          'generic/bootstrapform.html',
                          {'name': name, 'form': form})
    else:
        # this is an HTTP  GET
        form_data = {'invitation_code': request.GET.get('invitation_code', ''),
                     'email': request.GET.get('email', '')}
        if mode['type'] == "DEV":
            form = SignupDeveloperForm(initial=form_data)
        else:
            form = SignupUserForm(initial=form_data)
        if form_data['invitation_code']:
            pass
        else:
            messages.info(request,
                          _("An invitation code is required to register."))
        return render(request,
                      'generic/bootstrapform.html',
                      {'name': name, 'form': form})


@login_required
def account_settings(request):
    name = _('Account Settings')
    up = get_object_or_404(UserProfile, user=request.user)

    groups = request.user.groups.values_list('name', flat=True)
    for g in groups:
        messages.info(request, _('You are in the group: %s' % (g)))

    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # update the user info
            request.user.username = data['username']
            request.user.email = data['email']
            request.user.first_name = data['first_name']
            request.user.last_name = data['last_name']
            request.user.save()
            # update the user profile
            up.organization_name = data['organization_name']
            up.create_applications = data['create_applications']
            up.mfa_login_mode = data['mfa_login_mode']
            up.mobile_phone_number = data['mobile_phone_number']
            up.save()
            messages.success(request,
                             'Your account settings have been updated.')
            return render(request,
                          'account-settings.html',
                          {'form': form, 'name': name})
        else:
            # the form had errors
            return render(request,
                          'account-settings.html',
                          {'form': form, 'name': name})

    # this is an HTTP GET
    form = AccountSettingsForm(
        initial={
            'username': request.user.username,
            'email': request.user.email,
            'organization_name': up.organization_name,
            'mfa_login_mode': up.mfa_login_mode,
            'mobile_phone_number': up.mobile_phone_number,
            'create_applications': up.create_applications,
            'last_name': request.user.last_name,
            'first_name': request.user.first_name,
            'access_key_reset': up.access_key_reset,
        }
    )
    return render(request,
                  'account-settings.html',
                  {'name': name, 'form': form})


def activation_verify(request, activation_key):
    if validate_activation_key(activation_key):
        messages.success(request,
                         'Your account has been activated. You may now login.')
    else:
        messages.error(request,
                       'This key does not exist or has already been used.')
    if settings.MFA:
        return HttpResponseRedirect(reverse('mfa_login'))
    else:
        return HttpResponseRedirect(reverse('login'))


def issue_invite(email, user_type="BEN"):
    """ Check if an invite is available """
    if invite_available(email, user_type):
        invitation = Invitation()
        invitation.code = random_code()
        invitation.valid = True
        invitation.email = email
        invitation.user_type = user_type
        invitation.save()

        logger.debug("Invitation %s created: %s" % (invitation.code,
                                                    invitation.email))
        return invitation
    else:
        return


def invite_available(email, user_type="BEN"):
    """" Update the issued counter """

    try:
        ia = InvitesAvailable.objects.get(user_type=user_type)
    except InvitesAvailable.DoesNotExist:
        return

    if ia.available <= ia.issued:
        logger.debug("No invites available for %s: %s/%s" % (ia.user_type,
                                                             ia.issued,
                                                             ia.available
                                                             ))
        return
    else:
        ia.issued += 1
        ia.email = email
        ia.save()

        logger.debug("%s invitation:%s to %s" % (ia.user_type,
                                                 ia.issued,
                                                 ia.email))
        return ia
