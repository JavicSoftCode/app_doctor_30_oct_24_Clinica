from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

# from aplication.core.views.home import HomeTemplateView
# from aplication.core.views.home import HomeTemplateView, filter_atenciones, filter_citas, filter_citas_estado
from aplication.security.views import auth, groupModulePermissions, menus, modulos, user
from aplication.security.views.groupModulePermissions import get_group_permissions

app_name = "security"

urlpatterns = [
                # ___________________ CREDENCIALES ADMIN  ___________________

                # URLS de login & logout & signup & profile & changue profile & changue password
                path('auth/login/', auth.SigninView.as_view(), name="auth_login"),
                path('auth/logout/', auth.SignoutView.as_view(), name='auth_logout'),
                path('auth/signup/', auth.SignupView.as_view(), name='auth_signup'),
                path('auth/profile/', auth.ProfileView.as_view(), name='auth_profile'),
                path('auth/update_profile/', auth.UpdateProfileView.as_view(), name='auth_update_profile'),
                path('auth/change_password/', auth.ChangePasswordView.as_view(), name='auth_change_password'),

                # _________________________ SEGURIDAD _________________________

                # URLS de modulos
                path('modules_list/', modulos.ModuleListView.as_view(), name='modules_list'),
                path('modules_create/', modulos.ModuleCreateView.as_view(), name='modules_create'),
                path('modules_update/<int:pk>/', modulos.ModuleUpdateView.as_view(), name='modules_update'),
                path('modules_delete/<int:pk>/', modulos.ModuleDeleteView.as_view(), name='modules_delete'),
                path('modules-suggestions/', modulos.ModuleSuggestionsView.as_view(), name='modules_suggestions'),

                # URLS de menu
                path('menus_list/', menus.MenuListView.as_view(), name='menus_list'),
                path('menus_create/', menus.MenuCreateView.as_view(), name='menus_create'),
                path('menus_update/<int:pk>/', menus.MenuUpdateView.as_view(), name='menus_update'),
                path('menus_delete/<int:pk>/', menus.MenuDeleteView.as_view(), name='menus_delete'),
                path('menus-suggestions/', menus.MenuSuggestionsView.as_view(), name='menus_suggestions'),

                # URLS de grupo modulos permios
                path('groupmodulepermission_list/', groupModulePermissions.GroupModulePermissionListView.as_view(),
                     name='groupmodulepermission_list'),
                path('groupmodulepermission_create/', groupModulePermissions.GroupModulePermissionCreateView.as_view(),
                     name='groupmodulepermission_create'),
                path('get_group_permissions/<int:group_id>/', get_group_permissions, name='get_group_permissions'),
                path('groupmodulepermission-suggestions/',
                     groupModulePermissions.GroupModulePermissionSuggestionsView.as_view(),
                     name='groupmodulepermission_suggestions'),

                # URLS de usuarios
                path('users_list/', user.UsersListView.as_view(), name='users_list'),
                path('users/create/', user.UserCreateView.as_view(), name='users_create'),
                path('users/update/<int:pk>/', user.UserUpdateView.as_view(), name='users_update'),
                path('users/delete/<int:pk>/', user.UserDeleteView.as_view(), name='users_delete'),
                path('users/groups/<int:user_id>/', user.UserGroupView.as_view(), name='users_groups'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
