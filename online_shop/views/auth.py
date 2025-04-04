from online_shop.forms import AccountUpdateForm, EmailForm, RegisterForm, ForgotPasswordForm, LoginForm
from django.contrib.auth.views import PasswordResetConfirmView, LogoutView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from online_shop.token import account_activation_token
from django.template.loader import render_to_string
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_str
from config.settings import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views.generic import View
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages

class LoginMixin:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('online_store:index_page')
        return super().get(request, *args, **kwargs)


class ActivateEmailView(View):
    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "Your account has been successfully activated!")
            return redirect(reverse_lazy('online_store:index_page'))
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect (reverse_lazy('online_store:login'))

        

@login_required
def account_update(request):
    user = request.user
    form = AccountUpdateForm(instance=user)

    if request.method == "POST":
        form = AccountUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been updated successfully!")
            return redirect('online_store:account')
    return render(request, 'auth/account.html', {'form': form})


def send_activation_email(email, request):
    try:
        user = User.objects.get(email=email)
        subject = 'Password Reset Request'
        current_site = get_current_site(request)

        html_message = render_to_string('auth/reset-password-email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })

        from_email = EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject,
                    message = "User an HTML compatible email client to view this message",
                      from_email = from_email,
                        recipient_list = recipient_list,
                        fail_silently=False,
                        html_message=html_message)
        return True
    except User.DoesNotExist:
        return False

class ForgotPasswordPage(FormView):
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('auth:login_page')
    template_name = 'auth/forgot-password.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        email_sent = send_activation_email(email, self.request)

        if email_sent:
            messages.success(self.request, "A password sent your email pls check your inbox")
        else:
            messages.error(self.request, "No account found with this email")
            return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.error(self.request, "Invalid email. Please enter valid email address")
        return self.render_to_response(self.get_contect_data(form=form))

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                send_mail(
                    subject="Password reset request",
                    message="Click the link below to reset your password.",
                    from_email="shobushomurotov@gmail.com",
                    recipient_list=[user.email],
                )
                messages.success(request, "A password reset email has been sent.")
                return redirect(reverse_lazy('auth:login_page'))
            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")
                return redirect('auth:reset-password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'auth/forgot-password.html', {'form': form})


class RegisterPage(FormView):
    form_class = RegisterForm
    success_url = reverse_lazy('online_store:index_page')
    template_name = 'auth/registration.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


def reset_password(request):
    return render(request, 'auth/confirm-mail.html')

class CustomResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'auth/reset-password.html'
    success_url = reverse_lazy('password-reset-complete')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activated successfully! <a href="/">Go to home page</a>')
    else:
        return HttpResponse('Activation link is invalid!')


def sending_email(request):
    sent = False
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            from_email = request.POST.get('from_email')
            to = request.POST.get('to')
            send_mail(subject, message, from_email, [to])
            sent = True
    else:
        form = EmailForm()
    return render(request, 'auth/sending-email.html', {'form': form, 'sent': sent})

def verify_email_done(request):
    return render(request, 'online_store/email/verify-email-done.html')


def verify_email_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user:
        if user.is_active:
            messages.info(request, 'Your account has already been activated. Please log in')
            return redirect('login')
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been succesfully activated')
            return redirect('verify_email_complete')
    else:
        messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
    return render(request, 'online_store/email/verify-email-confirm.html')


def verify_email_complete(request):
    return render(request, 'online_store/email/verify-email-complete.html')

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return reverse_lazy('online_store:index_page')


class LoginPage(LoginMixin, FormView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        return reverse_lazy('online_store:index_page')



def account(request):
    return render(request, 'auth/account.html')

@login_required
def update_account(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)

        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password and password == password_confirm:
            user.set_password(password)
            update_session_auth_hash(request, user)

        user.save()
        messages.success(request, "Your account has been updated successfully!")
        return redirect("online_store:index_page")

    return render(request, "online_store/index.html")
